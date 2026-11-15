"""Live step-response plot and logger (R5).

Hardware:  python -m src.plot_live --port COM3 --set "SET,120,1.2,8.0,0.0" --seconds 5
Replay:    python -m src.plot_live --replay data/sample_step.csv
Find your port in the Arduino IDE (Tools > Port), e.g. COM3 or /dev/ttyACM0.
Each run is saved to data/run_<time>.csv; analyse it with src.analyze_log.
"""
import argparse
import time
from collections import deque
from pathlib import Path

import matplotlib.pyplot as plt

from src.logger import read_stream, dropped_frames, sample_rate_hz
from src.protocol import parse_telemetry

BAUD = 115200


def open_serial(port):
    import serial                      # pyserial
    ser = serial.Serial(port, BAUD, timeout=0.1)
    time.sleep(2.0)                    # Arduino resets when the port opens
    ser.reset_input_buffer()
    return ser


def stream_from_serial(ser, set_cmd, seconds):
    if set_cmd:
        ser.write((set_cmd.strip() + "\n").encode())
    end = time.time() + seconds
    while time.time() < end:
        line = ser.readline().decode(errors="replace").strip()
        if not line:
            continue
        if line.startswith(("ACK", "ERR", "READY")):
            print("Arduino:", line)
            continue
        yield line
    ser.write(b"SET,0,0,0,0\n")        # stop the motor at the end


def stream_from_file(path, speed=1.0):
    for line in Path(path).read_text().splitlines():
        time.sleep(0.01 / speed)
        yield line


def run(lines, save_path=None, show=True, window_s=5.0):
    t, sp, rpm = deque(maxlen=int(window_s * 100)), deque(maxlen=500), deque(maxlen=500)
    raw = []
    if show:
        plt.ion()
        fig, ax = plt.subplots()
        l_sp, = ax.plot([], [], "--", label="Setpoint")
        l_rpm, = ax.plot([], [], label="Measured RPM")
        ax.set_xlabel("Time (s)"); ax.set_ylabel("Speed (RPM)")
        ax.set_ylim(0, 320); ax.grid(); ax.legend(loc="lower right")
    for i, line in enumerate(lines):
        try:
            row = parse_telemetry(line)
        except ValueError:
            continue
        raw.append(line)
        t.append(row[0] / 1000); sp.append(row[1]); rpm.append(row[2])
        if show and i % 5 == 0:        # redraw at 20 Hz, data still logged at 100 Hz
            l_sp.set_data(t, sp); l_rpm.set_data(t, rpm)
            ax.set_xlim(max(0, t[-1] - window_s), max(window_s, t[-1]))
            plt.pause(0.001)
    if save_path:
        Path(save_path).write_text("\n".join(raw) + "\n")
        print(f"Saved {len(raw)} rows to {save_path}")
    rows, _ = read_stream(raw)
    print(f"Rate {sample_rate_hz(rows):.1f} Hz, dropped frames: {dropped_frames(rows)}")
    if show:
        plt.ioff(); plt.show()
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port")
    ap.add_argument("--set", default="SET,120,1.2,8.0,0.0")
    ap.add_argument("--seconds", type=float, default=5.0)
    ap.add_argument("--replay")
    ap.add_argument("--no-plot", action="store_true")
    a = ap.parse_args()
    if a.replay:
        run(stream_from_file(a.replay), show=not a.no_plot)
    elif a.port:
        ser = open_serial(a.port)
        out = Path("data") / time.strftime("run_%Y%m%d_%H%M%S.csv")
        try:
            run(stream_from_serial(ser, a.set, a.seconds), save_path=out, show=not a.no_plot)
        finally:
            ser.close()
    else:
        ap.error("give --port COMx for hardware or --replay file.csv")


if __name__ == "__main__":
    main()
