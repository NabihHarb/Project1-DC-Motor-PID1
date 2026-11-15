"""Validation against known values (textbook formulas / hand calculations)."""
import math
import pytest
from src.motor_sim import MotorSim
from src.encoder import counts_to_rpm

DT = 0.01


@pytest.mark.parametrize("pwm", [64, 128, 200])
def test_motor_sim_matches_first_order_analytic_solution(pwm):
    """Open-loop step: w(t) = K*u*(1 - exp(-t/tau)) (first-order system)."""
    m = MotorSim()
    final = m.gain * pwm
    worst = 0.0
    for k in range(1, 101):                     # 1 s
        m.step(pwm, DT)
        exact = final * (1 - math.exp(-k * DT / m.tau))
        worst = max(worst, abs(m.rpm - exact))
    # Euler error bound for dt/tau = 0.067 is about 2.5% of final value
    assert worst <= 0.025 * final


def test_motor_sim_time_constant_is_63_percent():
    """At t = tau the speed must be 63.2% of the final value (textbook)."""
    m = MotorSim()
    for _ in range(int(round(m.tau / DT))):
        m.step(255, DT)
    assert m.rpm / 300 == pytest.approx(1 - math.exp(-1), abs=0.02)


@pytest.mark.parametrize("counts, dt, expected", [
    (1336, 1.0, 60.0),      # 1 rev in 1 s
    (2226.67, 1.0, 100.0),  # 100 RPM hand calc: 100/60*1336
    (668, 0.5, 60.0),
])
def test_rpm_formula_hand_calculations(counts, dt, expected):
    assert counts_to_rpm(counts, dt) == pytest.approx(expected, abs=0.01)
