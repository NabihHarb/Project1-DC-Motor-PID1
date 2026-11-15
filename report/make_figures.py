"""Generate the report figures from the tested code.  python -m report.make_figures"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from src.run_sim import simulate, settling_time
from src.motor_sim import MotorSim
from src.pid import PID, DT
from src.encoder import SpeedEstimator, simulate_counts, counts_to_rpm

OUT = Path(__file__).parent / "figures"
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#222222", "#6b6b6b", "#e6e6e6"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "axes.spines.top": False, "axes.spines.right": False,
                     "lines.linewidth": 2, "savefig.dpi": 200, "savefig.bbox": "tight"})


def diagram():
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis("off")
    def box(x, y, w, h, title, sub):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5",
                                    fc="#f4f7fc", ec=BLUE, lw=1.4))
        ax.text(x + w / 2, y + h - 3.2, title, ha="center", va="top", weight="bold", color=INK)
        ax.text(x + w / 2, y + h - 8.2, sub, ha="center", va="top", fontsize=7.5, color=MUTED,
                linespacing=1.35)
    def arrow(x0, y0, x1, y1, label="", dy=1.6):
        ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
        if label:
            ax.text((x0 + x1) / 2, (y0 + y1) / 2 + dy, label, ha="center", fontsize=7, color=INK)
    box(1, 14, 18, 22, "Host PC", "Python\nplot_live.py\nanalyze_log.py")
    box(34, 3, 24, 33, "Arduino Mega", "every 10 ms:\n1. RPM from encoder\n    (100 ms window)\n2. PID + anti-windup\n3. PWM out\n4. telemetry line")
    box(66, 22, 13, 14, "L298N", "H-bridge\n12 V")
    box(85, 22, 14, 14, "DC motor", "12 V gear\n≤ 300 RPM")
    box(85, 1, 14, 15, "Encoder", "334 CPR\n×4 = 1336/rev")
    ax.annotate("", (34, 30), (19.6, 30), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.text(26.8, 31.5, "SET,sp,Kp,Ki,Kd", ha="center", fontsize=6.5, color=INK)
    ax.annotate("", (19.6, 19), (34, 19), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.text(26.8, 15.8, "t,sp,rpm,pwm\nACK / ERR", ha="center", va="top", fontsize=6.5, color=INK)
    ax.text(26.8, 24.5, "USB serial\n115200 baud", ha="center", va="center", fontsize=6.5, color=MUTED)
    ax.annotate("", (66, 29), (58.6, 29), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.text(62.3, 30.5, "PWM", ha="center", fontsize=6.5, color=INK)
    ax.annotate("", (85, 29), (79.6, 29), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.annotate("", (92, 16.6), (92, 22), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.text(93, 19.3, "shaft", fontsize=6.5, color=MUTED, va="center")
    ax.annotate("", (58.6, 8.5), (85, 8.5), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.text(71.8, 10, "A/B pulses (pins 2, 3)", ha="center", fontsize=6.5, color=INK)
    fig.savefig(OUT / "fig1_system.png"); plt.close(fig)


def step_response():
    rows = simulate(setpoint=120, duration=1.5)
    t = [r[0] / 1000 for r in rows]
    ts = settling_time(rows, 120)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 4.2), sharex=True,
                                 gridspec_kw={"height_ratios": [2, 1]})
    a1.axhspan(114, 126, color=BLUE, alpha=0.08, lw=0)
    a1.plot(t, [r[1] for r in rows], "--", color=MUTED, lw=1.2)
    a1.plot(t, [r[2] for r in rows], color=BLUE)
    a1.axvline(ts, color=INK, lw=1, ls=":")
    a1.text(ts + 0.02, 40, f"settled at {ts:.2f} s", color=INK, fontsize=8)
    a1.text(1.48, 127.5, "±5 % band (114–126 RPM)", ha="right", fontsize=7.5, color=MUTED)
    a1.text(1.48, 108, "setpoint 120 RPM", ha="right", fontsize=7.5, color=MUTED)
    a1.set_ylabel("Speed (RPM)"); a1.set_ylim(0, 140)
    a1.set_title("Measured speed, simulated 0 → 120 RPM step (Kp = 1.2, Ki = 8.0)", loc="left",
                 fontsize=9, color=INK)
    a2.plot(t, [r[3] for r in rows], color=BLUE)
    a2.set_ylabel("PWM (0–255)"); a2.set_xlabel("Time (s)"); a2.set_ylim(0, 260)
    a2.set_title("Controller output", loc="left", fontsize=9, color=INK)
    fig.tight_layout(); fig.savefig(OUT / "fig2_step.png"); plt.close(fig)


def windup():
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    for aw, color, name in ((True, BLUE, "with anti-windup"), (False, ORANGE, "without anti-windup")):
        pid, m, t, y = PID(1.2, 8.0, 0.0, anti_windup=aw), MotorSim(load_rpm=60), [], []
        for k in range(600):
            sp = 300 if k < 300 else 120
            pwm = pid.update(sp, m.rpm); m.step(pwm, DT)
            t.append(k * DT); y.append(m.rpm)
        ax.plot(t, y, color=color, label=name)
    ax.axvline(3.0, color=MUTED, lw=1, ls=":")
    ax.text(0.05, 250, "setpoint 300 RPM, load limits speed to 240 RPM\n→ PWM saturated at 255",
            fontsize=7.5, color=INK)
    ax.text(3.05, 255, "setpoint → 120 RPM", fontsize=7.5, color=INK)
    ax.set_xlabel("Time (s)"); ax.set_ylabel("Speed (RPM)"); ax.set_ylim(0, 290)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("A2: recovery after saturation (simulation)", loc="left", fontsize=9, color=INK)
    fig.tight_layout(); fig.savefig(OUT / "fig3_windup.png"); plt.close(fig)


def encoder_error():
    counts = simulate_counts(100, 150)
    single = [counts_to_rpm(c) - 100 for c in counts]
    est = SpeedEstimator(); window = [est.update(c) - 100 for c in counts]
    t = [k * 10 for k in range(len(counts))]
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.axhspan(-2, 2, color=BLUE, alpha=0.08, lw=0)
    ax.plot(t, single, color=ORANGE, lw=1.2, label="single 10 ms window (bug B1)")
    ax.plot(t[10:], window[10:], color=BLUE, label="100 ms moving window (fixed)")
    ax.text(10, -2.8, "shaded: A1 limit ±2 RPM", ha="left", fontsize=7.5, color=MUTED)
    ax.set_xlabel("Time (ms)"); ax.set_ylabel("Error (RPM)"); ax.set_ylim(-5, 5)
    ax.legend(frameon=False, loc="lower right", ncol=2)
    ax.set_title("A1: speed error at a true 100 RPM, ideal encoder", loc="left", fontsize=9, color=INK)
    fig.tight_layout(); fig.savefig(OUT / "fig4_encoder.png"); plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    diagram(); step_response(); windup(); encoder_error()
    print("Figures written to", OUT)
