# Project Specification: DC Motor PID Speed Control

## 1. Goal and Users
* **Goal:** Design and implement a closed-loop PID control system on an Arduino to regulate DC motor rotational speed using encoder feedback, alongside a desktop plotting interface for real-time visualization of step responses and tuning parameters.
* **Target Users:** Control systems students, lab instructors, and mechatronics hobbyists needing an interactive platform to test and evaluate PID tuning parameters.

## 2. Context
* **Hardware:**
  * Microcontroller: Arduino Mega 2560 Rev3
  * Motor Driver: L298N Dual H-Bridge Module
  * Actuator: 12V DC Gear Motor with integrated quadrature optical encoder (334 CPR)
  * Power Supply: External 12V DC / 2A supply
* **Software & Toolchain:**
  * Microcontroller Firmware: C++ / Arduino IDE v2.x
  * Host Analysis & Visualization: Python 3.10+ (using `matplotlib` and `pyserial`)
  * Operating System: Cross-platform (Windows / macOS / Linux)

## 3. Requirements
* **R1:** The system shall read pulse signals from a quadrature encoder using hardware interrupts to calculate current speed in RPM every 10 ms.
* **R2:** The PID algorithm shall compute the control output (PWM) using proportional, integral, and derivative terms with anti-windup protection.
* **R3:** The motor speed shall settle within $\pm 5\%$ of a step target of 120 RPM in under 1.0 second.
* **R4:** The controller shall accept PID gain parameters ($K_p$, $K_i$, $K_d$) and speed setpoints via Serial communication at 115200 baud.
* **R5:** The system shall log setpoint, measured RPM, and PWM output over Serial to a Python script that displays real-time step response and tuning plots.

## 4. Constraints
* The maximum operating motor speed shall be limited by hardware to 300 RPM.
* Control loop iteration frequency must strictly operate at $100\text{ Hz}$ ($\Delta t = 10\text{ ms}$).
* Total physical demonstration time must be completed within 10 minutes.

## 5. Interfaces

### Inputs
* **Serial Commands (Host $\rightarrow$ Arduino):**
  * Format: `SET,<setpoint_rpm>,<Kp>,<Ki>,<Kd>\n`
  * Example: `SET,120,1.2,0.05,0.01`

### Outputs
* **Serial Telemetry Stream (Arduino $\rightarrow$ Host):**
  * Acknowledgement (Arduino $\rightarrow$ Host): `ACK,<setpoint>,<Kp>,<Ki>,<Kd>` (gains with 3 decimals) or `ERR,<reason>` for invalid commands.
  * Format: `<timestamp_ms>,<setpoint_rpm>,<measured_rpm>,<pwm_output>\n`
  * Example: `1000,120,118.5,142`
* **Desktop Plot:** A 2D plot showing target speed vs. actual speed over time.

## 6. Acceptance Criteria

### Requirement 1 (R1)
* **Given:** A motor rotating at a known constant speed of 100 RPM measured via tachometer.
* **When:** The encoder interrupt routine processes state changes over a $10\text{ ms}$ interval.
* **Then:** The calculated RPM returned by the system shall be within $\pm 2\text{ RPM}$ of the measured reference.

### Requirement 2 (R2)
* **Given:** The control output reaches maximum PWM saturation (255) due to a step change.
* **When:** The setpoint error persists.
* **Then:** The integral term shall be clamped at max/min bounds to prevent integrator windup upon settling.

### Requirement 3 (R3)
* **Given:** The motor is initially at rest (0 RPM) and a step setpoint of 120 RPM is commanded.
* **When:** The PID control loop actively adjusts motor PWM.
* **Then:** The measured RPM must reach and stay within $114\text{ RPM}$ to $126\text{ RPM}$ ($\pm 5\%$) within $1.0\text{ second}$.

### Requirement 4 (R4)
* **Given:** The system is actively controlling motor speed using initial gain parameters.
* **When:** A string `SET,150,2.0,0.1,0.0` is sent over Serial.
* **Then:** The Arduino updates $K_p=2.0$, $K_i=0.1$, $K_d=0.0$, sets the new target to $150\text{ RPM}$, and returns an acknowledgement message.

### Requirement 5 (R5)
* **Given:** The host plotting script is listening on the active Serial port.
* **When:** A 120 RPM step response test is executed.
* **Then:** The script renders a real-time window showing step response data points logged at $100\text{ Hz}$ without dropping frames or losing connection.

## 7. Out of Scope and Open Questions
* **Out of Scope:**
  * Hardware position/angle tracking (only velocity control is in scope).
  * Graphical user interface (GUI) button controls (Serial CLI and script execution are sufficient).
  * Dual-channel motor synchronization.
* **Open Questions:**
  * Will motor loading under external mechanical resistance require feedforward terms in addition to PID?

## 8. Changes Since Approval

| Date | Section | Change | Why |
|---|---|---|---|
| Nov 15, 2026 | R1 | RPM is still updated every 10 ms, but computed from the encoder edges of the last 100 ms (moving window). | One edge in a 10 ms window equals 4.49 RPM, so a single 10 ms window cannot meet A1 (±2 RPM). Found by test `test_A1_rpm_within_2rpm_every_10ms` (bug B1 in `TESTING.md`). |
| Nov 15, 2026 | R2 | The derivative term is computed on the measured speed, not on the error. | Avoids a PWM spike ("derivative kick") when the setpoint changes (bug B2). |
| Nov 15, 2026 | §5 Interfaces | Defined the acknowledgement message `ACK,...` and `ERR,...`. | A4 required "an acknowledgement message" but its format was not specified. |
| Nov 15, 2026 | §2 Context | Encoder decoded in 4x quadrature mode: 334 × 4 = 1336 edges per revolution. | Spec gave 334 CPR but not the decoding mode, which the RPM formula needs. |
| Nov 15, 2026 | R4 | Setpoints outside 0–300 RPM are rejected with `ERR`, settings kept. | Enforces the 300 RPM constraint (§4). |

---

## Appendix: AI Critique & Revision Log
* **Critique Query:** Evaluated using Session 4 AI critique prompt on initial requirements and acceptance criteria.
* **Key Changes Made:**
  1. *Refined R3*: Added explicit bound values ($114\text{ RPM}$ to $126\text{ RPM}$) inside the acceptance criteria to clarify testability.
  2. *Specified Interfaces*: Explicitly defined comma-delimited string formats for both Serial input commands and output telemetry data.
  3. *Added Anti-Windup Requirement (R2)*: Ensured edge-case handling for motor driver saturation was explicitly listed as a testable requirement.
