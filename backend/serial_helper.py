import struct
import numpy as np

SOF_BYTE = 0xAA
EVENT_DOWN = 1
EVENT_UP = 2
EVENT_MOVE = 3
EVENT_MATRIX = 4

# CRC‐8 (polynomial 0x07) implementation


def crc8(buffer: bytes, poly: int = 0x07, init: int = 0x00) -> int:
    crc = init
    for byte in buffer:
        crc ^= byte
        for _ in range(8):
            if (crc & 0x80) != 0:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFF
    return crc


def pack_touch_event(event_code: int, x: int, y: int, finger_id: int) -> bytes:
    # 1) Build the 7-byte header:
    header = struct.pack(
        '<B B H H B',
        SOF_BYTE,       # 0xAA
        event_code,     # 1,2,3
        x & 0xFFFF,     # uint16 LE
        y & 0xFFFF,     # uint16 LE
        finger_id & 0xFF
    )
    # 2) Compute CRC-8 over those 7 bytes:
    checksum = crc8(header)
    # 3) Append the CRC byte to get an 8-byte packet:
    return header + struct.pack('<B', checksum)


def pack_matrix_bitpacked(matrix: np.ndarray) -> bytes:
    """
    Build a 247-byte packet carrying a 20×96 uint8 array (with only 0/1 entries).
    Packet format:
      [0]      = 0xAA
      [1]      = EVENT_MATRIX (4)
      [2]      = rows (uint8)     → must be 20
      [3]      = cols (uint8)     → must be 96
      [4..5]   = payload_len (uint16 LE) → 240
      [6..245] = 240 bytes of bit-packed data (12 bytes per row × 20 rows)
      [246]    = CRC-8 over bytes [0..245]
    """
    # 1) Validate shape & dtype
    if matrix.dtype != np.uint8:
        raise ValueError("Matrix must be dtype=uint8 containing only 0 or 1.")
    rows, cols = matrix.shape
    if (rows, cols) != (20, 96):
        raise ValueError(f"Expected shape (20,96), got ({rows},{cols})")

    # 2) Bit-pack each row: 96 bits → 12 bytes
    #    np.packbits packs along the last axis by default;
    #    axis=1 ensures each row of length 96 → array of length 12.
    packed = np.packbits(matrix, axis=1)
    #    shape of `packed` is now (20, 12), dtype=uint8

    payload = packed.tobytes(order="C")  # 20*12 = 240 bytes

    # 3) Header: <B B B B H> → 1+1+1+1+2 = 6 bytes
    header = struct.pack(
        "<B B B B H",
        SOF_BYTE,           # 0xAA
        EVENT_MATRIX,           # 4
        rows & 0xFF,            # 20
        cols & 0xFF,            # 96
        len(payload) & 0xFFFF   # 240
    )

    # 4) Compute CRC over (header + payload)
    checksum = crc8(header + payload)

    return header + payload + struct.pack("<B", checksum)


def unpack_matrix_bitpacked_packet(header_payload: bytes, payload: bytes) -> np.ndarray:
    """
    Given:
      header_payload = the 6 bytes [SOF, TYPE_MATRIX, rows, cols, payload_len_low, payload_len_high]
      payload = the next (rows*pack_bytes_per_row) bytes (for a 20×96 array, that’s 240 bytes),
    returns a (rows × cols) numpy array of dtype uint8 containing 0/1.
    """
    # Unpack rows, cols, payload_len from header_payload:
    _, ptype, rows, cols, payload_len = struct.unpack(
        "<B B B B H", header_payload)
    # Sanity checks (you can relax if you want):
    if ptype != EVENT_MATRIX:
        raise ValueError(
            f"Incorrect packet type: expected {EVENT_MATRIX}, got {ptype}")
    if (rows, cols) != (20, 96):
        raise ValueError(
            f"Unexpected matrix shape: ({rows},{cols}), expected (20,96)")
    if payload_len != 240:
        raise ValueError(
            f"Unexpected payload length: {payload_len}, expected 240")

    # Now payload is 240 bytes; reshape into (20, 12) of uint8, then unpack bits:
    arr_packed = np.frombuffer(
        payload, dtype=np.uint8).reshape((20, 12), order="C")
    # → shape (20, 96), values 0 or 1
    matrix = np.unpackbits(arr_packed, axis=1)
    return matrix
