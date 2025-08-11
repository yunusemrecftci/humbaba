import struct

HEADER = [0xFF, 0xFF, 0x54, 0x52]
PACKET_SIZE = 78
FLOAT_COUNT = 64  # 16 grup x 4 float

def pack_floats(float_list):
    """Bir float listesini little-endian byte dizisine çevirir."""
    return b''.join(struct.pack('<f', f) for f in float_list)

def calculate_crc(data: bytes) -> int:
    """Verilen byte dizisinin XOR CRC'sini hesaplar (ilk 71 byte)."""
    crc = 0
    for b in data[:71]:
        crc ^= b
    return crc

def send_judge_packet(ser, team_id, packet_counter, float_values, durum):
    """
    Hakem yer istasyonu için 78 byte'lık veri paketini gönderir.
    float_values: 64 elemanlı float listesi (her biri 4 byte)
    """
    if len(float_values) != FLOAT_COUNT:
        raise ValueError(f"float_values must have {FLOAT_COUNT} elements!")

    packet = bytearray(PACKET_SIZE)
    # Header
    packet[0:4] = bytes(HEADER)
    packet[4] = team_id
    packet[5] = packet_counter
    # Float veriler
    packet[6:6+FLOAT_COUNT*4] = pack_floats(float_values)
    # Durum
    packet[70] = durum
    # CRC
    packet[71] = calculate_crc(packet)
    # Paket sonu
    packet[72] = 0x0D
    packet[73] = 0x0A
    # Son 4 byte (74-77) sıfır (isteğe bağlı başka veri eklenebilir)
    ser.write(packet)

def example_float_values():
    """Test için örnek 64 float'lık veri üretir."""
    # Her grup için 4 float (ör: irtifa1-4, roket_gps_irtifa1-4, ...)
    return [
        100.0, 101.0, 102.0, 103.0,  # irtifa1-4
        200.0, 201.0, 202.0, 203.0,  # roket_gps_irtifa1-4
        39.95, 39.96, 39.97, 39.98,  # roket_enlem1-4
        32.8, 32.81, 32.82, 32.83,   # roket_boylam1-4
        300.0, 301.0, 302.0, 303.0,  # yuk_gps_irtifa1-4
        39.85, 39.86, 39.87, 39.88,  # yuk_enlem1-4
        32.7, 32.71, 32.72, 32.73,   # yuk_boylam1-4
        400.0, 401.0, 402.0, 403.0,  # kademe_gps_irtifa1-4
        39.75, 39.76, 39.77, 39.78,  # kademe_enlem1-4
        32.6, 32.61, 32.62, 32.63,   # kademe_boylam1-4
        1.0, 1.1, 1.2, 1.3,          # gyro_x1-4
        2.0, 2.1, 2.2, 2.3,          # gyro_y1-4
        3.0, 3.1, 3.2, 3.3,          # gyro_z1-4
        4.0, 4.1, 4.2, 4.3,          # accel_x1-4
        5.0, 5.1, 5.2, 5.3,          # accel_y1-4
        6.0, 6.1, 6.2, 6.3,          # accel_z1-4
        45.0, 46.0, 47.0, 48.0       # aci1-4
    ] 