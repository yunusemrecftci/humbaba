"""
Hakem Paketi Modülü (Eski versiyon - Geriye uyumluluk için)
Yeni protokol modülü kullanılması önerilir
"""

from .protocol import HYIProtocol


def create_hyi_packet(team_id, packet_counter, altitude, rocket_gps_altitude,
                     rocket_latitude, rocket_longitude, payload_gps_altitude,
                     payload_latitude, payload_longitude, stage_gps_altitude,
                     stage_latitude, stage_longitude, gyroscope_x, gyroscope_y,
                     gyroscope_z, acceleration_x, acceleration_y, acceleration_z,
                     angle, status):
    """
    HYİ haberleşme protokolüne uygun 78 byte'lık bir paket oluşturur.
    Geriye uyumluluk için korunmuştur.
    """
    return HYIProtocol.create_hyi_packet(
        team_id, packet_counter, altitude, rocket_gps_altitude,
        rocket_latitude, rocket_longitude, payload_gps_altitude,
        payload_latitude, payload_longitude, stage_gps_altitude,
        stage_latitude, stage_longitude, gyroscope_x, gyroscope_y,
        gyroscope_z, acceleration_x, acceleration_y, acceleration_z,
        angle, status
    )


def send_judge_packet_new(ser, team_id, packet_counter, data):
    """
    Yeni HYİ protokolüne uygun paket gönderir.
    Geriye uyumluluk için korunmuştur.
    """
    try:
        # Veriyi HYI protokolü formatına çevir
        parsed_data = HYIProtocol.parse_telemetry_data(data)
        
        # HYI paketi oluştur
        packet = HYIProtocol.create_hyi_packet(
            team_id=team_id,
            packet_counter=packet_counter,
            **parsed_data
        )
        
        # Paketi gönder
        ser.write(packet)
        print(f"HYİ paketi gönderildi. TeamID: {team_id}, Counter: {packet_counter}")
        return True
        
    except Exception as e:
        print(f"HYİ paket gönderim hatası: {e}")
        return False


# Eski fonksiyonlar için alias'lar
def send_judge_packet(ser, team_id, packet_counter, float_values, durum):
    """
    Eski format için uyumluluk fonksiyonu
    """
    # Float değerlerini dict'e çevir
    data = {}
    for i, value in enumerate(float_values):
        data[f'f{i+1}'] = value
    data['durum'] = durum
    
    return send_judge_packet_new(ser, team_id, packet_counter, data) 