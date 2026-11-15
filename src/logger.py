"""Telemetry stream checks for the host logger (R5).

Each line is '<t_ms>,<setpoint>,<rpm>,<pwm>' and arrives every 10 ms.
A gap larger than 10 ms between timestamps means frames were dropped.
"""
from src.protocol import parse_telemetry

PERIOD_MS = 10


def read_stream(lines):
    """Parse lines into rows, counting malformed lines instead of crashing."""
    rows, bad = [], 0
    for line in lines:
        if not line.strip():
            continue
        try:
            rows.append(parse_telemetry(line))
        except ValueError:
            bad += 1
    return rows, bad


def dropped_frames(rows, period_ms=PERIOD_MS):
    """Number of missing samples, based on gaps in the timestamps."""
    missing = 0
    for (t0, *_), (t1, *_) in zip(rows, rows[1:]):
        missing += max(0, round((t1 - t0) / period_ms) - 1)
    return missing


def sample_rate_hz(rows):
    if len(rows) < 2:
        return 0.0
    return (len(rows) - 1) * 1000 / (rows[-1][0] - rows[0][0])
