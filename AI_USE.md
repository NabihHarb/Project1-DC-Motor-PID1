# AI Use Log

## Milestone 1: Specification & Proposal

* **Date:** October 25, 2026
* **AI Tool Used:** Gemini
* **Purpose / Context:** Formulating `SPEC.md`, creating acceptance criteria in Given/When/Then format, applying AI critique suggestions, and structuring project proposal requirements for `README.md`.
* **Prompt Provided:** "Generate a 7-section SPEC.md for a DC motor PID speed control project with numbered testable requirements, acceptance criteria, and a proposal for README.md."
* **Outcome / Revisions Made:** AI provided initial template structure. Refined acceptance criteria values to ensure numerical bounds ($\pm 5\%$ of 120 RPM) matched assignment constraints and explicitly formatted interface specs for Serial protocol.

## Milestone 2: Repository Setup & First Prototype

* **Date:** November 15, 2026
* **AI Tool Used:** Claude Code (Anthropic)
* **What we asked:** Organize the repository (src/, tests/, data/, .gitignore, requirements.txt) and build a first prototype that meets at least one requirement from SPEC.md, with tests for its acceptance criterion.
* **What the AI produced:** `src/pid.py` (PID with integral clamping), `src/motor_sim.py` (first-order motor model), `src/protocol.py` (SET/telemetry parsing), `src/run_sim.py`, the pytest tests and the Install/Run section of the README.
* **What we changed / decided:** We chose R2 as the first requirement because it can be tested without hardware. The motor model parameters (tau = 0.15 s, 300 RPM max) are estimates and will be replaced with values measured from our motor. Gains (Kp = 1.2, Ki = 8.0) are a starting point for hardware tuning.
* **How we verified it:** Ran `python -m pytest -v` (12 passed). We checked that the anti-windup test fails when the clamp is turned off (the integral grows without bound) and read the generated `data/sample_step.csv` to confirm it matches the telemetry format in SPEC.md §5. R3 is only verified in simulation and is not claimed as met.

## Milestone 3: Testing & Validation

* **Date:** November 15, 2026
* **AI Tool Used:** Claude Code (Anthropic)
* **What we asked:** Write one test per acceptance criterion (A1–A5), validate outputs against known values, find and fix bugs, and write `TESTING.md`.
* **Did AI write the tests?** Yes. Claude Code wrote the pytest tests, `src/encoder.py`, `src/controller.py`, `src/logger.py` and the hardware test procedures.
* **Did AI find bugs?** Yes, two, and both were in AI-written code (see bug log in `TESTING.md`): B1, an RPM quantization error that failed A1, and B2, a derivative kick in the Milestone 2 PID. Each was committed first as a failing test, then fixed in its own commit.
* **How we checked the tests were right:**
  1. Expected values come from hand calculations or textbook formulas, not from running the code (e.g. 1336 edges/s = 60 RPM; first-order response ω = K·u·(1 − e^(−t/τ)); 63.2 % at t = τ).
  2. Mutation check: we broke the code on purpose (removed the anti-windup clamp, set the RPM window back to 1, stopped the setpoint update, added an off-by-one, slowed the motor) and confirmed the matching tests failed each time.
  3. The A1 and derivative-kick tests were seen failing before the fixes and passing after.
* **Limits:** Tests run against a simulated motor. Hardware procedures P1, P3, P4, P5 are written but not yet measured; results are marked pending and must not be filled in until measured.

---

# Final AI Use Disclosure (Milestone 4)

## 1. Tools used
| Tool | Milestones |
|---|---|
| Gemini (Google) | M1: specification and proposal wording |
| Claude Code (Anthropic), cloud session | M2–M4: code, tests, firmware, documentation, report draft |

## 2. How they were used
* **Gemini** produced a first template for `SPEC.md` and the README proposal; we chose the hardware, numbers and requirements ourselves and revised the acceptance criteria.
* **Claude Code** wrote most of the code and documentation from our milestone instructions, working in a cloud copy of this repository. It ran the tests itself and we pushed its commits to GitHub from our own computer (Claude had read-only access to the repo).
* We reviewed every file, ran the tests on our own machine, and are responsible for all content.

## 3. Significant prompts
1. (M1, Gemini) "Generate a 7-section SPEC.md for a DC motor PID speed control project with numbered testable requirements, acceptance criteria, and a proposal for README.md."
2. (M2, Claude) The full Milestone 2 brief: organise the repository, build a first prototype that meets at least one requirement, document install/run commands, and update AI_USE.md, "explain it before execution".
3. (M3, Claude) The full Milestone 3 brief: one test per acceptance criterion, validate against reality, TESTING.md with results table and bug log, fix failures in separate commits.
4. (M4, Claude) The full final brief: implement every requirement, update SPEC/README/TESTING, write a 3–5 page report and this disclosure.

## 4. AI-generated contributions
| File / function | Generated by | Our changes / decisions |
|---|---|---|
| `SPEC.md` (first draft) | Gemini | Set numeric bounds (±5 % of 120 RPM), interface formats, anti-windup requirement |
| `firmware/motor_pid/motor_pid.ino` (all) | Claude | Pin choice and wiring to be checked on our board |
| `src/pid.py` `PID.update`, `integral_limits` | Claude | Gains Kp = 1.2, Ki = 8.0 are starting values for tuning |
| `src/encoder.py` `counts_to_rpm`, `SpeedEstimator` | Claude | Accepted the 100 ms window change to SPEC R1 |
| `src/controller.py`, `src/protocol.py`, `src/logger.py` | Claude | Accepted ACK/ERR format, added to SPEC §5 |
| `src/plot_live.py`, `src/analyze_log.py`, `src/run_sim.py`, `src/motor_sim.py` | Claude | Motor parameters (τ = 0.15 s) are estimates to be replaced by measured values |
| All files in `tests/` | Claude | Expected values checked by hand (see 5) |
| `README.md` (Milestone 2+ sections), `TESTING.md`, report draft | Claude | Reviewed, hardware results to be filled in by us |
| Project overview, team roles, problem choice | Us | — |

## 5. Corrections and verification
| What was wrong | How we found it | How it was fixed |
|---|---|---|
| B1: RPM from a single 10 ms window had up to 3.9 RPM error (A1 limit ±2 RPM) | Test `test_A1_rpm_within_2rpm_every_10ms` failed; hand calculation shows 1 edge per 10 ms = 4.49 RPM | 100 ms moving window, updated every 10 ms; SPEC §8 updated |
| B2: derivative kick (PWM spike to 188 on a setpoint change) in the M2 PID | We tested with Kd > 0 (M2 tests only used Kd = 0) | Derivative on measurement; new tests `test_R2_no_derivative_kick...` |
| B3: ACK message format differed between Python and firmware | Comparing the two while writing the firmware | Python changed to 3 decimals; format added to SPEC §5 |
| Report/README must not contain hardware numbers we did not measure | Our own review | Hardware results are marked "pending" until measured |

**How we checked the tests themselves:** expected values come from hand calculations and textbook formulas, not from running the code; we broke the code on purpose (mutation check, `TESTING.md` §2) and every relevant test failed; the B1/B2 tests were seen failing before their fixes.

**Not verified by AI:** the firmware could not be compiled or run in the AI's environment. We compile it in the Arduino IDE (Verify) and test it on the bench with procedures P1–P5.
