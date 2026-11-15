# Project 1: DC Motor PID Speed Control System

## Project Overview
Precise motor velocity control is fundamental in robotics, automated manufacturing, and automotive actuation. Uncontrolled DC motors experience speed fluctuations due to load variations, voltage drops, and friction. This project implements a closed-loop Proportional-Integral-Derivative (PID) speed controller using an Arduino Mega 2560 and a quadrature encoder, paired with a real-time plotting utility to analyze transient and steady-state responses.

## Team Members & Roles
* **Nabih Harb** – Firmware Development, PID Controller Implementation, Hardware Integration
* **Hussein Haidar** – Data Logging Script, Serial Communication Protocol, Testing & Documentation

## Repository Structure
```
README.md            This file: install, run, test
SPEC.md              Approved specification + changes since approval (section 8)
TESTING.md           Test results for every acceptance criterion, validation, bug log
AI_USE.md            AI Use Disclosure
requirements.txt     Python dependencies
firmware/motor_pid/  Arduino sketch (encoder ISR, PID, Serial commands, telemetry)
src/pid.py           PID with anti-windup and derivative on measurement (R2)
src/encoder.py       Encoder edges -> RPM, 100 ms moving window (R1)
src/controller.py    SET command handling with ACK/ERR reply (R4)
src/protocol.py      Serial message formats (SPEC section 5)
src/logger.py        Telemetry parsing and dropped-frame check (R5)
src/plot_live.py     Live plot + CSV logger from the Arduino, or replay of a CSV (R5)
src/analyze_log.py   Computes A1/A3/A5 results from a logged run
src/motor_sim.py     First-order motor model (testing without hardware)
src/run_sim.py       Simulated 120 RPM step response
tests/               pytest tests, named after the acceptance criteria (A1..A5)
data/sample_step.csv Small sample telemetry file (200 rows, 2 s)
report/              Technical report: report.pdf, report.html, make_figures.py
DEMO.md              8-minute demo plan
```

## Hardware Setup
| From | To |
|---|---|
| Encoder channel A | Mega pin 2 (interrupt) |
| Encoder channel B | Mega pin 3 (interrupt) |
| Encoder VCC / GND | Mega 5V / GND |
| L298N ENA (remove jumper) | Mega pin 5 (PWM) |
| L298N IN1 / IN2 | Mega pin 7 / pin 8 |
| L298N OUT1 / OUT2 | Motor + / − |
| L298N 12V / GND | 12 V 2 A supply + / − (GND shared with Mega) |

If the measured RPM stays at 0 while the motor spins, swap encoder A and B or the motor wires.

## Install (Python 3.10+)
```bash
git clone https://github.com/NabihHarb/Project1-DC-Motor-PID1.git
cd Project1-DC-Motor-PID1
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\activate   Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
```

## Upload the Firmware
1. Open `firmware/motor_pid/motor_pid.ino` in the Arduino IDE 2.x.
2. Tools → Board → **Arduino Mega or Mega 2560**; Tools → Port → your port (e.g. `COM3`).
3. Click **Upload**. Close the Serial Monitor before running the Python scripts.

## Run
Live step response from the motor (saves `data/run_<time>.csv`):
```bash
python -m src.plot_live --port COM3 --set "SET,120,1.2,8.0,0.0" --seconds 5
```
Check the acceptance criteria on that log:
```bash
python -m src.analyze_log data/run_YYYYMMDD_HHMMSS.csv --setpoint 120
```
Without hardware (replay the sample data, or simulate):
```bash
python -m src.plot_live --replay data/sample_step.csv
python -m src.run_sim --plot
```

## Test
```bash
python -m pytest -v
```
Expected: **37 passed**. Results per criterion are in [TESTING.md](TESTING.md).

## Requirement Status
| Req | Status | Where | Evidence |
|---|---|---|---|
| R1 Encoder RPM every 10 ms | Implemented | `firmware/`, `src/encoder.py` | A1 tests pass (worst 0.36 RPM, software); tachometer check P1 in TESTING.md |
| R2 PID with anti-windup | Implemented | `firmware/`, `src/pid.py` | A2 tests pass |
| R3 Settle ±5 % of 120 RPM in < 1 s | Implemented; met in simulation (0.32 s) | `src/run_sim.py` | Hardware result: see TESTING.md P3 |
| R4 SET command + ACK at 115200 | Implemented | `firmware/`, `src/controller.py` | A4 tests pass; P4 on hardware |
| R5 Telemetry + live plot | Implemented | `firmware/`, `src/plot_live.py` | A5 tests pass (100 Hz, 0 dropped); P5 on hardware |

## Report
`report/report.pdf` (source `report/report.html`). Regenerate the figures with `python -m report.make_figures`.
After adding bench results to `report/report.html`, open it in Chrome or Edge → Ctrl+P → **Save as PDF** (A4, background graphics on).
