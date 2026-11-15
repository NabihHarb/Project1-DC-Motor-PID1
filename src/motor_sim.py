"""First-order DC motor model used to test the controller without hardware.

tau * dw/dt = K * pwm - w, with speed limited to 300 RPM (SPEC section 4).
Parameters are rough estimates for a 12 V gear motor; replace with
values identified from real step-response data later.
"""

MAX_RPM = 300.0


class MotorSim:
    def __init__(self, gain=MAX_RPM / 255, tau=0.15, load_rpm=0.0):
        self.gain = gain        # steady-state RPM per PWM count
        self.tau = tau          # mechanical time constant (s)
        self.load_rpm = load_rpm  # constant speed drop from a load
        self.rpm = 0.0

    def step(self, pwm, dt):
        target = self.gain * pwm - self.load_rpm
        self.rpm += (target - self.rpm) * dt / self.tau
        self.rpm = max(0.0, min(MAX_RPM, self.rpm))
        return self.rpm
