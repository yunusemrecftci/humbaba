import sys
import json
import struct
import threading
import serial
import serial.tools.list_ports
import sqlite3
import datetime
import random
import time
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QUrl, QLocale, QVariant, QPoint
from PyQt5.QtGui import QPolygon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtTextToSpeech import QTextToSpeech
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor, QLinearGradient, QRadialGradient, QImage, QTransform, QPolygon
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtCore import Qt

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


def create_hyi_packet(team_id, packet_counter, altitude, rocket_gps_altitude,
                      rocket_latitude, rocket_longitude, payload_gps_altitude,
                      payload_latitude, payload_longitude, stage_gps_altitude,
                      stage_latitude, stage_longitude, gyroscope_x, gyroscope_y,
                      gyroscope_z, acceleration_x, acceleration_y, acceleration_z,
                      angle, status):
    """
    HYİ haberleşme protokolüne uygun 78 byte'lık bir paket oluşturur.
    """
    packet = bytearray(78) # 78 byte uzunluğunda boş bir bayt dizisi

    # Sabit başlık ve kuyruk değerleri
    packet[0] = 0xFF
    packet[1] = 0xFF
    packet[2] = 0x54
    packet[3] = 0x52

    # Takım ID (UINT8 - doğrudan atanabilir)
    packet[4] = team_id & 0xFF  # 0-255 aralığını garantilemek için bitmaske

    # Paket Sayacı (UINT8 - doğrudan atanabilir)
    packet[5] = packet_counter & 0xFF

    # FLOAT32 değerleri için byte dönüşümü ve atama
    def float_to_bytes(f):
        return struct.pack('<f', f)

    # İrtifa
    _bytes = float_to_bytes(altitude)
    packet[6:10] = _bytes

    # Roket GPS İrtifa
    _bytes = float_to_bytes(rocket_gps_altitude)
    packet[10:14] = _bytes

    # Roket Enlem
    _bytes = float_to_bytes(rocket_latitude)
    packet[14:18] = _bytes

    # Roket Boylam
    _bytes = float_to_bytes(rocket_longitude)
    packet[18:22] = _bytes

    # Görev Yükü GPS İrtifa
    _bytes = float_to_bytes(payload_gps_altitude)
    packet[22:26] = _bytes

    # Görev Yükü Enlem
    _bytes = float_to_bytes(payload_latitude)
    packet[26:30] = _bytes

    # Görev Yükü Boylam
    _bytes = float_to_bytes(payload_longitude)
    packet[30:34] = _bytes

    # Kademe GPS İrtifa
    _bytes = float_to_bytes(stage_gps_altitude)
    packet[34:38] = _bytes

    # Kademe Enlem
    _bytes = float_to_bytes(stage_latitude) 
    packet[38:42] = _bytes

    # Kademe Boylam
    _bytes = float_to_bytes(stage_longitude)
    packet[42:46] = _bytes

    # Jiroskop X
    _bytes = float_to_bytes(gyroscope_x)
    packet[46:50] = _bytes

    # Jiroskop Y
    _bytes = float_to_bytes(gyroscope_y)
    packet[50:54] = _bytes

    # Jiroskop Z
    _bytes = float_to_bytes(gyroscope_z)
    packet[54:58] = _bytes

    # İvme X
    _bytes = float_to_bytes(acceleration_x)
    packet[58:62] = _bytes

    # İvme Y
    _bytes = float_to_bytes(acceleration_y)
    packet[62:66] = _bytes

    # İvme Z
    _bytes = float_to_bytes(acceleration_z)
    packet[66:70] = _bytes

    # Açı
    _bytes = float_to_bytes(angle)
    packet[70:74] = _bytes

    # Durum (UINT8 - doğrudan atanabilir)
    packet[74] = status & 0xFF

    # Checksum Hesaplama
    checksum = sum(packet[4:75]) % 256
    packet[75] = checksum

    # Sabit kuyruk değerleri
    packet[76] = 0x0D
    packet[77] = 0x0A

    return packet

def send_judge_packet_new(ser, team_id, packet_counter, data):
    """
    Yeni HYİ protokolüne uygun paket gönderir.
    """
    try:
        # Paketi oluştur
        hyi_packet = create_hyi_packet(
            team_id,
            packet_counter,
            data.get("altitude", 0.0),
            data.get("rocket_gps_altitude", 0.0),
            data.get("rocket_latitude", 0.0),
            data.get("rocket_longitude", 0.0),
            data.get("payload_gps_altitude", 0.0),
            data.get("payload_latitude", 0.0),
            data.get("payload_longitude", 0.0),
            data.get("stage_gps_altitude", 0.0),
            data.get("stage_latitude", 0.0),
            data.get("stage_longitude", 0.0),
            data.get("gyroscope_x", 0.0),
            data.get("gyroscope_y", 0.0),
            data.get("gyroscope_z", 0.0),
            data.get("acceleration_x", 0.0),
            data.get("acceleration_y", 0.0),
            data.get("acceleration_z", 0.0),
            data.get("angle", 0.0),
            data.get("status", 1)
        )
        
        # Paketi gönder
        ser.write(hyi_packet)
        print(f"HYİ paketi gönderildi. TeamID: {team_id}, Counter: {packet_counter}")
        return True
    except Exception as e:
        print(f"HYİ paket gönderim hatası: {e}")
        return False


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


