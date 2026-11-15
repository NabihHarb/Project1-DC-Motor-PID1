# Testing Report

Run all automated tests:
```bash
python -m pytest -v
```
Result on commit tested: **37 passed, 0 failed**.

This is a hardware project. Every criterion has an automated software test
(logic checked against a motor model or known values). Criteria that need the
real motor also have a written hardware procedure (P1–P5 below). Hardware
results are marked **pending** until measured on the bench: we do not report
numbers we have not measured.

## 1. Acceptance criteria results

| Criterion | Test (name or procedure) | Expected | Actual | Result |
|---|---|---|---|---|
| A1 (R1) | `test_A1_rpm_formula_matches_hand_calculation` | 1336 edges/s = 60 RPM; 22.267 edges/10 ms = 100 RPM | 60.00 / 100.00 RPM | PASS |
| A1 (R1) | `test_A1_rpm_within_2rpm_every_10ms` (50–300 RPM, ideal encoder) | error ≤ ±2 RPM | worst 0.36 RPM (was 3.89 before fix B1) | PASS |
| A1 (R1) | Procedure P1 (tachometer at 100 RPM) | within ±2 RPM | pending hardware | — |
| A2 (R2) | `test_A2_output_saturates_at_255` | PWM hits 255, stays in 0–255 | max 255, all in range | PASS |
| A2 (R2) | `test_A2_integral_clamped_during_saturation` | Ki·I ≤ 255 while saturated | clamped at 255/Ki | PASS |
| A2 (R2) | `test_A2_anti_windup_recovers_faster_than_without` | less time above 126 RPM than without clamp | yes | PASS |
| R2 (extra) | `test_R2_no_derivative_kick_on_setpoint_change` | output change = P + I only (38.4) | 38.4 (was +188 spike before fix B2) | PASS |
| A3 (R3) | `test_A3_sim_settles_within_5_percent_under_1s` | settle in 114–126 RPM < 1.0 s | 0.32 s (simulation) | PASS (sim) |
| A3 (R3) | Procedure P3 (real step 0→120 RPM) | settle < 1.0 s | pending hardware | — |
| A4 (R4) | `test_A4_set_command_updates_gains_and_acknowledges` | Kp=2.0, Ki=0.1, Kd=0.0, SP=150, ACK sent | `ACK,150,2.000,0.100,0.000` | PASS |
| A4 (R4) | `test_A4_bad_command_is_rejected_and_settings_kept` | `ERR`, old gains kept | `ERR`, kept | PASS |
| A4 (R4) | Procedure P4 (Serial Monitor at 115200) | ACK printed by Arduino | pending firmware | — |
| A5 (R5) | `test_A5_sample_stream_is_100hz_with_no_dropped_frames` | 100 Hz, 0 dropped | 100.0 Hz, 0 dropped, 200 rows | PASS |
| A5 (R5) | `test_A5_detects_dropped_frames` | gap 10→40 ms = 2 dropped | 2 | PASS |
| A5 (R5) | `test_A5_malformed_line_does_not_crash_logger` | bad lines counted, no crash | 2 bad, 2 good | PASS |
| A5 (R5) | `test_A5_replay_through_plotter_logs_every_frame` | plotter logs all 200 rows, file identical | 200 rows, identical | PASS |
| A5 (R5) | Procedure P5 (live plot over USB) | no dropped frames in 10 s | pending hardware | — |

## 2. Validation against known values

| What | Trusted reference | Our output | Error |
|---|---|---|---|
| RPM formula | Hand calc: 1336 edges in 1 s = 60 RPM; 2226.67 edges in 1 s = 100 RPM; 668 edges in 0.5 s = 60 RPM | 60.00, 100.00, 60.00 | < 0.01 RPM |
| Encoder speed at 50, 100, 120, 200, 300 RPM | Exact speed fed to ideal encoder model | worst 0.30, 0.30, 0.36, 0.30, 0.00 RPM | **within 0.36 RPM at 50–300 RPM** (limit ±2) |
| Motor model, open-loop step PWM 64 / 128 / 200 | Textbook first-order solution ω(t) = K·u·(1 − e^(−t/τ)) | max deviation 0.95 / 1.90 / 2.97 RPM | **1.26 % of final speed** (Euler step, dt/τ = 0.067) |
| Motor model time constant | At t = τ, speed = 63.2 % of final (textbook) | 64.5 % | 1.3 percentage points |

