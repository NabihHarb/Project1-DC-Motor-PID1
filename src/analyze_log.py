"""Compute acceptance-criteria results from a telemetry log (CSV).

Usage:
  python -m src.analyze_log data/run.csv --setpoint 120          (A3, A5)
  python -m src.analyze_log data/run.csv --reference-rpm 100     (A1, tachometer value)
"""
import argparse
from pathlib import Path

from src.logger import read_stream, dropped_frames, sample_rate_hz


def settling_time_s(rows, setpoint, band=0.05):
    """Time from the setpoint step until speed stays within +/-band. None if never."""
    start = next((t for t, sp, _, _ in rows if sp == setpoint), None)
    if start is None:
        return None
    seg = [(t, rpm) for t, sp, rpm, _ in rows if t >= start and sp == setpoint]
    lo, hi = setpoint * (1 - band), setpoint * (1 + band)
    last_out = None
    for t, rpm in seg:
        if not lo <= rpm <= hi:
            last_out = t
    if last_out is None:
        return 0.0
    if last_out == seg[-1][0]:
        return None
    return (last_out + 10 - start) / 1000


def speed_error(rows, reference_rpm, skip_s=0.5):
    """Mean and worst error of measured RPM vs a tachometer reference."""
    t0 = rows[0][0]
    vals = [rpm for t, _, rpm, _ in rows if t - t0 >= skip_s * 1000]
    mean = sum(vals) / len(vals)
    return mean - reference_rpm, max(abs(v - reference_rpm) for v in vals)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--setpoint", type=float)
    ap.add_argument("--reference-rpm", type=float)
    a = ap.parse_args(argv)

    rows, bad = read_stream(Path(a.log).read_text().splitlines())
    print(f"Rows: {len(rows)}  malformed: {bad}  "
          f"rate: {sample_rate_hz(rows):.1f} Hz  dropped frames: {dropped_frames(rows)}")
    if a.setpoint is not None:
        ts = settling_time_s(rows, a.setpoint)
        verdict = "PASS" if ts is not None and ts < 1.0 else "FAIL"
        print(f"A3 settling time (+/-5% of {a.setpoint:g} RPM): {ts} s -> {verdict}")
    if a.reference_rpm is not None:
        mean_err, worst = speed_error(rows, a.reference_rpm)
        verdict = "PASS" if abs(mean_err) <= 2.0 else "FAIL"
        print(f"A1 mean error {mean_err:+.2f} RPM, worst sample {worst:.2f} RPM -> {verdict}")


if __name__ == "__main__":
    main()
