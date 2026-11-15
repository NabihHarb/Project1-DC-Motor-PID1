"""Acceptance criterion A2 (R2): integral is clamped during PWM saturation."""
from src.motor_sim import MotorSim
from src.pid import PID, DT, PWM_MAX


def run_saturated_then_step(anti_windup):
    """Hold an unreachable 300 RPM target under load (PWM pinned at 255),
    then step down to 120 RPM. Returns (pid, peak RPM after step, pwm log)."""
    pid = PID(1.2, 8.0, 0.0, anti_windup=anti_windup)
    motor = MotorSim(load_rpm=60)          # max reachable speed = 240 RPM
    pwm_log = []
    for _ in range(300):                   # 3 s saturated
        pwm = pid.update(300, motor.rpm)
        pwm_log.append(pwm)
        motor.step(pwm, DT)
    integral_while_saturated = pid.integral
    steps_above_band = 0
    for _ in range(300):                   # 3 s at 120 RPM
        pwm = pid.update(120, motor.rpm)
        motor.step(pwm, DT)
        if motor.rpm > 126:
            steps_above_band += 1
    return pid, integral_while_saturated, pwm_log, steps_above_band


def test_a2_output_saturates_at_255():
    _, _, pwm_log, _ = run_saturated_then_step(anti_windup=True)
    assert max(pwm_log) == PWM_MAX
    assert all(0 <= p <= PWM_MAX for p in pwm_log)


def test_a2_integral_clamped_during_saturation():
    pid, integral, _, _ = run_saturated_then_step(anti_windup=True)
    lo, hi = pid.integral_limits()
    assert lo <= integral <= hi
    assert pid.ki * integral <= PWM_MAX


def test_a2_anti_windup_recovers_faster_than_without():
    _, i_on, _, slow_on = run_saturated_then_step(anti_windup=True)
    _, i_off, _, slow_off = run_saturated_then_step(anti_windup=False)
    assert i_off > i_on                 # without clamp the integral winds up
    assert slow_on < slow_off           # and the motor stays above 126 RPM longer


def test_zero_error_gives_zero_output():
    pid = PID(1.0, 1.0, 1.0)
    assert pid.update(0, 0) == 0