class PacketSender(QObject):
    packetSent = pyqtSignal(str, str)
    connectionStatusChanged = pyqtSignal(bool)
    playOrder66Video = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_connected = False
        self.player = QMediaPlayer()
        self.muted = False

    @pyqtSlot()
    def connectToGroundStation(self):
        # Simulate connection to ground station
        self.is_connected = True
        self.connectionStatusChanged.emit(True)

    @pyqtSlot()
    def disconnectFromGroundStation(self):
        self.is_connected = False
        self.connectionStatusChanged.emit(False)

    @pyqtSlot(str, str)
    def sendPacket(self, packet_type, data):
        # Eğer özel komut ise sadece mp3 çal veya sesli oku
        if data.strip().lower() in ["execute order 66", "boğa"]:
            mp3_path = os.path.abspath("a.mp3")
            if os.path.exists(mp3_path):
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(mp3_path)))
                self.player.setVolume(0 if self.muted else 100)
                self.player.play()
            return
        if data.strip().lower() == "canpolat":
            # Sadece 'tam bir adam' cümlesini sesli oku
            app = QApplication.instance()
            for obj in app.children():
                if hasattr(obj, 'tts'):
                    obj.tts.say("tam bir göt")
                    break
            return
        # Simulate packet sending
        status = "Başarılı" if self.is_connected else "Başarısız"
        self.packetSent.emit(packet_type, status)

    @pyqtSlot()
    def clearPacketQueue(self):
        # Simulate clearing packet queue
        pass

    @pyqtSlot(bool)
    def setMuted(self, muted):
        self.muted = muted
        self.player.setVolume(0 if self.muted else 100)

