import pytest
from src.protocol import parse_set_command, format_telemetry, parse_telemetry


def test_parse_set_command_spec_example():
    assert parse_set_command("SET,150,2.0,0.1,0.0\n") == {
        "setpoint": 150.0, "kp": 2.0, "ki": 0.1, "kd": 0.0}


@pytest.mark.parametrize("bad", ["SET,150,2.0", "GO,1,2,3,4", "SET,a,1,1,1", "SET,400,1,1,1"])
def test_parse_set_command_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        parse_set_command(bad)


def test_telemetry_round_trip():
    line = format_telemetry(1000, 120, 118.5, 142)
    assert line == "1000,120,118.5,142"
    assert parse_telemetry(line) == (1000, 120.0, 118.5, 142)
