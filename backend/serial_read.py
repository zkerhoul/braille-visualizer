# === backend/serial_read.py ===
import serial
import threading
import numpy as np

SERIAL_PORT = '/dev/tty.usbmodem1101'
BAUDRATE = 115200

class SerialHandler:
    def __init__(self, port=SERIAL_PORT, baudrate=BAUDRATE):
        # initialize serial connection
        self.ser = serial.Serial(port, baudrate)

        self.matrix = None
        self.lock = threading.Lock()
        self.running = True

        self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
        self.read_thread.start()

    def read_bytes(self, n):
        data = b''
        while len(data) < n:
            data += self.ser.read(n - len(data))
        return data

    def read_loop(self):
        while self.running:
            try:
                header = self.read_bytes(4)
            except Exception as e:
                print(f"Serial read header failed: {e}")
                continue

            if header == b'DOTS':
                try:
                    n = int.from_bytes(self.read_bytes(2), 'big')
                    m = int.from_bytes(self.read_bytes(2), 'big')

                    raw_mat = self.read_bytes(n * m * np.dtype('int32').itemsize)
                    mat = np.frombuffer(raw_mat, dtype=np.int32).reshape((n, m))

                    with self.lock:
                        self.matrix = mat.tolist()
                    print(f"Received matrix of shape {mat.shape}")

                except Exception as e:
                    print(f"Failed to handle DOTS message: {e}")

            # elif header == b'DOWN':
            #     try:
            #         x = int.from_bytes(self.read_bytes(2), 'big')
            #         y = int.from_bytes(self.read_bytes(2), 'big')
            #         id_num = int.from_bytes(self.read_bytes(1), 'big')
            #         finger = self.get_finger(id_num)
            #         finger['down'] = True
            #         finger['x'], finger['y'] = x, y
            #     except Exception as e:
            #         print(f"Error processing DOWN: {e}")
            #
            # elif header == b'UP__':
            #     try:
            #         x = int.from_bytes(self.read_bytes(2), 'big')
            #         y = int.from_bytes(self.read_bytes(2), 'big')
            #         id_num = int.from_bytes(self.read_bytes(1), 'big')
            #         finger = self.get_finger(id_num)
            #         finger['down'] = False
            #         finger['x'] = finger['y'] = None
            #     except Exception as e:
            #         print(f"Error processing UP: {e}")
            #
            # elif header == b'MOVE':
            #     try:
            #         x = int.from_bytes(self.read_bytes(2), 'big')
            #         y = int.from_bytes(self.read_bytes(2), 'big')
            #         id_num = int.from_bytes(self.read_bytes(1), 'big')
            #         self.root.after(0, self.handle_move, id_num, x, y)
            #     except Exception as e:
            #         print(f"Error processing MOVE: {e}")

            else:
                print(f"Unknown header: {header}")

    def close(self):
        self.running = False
        if self.ser.is_open:
            self.ser.close()
            print("Serial port closed")
