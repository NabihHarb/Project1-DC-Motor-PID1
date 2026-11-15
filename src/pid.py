"""Discrete PID speed controller with integral anti-windup (R2).

Mirrors the logic that will run on the Arduino at 100 Hz (dt = 10 ms).
"""

DT = 0.01          # control period in seconds (100 Hz, SPEC section 4)
PWM_MIN = 0
PWM_MAX = 255


class PID:
    def __init__(self, kp, ki, kd, dt=DT, out_min=PWM_MIN, out_max=PWM_MAX,
                 anti_windup=True):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.dt = dt
        self.out_min, self.out_max = out_min, out_max
        self.anti_windup = anti_windup
        self.reset()

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0

    def set_gains(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd

    def integral_limits(self):
        """Bounds for the integral state so Ki*integral stays inside the PWM range."""
        if self.ki == 0:
            return (0.0, 0.0)
        return (self.out_min / self.ki, self.out_max / self.ki)

    def update(self, setpoint, measured):
        """Return the PWM output (0..255) for one control step."""
        error = setpoint - measured
        self.integral += error * self.dt
        if self.anti_windup:
            lo, hi = self.integral_limits()
            self.integral = max(lo, min(hi, self.integral))
        derivative = (error - self.prev_error) / self.dt
        self.prev_error = error

        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        return max(self.out_min, min(self.out_max, output))
