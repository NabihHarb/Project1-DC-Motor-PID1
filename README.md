 Project 1: DC Motor PID Speed Control System

## Project Overview
Precise motor velocity control is fundamental in robotics, automated manufacturing, and automotive actuation. Uncontrolled DC motors experience speed fluctuations due to load variations, voltage drops, and friction. This project implements a closed-loop Proportional-Integral-Derivative (PID) speed controller using an Arduino Mega 2560 and a quadrature encoder, paired with a real-time plotting utility to analyze transient and steady-state responses.

## Why It Matters
In mechatronics systems, open-loop motor actuation is insufficient for precise motion. Implementing closed-loop control demonstrates core principles of feedback systems, real-time data logging, digital signal processing via hardware interrupts, and system tuning.

## Team Members & Roles
* **Nabih Harb** – Firmware Development, PID Controller Implementation, Hardware Integration
* **Hussein Haidar** – Data Logging Script, Serial Communication Protocol, Testing & Documentation

## Tools & Hardware Plan
* **Microcontroller & Hardware:** Arduino Mega 2560 Rev3, L298N H-Bridge Driver, 12V DC Motor with Quadrature Encoder, External Power Supply.
* **Firmware:** Arduino C++ (Interrupt-driven encoder reading, $100\text{ Hz}$ timer loop).
* **Software & Analysis:** Python 3 (`pyserial`, `matplotlib`) for real-time visualization and step-response analysis.
* **Version Control:** GitHub for specification tracking, firmware code hosting, and project documentation.

---

## Repository Structure
```
README.md          Project overview, how to run, status
SPEC.md            Approved specification (R1–R5, acceptance criteria)
AI_USE.md          Log of AI tool usage
requirements.txt   Python dependencies
src/pid.py         PID controller with integral anti-windup (R2)
src/motor_sim.py   First-order DC motor model (testing without hardware)
src/protocol.py    Serial SET command / telemetry formats (SPEC §5)
src/run_sim.py     Runs a simulated 120 RPM step response
tests/             pytest tests for the acceptance criteria
data/sample_step.csv  Small sample telemetry output (200 rows)
```

## Install and Run (Milestone 2 prototype)
Requires Python 3.10+.

```bash
git clone https://github.com/NabihHarb/Project1-DC-Motor-PID1.git
cd Project1-DC-Motor-PID1
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the tests:
```bash
python -m pytest -v
```

Run the simulated step response (writes `data/sample_step.csv`; add `--plot` to see the graph):
```bash
python -m src.run_sim --plot
```

## Requirement Met: R2 (PID with anti-windup)
The PID algorithm in `src/pid.py` mirrors the firmware logic that will run at 100 Hz on the Arduino. Because the hardware is not wired yet, it is tested against a simulated motor (`src/motor_sim.py`).

**Acceptance criterion A2:** *Given the output saturates at PWM 255, when the error persists, then the integral term is clamped.*

How we checked it (`tests/test_pid.py`): a 300 RPM target is commanded on a loaded motor that can only reach 240 RPM, so the PWM is held at 255 for 3 s. The setpoint then drops to 120 RPM.

| Check | Result |
|---|---|
| PWM output reaches 255 and never leaves 0–255 | PASS |
| Integral stays within its limits (Ki·I ≤ 255) during saturation | PASS |
| Without anti-windup the integral winds up and the motor overshoots 126 RPM for longer; with anti-windup it recovers faster | PASS |

Test run result: **12 passed** (`python -m pytest -v`).

### Also prepared (partial, not yet claimed as met)
* **R3 (simulation only):** the simulated 120 RPM step settles within ±5% in **0.32 s** (< 1.0 s). It still has to be confirmed on the real motor.
* **R4/R5:** the `SET,...` command parser and telemetry format are implemented and tested. Serial communication with the Arduino comes in the next milestone.

### Next steps
Arduino firmware (encoder interrupts for R1, Serial commands for R4), the live plotting script (R5) and hardware tuning (R3).
