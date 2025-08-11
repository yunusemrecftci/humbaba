"""
UI Bridge Modülü
QML ile Python arasındaki köprü sınıfları
"""

import json
import random
import time
import threading
from typing import Dict, Any
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QVariant
from PyQt5.QtTextToSpeech import QTextToSpeech
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

from .serial_manager import SerialManager
from .database_manager import DatabaseManager
from .protocol import HYIProtocol


class TelemetryBridge(QObject):
    """Telemetri verilerini QML'e bağlayan köprü sınıfı"""
    
    # Sinyaller
    telemetry_updated = pyqtSignal('QVariant')
    packet_sent = pyqtSignal(str, str)
    port_list_changed = pyqtSignal(list)
    connection_status_changed = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.serial_manager = SerialManager()
        self.database_manager = DatabaseManager()
        self.packet_counter = 0
        self.fake_telemetry_running = False
        
        # Sinyal bağlantıları
        self.serial_manager.data_received.connect(self._on_data_received)
        self.serial_manager.connection_status_changed.connect(self.connection_status_changed.emit)
        self.serial_manager.port_list_changed.connect(self.port_list_changed.emit)
        
        # Veri işleme callback'i
        self.serial_manager.set_data_callback(self._process_telemetry_data)
    
    @pyqtSlot(result=list)
    def get_ports(self):
        """Kullanılabilir portları döndürür"""
        return self.serial_manager.get_available_ports()
    
    @pyqtSlot(str, int, int)
    def connect_port(self, port_name: str, team_id: int, baudrate: int):
        """Seri porta bağlanır"""
        success = self.serial_manager.connect_to_port(port_name, baudrate, team_id)
        if success:
            # Uçuş başlat
            flight_name = f"Uçuş_{int(time.time())}"
            self.database_manager.start_flight(flight_name)
    
    @pyqtSlot()
    def disconnect_port(self):
        """Seri port bağlantısını keser"""
        # Fake telemetriyi durdur
        self.fake_telemetry_running = False
        
        self.serial_manager.disconnect_from_port()
        # Mevcut uçuşu sonlandır
        if self.database_manager.current_flight_id:
            self.database_manager.end_flight(self.database_manager.current_flight_id)
    
    def _on_data_received(self, data: str):
        """Seri porttan veri alındığında çağrılır"""
        try:
            # JSON verisini parse et
            telemetry_data = json.loads(data)
            self._process_telemetry_data(telemetry_data)
        except json.JSONDecodeError:
            print(f"JSON parse hatası: {data}")
    
    def _process_telemetry_data(self, data: Dict[str, Any]):
        """Telemetri verisini işler"""
        # Veritabanına logla
        self.database_manager.log_telemetry(data)
        
        # QML'e gönder
        self.telemetry_updated.emit(QVariant(data))
        
        # Hakem yer istasyonuna gönder
        self._send_to_judge(data)
    
    def _send_to_judge(self, data: Dict[str, Any]):
        """Hakem yer istasyonuna veri gönderir"""
        if not self.serial_manager.is_connected():
            return
        
        try:
            # Veriyi HYI protokolü formatına çevir
            parsed_data = HYIProtocol.parse_telemetry_data(data)
            
            # HYI paketi oluştur
            packet = HYIProtocol.create_hyi_packet(
                team_id=self.serial_manager.team_id,
                packet_counter=self.packet_counter,
                **parsed_data
            )
            
            # Paketi gönder
            if self.serial_manager.send_data(packet):
                self.packet_counter += 1
                self.packet_sent.emit("HYI", f"Paket {self.packet_counter} gönderildi")
            
        except Exception as e:
            print(f"Hakem veri gönderme hatası: {e}")
    
    @pyqtSlot()
    def start_fake_telemetry(self):
        """Sahte telemetri verisi üretir (test için)"""
        # Fake telemetri için özel bir durum oluştur
        self.fake_telemetry_running = True
        
        # Fake telemetri için uçuş başlat
        flight_name = f"Fake_Uçuş_{int(time.time())}"
        self.database_manager.start_flight(flight_name)
        
        # Bağlantı durumunu güncelle
        self.connection_status_changed.emit(True, "Fake telemetri başlatıldı")
        
        def fake_loop():
            while self.fake_telemetry_running:
                fake_data = {
                    'irtifa': random.uniform(1000, 2000),
                    'gps_irtifa': random.uniform(995, 2005),
                    'enlem': 39.9254 + random.uniform(-0.001, 0.001),
                    'boylam': 32.8667 + random.uniform(-0.001, 0.001),
                    'ivme_x': random.uniform(-1, 1),
                    'ivme_y': random.uniform(-1, 1),
                    'ivme_z': random.uniform(9.5, 10.5),
                    'jiroskop_x': random.uniform(-5, 5),
                    'jiroskop_y': random.uniform(-5, 5),
                    'jiroskop_z': random.uniform(-5, 5),
                    'aci': random.uniform(0, 90),
                    'durum': random.randint(0, 3)
                }
                
                self._process_telemetry_data(fake_data)
                time.sleep(1)
        
        threading.Thread(target=fake_loop, daemon=True).start()


