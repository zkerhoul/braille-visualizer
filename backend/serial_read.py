# === backend/serial_read.py ===
import serial
import threading
import numpy as np
import queue

from gestures import GestureDetector

SERIAL_PORT = 'COM6'
BAUDRATE = 115200

class SerialHandler:
    def __init__(self, port=SERIAL_PORT, baudrate=BAUDRATE):
        # initialize serial connection
        self.ser = serial.Serial(port, baudrate)

        self.running = True
        self.matrix = None
        self.events = queue.Queue()

        self.gesture_detector = GestureDetector()

        self.lock = threading.Lock()
        self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
        self.read_thread.start()

    def read_bytes(self, n):
        data = b''
        while len(data) < n:
            data += self.ser.read(n - len(data))
        return data

    def sync_header(self):
        while self.running:
            try:
                # read one byte at a time until 'M' is found (indicates start of message)
                b = self.ser.read(1)
                if b == b'M':
                    peek = self.ser.read(3)
                    if peek == b'FDN': # finger down
                        return b'MFDN'
                    elif peek ==b'FUP': # finger up
                        return b'MFUP'
                    elif peek == b'FMV': # finger move
                        return b'MFMV'
                    elif peek == b'MAT': # matrix update
                        return b'MMAT'
                    else:
                        # skip ahead one byte and try again
                        continue
            except Exception as e:
                print("Serial sync error:", e)

    def read_loop(self):
        while self.running:
            try:
                header = self.sync_header()
            except Exception as e:
                print(f"Serial read header failed: {e}")
                continue

            if header == b'MMAT':
                try:
                    n = int.from_bytes(self.read_bytes(2), 'big')
                    m = int.from_bytes(self.read_bytes(2), 'big')

                    raw_mat = self.read_bytes(n * m * np.dtype('int32').itemsize)
                    mat = np.frombuffer(raw_mat, dtype=np.int32).reshape((n, m))

                    with self.lock:
                        self.matrix = mat.tolist()
                    self.events.put({'type': 'matrix', 'mat': self.matrix})
                    # print(f"Received matrix of shape ({n},{m})")

                except Exception as e:
                    print(f"Error processing MAT: {e}")

            elif header == b'MFDN':
                try:
                    x = int.from_bytes(self.read_bytes(2), 'big')
                    y = int.from_bytes(self.read_bytes(2), 'big')
                    id_num = int.from_bytes(self.read_bytes(1), 'big')
                    
                    event = {'type': 'touch', 'action': 'down', 
                             'id': id_num, 'x': x, 'y': y}
                    self.events.put(event)
                    # print(f"Received DOWN message for id {id_num} at position ({x}, {y})")

                except Exception as e:
                    print(f"Error processing DOWN: {e}")
            
            elif header == b'MFUP':
                try:
                    x = int.from_bytes(self.read_bytes(2), 'big')
                    y = int.from_bytes(self.read_bytes(2), 'big')
                    id_num = int.from_bytes(self.read_bytes(1), 'big')

                    event = {'type': 'touch', 'action': 'up',
                             'id': id_num, 'x': x, 'y': y}
                    self.events.put(event)
                    # print(f"Received UP message for id {id_num} at position ({x}, {y})")

                except Exception as e:
                    print(f"Error processing UP: {e}")
            
            elif header == b'MFMV':
                try:
                    x = int.from_bytes(self.read_bytes(2), 'big')
                    y = int.from_bytes(self.read_bytes(2), 'big')
                    id_num = int.from_bytes(self.read_bytes(1), 'big')

                    gesture = self.gesture_detector.update(id_num, x, y)

                    event = {
                        'type': 'touch',
                        'action': 'move',
                        'gesture': gesture,
                        'id': id_num,
                        'x': x,
                        'y': y
                    }
                    self.events.put(event)
                    print(f"Received MOVE message for id {id_num} at position ({x}, {y})")

                except Exception as e:
                    print(f"Error processing MOVE: {e}")

            else:
                print(f"Unknown header: {header}")

    def close(self):
        self.running = False
        if self.ser.is_open:
            self.ser.close()
            print("Serial port closed")
