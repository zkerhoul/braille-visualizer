# === backend/serial_matrix.py ===
import serial
import numpy as np

SERIAL_PORT = '/dev/ttyACM0'
BAUDRATE = 115200

# initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUDRATE)

def read_bytes(self, n):
    data = b''
    while len(data) < n:
        data += ser.read(n - len(data))
    return data

def read_serial(self):
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

                raw_arr = self.read_bytes(n * m * np.dtype('int32').itemsize)
                arr = np.frombuffer(raw_arr, dtype=np.int32).reshape((n, m))

                print(f"Received array of shape {arr.shape}")
                self.root.after(0, self.update_dots, arr)
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


