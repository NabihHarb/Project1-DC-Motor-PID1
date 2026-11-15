"""A4 (R4): SET command updates gains and setpoint and is acknowledged."""
from src.controller import Controller


def test_A4_set_command_updates_gains_and_acknowledges():
    c = Controller(setpoint=120, kp=1.2, ki=8.0, kd=0.0)
    c.step(100)                                    # actively controlling
    reply = c.handle_command("SET,150,2.0,0.1,0.0\n")
    assert (c.pid.kp, c.pid.ki, c.pid.kd) == (2.0, 0.1, 0.0)
    assert c.setpoint == 150
    assert reply == "ACK,150,2,0.1,0"


def test_A4_bad_command_is_rejected_and_settings_kept():
    c = Controller(setpoint=120, kp=1.2, ki=8.0, kd=0.0)
    reply = c.handle_command("SET,150,2.0")
    assert reply.startswith("ERR")
    assert c.setpoint == 120 and c.pid.kp == 1.2
