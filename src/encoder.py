"""Encoder count -> RPM conversion (R1), mirrors the Arduino ISR logic.

The encoder gives 334 counts per revolution per channel (SPEC section 2).
With 4x quadrature decoding (both edges of A and B) that is 1336 edges/rev.
"""

CPR = 334
EDGES_PER_REV = CPR * 4   # 4x quadrature decoding
DT = 0.01                 # 10 ms sample period (R1)


def counts_to_rpm(counts, dt=DT, edges_per_rev=EDGES_PER_REV):
    """RPM from the number of encoder edges counted in a window of dt seconds."""
    return counts / edges_per_rev / dt * 60.0


WINDOW = 10   # samples in the moving window (10 x 10 ms = 100 ms)


class SpeedEstimator:
    """Called every 10 ms with the edges counted since the last call.

    A single 10 ms window has a resolution of 60/(1336*0.01) = 4.49 RPM per
    edge, which cannot meet A1 (+/-2 RPM). Summing the last WINDOW samples
    still gives a new value every 10 ms, with 0.45 RPM resolution.
    """

    def __init__(self, window=WINDOW):
        self.window = window
        self.history = []

    def update(self, counts):
        self.history.append(counts)
        if len(self.history) > self.window:
            self.history.pop(0)
        return counts_to_rpm(sum(self.history), dt=DT * len(self.history))


def simulate_counts(rpm, n_samples, dt=DT, edges_per_rev=EDGES_PER_REV):
    """Edges an ideal encoder produces in each dt window at constant rpm."""
    edges_per_s = rpm / 60.0 * edges_per_rev
    out, total_prev = [], 0
    for k in range(1, n_samples + 1):
        total = int(edges_per_s * k * dt)   # edges seen up to time k*dt
        out.append(total - total_prev)
        total_prev = total
    return out
