"""
Seri Port Yönetimi Modülü
Seri port bağlantısı ve veri okuma/yazma işlemleri
"""

import serial
import serial.tools.list_ports
import threading
import time
from typing import List, Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal


class SerialManager(QObject):
    """Seri port yönetimi sınıfı"""
    
    # Sinyaller
    data_received = pyqtSignal(str)
    connection_status_changed = pyqtSignal(bool, str)
    port_list_changed = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.serial_port: Optional[serial.Serial] = None
        self.running = False
        self.team_id = 1
        self.packet_counter = 0
        self.data_callback: Optional[Callable] = None
        
    def get_available_ports(self) -> List[str]:
        """Kullanılabilir seri portları listeler"""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        return ports
    
    def connect_to_port(self, port_name: str, baudrate: int = 9600, 
                       team_id: int = 1) -> bool:
        """Seri porta bağlanır"""
        try:
            self.serial_port = serial.Serial(port_name, baudrate, timeout=1)
            self.team_id = team_id
            self.running = True
            
            # Okuma thread'ini başlat
            threading.Thread(target=self._read_serial, daemon=True).start()
            
            self.connection_status_changed.emit(
                True, f"{port_name} portuna bağlandı ({baudrate} baud)"
            )
            return True
            
        except Exception as e:
            self.connection_status_changed.emit(False, f"Bağlantı hatası: {e}")
            return False
    
    def disconnect_from_port(self):
        """Seri port bağlantısını keser"""
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.connection_status_changed.emit(False, "Bağlantı kesildi")
    
    def send_data(self, data: bytes) -> bool:
        """Seri porta veri gönderir"""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(data)
                return True
            except Exception as e:
                print(f"Veri gönderme hatası: {e}")
                return False
        return False
    
    def _read_serial(self):
        """Seri porttan veri okuma thread'i"""
        while self.running:
            try:
                if not self.serial_port or not self.serial_port.is_open:
                    print("Seri port kapalı, okuma thread'i sonlandırılıyor.")
                    break
                    
                line = self.serial_port.readline().decode(errors="ignore").strip()
                if line:
                    self.data_received.emit(line)
                    
                    # Callback varsa çağır
                    if self.data_callback:
                        self.data_callback(line)
                        
            except Exception as e:
                print(f"Seri okuma hatası: {e}")
                break
    
    def set_data_callback(self, callback: Callable):
        """Veri alındığında çağrılacak callback fonksiyonunu ayarlar"""
        self.data_callback = callback
    
    def is_connected(self) -> bool:
        """Bağlantı durumunu kontrol eder"""
        return self.serial_port is not None and self.serial_port.is_open
    
    def get_connection_info(self) -> dict:
        """Bağlantı bilgilerini döndürür"""
        if self.is_connected():
            return {
                'port': self.serial_port.port,
                'baudrate': self.serial_port.baudrate,
                'team_id': self.team_id,
                'connected': True
            }
        return {'connected': False}
