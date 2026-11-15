"""R3 checked in SIMULATION only (real hardware test still pending)."""
from src.run_sim import simulate, settling_time


def test_A3_sim_settles_within_5_percent_under_1s():
    rows = simulate(setpoint=120, duration=2.0)
    ts = settling_time(rows, 120)
    assert ts is not None and ts < 1.0


def test_sample_rate_is_100hz():
    rows = simulate(duration=1.0)
    assert len(rows) == 100
    assert rows[1][0] - rows[0][0] == 10
