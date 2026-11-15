"""A1 (R1): RPM computed every 10 ms is within +/-2 RPM of the true speed.

The real criterion uses a tachometer at 100 RPM (see TESTING.md procedure P1).
Here the 'trusted reference' is the exact speed fed to an ideal encoder model.
"""
import pytest
from src.encoder import counts_to_rpm, simulate_counts, SpeedEstimator


def test_A1_rpm_formula_matches_hand_calculation():
    # Hand calc: 1336 edges in 1 s = 1 rev/s = 60 RPM
    assert counts_to_rpm(1336, dt=1.0) == pytest.approx(60.0)
    # 100 RPM -> 100/60*1336*0.01 = 22.267 edges per 10 ms
    assert counts_to_rpm(22.267) == pytest.approx(100.0, abs=0.01)


@pytest.mark.parametrize("true_rpm", [50, 100, 120, 200, 300])
def test_A1_rpm_within_2rpm_every_10ms(true_rpm):
    est = SpeedEstimator()
    counts = simulate_counts(true_rpm, 300)          # 3 s of samples
    readings = [est.update(c) for c in counts][20:]  # skip first 200 ms
    worst = max(abs(r - true_rpm) for r in readings)
    assert worst <= 2.0, f"worst error {worst:.2f} RPM at {true_rpm} RPM"
