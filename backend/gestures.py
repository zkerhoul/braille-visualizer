# === backend/gestures.py ===
import time
from collections import deque

class GestureDetector:
    def __init__(self, window_ms=750):
        self.window = window_ms

        self.history = {}  # dictionary: finger ID -> list of recent (x, y, t)
        self.last_gesture = {}

    def update(self, id_num, x, y):
        now = time.time() * 1000
        if id_num not in self.history:
            self.history[id_num] = deque()
            self.last_gesture[id_num] = None
        self.history[id_num].append((x, y, now))

        # clear data older than window
        while self.history[id_num] and now - self.history[id_num][0][2] > self.window:
            self.history[id_num].popleft()

        gesture = self.detect(self.history[id_num], self.last_gesture[id_num])
        self.last_gesture[id_num] = gesture
        return gesture

    def detect(self, path, last_gesture):
        # not enough data
        if len(path) < 5:
            return None

        if self.is_scrubbing(path):
            return "scrubbing"

        elif self.is_regression(path, last_gesture):
            return "regression"

        else:
            return None

    def is_scrubbing(self, path):
        x_path = [p[0] for p in path]
        y_path = [p[1] for p in path]

        x_range = max(x_path) - min(x_path)
        y_range = max(y_path) - min(y_path)

        # check that horizontal movement is minimal
        if x_range > 25:
            # print(f"[NEGATIVE] Exceeded horizontal threshold - dx = {dx}")
            return False

        # estimate zero-crossings (up-down movements)
        y_mid = sorted(y_path)[len(y_path) // 2]
        y_signs = [1 if y > y_mid else -1 for y in y_path]
        y_crossings = sum(1 for i in range(1, len(y_signs)) if y_signs[i] != y_signs[i - 1])

        if y_crossings < 2:
            # print(f"[NEGATIVE] Too few crossings - y_crossings = {y_crossings}")
            return False

        # print(f"\n[POSITIVE] Scrubbing detected - dx = {dx}, y_crossings = {y_crossings}\n")
        return True

    def is_regression(self, path, last_gesture):
        x_path = [p[0] for p in path]
        y_path = [p[1] for p in path]

        # check if we are in the middle of a regression
        dx = x_path[-1] - x_path[-2]
        dy = y_path[-1] - y_path[-2]
        if last_gesture == "regression" and dx <= 0 and dy <= 50:
            return True

        # check that we're on the same braille line
        y_range = max(y_path) - min(y_path)
        if y_range > 50:
            # print(f"[LOG] Exceeded vertical threshold - y_range: {y_range}")
            return False

        # look for forward movement, then backward movement
        forward = False
        backward = False
        for i in range(1, len(x_path)):
            dx = x_path[i] - x_path[i - 1]
            if dx > 5:
                # print(f"[LOG] Forward movement detected - dx: {dx}")
                forward = True
            if dx < -5 and (forward is True or last_gesture == "scrubbing"):
                # print(f"[LOG] Backward movement detected - dx: {dx}")
                backward = True
                break
            # print(f"[LOG] Movement detected - dx: {dx}")

        if backward:
            # print("\n[POSITIVE] Regression detected\n")
            return True
        else:
            return False