class TelemetryBridge(QObject):
    telemetryUpdated = pyqtSignal('QVariant')
    packetSent = pyqtSignal(str, str)
    portListChanged = pyqtSignal(list)
    connectionStatusChanged = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.counter = 0
        self.ser = None
        self.running = False
        self.selected_port = None
        self.team_id = 0
        self.ports = []
        self.scan_ports()

    @pyqtSlot(result=list)
    def get_ports(self):
        self.scan_ports()
        return self.ports

    def scan_ports(self):
        self.ports = [p.
        device for p in serial.tools.list_ports.comports()]
        self.portListChanged.emit(self.ports)

    @pyqtSlot(str, int, int)
    def connect_port(self, port_name, team_id, baudrate):
        self.selected_port = port_name
        self.team_id = team_id
        try:
            self.ser = serial.Serial(port_name, baudrate, timeout=1)
            self.running = True
            self.connectionStatusChanged.emit(True, f"{port_name} portuna bağlandı ({baudrate} baud)")
            threading.Thread(target=self.read_serial, daemon=True).start()
        except Exception as e:
            self.connectionStatusChanged.emit(False, f"Bağlantı hatası: {e}")

    @pyqtSlot()
    def disconnect_port(self):
        if self.ser and self.running:
            self.running = False
            self.ser.close()
            self.ser = None
            self.connectionStatusChanged.emit(False, "Bağlantı kesildi")
        # Fake telemetriyi de durdur
        if not self.ser and self.running:
            self.running = False
            self.connectionStatusChanged.emit(False, "Fake telemetri durduruldu")

    def read_serial(self):
        while self.running:
            try:
                if not self.ser or not self.ser.is_open:
                    print("Seri port kapalı, okuma thread'i sonlandırılıyor.")
                    break
                line = self.ser.readline().decode(errors="ignore").strip()
                if not line:
                    continue
                # Saat ve ok işaretinden sonrasını al
                if '->' in line:
                    _, json_str = line.split('->', 1)
                    json_str = json_str.strip()
                else:
                    json_str = line
                json_data = json.loads(json_str)
                # Convert to QVariant for QML compatibility
                qvariant_data = QVariant(json_data)
                self.telemetryUpdated.emit(qvariant_data)
                self.send_to_judge(json_data)  # Keep original dict for judge
                # Log telemetry data if logManager is available
                if hasattr(self, 'log_manager') and self.log_manager:
                    self.log_manager.log_telemetry(json_data)
            except Exception as e:
                print(f"Seri okuma/işleme hatası: {e}")
                break  # Hata olursa thread'i sonlandır

    def send_to_judge(self, data):
        # EK-7'ye uygun veri gönderimi
        try:
            from modules.judge_packet import send_judge_packet, FLOAT_COUNT
        except ImportError:
            print("judge_packet modülü bulunamadı!")
            return
        if not self.ser:
            print("Seri port bağlı değil!")
            return
        # 64 float'lık listeyi EK-7'ye uygun sırayla oluştur
        float_values = []
        # Örnek: 16 grup x 4 float (EK-7'ye göre doldurulmalı)
        # Burada örnek olarak 0.0 ile dolduruluyor, gerçek verilerle değiştirilmeli
        for i in range(FLOAT_COUNT):
            key = f"f{i+1}"
            float_values.append(float(data.get(key, 0.0)))
        # Durum byte'ı (örnek: 0, gerçek uygulamada uygun şekilde ayarlanmalı)
        durum = int(data.get("durum", 0))
        # Takım numarası ve sayaç
        team_id = self.team_id % 256
        packet_counter = self.counter % 256
        self.counter += 1
        try:
            send_judge_packet(self.ser, team_id, packet_counter, float_values, durum)
            print(f"EK-7'ye uygun paket gönderildi. TeamID: {team_id}, Counter: {packet_counter}, Durum: {durum}")
            self.packetSent.emit("json", "Başarılı")
        except Exception as e:
            print(f"Hakem paket gönderim hatası: {e}")
            self.packetSent.emit("json", "Başarısız")

    def start_fake_telemetry(self):
        print("Fake telemetri başlatılıyor...")
        self.running = True
        self.ser = None
        def fake_loop():
            while self.running:
                # Create Python dict and convert to QVariant
                data = {
                    "irtifa": round(random.uniform(100, 5400), 2),
                    "gps_irtifa": round(random.uniform(100,4000), 2),
                    "enlem": round(random.uniform(39.9, 40.1), 6),
                    "boylam": round(random.uniform(32.7, 32.9), 6),
                    "ivme_x": round(random.uniform(-2, 2), 2),
                    "ivme_y": round(random.uniform(-2, 2), 2),
                    "ivme_z": round(random.uniform(-2, 2), 2),
                    "jiroskop_x": round(random.uniform(-180, 180), 2),
                    "jiroskop_y": round(random.uniform(-180, 180), 2),
                    "jiroskop_z": round(random.uniform(-180, 180), 2),
                    "aci": round(random.uniform(0, 360), 2),
                    "yuk": round(random.uniform(0, 100), 2),
                    "basinc": round(random.uniform(900, 1100), 2)
                }
                
                print(f"Fake telemetri verisi gönderiliyor: {data}")
                print(f"Veri türü: {type(data)}")
                print(f"İrtifa değeri: {data['irtifa']} (tür: {type(data['irtifa'])})")
                
                # Convert to QVariant for QML compatibility
                qvariant_data = QVariant(data)
                self.telemetryUpdated.emit(qvariant_data)
                
                # Log telemetry data if logManager is available
                if hasattr(self, 'log_manager') and self.log_manager:
                    self.log_manager.log_telemetry(data)
                time.sleep(1)
        threading.Thread(target=fake_loop, daemon=True).start()

    @pyqtSlot()
    def startFakeTelemetry(self):
        self.start_fake_telemetry()

class SpeechHelper(QObject):
    def __init__(self):
        super().__init__()
        self.tts = QTextToSpeech()
        self.tts.setLocale(QLocale("tr_TR"))
        self.muted = False

    @pyqtSlot(str)
    def speak(self, text):
        if not self.muted:
            self.tts.say(text)

    @pyqtSlot(bool)
    def setMuted(self, muted):
        self.muted = muted

    @pyqtSlot()
    def stopSpeaking(self):
        self.tts.stop()

