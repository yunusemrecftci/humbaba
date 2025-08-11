"""
Seri Okuyucu Modülü (Eski versiyon - Geriye uyumluluk için)
Yeni serial_manager modülü kullanılması önerilir
"""

from .serial_manager import SerialManager


class SerialReader(SerialManager):
    """
    Eski SerialReader sınıfı için uyumluluk wrapper'ı
    Yeni SerialManager kullanılması önerilir
    """
    
    def __init__(self):
        super().__init__()
    
    # Eski metodlar için alias'lar
    def read_serial(self):
        """Eski metod - artık _read_serial kullanılıyor"""
        return self._read_serial()
    
    def get_ports(self):
        """Eski metod - artık get_available_ports kullanılıyor"""
        return self.get_available_ports()
    
    def connect_port(self, port_name, baudrate=9600):
        """Eski metod - artık connect_to_port kullanılıyor"""
        return self.connect_to_port(port_name, baudrate)
    
    def disconnect_port(self):
        """Eski metod - artık disconnect_from_port kullanılıyor"""
        return self.disconnect_from_port() 