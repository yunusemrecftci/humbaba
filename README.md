# Humbaba Yer İstasyonu

> ⚠️ **Geliştirme Aşamasında** ⚠️
> 
> Bu proje aktif geliştirme aşamasındadır ve bazı hatalar içerebilir. Üretim ortamında kullanmadan önce kapsamlı test yapılması önerilir.

Humbaba Yer İstasyonu, roket telemetri verilerini gerçek zamanlı olarak izlemek ve hakem yer istasyonuna HYİ protokolüne uygun veri göndermek için geliştirilmiş bir Python/QML uygulamasıdır. Bu proje, **genel kullanım** için tasarlanmış olup, çeşitli roket sistemlerine entegre edilebilir.

## 🚀 Özellikler

- **Gerçek Zamanlı Telemetri**: Roket verilerini canlı olarak izleme
- **Hakem Yer İstasyonu Entegrasyonu**: HYİ protokolüne uygun veri gönderimi
- **Çoklu Tema Desteği**: Dark, Light, Milenyum, Roma, Cyberpunk temaları
- **Sesli Uyarılar**: İrtifa ve durum değişikliklerinde sesli bildirimler
- **Uçuş Kayıtları**: Telemetri verilerini veritabanında saklama
- **Harita Görünümü**: Roket konumunu harita üzerinde takip etme
- **Fake Telemetri**: Test için simüle edilmiş veri üretimi
- **Modüler Yapı**: Kolay entegrasyon ve genişletilebilirlik
- **Cross-Platform**: Windows, macOS ve Linux desteği

## 🎯 Kullanım Alanları

### Roket Yarışmaları
- TEKNOFEST Roket Yarışması
- TÜBİTAK Roket Yarışması
- Uluslararası roket yarışmaları
- Eğitim kurumları roket projeleri

### Araştırma ve Geliştirme
- Roket performans analizi
- Telemetri veri toplama
- Sistem entegrasyonu testleri
- Prototip geliştirme

### Eğitim
- Roket teknolojileri eğitimi
- Telemetri sistemleri öğretimi
- Yazılım geliştirme projeleri

## 📁 Proje Yapısı

```
yerist/
├── src/
│   ├── main.py              # Ana uygulama dosyası
│   ├── ui/
│   │   └── Main.qml         # QML arayüz dosyası
│   └── modules/
│       ├── __init__.py
│       ├── judge_packet.py  # Hakem paket işlemleri
│       └── serial_reader.py # Seri port okuma
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
├── main.spec
└── README.md
```

## 🛠️ Kurulum

### Gereksinimler

- Python 3.8+
- PyQt5
- pyserial
- sqlite3

### Adımlar

1. **Repository'yi klonlayın:**
   ```bash
   git clone https://github.com/kullaniciadi/yerist.git
   cd yerist
   ```

2. **Sanal ortam oluşturun:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # veya
   .venv\Scripts\activate     # Windows
   ```

3. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Uygulamayı çalıştırın:**
   ```bash
   python src/main.py
   ```

## 📖 Kullanım

### Ana Ekran
- **Telemetri Sekmesi**: Canlı roket verilerini görüntüleme
- **Hakem Portu Sekmesi**: Hakem yer istasyonuna bağlantı ayarları
- **Geçmiş Sekmesi**: Önceki uçuş kayıtları ve istatistikler

### Hakem Yer İstasyonu Bağlantısı
1. "Hakem Portu" sekmesine gidin
2. Port listesinden uygun portu seçin
3. Baudrate'i ayarlayın (genellikle 9600, 19200, 115200)
4. "Bağlan" butonuna basın
5. Bağlantı durumunu kontrol edin

### HYİ Protokolü
Uygulama, hakem yer istasyonuna HYİ protokolüne uygun 78 byte'lık paketler gönderir:
- Header: 0xFF, 0xFF, 0x54, 0x52
- Takım ID ve paket sayacı
- 16 adet float değer (irtifa, GPS, sensör verileri)
- Durum byte'ı
- Checksum
- Kuyruk: 0x0D, 0x0A

## 🔧 Konfigürasyon

### Takım ID
Arayüzde "Takım ID" alanından takım numaranızı ayarlayabilirsiniz.

### Port Ayarları
- **Port**: Seri port seçimi
- **Baudrate**: 9600, 19200, 38400, 57600, 115200
- **Fake Telemetri**: Test için simüle edilmiş veri

## 📊 Veritabanı

Telemetri verileri `flight_logs.db` SQLite veritabanında saklanır:
- `flights`: Uçuş kayıtları
- `telemetry_logs`: Telemetri verileri

## 🎨 Temalar

- **Dark**: Koyu tema (varsayılan)
- **Light**: Açık tema
- **Milenyum**: Starwars tema
- **Roma**: Roma tema
- **Cyberpunk**: Cyberpunk teması

## 🔌 Sistem Entegrasyonu

### Roket Sistemlerine Entegrasyon
Bu uygulama, çeşitli roket sistemleriyle entegre edilebilir:

1. **Seri Port Üzerinden Veri Alma**
   - Arduino tabanlı telemetri sistemleri
   - Raspberry Pi telemetri modülleri
   - Özel telemetri kartları

2. **Veri Formatı Uyumluluğu**
   - JSON formatında telemetri verisi
   - Standart sensör verileri (irtifa, GPS, ivme, jiroskop)
   - Özel veri alanları eklenebilir

3. **Protokol Desteği**
   - HYİ protokolü (hakem yer istasyonu)
   - Özel protokoller için genişletilebilir
   - UDP/TCP üzerinden veri alma

### Entegrasyon Örnekleri
```python
# Arduino telemetri sistemi entegrasyonu
# Arduino'dan gelen veri formatı:
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


## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👨‍💻 Geliştirici

**Yunus Emre Çiftçi**
- Proje: Humbaba Yer İstasyonu
- Teknoloji: Python, PyQt5, QML, SQLite
- Amaç: Roket teknolojileri ve telemetri sistemleri

## 📞 İletişim

Sorularınız için issue açabilir veya pull request gönderebilirsiniz.

## 📚 Referanslar


- [PyQt5 Dokümantasyonu](https://doc.qt.io/qtforpython/)
- [QML Dokümantasyonu](https://doc.qt.io/qt-6/qmlapplications.html)

---

**Not**: Bu uygulama roket yarışmaları ve genel kullanım için geliştirilmiştir. HYİ protokolüne uygun veri gönderimi yapar ve çeşitli roket sistemlerine entegre edilebilir. Geliştirme aşamasında olduğu için üretim ortamında kullanmadan önce kapsamlı test yapılması önerilir.


