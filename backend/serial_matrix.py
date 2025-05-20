# === backend/serial_matrix.py ===
import serial

SERIAL_PORT = '/dev/ttyACM0'
BAUDRATE = 115200

# initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUDRATE)

def read_bytes(self, n):
    data = b''
    while len(data) < n:
        data += ser.read(n - len(data))
    return data

