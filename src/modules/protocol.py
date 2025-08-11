"""
HYI Protokolü Modülü
Hakem Yer İstasyonu ile haberleşme protokolü
"""

import struct
from typing import List, Dict, Any


class HYIProtocol:
    """HYI (Hakem Yer İstasyonu) Protokolü"""
    
    HEADER = [0xFF, 0xFF, 0x54, 0x52]
    PACKET_SIZE = 78
    FLOAT_COUNT = 64  # 16 grup x 4 float
    
    @staticmethod
    def pack_floats(float_list: List[float]) -> bytes:
        """Bir float listesini little-endian byte dizisine çevirir."""
        return b''.join(struct.pack('<f', f) for f in float_list)
    
    @staticmethod
    def calculate_crc(data: bytes) -> int:
        """Verilen byte dizisinin XOR CRC'sini hesaplar (ilk 71 byte)."""
        crc = 0
        for b in data[:71]:
            crc ^= b
        return crc
    
    @staticmethod
    def create_hyi_packet(team_id: int, packet_counter: int, 
                         altitude: float, rocket_gps_altitude: float,
                         rocket_latitude: float, rocket_longitude: float, 
                         payload_gps_altitude: float, payload_latitude: float, 
                         payload_longitude: float, stage_gps_altitude: float,
                         stage_latitude: float, stage_longitude: float, 
                         gyroscope_x: float, gyroscope_y: float, gyroscope_z: float,
                         acceleration_x: float, acceleration_y: float, acceleration_z: float,
                         angle: float, status: int) -> bytes:
        """
        HYİ haberleşme protokolüne uygun 78 byte'lık bir paket oluşturur.
        """
        packet = bytearray(78)
        
        # Sabit başlık
        packet[0:4] = HYIProtocol.HEADER
        
        # Takım ID (UINT8)
        packet[4] = team_id & 0xFF
        
        # Paket Sayacı (UINT8)
        packet[5] = packet_counter & 0xFF
        
        # Float değerleri
        float_values = [
            altitude, rocket_gps_altitude, rocket_latitude, rocket_longitude,
            payload_gps_altitude, payload_latitude, payload_longitude,
            stage_gps_altitude, stage_latitude, stage_longitude,
            gyroscope_x, gyroscope_y, gyroscope_z,
            acceleration_x, acceleration_y, acceleration_z,
            angle, 0.0, 0.0, 0.0,  # Son 3 değer boş
            # ... 64 float değeri tamamlanana kadar 0.0 ile doldur
        ]
        
        # 64 float değeri için doldur
        while len(float_values) < 64:
            float_values.append(0.0)
        
        # Float değerleri byte'lara çevir ve pakete ekle
        float_bytes = HYIProtocol.pack_floats(float_values)
        packet[6:70] = float_bytes
        
        # Durum byte'ı
        packet[70] = status & 0xFF
        
        # CRC hesapla ve ekle
        crc = HYIProtocol.calculate_crc(packet)
        packet[71] = crc
        
        # Son byte'lar
        packet[72] = 0x0D
        packet[73] = 0x0A
        
        return bytes(packet)
    
    @staticmethod
    def parse_telemetry_data(data: Dict[str, Any]) -> Dict[str, float]:
        """Telemetri verisini HYI protokolü için uygun formata çevirir."""
        return {
            'altitude': data.get('irtifa', 0.0),
            'rocket_gps_altitude': data.get('gps_irtifa', 0.0),
            'rocket_latitude': data.get('enlem', 0.0),
            'rocket_longitude': data.get('boylam', 0.0),
            'payload_gps_altitude': data.get('gps_irtifa', 0.0),
            'payload_latitude': data.get('enlem', 0.0),
            'payload_longitude': data.get('boylam', 0.0),
            'stage_gps_altitude': data.get('gps_irtifa', 0.0),
            'stage_latitude': data.get('enlem', 0.0),
            'stage_longitude': data.get('boylam', 0.0),
            'gyroscope_x': data.get('jiroskop_x', 0.0),
            'gyroscope_y': data.get('jiroskop_y', 0.0),
            'gyroscope_z': data.get('jiroskop_z', 0.0),
            'acceleration_x': data.get('ivme_x', 0.0),
            'acceleration_y': data.get('ivme_y', 0.0),
            'acceleration_z': data.get('ivme_z', 0.0),
            'angle': data.get('aci', 0.0),
            'status': data.get('durum', 1)
        }
