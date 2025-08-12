# Humbaba Ground Station

> ⚠️ **Under Development** ⚠️
> 
> This project is in active development and may contain some bugs. Comprehensive testing is recommended before using in production environments.

Humbaba Ground Station is a Python/QML application developed for real-time rocket telemetry monitoring and sending data to judge ground stations in compliance with HYI protocol. This project is designed for **general use** and can be integrated with various rocket systems.

## 🚀 Features

- **Real-Time Telemetry**: Live rocket data monitoring
- **Judge Ground Station Integration**: HYI protocol compliant data transmission
- **Multi-Theme Support**: Dark, Light, Millennium, Rome, Cyberpunk themes
- **Voice Alerts**: Audio notifications for altitude and status changes
- **Flight Records**: Store telemetry data in database
- **Map View**: Track rocket position on map
- **Fake Telemetry**: Simulated data generation for testing
- **Modular Structure**: Easy integration and extensibility
- **Voice Reading**: Voice alerts with Turkish language support
- **Cross-Platform**: Windows, macOS and Linux support

## 🎯 Use Cases

### Rocket Competitions
- TEKNOFEST Rocket Competition

### Research and Development
- Rocket performance analysis
- Telemetry data collection
- System integration tests
- Prototype development

### Education
- Rocket technology education
- Telemetry systems teaching
- Software development projects

## 📁 Project Structure

```
yerist/
├── src/
│   ├── main.py                 # Main application file
│   ├── ui/
│   │   └── Main.qml            # QML interface file
│   └── modules/
│       ├── __init__.py         # Module package
│       ├── protocol.py         # HYI protocol operations
│       ├── serial_manager.py   # Serial port management
│       ├── database_manager.py # Database operations
│       ├── ui_bridge.py        # QML-Python bridge classes
│       ├── judge_packet.py     # Judge packet operations (backward compatibility)
│       └── serial_reader.py    # Serial port reading (backward compatibility)
├── assets/
│   ├── images/
│   │   ├── LOGO.PNG
│   │   └── ab.png
│   ├── audio/
│   │   ├── a.mp3
│   │   ├── b.mp3
│   │   ├── c.mp3
│   │   ├── d.mp3
│   │   └── f.mp3
│   └── video/
│       ├── bekir.mp4
│       └── p.mp4
├── docs/
│   └── EK-7_Hakem_Yer_İstasyonu_y52A5 (8).docx
├── requirements.txt
├── .gitignore
└── README.md
```

## 🛠️ Installation

### Requirements

- Python 3.8+
- PyQt5 >= 5.15.0
- pyserial >= 3.5
- sqlite3 (comes with Python)

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/username/yerist.git
   cd yerist
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python src/main.py
   ```

## 📖 Usage

### Main Screen
- **Telemetry Tab**: Display live rocket data
- **Judge Port Tab**: Judge ground station connection settings
- **History Tab**: Previous flight records and statistics

### Judge Ground Station Connection
1. Go to "Judge Port" tab
2. Select appropriate port from port list
3. Set baudrate (usually 9600, 19200, 115200)
4. Click "Connect" button
5. Check connection status

### HYI Protocol
The application sends 78-byte packets to judge ground stations in compliance with HYI protocol:
- Header: 0xFF, 0xFF, 0x54, 0x52
- Team ID and packet counter
- 16 float values (altitude, GPS, sensor data)
- Status byte
- Checksum
- Tail: 0x0D, 0x0A

## 🔧 Configuration

### Team ID
You can set your team number from the "Team ID" field in the interface.

### Port Settings
- **Port**: Serial port selection
- **Baudrate**: 9600, 19200, 38400, 57600, 115200
- **Fake Telemetry**: Simulated data for testing

### Voice Reading Settings
- **Language**: Turkish (tr_TR) is set as default
- **Volume**: Full volume (1.0)
- **Speed**: Normal speed (0.0)
- **Pitch**: Normal pitch (0.0)
- **Silent Mode**: Can be turned on/off with button

## 📊 Database

Telemetry data is stored in `flight_logs.db` SQLite database:
- `flights`: Flight records
- `telemetry_logs`: Telemetry data

## 🎨 Themes

- **Dark**: Dark theme (default)
- **Light**: Light theme
- **Millennium**: Starwars theme
- **Rome**: Rome theme
- **Cyberpunk**: Cyberpunk theme

## 🔌 System Integration

### Integration with Rocket Systems
This application can be integrated with various rocket systems:

1. **Data Reception via Serial Port**
   - Arduino-based telemetry systems
   - Raspberry Pi telemetry modules
   - Custom telemetry cards

2. **Data Format Compatibility**
   - Telemetry data in JSON format
   - Standard sensor data (altitude, GPS, accelerometer, gyroscope)
   - Custom data fields can be added

3. **Protocol Support**
   - HYI protocol (judge ground station)
   - Extensible for custom protocols
   - Data reception via UDP/TCP

### Modular Structure
The application has a modular structure:

- **`protocol.py`**: HYI protocol operations
- **`serial_manager.py`**: Serial port management
- **`database_manager.py`**: Database operations
- **`ui_bridge.py`**: QML-Python bridge classes

### Integration Examples
```python
# Arduino telemetry system integration
# Data format from Arduino:
{
    "irtifa": 1500.5,
    "gps_irtifa": 1498.2,
    "enlem": 39.9254,
    "boylam": 32.8667,
    "ivme_x": 0.1,
    "ivme_y": -0.2,
    "ivme_z": 9.8,
    "jiroskop_x": 0.5,
    "jiroskop_y": -0.3,
    "jiroskop_z": 0.1,
    "aci": 45.0,
    "durum": 1
}
```

## 🐛 Known Bugs and Issues

### Current Bugs
- **File Path Issues**: Wrong paths for some asset files
- **QML Layout Warnings**: Warnings in layout and anchors usage
- **Signal Connection Warnings**: Warnings in some QML signal connections

### Future Fixes
- [ ] Fix file path issues
- [ ] Resolve QML layout warnings
- [ ] Fix signal connection warnings
- [ ] Improve error handling mechanisms

## 🐛 Troubleshooting

### Connection Issues
1. Make sure port list is populated
2. Check if you selected the correct port
3. Verify baudrate settings
4. Ensure port is not used by another application

### Voice Reading Issues
1. Check system audio settings
2. Make sure Turkish language support is installed
3. Check if silent mode is turned off

### General Issues
- If you get an error when starting the application, check terminal output
- Check write permissions for database file
- Make sure Python version is compatible

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Developer

**Yunus Emre Çiftçi**
- Project: Humbaba Ground Station
- Technology: Python, PyQt5, QML, SQLite
- Purpose: Rocket technologies and telemetry systems

## 📞 Contact

You can open an issue or send a pull request for your questions.

## 📚 References

- [HYI Protocol Documentation](docs/EK-7_Hakem_Yer_İstasyonu_y52A5%20(8).docx)
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [QML Documentation](https://doc.qt.io/qt-6/qmlapplications.html)

---

**Note**: This application is developed for rocket competitions and general use. It sends data in compliance with HYI protocol and can be integrated with various rocket systems. Since it's in development stage, comprehensive testing is recommended before using in production environments.

---

## 🌍 Language

- 🇺🇸 [English](README.md) (Current)
- 🇹🇷 [Türkçe](README_TR.md)
