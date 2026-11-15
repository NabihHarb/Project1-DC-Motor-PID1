"""Serial message formats from SPEC section 5 (prepares R4 and R5)."""


def parse_set_command(line):
    """Parse 'SET,<setpoint>,<Kp>,<Ki>,<Kd>' -> dict. Raises ValueError if bad."""
    parts = line.strip().split(",")
    if len(parts) != 5 or parts[0] != "SET":
        raise ValueError(f"Invalid command: {line!r}")
    sp, kp, ki, kd = (float(p) for p in parts[1:])
    if not 0 <= sp <= 300:
        raise ValueError("Setpoint must be between 0 and 300 RPM")
    return {"setpoint": sp, "kp": kp, "ki": ki, "kd": kd}


def format_telemetry(t_ms, setpoint, rpm, pwm):
    """Build '<timestamp_ms>,<setpoint_rpm>,<measured_rpm>,<pwm_output>'."""
    return f"{int(t_ms)},{setpoint:g},{rpm:.1f},{int(round(pwm))}"


def parse_telemetry(line):
    t, sp, rpm, pwm = line.strip().split(",")
    return int(t), float(sp), float(rpm), int(pwm)