class LogManager(QObject):
    logUpdated = pyqtSignal()
    flightListUpdated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db_path = "flight_logs.db"
        self.current_flight_id = None
        self.init_database()
    
    def init_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS telemetry_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flight_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data TEXT,
                    FOREIGN KEY (flight_id) REFERENCES flights (id)
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    @pyqtSlot(str)
    def start_flight(self, flight_name):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO flights (name) VALUES (?)", (flight_name,))
            self.current_flight_id = cursor.lastrowid
            conn.commit()
            conn.close()
            self.flightListUpdated.emit()
        except Exception as e:
            print(f"Error starting flight: {e}")
    
    @pyqtSlot(int)
    def end_flight(self, flight_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE flights SET end_time = CURRENT_TIMESTAMP WHERE id = ?", (flight_id,))
            conn.commit()
            conn.close()
            self.flightListUpdated.emit()
        except Exception as e:
            print(f"Error ending flight: {e}")
    
    @pyqtSlot(result='QVariant')
    def get_flight_list(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, start_time, end_time FROM flights ORDER BY start_time DESC")
            flights = []
            for row in cursor.fetchall():
                flights.append({
                    "id": row[0],
                    "name": row[1],
                    "start_time": row[2],
                    "end_time": row[3]
                })
            conn.close()
            return flights
        except Exception as e:
            print(f"Error getting flight list: {e}")
            return []
    
    @pyqtSlot(int, result='QVariant')
    def get_logs_for_flight(self, flight_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, data FROM telemetry_logs WHERE flight_id = ? ORDER BY timestamp", (flight_id,))
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    "timestamp": row[0],
                    "data": row[1]
                })
            conn.close()
            return logs
        except Exception as e:
            print(f"Error getting logs for flight: {e}")
            return []
    
    @pyqtSlot(dict)
    def log_telemetry(self, data):
        if self.current_flight_id:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO telemetry_logs (flight_id, data) VALUES (?, ?)", 
                             (self.current_flight_id, json.dumps(data)))
                conn.commit()
                conn.close()
                self.logUpdated.emit()
            except Exception as e:
                print(f"Error logging telemetry: {e}")
    
    @pyqtSlot(int, result='QVariant')
    def get_flight_statistics(self, flight_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM telemetry_logs WHERE flight_id = ? ORDER BY timestamp", (flight_id,))
            logs = cursor.fetchall()
            conn.close()
            
            if not logs:
                return {}
            
            # Parse all telemetry data
            telemetry_data = []
            for log in logs:
                try:
                    data = json.loads(log[0])
                    telemetry_data.append(data)
                except:
                    continue
            
            if not telemetry_data:
                return {}
            
            # Calculate statistics for each field
            stats = {}
            numeric_fields = [
                "irtifa", "gps_irtifa", "enlem", "boylam",
                "ivme_x", "ivme_y", "ivme_z",
                "jiroskop_x", "jiroskop_y", "jiroskop_z",
                "aci", "yuk", "basinc"
            ]
            
            for field in numeric_fields:
                values = []
                for data in telemetry_data:
                    if field in data and data[field] is not None:
                        try:
                            values.append(float(data[field]))
                        except:
                            continue
                
                if values:
                    stats[field] = {
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                        "count": len(values)
                    }
            
            return stats
        except Exception as e:
            print(f"Error getting flight statistics: {e}")
            return {}
    
    @pyqtSlot(int, result='QVariant')
    def get_flight_data_for_graph(self, flight_id, field):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, data FROM telemetry_logs WHERE flight_id = ? ORDER BY timestamp", (flight_id,))
            logs = cursor.fetchall()
            conn.close()
            
            data_points = []
            for log in logs:
                try:
                    data = json.loads(log[0])
                    if field in data and data[field] is not None:
                        data_points.append({
                            "timestamp": log[0],
                            "value": float(data[field])
                        })
                except:
                    continue
            
            return data_points
        except Exception as e:
            print(f"Error getting flight data for graph: {e}")
            return []

    @pyqtSlot(result='QVariant')
    def get_current_flight_statistics(self):
        if self.current_flight_id:
            return self.get_flight_statistics(self.current_flight_id)
        return {}

    @pyqtSlot(str, result='QVariant')
    def get_current_flight_data_for_graph(self, field):
        if self.current_flight_id:
            return self.get_flight_data_for_graph(self.current_flight_id, field)
        return []

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Ultra havalı Splash Screen
    splash_pix = QPixmap(800, 480)
    # splash_pix.fill(Qt.transparent)
    splash_pix.fill(QColor(10, 10, 20))  # Daha koyu bir arka plan
    painter = QPainter(splash_pix)
    painter.setRenderHint(QPainter.Antialiasing)

    # Sade splash: sadece logo ve başlık
    logo = QPixmap("assets/images/LOGO.PNG")
    painter.drawPixmap(210, 40, 280, 280, logo)
    font = QFont("Arial", 38, QFont.Bold)
    painter.setFont(font)
    painter.setPen(QColor("#fff"))
    painter.drawText(0, 350, 800, 60, Qt.AlignHCenter, "Humbaba Yer İstasyonu")

    splash = QSplashScreen(splash_pix)
    splash.show()
    app.processEvents()
    import time as _time
    _time.sleep(2)

    engine = QQmlApplicationEngine()
    telemetry_bridge = TelemetryBridge()
    packet_sender = PacketSender()
    speech_helper = SpeechHelper()
    log_manager = LogManager()
    telemetry_bridge.log_manager = log_manager
    engine.rootContext().setContextProperty("telemetryBridge", telemetry_bridge)
    engine.rootContext().setContextProperty("packetSender", packet_sender)
    engine.rootContext().setContextProperty("speechHelper", speech_helper)
    engine.rootContext().setContextProperty("logManager", log_manager)
    engine.load(QUrl("src/ui/Main.qml"))
    splash.finish(None)
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())