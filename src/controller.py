"""Command handling for the speed controller (R4), mirrors the firmware.

On 'SET,<sp>,<Kp>,<Ki>,<Kd>' the gains and setpoint are updated and an
acknowledgement 'ACK,<sp>,<Kp>,<Ki>,<Kd>' is returned. Bad input returns
'ERR,<reason>' and leaves the old settings unchanged.
"""
from src.pid import PID
from src.protocol import parse_set_command


class Controller:
    def __init__(self, setpoint=0.0, kp=1.2, ki=8.0, kd=0.0):
        self.setpoint = setpoint
        self.pid = PID(kp, ki, kd)

    def handle_command(self, line):
        try:
            cmd = parse_set_command(line)
        except ValueError as e:
            return f"ERR,{e}"
        self.setpoint = cmd["setpoint"]
        self.pid.set_gains(cmd["kp"], cmd["ki"], cmd["kd"])
        return "ACK,{setpoint:g},{kp:g},{ki:g},{kd:g}".format(**cmd)

    def step(self, measured_rpm):
        return self.pid.update(self.setpoint, measured_rpm)
