# Demo Plan (8 minutes)

**Day before:** charge laptop, `git pull`, `pip install -r requirements.txt`, `python -m pytest -q` (37 passed), upload firmware, run P5 once, copy a good run to `data/` as backup. Bring: laptop, Mega + USB cable, L298N, motor, 12 V supply, tachometer, tape.

| Time | Who | What | Command / action |
|---|---|---|---|
| 0:00–1:00 | Nabih | Problem: open-loop speed drifts with load; goal R1–R5 | Figure 1 of the report |
| 1:00–1:45 | Hussein | Tests pass (all criteria in software) | `python -m pytest -v` |
| 1:45–3:00 | Nabih | **A3 + A5** live step to 120 RPM, plot updates | `python -m src.plot_live --port COM3 --set "SET,120,1.2,8.0,0.0" --seconds 5` |
| 3:00–3:30 | Hussein | A3/A5 numbers from that run | `python -m src.analyze_log data/run_<time>.csv --setpoint 120` |
| 3:30–4:30 | Nabih | **A4** change gains live; show `ACK` and `ERR` | Serial Monitor: `SET,150,2.0,0.1,0.0`, then `SET,400,1,1,1` |
| 4:30–5:30 | Hussein | **A1** tachometer vs Arduino RPM at 100 RPM | read tachometer; `--reference-rpm <value>` |
| 5:30–6:00 | Nabih | **A2** pinch the shaft lightly (load) → PWM 255, release: no big overshoot | live plot |
| 6:00–8:00 | both | Limitations (sim vs real, 50 ms lag, one direction) and improvements | Report §4–5 |

**If hardware fails:** `python -m src.plot_live --replay data/<backup run>.csv` and `python -m src.run_sim --plot`; say clearly it is a replay.

**Oral questions – be ready to explain:** the quadrature lookup table in `encoderISR()`; why 4.49 RPM per edge (bug B1); the anti-windup clamp `255/Ki`; derivative on measurement (B2); the `micros()` scheduler; how `dropped_frames` works. Practise a small live change, e.g. changing `WINDOW` or the PWM limit, then re-running the tests.
