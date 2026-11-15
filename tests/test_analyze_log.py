"""Tools used to turn bench logs into A1/A3/A5 results."""
from pathlib import Path
import pytest
from src.analyze_log import settling_time_s, speed_error
from src.logger import read_stream
from src.plot_live import run, stream_from_file

SAMPLE = Path(__file__).parent.parent / "data" / "sample_step.csv"


def rows_of(lines):
    return read_stream(lines)[0]


def test_settling_time_on_sample_log_matches_simulation():
    rows = rows_of(SAMPLE.read_text().splitlines())
    assert settling_time_s(rows, 120) == pytest.approx(0.32)


def test_settling_time_measured_from_the_step_not_from_log_start():
    pre = [f"{t},0,0.0,0" for t in range(0, 500, 10)]              # 0.5 s idle
    step = [f"{500 + t},120,{0 if t < 300 else 120}.0,150" for t in range(0, 1000, 10)]
    assert settling_time_s(rows_of(pre + step), 120) == pytest.approx(0.30)


def test_never_settles_returns_none():
    assert settling_time_s(rows_of([f"{t},120,50.0,255" for t in range(0, 500, 10)]), 120) is None


def test_speed_error_against_tachometer_reference():
    rows = rows_of([f"{t},100,{101 if t % 20 else 99}.0,120" for t in range(0, 2000, 10)])
    mean_err, worst = speed_error(rows, 100)
    assert abs(mean_err) < 0.1 and worst == pytest.approx(1.0)


def test_A5_replay_through_plotter_logs_every_frame(tmp_path):
    out = tmp_path / "run.csv"
    rows = run(stream_from_file(SAMPLE, speed=1000), save_path=out, show=False)
    assert len(rows) == 200
    assert out.read_text() == SAMPLE.read_text()
