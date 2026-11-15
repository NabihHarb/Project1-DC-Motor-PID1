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
