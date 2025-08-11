"""
Humbaba Yer İstasyonu - Ana Uygulama
Roket telemetri sistemi ve hakem yer istasyonu entegrasyonu
"""

import sys
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtCore import Qt

# Modülleri import et
from modules.ui_bridge import TelemetryBridge, SpeechHelper, LogManager


def create_splash_screen():
    """Splash screen oluşturur"""
    try:
        logo = QPixmap("assets/images/LOGO.PNG")
        splash = QSplashScreen(logo)
        splash.showMessage("Humbaba Yer İstasyonu", Qt.AlignCenter, Qt.white)
        return splash
    except Exception as e:
        print(f"Splash screen oluşturma hatası: {e}")
        return None


def main():
    """Ana uygulama fonksiyonu"""
    app = QApplication(sys.argv)
    
    # Splash screen göster
    splash = create_splash_screen()
    if splash:
        splash.show()
        app.processEvents()
    
    # QML engine oluştur
    engine = QQmlApplicationEngine()
    
    # Modül nesnelerini oluştur
    telemetry_bridge = TelemetryBridge()
    speech_helper = SpeechHelper()
    log_manager = LogManager()
    
    # QML context'e nesneleri ekle
    context = engine.rootContext()
    context.setContextProperty("telemetryBridge", telemetry_bridge)
    context.setContextProperty("speechHelper", speech_helper)
    context.setContextProperty("logManager", log_manager)
    
    # QML dosyasını yükle
    qml_file = "src/ui/Main.qml"
    if not os.path.exists(qml_file):
        print(f"QML dosyası bulunamadı: {qml_file}")
        return -1
    
    engine.load(QUrl.fromLocalFile(qml_file))
    
    # QML yüklenemediyse hata ver
    if not engine.rootObjects():
        print("QML yüklenemedi!")
        return -1
    
    # Splash screen'i kapat
    if splash:
        splash.finish(None)
    
    # Uygulamayı başlat
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())