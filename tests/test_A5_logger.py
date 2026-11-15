"""A5 (R5): logger receives 100 Hz step-response data without dropping frames.

The live plot window and the USB link need the hardware (TESTING.md P5);
these tests check the logging logic on the sample data file.
"""
from pathlib import Path
from src.logger import read_stream, dropped_frames, sample_rate_hz

SAMPLE = Path(__file__).parent.parent / "data" / "sample_step.csv"


def test_A5_sample_stream_is_100hz_with_no_dropped_frames():
    rows, bad = read_stream(SAMPLE.read_text().splitlines())
    assert bad == 0
    assert len(rows) == 200
    assert dropped_frames(rows) == 0
    assert sample_rate_hz(rows) == 100.0


def test_A5_detects_dropped_frames():
    lines = ["0,120,0.0,154", "10,120,12.0,148", "40,120,30.0,140"]
    rows, _ = read_stream(lines)
    assert dropped_frames(rows) == 2          # 20 ms and 30 ms missing


def test_A5_malformed_line_does_not_crash_logger():
    rows, bad = read_stream(["0,120,0.0,154", "10,12", "garbage", "20,120,22.8,143"])
    assert len(rows) == 2 and bad == 2
