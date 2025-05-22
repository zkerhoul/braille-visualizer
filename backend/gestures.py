# === backend/sketch.js ===
import time
from collections import deque

class GestureDetector:
    def __init__(self, window_ms=1000):
        self.history = {}  # dictionary: finger ID -> list of recent (x, y, t)
        self.window = window_ms

    def update(self, id_num, x, y):
        now = time.time() * 1000
        if id_num not in self.history:
            self.history[id_num] = deque()
        self.history[id_num].append((x, y, now))

        # clear data older than window
        while self.history[id_num] and now - self.history[id_num][0][2] > self.window:
            self.history[id_num].popleft()

        return self.detect(self.history[id_num])

    def detect(self, path):
        # not enough data to determine
        if len(path) < 5:
            return None

        x0, y0, _ = path[0]
        x1, y1, _ = path[-1]
        dx = x1 - x0
        dy = y1 - y0
        net_dist = (dx ** 2 + dy ** 2) ** 0.5

        total_dist = sum(
            ((path[i][0] - path[i - 1][0]) ** 2 +
             (path[i][1] - path[i - 1][1]) ** 2) ** 0.5
            for i in range(1, len(path))
        )

        ratio = total_dist / (net_dist + 1e-5)

        vertical_motion = abs(dy)
        horizontal_motion = abs(dx)

        if vertical_motion > 30 and horizontal_motion < 10 and total_dist > 100:
            return f"scrubbing - vertical motion: {vertical_motion} horizontal motion: {horizontal_motion}"

        # if ratio > 4 and total_dist > 100:
        #     return "scrubbing"
        # if dx < -50:
        #     return "regression"
        # if dx > 50 and ratio < 1.5:
        #     return "tracking"

        return None
