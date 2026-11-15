"""Run a simulated 120 RPM step response and save it in telemetry format.

Usage:  python -m src.run_sim [--plot]
"""
import argparse
from pathlib import Path

from src.motor_sim import MotorSim
from src.pid import PID, DT
from src.protocol import format_telemetry

KP, KI, KD = 1.2, 8.0, 0.0


def simulate(setpoint=120.0, duration=2.0, kp=KP, ki=KI, kd=KD,
             anti_windup=True, motor=None):
    pid = PID(kp, ki, kd, anti_windup=anti_windup)
    motor = motor or MotorSim()
    rows = []
    for k in range(int(round(duration / DT))):
        rpm = motor.rpm
        pwm = pid.update(setpoint, rpm)
        rows.append((k * 10, setpoint, rpm, pwm))
        motor.step(pwm, DT)
    return rows


def settling_time(rows, setpoint, band=0.05):
    """Time (s) after which speed stays within +/-band of setpoint, or None."""
    lo, hi = setpoint * (1 - band), setpoint * (1 + band)
    last_out = None
    for t_ms, _, rpm, _ in rows:
        if not lo <= rpm <= hi:
            last_out = t_ms
    if last_out is None:
        return 0.0
    if last_out == rows[-1][0]:
        return None
    return (last_out + 10) / 1000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plot", action="store_true", help="show a plot")
    args = ap.parse_args()

    rows = simulate()
    out = Path("data/sample_step.csv")
    out.write_text("\n".join(format_telemetry(*r) for r in rows) + "\n")
    print(f"Wrote {len(rows)} samples to {out}")
    print(f"Settling time (+/-5% of 120 RPM): {settling_time(rows, 120)} s")

    if args.plot:
        import matplotlib.pyplot as plt
        t = [r[0] / 1000 for r in rows]
        plt.plot(t, [r[1] for r in rows], "--", label="Setpoint")
        plt.plot(t, [r[2] for r in rows], label="Measured RPM")
        plt.xlabel("Time (s)"); plt.ylabel("Speed (RPM)")
        plt.title("Simulated step response"); plt.legend(); plt.grid()
        plt.show()


if __name__ == "__main__":
    main()