Real-world validation still to do (next milestone, on the bench): compare
encoder RPM with a handheld optical tachometer at 60, 100 and 150 RPM, and
measure τ and gain K from a real open-loop step to replace the estimated model
parameters (τ = 0.15 s, 300 RPM at PWM 255).

### Checking the tests themselves (mutation check)
We broke the code on purpose and confirmed each test catches it:

| Deliberate bug | Tests that failed |
|---|---|
| Anti-windup clamp disabled | 2 of 6 in `test_A2_anti_windup.py` |
| RPM window set back to 1 sample | 5 of 6 in `test_A1_encoder.py` |
| SET command does not update setpoint | 1 of 2 in `test_A4_serial_command.py` |
| Off-by-one in dropped-frame count | 2 of 3 in `test_A5_logger.py` |
| Motor 4× slower (τ = 0.6 s) | `test_A3_sim_settles...` |

## 3. Hardware test procedures

**Setup (all):** Arduino Mega 2560 with `firmware/motor_pid/motor_pid.ino`,
L298N, 12 V gear motor with 334 CPR encoder, 12 V/2 A supply, USB at 115200
baud, wired as in `README.md`. Fill in the *Measured* lines only with values
you actually measured, and keep the log files in `data/`.

- **P1 – A1 speed accuracy.** Put reflective tape on the output shaft. Send a setpoint of 100 RPM and wait 2 s. Measure the shaft with an optical tachometer while logging:
  `python -m src.plot_live --port COM3 --set "SET,100,1.2,8.0,0.0" --seconds 5`
  then `python -m src.analyze_log data/run_<time>.csv --reference-rpm <tachometer value>`.
  *Expected:* mean error within ±2 RPM. Repeat at 60 and 150 RPM.
  *Measured:* pending (tachometer: ___ RPM, Arduino mean: ___ RPM, error: ___ RPM).
- **P3 – A3 settling.** Motor at rest. `python -m src.plot_live --port COM3 --set "SET,120,1.2,8.0,0.0" --seconds 3`, then `python -m src.analyze_log data/run_<time>.csv --setpoint 120`.
  *Expected:* settling time < 1.0 s. *Measured:* pending (___ s, 3 runs: ___ / ___ / ___).
- **P4 – A4 command.** Open the Serial Monitor (115200, newline), wait for `READY`, send `SET,120,1.2,8.0,0.0`, then `SET,150,2.0,0.1,0.0`.
  *Expected:* `ACK,150,2.000,0.100,0.000` and the speed column moves to 150. Then send `SET,400,1,1,1` → `ERR,...`, speed unchanged.
  *Measured:* pending.
- **P5 – A5 logging.** `python -m src.plot_live --port COM3 --seconds 10`.
  *Expected:* plot window updates live; printout shows `Rate 100.0 Hz, dropped frames: 0` and about 1000 rows.
  *Measured:* pending.

## 4. Bug log

| # | Bug | Cause | Fix (commit) | Introduced by AI? |
|---|---|---|---|---|
| B1 | A1 failed: speed error up to 3.9 RPM (limit ±2) | One edge in 10 ms = 4.49 RPM, so a single 10 ms window cannot resolve ±2 RPM. Spec asked for RPM "every 10 ms" and the first version also measured over only 10 ms. | 100 ms moving window, still updated every 10 ms → 0.45 RPM resolution. "Fix RPM quantization error with 100 ms moving window (A1)" | Yes – first version of `SpeedEstimator` was AI-written. Root cause partly in our spec. |
| B2 | Derivative kick: setpoint 120→150 made PWM jump to 188 then drop to 41 | D term computed on error, so a setpoint step looks like an infinite rate of change. Also D spiked on the first call after reset. | Derivative on measurement, D = 0 on first call. "Fix derivative kick by differentiating measurement (R2)" | Yes – introduced in the Milestone 2 AI-written `pid.py`; not caught then because tests used Kd = 0. |
| B3 | A4 acknowledgement text differed between Python (`ACK,150,2,0.1,0`) and firmware (`ACK,150,2.000,0.100,0.000`) | Python used `:g` formatting, Arduino `Serial.print(x, 3)` prints 3 decimals | Python now formats with 3 decimals; SPEC §5 documents the format. "Match ACK format to firmware output, 3-decimal gains (A4)" | Yes – both versions AI-written; found when writing the firmware. |
