// DC Motor PID Speed Control - Arduino Mega 2560 + L298N + 334 CPR encoder
// Implements R1 (interrupt encoder, RPM every 10 ms), R2 (PID + anti-windup),
// R4 (SET command at 115200 baud) and R5 (telemetry stream).
// Logic mirrors the tested Python modules in src/ (encoder.py, pid.py,
// controller.py, protocol.py).

// ---------- Pins (Mega 2560: pins 2 and 3 are external interrupts) ----------
const uint8_t ENC_A = 2;
const uint8_t ENC_B = 3;
const uint8_t PIN_ENA = 5;   // L298N ENA (PWM)
const uint8_t PIN_IN1 = 7;   // L298N IN1
const uint8_t PIN_IN2 = 8;   // L298N IN2

// ---------- Constants (SPEC sections 2 and 4) ----------
const long  EDGES_PER_REV = 334L * 4;       // 4x quadrature decoding
const unsigned long PERIOD_US = 10000UL;    // 10 ms -> 100 Hz
const float DT = 0.01f;
const uint8_t WINDOW = 10;                  // 100 ms moving window (bug B1)
const float MAX_RPM = 300.0f;

// ---------- Encoder state (written in ISRs) ----------
volatile long encoderCount = 0;
volatile uint8_t lastState = 0;

// Quadrature lookup: index = (old << 2) | new, value = -1, 0 or +1
const int8_t QDEC[16] = {0,+1,-1,0, -1,0,0,+1, +1,0,0,-1, 0,-1,+1,0};

void encoderISR() {
  uint8_t s = (digitalRead(ENC_A) << 1) | digitalRead(ENC_B);
  encoderCount += QDEC[(lastState << 2) | s];
  lastState = s;
}

// ---------- PID (same as src/pid.py) ----------
float kp = 1.2f, ki = 8.0f, kd = 0.0f;
float setpoint = 0.0f;
float integral = 0.0f;
float prevMeasured = 0.0f;
bool  firstStep = true;

float pidUpdate(float sp, float measured) {
  float error = sp - measured;
  integral += error * DT;
  if (ki > 0) {                       // anti-windup: keep Ki*I in [0, 255]
    integral = constrain(integral, 0.0f, 255.0f / ki);
  } else {
    integral = 0.0f;
  }
  float derivative = firstStep ? 0.0f : -(measured - prevMeasured) / DT;
  firstStep = false;
  prevMeasured = measured;
  float out = kp * error + ki * integral + kd * derivative;
  return constrain(out, 0.0f, 255.0f);
}

// ---------- Speed estimate: 100 ms moving window, new value every 10 ms ----------
long history[WINDOW];
uint8_t histIdx = 0, histLen = 0;
long histSum = 0;
long prevCount = 0;

float updateRpm() {
  noInterrupts();
  long c = encoderCount;
  interrupts();
  long delta = c - prevCount;
  prevCount = c;
  if (histLen == WINDOW) histSum -= history[histIdx]; else histLen++;
  history[histIdx] = delta;
  histSum += delta;
  histIdx = (histIdx + 1) % WINDOW;
  float rpm = (float)histSum / EDGES_PER_REV / (DT * histLen) * 60.0f;
  return fabs(rpm);   // one direction only (velocity control)
}

// ---------- Serial command: SET,<sp>,<Kp>,<Ki>,<Kd> ----------
char buf[64];
uint8_t bufLen = 0;

void handleCommand(char *line) {
  float v[4];
  char *tok = strtok(line, ",");
  if (!tok || strcmp(tok, "SET") != 0) { Serial.println(F("ERR,Invalid command")); return; }
  for (uint8_t i = 0; i < 4; i++) {
    tok = strtok(NULL, ",");
    char *end;
    if (!tok) { Serial.println(F("ERR,Invalid command")); return; }
    v[i] = strtod(tok, &end);
    if (end == tok) { Serial.println(F("ERR,Invalid number")); return; }
  }
  if (strtok(NULL, ",")) { Serial.println(F("ERR,Invalid command")); return; }
  if (v[0] < 0 || v[0] > MAX_RPM) { Serial.println(F("ERR,Setpoint must be between 0 and 300 RPM")); return; }
  setpoint = v[0]; kp = v[1]; ki = v[2]; kd = v[3];
  Serial.print(F("ACK,"));
  Serial.print(setpoint, 0); Serial.print(',');
  Serial.print(kp, 3); Serial.print(',');
  Serial.print(ki, 3); Serial.print(',');
  Serial.println(kd, 3);
}

void readSerial() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') {
      if (bufLen) { buf[bufLen] = '\0'; handleCommand(buf); bufLen = 0; }
    } else if (bufLen < sizeof(buf) - 1) {
      buf[bufLen++] = ch;
    } else {
      bufLen = 0;                     // line too long: drop it
      Serial.println(F("ERR,Line too long"));
    }
  }
}

void setMotor(int pwm) {
  digitalWrite(PIN_IN1, HIGH);        // forward only
  digitalWrite(PIN_IN2, LOW);
  analogWrite(PIN_ENA, pwm);
}

// ---------- Main ----------
unsigned long nextTick, t0;
unsigned long tick = 0;            // number of 10 ms periods since start

void setup() {
  Serial.begin(115200);
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);
  pinMode(PIN_ENA, OUTPUT);
  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  lastState = (digitalRead(ENC_A) << 1) | digitalRead(ENC_B);
  attachInterrupt(digitalPinToInterrupt(ENC_A), encoderISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_B), encoderISR, CHANGE);
  setMotor(0);
  Serial.println(F("READY"));
  t0 = micros();
  nextTick = t0 + PERIOD_US;
}

void loop() {
  readSerial();
  if ((long)(micros() - nextTick) >= 0) {   // overflow-safe 100 Hz tick
    nextTick += PERIOD_US;
    tick++;
    float rpm = updateRpm();
    float pwm = (setpoint > 0) ? pidUpdate(setpoint, rpm) : 0;
    if (setpoint == 0) { integral = 0; firstStep = true; }
    setMotor((int)(pwm + 0.5f));
    // Telemetry: <timestamp_ms>,<setpoint_rpm>,<measured_rpm>,<pwm_output>
    Serial.print(tick * 10UL); Serial.print(',');
    Serial.print(setpoint, 0); Serial.print(',');
    Serial.print(rpm, 1); Serial.print(',');
    Serial.println((int)(pwm + 0.5f));
  }
}
