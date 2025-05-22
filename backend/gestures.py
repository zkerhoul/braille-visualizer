# === backend/gestures.py ===
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
        if len(path) < 5:
            return None

        x_path = [p[0] for p in path]
        y_path = [p[1] for p in path]

        dx = max(x_path) - min(x_path)
        dy = max(y_path) - min(y_path)

        # check that horizontal movement is minimal
        if dx > 25:
            # print(f"[NEGATIVE] Exceeded horizontal threshold - dx = {dx}")
            return None

        # estimate zero-crossings (up-down movements)
        y_mid = sorted(y_path)[len(y_path) // 2]
        y_signs = [1 if y > y_mid else -1 for y in y_path]
        y_crossings = sum(1 for i in range(1, len(y_signs)) if y_signs[i] != y_signs[i - 1])

        if y_crossings < 2:
            # print(f"[NEGATIVE] Too few crossings - y_crossings = {y_crossings}")
            return None

        # print(f"\n[POSITIVE] Scrubbing detected - dx = {dx}, y_crossings = {y_crossings}\n")
        return "scrubbing"
