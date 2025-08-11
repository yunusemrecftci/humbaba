from PyQt5.QtCore import QObject, pyqtSignal, QThread
import serial
import json

class SerialReaderThread(QThread):
    dataReceived = pyqtSignal(dict)
    def __init__(self, port, baudrate=115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True

    def run(self):
        ser = serial.Serial(self.port, self.baudrate)
        while self.running:
            line = ser.readline().decode(errors='ignore').strip()
            if not line:
                continue
            if '{' in line:
                json_str = line[line.find('{'):]
                try:
                    data = json.loads(json_str)
                    self.dataReceived.emit(data)
                except json.JSONDecodeError:
                    continue

    def stop(self):
        self.running = False

# Örnek kullanım:
# from modules.serial_reader import SerialReaderThread
# serial_thread = SerialReaderThread('/dev/ttyACM0', 115200)
# serial_thread.dataReceived.connect(lambda data: print(data))
# serial_thread.start() 