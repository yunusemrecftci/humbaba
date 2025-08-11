"""
Veritabanı Yönetimi Modülü
SQLite veritabanı işlemleri ve uçuş logları
"""

import sqlite3
import json
import datetime
from typing import List, Dict, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal


class DatabaseManager(QObject):
    """Veritabanı yönetimi sınıfı"""
    
    # Sinyaller
    log_updated = pyqtSignal()
    flight_list_updated = pyqtSignal()
    
    def __init__(self, db_path: str = "flight_logs.db"):
        super().__init__()
        self.db_path = db_path
        self.current_flight_id: Optional[int] = None
        self.init_database()
    
    def init_database(self):
        """Veritabanını başlatır ve tabloları oluşturur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Uçuşlar tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Telemetri logları tablosu
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
            print(f"Veritabanı başlatma hatası: {e}")
    
    def start_flight(self, flight_name: str) -> int:
        """Yeni bir uçuş başlatır"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO flights (name, start_time) VALUES (?, ?)",
                (flight_name, datetime.datetime.now())
            )
            
            flight_id = cursor.lastrowid
            self.current_flight_id = flight_id
            
            conn.commit()
            conn.close()
            
            self.flight_list_updated.emit()
            return flight_id
            
        except Exception as e:
            print(f"Uçuş başlatma hatası: {e}")
            return -1
    
    def end_flight(self, flight_id: int) -> bool:
        """Uçuşu sonlandırır"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE flights SET end_time = ?, status = 'completed' WHERE id = ?",
                (datetime.datetime.now(), flight_id)
            )
            
            if flight_id == self.current_flight_id:
                self.current_flight_id = None
            
            conn.commit()
            conn.close()
            
            self.flight_list_updated.emit()
            return True
            
        except Exception as e:
            print(f"Uçuş sonlandırma hatası: {e}")
            return False
    
    def get_flight_list(self) -> List[Dict[str, Any]]:
        """Tüm uçuşları listeler"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, start_time, end_time, status
                FROM flights
                ORDER BY start_time DESC
            ''')
            
            flights = []
            for row in cursor.fetchall():
                flights.append({
                    'id': row[0],
                    'name': row[1],
                    'start_time': row[2],
                    'end_time': row[3],
                    'status': row[4]
                })
            
            conn.close()
            return flights
            
        except Exception as e:
            print(f"Uçuş listesi alma hatası: {e}")
            return []
    
    def log_telemetry(self, data: Dict[str, Any]) -> bool:
        """Telemetri verisini loglar"""
        if not self.current_flight_id:
            return False
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO telemetry_logs (flight_id, data) VALUES (?, ?)",
                (self.current_flight_id, json.dumps(data))
            )
            
            conn.commit()
            conn.close()
            
            self.log_updated.emit()
            return True
            
        except Exception as e:
            print(f"Telemetri loglama hatası: {e}")
            return False
    
    def get_logs_for_flight(self, flight_id: int) -> List[Dict[str, Any]]:
        """Belirli bir uçuşun loglarını getirir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT timestamp, data FROM telemetry_logs WHERE flight_id = ? ORDER BY timestamp",
                (flight_id,)
            )
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'timestamp': row[0],
                    'data': json.loads(row[1])
                })
            
            conn.close()
            return logs
            
        except Exception as e:
            print(f"Log alma hatası: {e}")
            return []
    
    def get_flight_statistics(self, flight_id: int) -> Dict[str, Any]:
        """Uçuş istatistiklerini hesaplar"""
        logs = self.get_logs_for_flight(flight_id)
        
        if not logs:
            return {}
        
        # İstatistikleri hesapla
        altitudes = [log['data'].get('irtifa', 0) for log in logs]
        speeds = [log['data'].get('hiz', 0) for log in logs]
        
        return {
            'total_logs': len(logs),
            'max_altitude': max(altitudes) if altitudes else 0,
            'min_altitude': min(altitudes) if altitudes else 0,
            'avg_altitude': sum(altitudes) / len(altitudes) if altitudes else 0,
            'max_speed': max(speeds) if speeds else 0,
            'avg_speed': sum(speeds) / len(speeds) if speeds else 0,
            'duration': len(logs)  # Basit süre hesaplama
        }
    
    def get_current_flight_statistics(self) -> Dict[str, Any]:
        """Mevcut uçuşun istatistiklerini getirir"""
        if self.current_flight_id:
            return self.get_flight_statistics(self.current_flight_id)
        return {}
    
    def get_flight_data_for_graph(self, flight_id: int, field: str) -> List[Dict[str, Any]]:
        """Grafik için uçuş verilerini getirir"""
        logs = self.get_logs_for_flight(flight_id)
        
        graph_data = []
        for i, log in enumerate(logs):
            value = log['data'].get(field, 0)
            graph_data.append({
                'x': i,
                'y': value,
                'timestamp': log['timestamp']
            })
        
        return graph_data
    
    def get_current_flight_data_for_graph(self, field: str) -> List[Dict[str, Any]]:
        """Mevcut uçuşun grafik verilerini getirir"""
        if self.current_flight_id:
            return self.get_flight_data_for_graph(self.current_flight_id, field)
        return []