class SpeechHelper(QObject):
    """Sesli okuma yardımcı sınıfı"""
    
    def __init__(self):
        super().__init__()
        self.speech = QTextToSpeech()
        self.muted = False
    
    @pyqtSlot(str)
    def speak(self, text: str):
        """Metni sesli okur"""
        if not self.muted:
            self.speech.say(text)
    
    @pyqtSlot(bool)
    def set_muted(self, muted: bool):
        """Sesli okumayı açıp kapatır"""
        self.muted = muted
    
    @pyqtSlot()
    def stop_speaking(self):
        """Sesli okumayı durdurur"""
        self.speech.stop()


class LogManager(QObject):
    """Log yönetimi köprü sınıfı"""
    
    # Sinyaller
    log_updated = pyqtSignal()
    flight_list_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.database_manager = DatabaseManager()
        
        # Sinyal bağlantıları
        self.database_manager.log_updated.connect(self.log_updated.emit)
        self.database_manager.flight_list_updated.connect(self.flight_list_updated.emit)
    
    @property
    def current_flight_id(self):
        """Mevcut uçuş ID'sini döndürür"""
        return self.database_manager.current_flight_id
    
    @pyqtSlot(str)
    def start_flight(self, flight_name: str):
        """Yeni uçuş başlatır"""
        self.database_manager.start_flight(flight_name)
    
    @pyqtSlot(int)
    def end_flight(self, flight_id: int):
        """Uçuşu sonlandırır"""
        self.database_manager.end_flight(flight_id)
    
    @pyqtSlot(result='QVariant')
    def get_flight_list(self):
        """Uçuş listesini döndürür"""
        return QVariant(self.database_manager.get_flight_list())
    
    @pyqtSlot(int, result='QVariant')
    def get_logs_for_flight(self, flight_id: int):
        """Uçuş loglarını döndürür"""
        return QVariant(self.database_manager.get_logs_for_flight(flight_id))
    
    @pyqtSlot(int, result='QVariant')
    def get_flight_statistics(self, flight_id: int):
        """Uçuş istatistiklerini döndürür"""
        return QVariant(self.database_manager.get_flight_statistics(flight_id))
    
    @pyqtSlot(result='QVariant')
    def get_current_flight_statistics(self):
        """Mevcut uçuş istatistiklerini döndürür"""
        return QVariant(self.database_manager.get_current_flight_statistics())
    
    @pyqtSlot(int, result='QVariant')
    def get_flight_data_for_graph(self, flight_id: int, field: str):
        """Grafik verilerini döndürür"""
        return QVariant(self.database_manager.get_flight_data_for_graph(flight_id, field))
    
    @pyqtSlot(str, result='QVariant')
    def get_current_flight_data_for_graph(self, field: str):
        """Mevcut uçuş grafik verilerini döndürür"""
        return QVariant(self.database_manager.get_current_flight_data_for_graph(field))
