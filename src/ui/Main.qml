import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import QtMultimedia 5.15

ApplicationWindow {
    id: window
    visible: true
    width: 1200
    height: 800
    title: "Humbaba Yer İstasyonu"
    
    Component.onCompleted: {
        speechHelper.speak("Ben Humbaba")
    }

    Component {
        id: logoImage
        Image {
            source: "../assets/images/LOGO.PNG"
            fillMode: Image.PreserveAspectFit
            width: 48
            height: 48
        }
    }

    // Theme support
    property string theme: "dark"
    property color mainBg: {
        if (theme === "light") return "#f5f6fa"
        else if (theme === "milenyum") return "#24262b"
        else if (theme === "roma") return "#2d1b69"
        else if (theme === "cyberpunk") return "#24262b"
        else return "#24262b" // çok koyu gri
    }
    property color cardBg: {
        if (theme === "light") return "#ffffff"
        else if (theme === "milenyum") return "#292b31"
        else if (theme === "roma") return "#4a148c"
        else if (theme === "cyberpunk") return "#292b31"
        else return "#292b31" // koyu gri
    }
    property color accent: {
        if (theme === "light") return "#4fc3f7"
        else if (theme === "milenyum") return "#90caf9"
        else if (theme === "roma") return "#ffd700"
        else if (theme === "cyberpunk") return "#4fc3f7"
        else return "#4fc3f7" // pastel mavi
    }
    property color accent2: {
        if (theme === "cyberpunk") return "#b0bec5"
        else if (theme === "roma") return "#b388ff"
        else return accent
    }
    property color textMain: {
        if (theme === "light") return "#24262b"
        else if (theme === "milenyum") return "#f5f5f5"
        else if (theme === "roma") return "#fff3e0"
        else if (theme === "cyberpunk") return "#e0e0e0"
        else return "#e0e0e0" // çok açık gri
    }
    property color portBg: {
        if (theme === "light") return "#b0bec5"
        else if (theme === "milenyum") return "#b0bec5"
        else if (theme === "roma") return "#b0bec5"
        else if (theme === "cyberpunk") return "#b0bec5"
        else return "#b0bec5"
    }
    property color portText: {
        if (theme === "light") return "#24262b"
        else if (theme === "milenyum") return "#f5f5f5"
        else if (theme === "roma") return "#f5f5f5"
        else if (theme === "cyberpunk") return "#f5f5f5"
        else return "#f5f5f5"
    }
    property color successColor: "#81c784"
    property color errorColor: "#e57373"
    property color warningColor: "#ffd54f"
    
    // Global properties
    property string selectedPort: ""
    property var flightList: []
    property int teamId: 1
    property int baudrate: 9600
    property string connectionStatus: "Bağlı değil"
    property var telemetryData: ({})
    property var selectedFlightStats: ({})
    property int currentTab: 0
    property var packetStats: ({total: 0, success: 0, failed: 0, successRate: 0})
    property int lastAltitudeAnnouncement: 0
    property string lastFlightName: ""
    property string lastFlightTime: ""
    property var statusMessages: []
    property bool bekirVisible: false
    property bool isMuted: false // Ses kapalı mı?
    property bool splashVisible: true

    MediaPlayer {
        id: audioPlayer
    }

    // Theme audio players
    MediaPlayer {
        id: milenyumAudio
        source: "assets/audio/b.mp3"
        loops: MediaPlayer.Infinite
    }

    MediaPlayer {
        id: romaAudio
        source: "assets/audio/c.mp3"
        loops: MediaPlayer.Infinite
    }

    MediaPlayer {
        id: rapidClickAudio
        source: "assets/audio/a.mp3"
    }
    MediaPlayer {
        id: sonUcushAudio
        source: "assets/audio/d.mp3"
    }
    MediaPlayer {
        id: roketAudio
        source: "assets/audio/f.mp3"
    }

    // Theme switching function
    function switchTheme(newTheme) {
        // Stop all theme audio
        milenyumAudio.stop()
        romaAudio.stop()
        
        // Set new theme
        theme = newTheme
        
        // Start theme-specific audio
        if (theme === "milenyum") {
            milenyumAudio.play()
        } else if (theme === "roma") {
            romaAudio.play()
        }
        // Tema değişikliğini durum mesajı olarak ekle
        var themeNames = {"dark": "Dark", "light": "Light", "milenyum": "Milenyum", "roma": "Roma"};
        addStatusMessage("Tema değiştirildi: " + (themeNames[newTheme] || newTheme), "info");
    }

    // Arka plan için degrade ve blur efekti
    Rectangle {
        anchors.fill: parent
        z: -1
        gradient: Gradient {
            GradientStop { position: 0.0; color: theme === "light" ? "#f5f6fa" : "#24262b" }
            GradientStop { position: 1.0; color: theme === "light" ? "#dbe6e4" : "#292b31" }
        }
        // Hafif blur efekti
        FastBlur {
            anchors.fill: parent
            source: parent
            radius: theme === "light" ? 0 : 8
            visible: theme !== "light"
        }
    }
    // Arka plan için cyberpunk degrade ve grid efekti
    Rectangle {
        anchors.fill: parent
        z: -2
        visible: theme === "cyberpunk"
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#24262b" }
            GradientStop { position: 1.0; color: "#292b31" }
        }
    }
    Canvas {
        anchors.fill: parent
        z: -1
        visible: theme === "cyberpunk"
        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0,0,width,height);
            ctx.globalAlpha = 0.05;
            ctx.strokeStyle = "#b0bec5";
            for (var x=0; x<width; x+=40) {
                ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,height); ctx.stroke();
            }
            for (var y=0; y<height; y+=40) {
                ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(width,y); ctx.stroke();
            }
        }
    }

    // Üst Bar ve Sekmeler
    Rectangle {
        width: parent.width
        height: 60
        color: accent
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 10
            spacing: 20
            Loader {
                width: 48; height: 48
                sourceComponent: logoImage
            }
            Text {
                text: "Humbaba Yer İstasyonu"
                color: textMain
                font.pixelSize: 24
                font.bold: true
                Layout.alignment: Qt.AlignVCenter
                // Neon gölge efekti
                layer.enabled: true
                layer.effect: DropShadow {
                    color: accent
                    radius: 16
                    x: 0; y: 0
                    spread: 0.4
                }
            }
            Item { Layout.fillWidth: true }
            Text {
                text: "Takım ID:"
                color: textMain
                font.pixelSize: 14
                Layout.alignment: Qt.AlignVCenter
            }
            TextField {
                id: teamIdInput
                text: teamId.toString()
                width: 60
                height: 30
                horizontalAlignment: TextInput.AlignCenter
                inputMethodHints: Qt.ImhDigitsOnly
                validator: IntValidator { bottom: 1; top: 999 }
                onTextChanged: {
                    if (text !== "") {
                        teamId = parseInt(text) || 1
                    }
                }
                background: Rectangle {
                    color: "white"
                    radius: 6
                    border.color: accent
                    border.width: 1
                }
            }
            Text {
                text: "Baudrate:"
                color: textMain
                font.pixelSize: 14
                Layout.alignment: Qt.AlignVCenter
            }
            ComboBox {
                id: baudrateCombo
                model: [9600, 19200, 38400, 57600, 115200]
                currentIndex: 0
                width: 100
                onCurrentIndexChanged: baudrate = parseInt(model[currentIndex])
                Layout.alignment: Qt.AlignVCenter
            }
            ComboBox {
                id: portCombo
                model: telemetryBridge ? telemetryBridge.get_ports() : []
                width: 200
                onActivated: selectedPort = model[currentIndex]
                Component.onCompleted: {
                    if (telemetryBridge) {
                        var ports = telemetryBridge.get_ports()
                        ports.push("Fake Telemetri")
                        model = ports
                    } else {
                        model = ["Fake Telemetri"]
                    }
                }
            }
            Button {
                text: "Bağlan"
                width: 100
                background: Rectangle {
                    color: successColor
                    radius: 8
                }
                onClicked: {
                    if (portCombo.currentText === "Fake Telemetri") {
                        telemetryBridge.start_fake_telemetry()
                        speechHelper.speak("Fake telemetri başlatıldı")
                        currentTab = 0  // Telemetri sayfasına geç
                    } else if (portCombo.currentText) {
                        telemetryBridge.connect_port(portCombo.currentText, teamId, baudrate)
                    }
                }
            }
            Button {
                text: "Kes"
                width: 100
                background: Rectangle {
                    color: errorColor
                    radius: 8
                }
                onClicked: telemetryBridge.disconnect_port()
            }

            // Theme selector ve ses butonu bir arada
            Row {
                id: themeAndMuteRow
                spacing: 24 // spacing artırıldı
                Layout.alignment: Qt.AlignVCenter
                // Tema seçici ve popup aynı Item içinde
                Item {
                    id: themeMenuRoot
                    property bool menuOpen: false
                    width: 40; height: 40
                    Rectangle {
                        id: themeMenuButton
                        width: 40; height: 40; radius: 20
                        color: "#ffffff22" // Modern yarı şeffaf beyaz
                        border.color: accent
                        border.width: 1
                        Text {
                            anchors.centerIn: parent
                            text: "🎨"
                            font.pixelSize: 22
                            color: accent
                        }
                        MouseArea {
                            anchors.fill: parent
                            onClicked: themeMenuRoot.menuOpen = !themeMenuRoot.menuOpen
                        }
                    }
                    Popup {
                        id: themePopup
                        x: themeMenuButton.x + themeMenuButton.width/2 - width/2
                        y: themeMenuButton.y + themeMenuButton.height + 8
                        width: 260
                        height: 60
                        modal: true
                        focus: true
                        visible: themeMenuRoot.menuOpen
                        onVisibleChanged: if (!visible) themeMenuRoot.menuOpen = false
                        background: Rectangle {
                            color: "#cc222222"
                            radius: 16
                            border.color: accent
                            border.width: 1
                        }
                        Row {
                            Layout.alignment: Qt.AlignHCenter
                            spacing: 10
                            Repeater {
                                model: [
                                    { key: "dark", icon: "🌙", name: "Dark" },
                                    { key: "light", icon: "☀️", name: "Light" },
                                    { key: "milenyum", icon: "🦾", name: "Milenyum" },
                                    { key: "roma", icon: "🏛️", name: "Roma" },
                                    { key: "cyberpunk", icon: "💾", name: "Cyberpunk" }
                                ]
                                delegate: Rectangle {
                                    width: 55; height: 55; radius: 12
                                    color: theme === modelData.key ? accent : "#22ffffff"
                                    border.color: theme === modelData.key ? "#fff" : accent
                                    border.width: theme === modelData.key ? 2 : 1
                                    Column {
                                        anchors.centerIn: parent
                                        spacing: 2
                                        Text {
                                            text: modelData.icon
                                            font.pixelSize: 22
                                            color: theme === modelData.key ? "#fff" : accent
                                        }
                                        Text {
                                            text: modelData.name
                                            font.pixelSize: 10
                                            color: theme === modelData.key ? "#fff" : accent
                                            font.bold: true
                                        }
                                    }
                                    property int clickCount: 0
                                    property double lastClickTime: 0
                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: {
                                            var now = Date.now();
                                            if (now - lastClickTime < 500) {
                                                clickCount++;
                                            } else {
                                                clickCount = 1;
                                            }
                                            lastClickTime = now;
                                            if (clickCount >= 3) {
                                                rapidClickAudio.stop();
                                                rapidClickAudio.play();
                                                clickCount = 0;
                                            }
                                            switchTheme(modelData.key);
                                            themeMenuRoot.menuOpen = false;
                                        }
                                    }
                                }
                            }
                        }
                    }
                    // Kapanma için dışarı tıklama
                    MouseArea {
                        anchors.fill: parent
                        z: 1
                        enabled: themeMenuRoot.menuOpen
                        visible: themeMenuRoot.menuOpen
                        propagateComposedEvents: true
                        onClicked: themeMenuRoot.menuOpen = false
                    }
                }
                Rectangle {
                    id: muteButton
                    width: 40; height: 40; radius: 20
                    color: "#ffffff22" // Modern yarı şeffaf beyaz
                    border.color: accent
                    border.width: 1
                    Text {
                        anchors.centerIn: parent
                        text: isMuted ? "🔇" : "🔊"
                        font.pixelSize: 22
                        color: accent
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            isMuted = !isMuted
                            milenyumAudio.volume = isMuted ? 0 : 1.0
                            romaAudio.volume = isMuted ? 0 : 1.0
                            rapidClickAudio.volume = isMuted ? 0 : 1.0
                            sonUcushAudio.volume = isMuted ? 0 : 1.0
                            roketAudio.volume = isMuted ? 0 : 1.0
                            audioPlayer.volume = isMuted ? 0 : 1.0
                            speechHelper.setMuted(isMuted)
                            speechHelper.stopSpeaking()
                        }
                    }
                }
            }
            // Butonlar ile Durum yazısı arasına geniş boşluk bırak
            Item { width: 40 }
            Text {
                text: "Durum: " + connectionStatus
                color: textMain
                font.pixelSize: 14
                Layout.alignment: Qt.AlignVCenter
            }
        }
    }

    // Sekme Barı
    Rectangle {
        width: parent.width
        height: 50
        y: 60
        color: cardBg
        Row {
            anchors.centerIn: parent
            spacing: 10
            TabButton { 
                text: "Telemetri"; 
                checked: currentTab === 0; 
                onClicked: currentTab = 0 
                background: Rectangle {
                    color: parent.checked ? accent : "transparent"
                    radius: 8
                }
            }
            TabButton { 
                text: "Hakem Portu"; 
                checked: currentTab === 1; 
                onClicked: currentTab = 1 
                background: Rectangle {
                    color: parent.checked ? accent : "transparent"
                    radius: 8
                }
            }
            TabButton { 
                text: "Geçmiş"; 
                checked: currentTab === 2; 
                onClicked: currentTab = 2 
                background: Rectangle {
                    color: parent.checked ? accent : "transparent"
                    radius: 8
                }
            }
        }
    }

    // Sayfa Loader
    Loader {
        id: pageLoader
        anchors.top: parent.top
        anchors.topMargin: 110
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        sourceComponent: currentTab === 0 ? pageTelemetry :
                        currentTab === 1 ? pageJudgePort :
                        pageHistory
    }

    // TELEMETRİ COMPONENT
    Component {
        id: pageTelemetry
        Rectangle {
            color: mainBg
            anchors.fill: parent
            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                Row {
                    spacing: 20
                    Rectangle {
                        width: 800
                        height: 500
                        radius: 16
                        color: cardBg
                        Column {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 10
                            Row {
                                spacing: 20
                        Text {
                                    text: "🚀 Canlı Roket Takibi"
                                    font.pixelSize: 18
                                    color: textMain
                            font.bold: true
                        }
                                
                                Item { Layout.fillWidth: true }
                                
                                TextField {
                                    id: flightNameInput
                                    placeholderText: "Uçuş Adı"
                                    width: 150
                                    height: 30
                                    background: Rectangle {
                                        color: "white"
                                        radius: 6
                                        border.color: accent
                                        border.width: 1
                                    }
                                }
                                
                    Button {
                                    text: "📹 Uçuş Başlat"
                                    width: 120
                                    height: 30
                                    background: Rectangle {
                                        color: "#27ae60"
                                        radius: 6
                                    }
                                    onClicked: {
                                        if (flightNameInput.text.trim() !== "") {
                                            var flightNameLower = flightNameInput.text.trim().toLowerCase();
                                            if (flightNameLower === "humbaba") {
                                                speechHelper.speak("Humbaba, Mezopotamya mitolojisinde dev bir canavardır. Enkidu ve Gılgamış destanında geçer.");
                                                flightNameInput.text = "";
                                                return;
                                            }
                                            if (["roket", "roketcilik", "gebze", "gebze teknik", "gtü", "gtu"].indexOf(flightNameLower) !== -1) {
                                                roketAudio.stop();
                                                roketAudio.play();
                                            } else if (["son uçuş", "aksaray", "roketsan", "oğuz", "oguz"].indexOf(flightNameLower) !== -1) {
                                                sonUcushAudio.stop();
                                                sonUcushAudio.play();
                                            }
                                            logManager.start_flight(flightNameInput.text)
                                            lastFlightName = flightNameInput.text
                                            lastFlightTime = Qt.formatDateTime(new Date(), "dd.MM.yyyy hh:mm:ss")
                                            speechHelper.speak("Uçuş kaydı başlatıldı: " + flightNameInput.text)
                                            addStatusMessage("Uçuş kaydı başlatıldı: " + flightNameInput.text, "success")
                                            flightNameInput.text = ""
                                        } else {
                                            speechHelper.speak("Lütfen uçuş adı girin")
                                            addStatusMessage("Lütfen uçuş adı girin", "warn")
                                        }
                                    }
                                }
                                
                    Button {
                                    text: "⏹️ Uçuş Bitir"
                                    width: 120
                                    height: 30
                                    background: Rectangle {
                                        color: "#e74c3c"
                                        radius: 6
                                    }
                        onClicked: {
                                        if (logManager.current_flight_id) {
                                            logManager.end_flight(logManager.current_flight_id)
                                            speechHelper.speak("Uçuş kaydı tamamlandı: " + lastFlightName)
                                            addStatusMessage("Uçuş kaydı tamamlandı: " + lastFlightName, "success")
                            } else {
                                            speechHelper.speak("Aktif uçuş bulunamadı")
                                            addStatusMessage("Aktif uçuş bulunamadı", "warn")
                                        }
                                    }
                                }
                            }
                Rectangle {
                                width: parent.width - 32
                                height: 420
                                radius: 8
                                color: "#222f3e"
                    border.color: accent
                    border.width: 2

                                // Harita arka planı
                                Rectangle {
                        anchors.fill: parent
                                    anchors.margins: 4
                                    radius: 6
                                    color: "#34495e"
                                    
                                    // Harita sınırları
                                    property real minLat: 39.9
                                    property real maxLat: 40.1
                                    property real minLon: 32.7
                                    property real maxLon: 32.9
                                    
                                    // Canlı harita görünümü
                        // WebEngineView kaldırıldı, yerine placeholder eklendi
                        Rectangle {
                                        id: mapView
                                        anchors.fill: parent
                                        color: "#34495e"
                                        Text {
                                            anchors.centerIn: parent
                                            text: "Harita devre dışı"
                                            color: "#fff"
                                            font.pixelSize: 18
                                            font.bold: true
                                        }
                                    }
                                    
                                    // Roket konumu
                                    Rectangle {
                                        id: rocketPosition
                                        width: 20
                                        height: 20
                                        radius: 10
                                        color: "#e74c3c"
                                        border.color: "#ffffff"
                                        border.width: 3
                                        x: {
                                            var lon = telemetryData.boylam || 32.8;
                                            var frac = (lon - parent.minLon) / (parent.maxLon - parent.minLon);
                                            return Math.max(0, Math.min(parent.width - width, frac * (parent.width - width)));
                                        }
                                        y: {
                                            var lat = telemetryData.enlem || 39.95;
                                            var frac = 1.0 - (lat - parent.minLat) / (parent.maxLat - parent.minLat);
                                            return Math.max(0, Math.min(parent.height - height, frac * (parent.height - height)));
                                        }
                                        
                                        // Roket animasyonu
                                        SequentialAnimation on scale {
                                            running: telemetryData.irtifa !== undefined
                                            loops: Animation.Infinite
                                            NumberAnimation { to: 1.4; duration: 200 }
                                            NumberAnimation { to: 1.0; duration: 200 }
                                        }
                                        
                                        // Roket izi
                                        Canvas {
                                            anchors.centerIn: parent
                                            width: 300
                                            height: 300
                                            onPaint: {
                                                var ctx = getContext("2d")
                                                ctx.strokeStyle = "#e74c3c"
                                                ctx.lineWidth = 3
                                                ctx.globalAlpha = 0.2
                                                
                                                // Roket izi çizimi
                                                ctx.beginPath()
                                                ctx.arc(width/2, height/2, 80, 0, 2 * Math.PI)
                                                ctx.stroke()
                                                
                                                // İç halka
                                                ctx.globalAlpha = 0.1
                                                ctx.beginPath()
                                                ctx.arc(width/2, height/2, 40, 0, 2 * Math.PI)
                                                ctx.stroke()
                                            }
                                        }
                                        
                                        // Roket etiketi
                                        Rectangle {
                                            anchors.bottom: parent.top
                                            anchors.bottomMargin: 5
                                            anchors.horizontalCenter: parent.horizontalCenter
                                            width: 80
                                            height: 25
                                            radius: 12
                                            color: "#e74c3c"
                                            opacity: 0.9
                                            
                                            Text {
                                                anchors.centerIn: parent
                                                text: "🚀 " + (telemetryData.irtifa ? telemetryData.irtifa.toFixed(0) + "m" : "Roket")
                                                color: "white"
                                                font.pixelSize: 10
                                                font.bold: true
                                            }
                                        }
                                    }
                                    
                                    // Koordinat eksenleri
                Rectangle {
                                        width: parent.width
                                        height: 1
                                        color: "#4a5568"
                                        anchors.verticalCenter: parent.verticalCenter
                                    }
                                    Rectangle {
                                        width: 1
                                        height: parent.height
                                        color: "#4a5568"
                    anchors.horizontalCenter: parent.horizontalCenter
                                    }
                                    
                                    // Uçuş kaydı bilgisi göster
                                    Rectangle {
                                        width: parent.width - 20
                                        height: 36
                                        anchors.top: parent.top
                                        anchors.topMargin: 50
                            anchors.horizontalCenter: parent.horizontalCenter
                                        radius: 8
                                        color: logManager.current_flight_id ? "#27ae60" : "#e74c3c"
                                        opacity: 0.9
                            Text {
                                            anchors.centerIn: parent
                                            text: logManager.current_flight_id ? ("Son Uçuş: " + lastFlightName + " | " + lastFlightTime) : "⏸️ Uçuş Kaydı Beklemede"
                                            color: "white"
                                            font.pixelSize: 14
                                font.bold: true
                                        }
                                    }
                                    
                                    // Canlı konum bilgileri
                                    Rectangle {
                                        width: parent.width - 20
                                        height: 100
                                        anchors.bottom: parent.bottom
                                        anchors.bottomMargin: 10
                                anchors.horizontalCenter: parent.horizontalCenter
                                    radius: 8
                                        color: "#2c3e50"
                                        opacity: 0.95
                                        
                                Row {
                                    anchors.fill: parent
                                            anchors.margins: 10
                                            spacing: 20
                                            
                                            Column {
                                                anchors.verticalCenter: parent.verticalCenter
                                                spacing: 4
                                    Text {
                                                    text: "📍 GPS Koordinatları"
                                                    color: textMain
                                        font.pixelSize: 14
                                                    font.bold: true
                                    }
                                    Text {
                                                    text: "Enlem: " + (telemetryData.enlem ? telemetryData.enlem.toFixed(6) : "Bilinmiyor")
                                                    color: textMain
                                                    font.pixelSize: 12
                                    }
                                    Text {
                                                    text: "Boylam: " + (telemetryData.boylam ? telemetryData.boylam.toFixed(6) : "Bilinmiyor")
                                                    color: textMain
                                                    font.pixelSize: 12
                                                }
                                            }
                                            
                                            Column {
                                                anchors.verticalCenter: parent.verticalCenter
                                                spacing: 4
                                    Text {
                                                    text: "📊 Uçuş Verileri"
                                                    color: textMain
                                        font.pixelSize: 14
                                        font.bold: true
                                                }
                                                Text {
                                                    text: "İrtifa: " + (telemetryData.irtifa ? telemetryData.irtifa.toFixed(1) + " m" : "Bilinmiyor")
                                                    color: textMain
                                                    font.pixelSize: 12
                                                }
                                                Text {
                                                    text: "GPS İrtifa: " + (telemetryData.gps_irtifa ? telemetryData.gps_irtifa.toFixed(1) + " m" : "Bilinmiyor")
                                                    color: textMain
                                                    font.pixelSize: 12
                                                }
                                            }
                                            
                                            Column {
                                                anchors.verticalCenter: parent.verticalCenter
                                                spacing: 4
                                Text {
                                                    text: "🎯 Durum"
                                                    color: textMain
                                    font.pixelSize: 14
                                                    font.bold: true
                                                }
                                                Text {
                                                    text: "Açı: " + (telemetryData.aci ? telemetryData.aci.toFixed(1) + "°" : "Bilinmiyor")
                                                    color: textMain
                                                    font.pixelSize: 12
                                                }
                                                Text {
                                                    text: "Yük: " + (telemetryData.yuk ? telemetryData.yuk.toFixed(1) + "%" : "Bilinmiyor")
                                                    color: textMain
                                                    font.pixelSize: 12
                                                }
                                            }
                                        }
                                    }
                                    

                                }
                            }
                        }
                    }
        Rectangle {
                        width: 350
                        height: 500
                radius: 16
                        color: cardBg
            Column {
                anchors.fill: parent
                            anchors.margins: 16
                            spacing: 10
                Text {
                                text: "📊 Canlı Telemetri"
                                font.pixelSize: 16
                                color: textMain
                    font.bold: true
                            }
                            Column {
                                spacing: 6
                                // Durum Mesajları Başlığı
                                Text {
                                    text: "Durum Mesajları"
                                    font.pixelSize: 14
                                    color: textMain
                                    font.bold: true
                                    anchors.topMargin: 16
                                }
                                // Durum Mesajları Listesi
                                Column {
                                    spacing: 4
                                    Repeater {
                                        model: statusMessages
                                        delegate: Rectangle {
                                            width: 320
                                            height: 28
                                            radius: 6
                                            color: {
                                                if (modelData.type === "success") return successColor
                                                else if (modelData.type === "error") return errorColor
                                                else if (modelData.type === "warn") return warningColor
                                                else return "#2c3e50"
                                            }
                                            Row {
                                                width: parent.width
                                                anchors.verticalCenter: parent.verticalCenter
                                                spacing: 8
                                                Text {
                                                    text: modelData.time + " -"
                                                    color: "#fff"
                                                    font.pixelSize: 11
                                                }
                                                Text {
                                                    text: modelData.text
                                                    color: "#fff"
                                                    font.pixelSize: 12
                                                    font.bold: true
                                                }
                                            }
                                        }
                                    }
                                }
                                // Her 4 saniyede bir mevcut irtifa ve bağlantı durumu mesajı ekleyen timer
                                Timer {
                                    interval: 4000
                                    running: true
                                    repeat: true
                                    onTriggered: {
                                        var irtifaMsg = telemetryData.irtifa ? ("Mevcut İrtifa: " + telemetryData.irtifa.toFixed(1) + " m") : "İrtifa verisi yok";
                                        var connMsg = connectionStatus === "Bağlı" ? "Telemetri bağlantısı aktif" : "Telemetri bağlantısı yok";
                                        // Son eklenen mesajlar aynıysa tekrar ekleme
                                        if (!statusMessages.length || statusMessages[0].text !== irtifaMsg) {
                                            window.addStatusMessage(irtifaMsg, "info");
                                        }
                                        if (!statusMessages.length || statusMessages[0].text !== connMsg) {
                                            window.addStatusMessage(connMsg, connectionStatus === "Bağlı" ? "success" : "error");
                                        }
                                    }
                                }
                                // Rastgele eğlenceli mesajlar ekleyen timer
                                Timer {
                                    interval: 20000
                                    running: true
                                    repeat: true
                                    onTriggered: {
                                        var funnyMessages = [
                                            "Roket Patladı",
                                            "Kapa dükkanı",
                                            "Yörüngeye çıkıyoruz!",
                                            "Sistemler nominal",
                                            "Beklenmeyen bir şey yok",
                                            "Havada süzülüyor!",
                                            "Kontrol sende kaptan!"
                                        ];
                                        var idx = Math.floor(Math.random() * funnyMessages.length);
                                        addStatusMessage(funnyMessages[idx], "info");
                                    }
                                }
                            }
                        }
                    }
                }
                Rectangle {
                    width: parent.width
                    height: 150
                    radius: 16
                    color: cardBg
                    Column {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 10
                        Text {
                            text: "🎯 Hızlı Durum Özeti"
                            font.pixelSize: 16
                            color: textMain
                            font.bold: true
                        }
                        Row {
                            spacing: 40
                Rectangle {
                                width: 200
                                height: 80
                                radius: 8
                                color: successColor
                    Column {
                                    anchors.centerIn: parent
                                    spacing: 4
                        Text {
                                        text: "🚀 Roket Durumu"
                                        color: "white"
                                        font.pixelSize: 14
                            font.bold: true
                                    }
                                    Text {
                                        text: telemetryData.irtifa ? "Aktif - " + telemetryData.irtifa.toFixed(0) + "m" : "Beklemede"
                                        color: "white"
                                        font.pixelSize: 12
                                    }
                                }
                            }
                            Rectangle {
                                width: 200
                                height: 80
                            radius: 8
                                color: accent
                                Column {
                                    anchors.centerIn: parent
                                    spacing: 4
                                    Text {
                                        text: "📍 Konum"
                                        color: "white"
                                        font.pixelSize: 14
                                        font.bold: true
                                    }
                                    Text {
                                        text: telemetryData.enlem ? telemetryData.enlem.toFixed(4) + ", " + telemetryData.boylam.toFixed(4) : "Bilinmiyor"
                                        color: "white"
                                        font.pixelSize: 12
                                    }
                                }
                            }
                Rectangle {
                                width: 200
                    height: 80
                                radius: 8
                                color: warningColor
                    Column {
                                    anchors.centerIn: parent
                                    spacing: 4
                        Text {
                                        text: "⚡ Sistem"
                                        color: "white"
                            font.pixelSize: 14
                            font.bold: true
                        }
                        Text {
                                        text: telemetryData.yuk ? "Yük: " + telemetryData.yuk.toFixed(1) + "%" : "Bilinmiyor"
                                        color: "white"
                            font.pixelSize: 12
                                    }
                                }
                            }
                        }
                    }
                }
            }
            Connections {
                target: telemetryBridge
                function onTelemetryUpdated(data) {
                    console.log("=== TELEMETRİ VERİSİ ALINDI ===")
                    console.log("Ham veri:", data)
                    console.log("Veri türü:", typeof data)
                    console.log("JSON string:", JSON.stringify(data))
                    console.log("İrtifa:", data.irtifa, "tür:", typeof data.irtifa)
                    console.log("GPS İrtifa:", data.gps_irtifa, "tür:", typeof data.gps_irtifa)
                    console.log("Enlem:", data.enlem, "tür:", typeof data.enlem)
                    console.log("Boylam:", data.boylam, "tür:", typeof data.boylam)
                    console.log("Tüm anahtarlar:", Object.keys(data))
                    telemetryData = data
                    console.log("telemetryData güncellendi:", telemetryData)
                    
                    // İrtifa sesli uyarı sistemi
                    if (data.irtifa && data.irtifa > 0) {
                        var currentAltitude = Math.floor(data.irtifa / 200) * 200
                        if (currentAltitude > lastAltitudeAnnouncement) {
                            lastAltitudeAnnouncement = currentAltitude
                            speechHelper.speak("İrtifa " + currentAltitude + " metre")
                            addStatusMessage("İrtifa " + currentAltitude + " metre", "info")
                        }
                    }
                    
                    // Haritayı güncelle
                    if (data.enlem && data.boylam) {
                        // mapView.url = "https://www.openstreetmap.org/export/embed.html?bbox=" + 
                        //              (data.boylam - 0.01) + "," + (data.enlem - 0.01) + "," + 
                        //              (data.boylam + 0.01) + "," + (data.enlem + 0.01) + 
                        //              "&layer=mapnik&marker=" + data.enlem + "," + data.boylam
                    }
                    
                    // GPS sinyali kaybolduğunda sesli uyarı ve durum mesajı
                    if (!data.enlem || !data.boylam) {
                        speechHelper.speak("GPS sinyali kayboldu")
                        addStatusMessage("GPS sinyali kayboldu", "warn")
                    }
                }
                function onConnectionStatusChanged(connected, message) {
                    connectionStatus = message
                    if (connected) {
                        speechHelper.speak("Bağlantı kuruldu")
                        addStatusMessage("Bağlantı kuruldu", "success")
                    } else {
                        speechHelper.speak("Bağlantı kesildi")
                        addStatusMessage("Bağlantı kesildi", "error")
                    }
                }
            }
        }
    }

    // HAKEM PORTU COMPONENT
    Component {
        id: pageJudgePort
        Rectangle {
            color: mainBg
            anchors.fill: parent
            Column {
                anchors.centerIn: parent
                spacing: 30
                Text {
                    text: "Hakem Yer İstasyonu Port Ayarları"
                    font.pixelSize: 22
                    color: textMain
                    font.bold: true
                }
                Row {
                    spacing: 20
                    Text {
                        text: "Port:"
                        color: textMain
                        font.pixelSize: 16
                    }
                    ComboBox {
                        id: judgePortCombo
                        model: telemetryBridge ? telemetryBridge.get_ports() : []
                        width: 200
                        onActivated: selectedPort = model[currentIndex]
                    }
                    Text {
                        text: "Baudrate:"
                        color: textMain
                        font.pixelSize: 16
                    }
                    ComboBox {
                        id: judgeBaudrateCombo
                        model: [9600, 19200, 38400, 57600, 115200]
                        currentIndex: 0
                        width: 120
                        onCurrentIndexChanged: baudrate = parseInt(model[currentIndex])
                    }
                    Button {
                        text: "Bağlan"
                        width: 100
                        background: Rectangle {
                            color: successColor
                            radius: 8
                        }
                        onClicked: {
                            if (judgePortCombo.currentText) {
                                telemetryBridge.connect_port(judgePortCombo.currentText, teamId, baudrate)
                            }
                        }
                    }
                    Button {
                        text: "Kes"
                        width: 100
                        background: Rectangle {
                            color: errorColor
                            radius: 8
                        }
                        onClicked: telemetryBridge.disconnect_port()
                    }
                }
                Text {
                    text: "Durum: " + connectionStatus
                    color: textMain
                    font.pixelSize: 16
                }
            }
        }
    }



    // GEÇMİŞ + İSTATİSTİKLERİ DÜZGÜN ALT ALTA KOY
    Component {
        id: pageHistory
                    Rectangle {
            color: mainBg
            anchors.fill: parent
                        Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                
                            Text {
                    text: "Uçuş Geçmişi"
                    font.pixelSize: 24
                                font.bold: true
                    color: textMain
                                anchors.horizontalCenter: parent.horizontalCenter
                }

                // Geçmiş Uçuşlar kutusu
                Rectangle {
                    width: parent.width
                    height: 400
                    radius: 16
                    color: cardBg
                    Column {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 10
                        Text {
                            text: "Geçmiş Uçuşlar"
                            font.pixelSize: 16
                            color: textMain
                            font.bold: true
                        }
                        ListView {
                            width: parent.width
                            height: 300
                            model: logManager.get_flight_list()
                            delegate: Rectangle {
                                width: parent.width
                                height: 60
                                radius: 8
                                color: index % 2 === 0 ? "#2c3e50" : "#34495e"
                                Row {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 20
                                    Column {
                                        anchors.verticalCenter: parent.verticalCenter
                                        Text {
                                            text: "Uçuş " + modelData.id + ": " + modelData.name
                                            color: "#ffffff"
                                            font.pixelSize: 14
                                            font.bold: true
                                        }
                                        Text {
                                            text: "Başlangıç: " + modelData.start_time
                                            color: "#ffffff"
                                            font.pixelSize: 12
                                        }
                                    }
                                    Item { Layout.fillWidth: true }
                                    Button {
                                        text: "Detaylar"
                                        width: 80
                                        height: 30
                                        anchors.verticalCenter: parent.verticalCenter
                                        background: Rectangle {
                                            color: accent
                                            radius: 6
                                        }
                                        onClicked: {
                                            selectedFlightStats = {}
                                            selectedFlightStats = logManager.get_flight_statistics(modelData.id)
                                            statsLoader.active = false
                                            statsLoader.active = true
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // Seçili Uçuş İstatistikleri kutusu
                Rectangle {
                    width: parent.width
                    height: 260
                    radius: 50
                    color: cardBg
                    Column {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 12
                        Text {
                            text: "Seçili Uçuş İstatistikleri"
                            font.pixelSize: 16
                            color: textMain
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Loader {
                            width: parent.width*0.95
                            id: statsLoader
                            anchors.horizontalCenter: parent.horizontalCenter
                            sourceComponent: Object.keys(selectedFlightStats).length === 0 ? noDataComp : statsComp
                        }
                        Component {
                            id: noDataComp
                            Text {
                                text: "Veri yok"
                                color: textMain
                                font.pixelSize: 14
                                anchors.horizontalCenter: parent.horizontalCenter
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                        Component {
                            id: statsComp
                            ScrollView {
                                width: parent.width
                                height: 180
                                clip: true
                                ScrollBar.horizontal.policy: ScrollBar.AlwaysOn
                                ScrollBar.vertical.policy: ScrollBar.AsNeeded
                                Row {
                                    id: statsRow
                                    spacing: 0
                                    height: 150
                                    width: Math.max(parent.width, Object.keys(selectedFlightStats).length * 120)
                                    Repeater {
                                        model: Object.keys(selectedFlightStats)
                                        delegate: Rectangle {
                                            width: 120
                                            height: 54
                                            radius: 10
                                            color: accent
                                            layer.enabled: true
                                            layer.effect: DropShadow {
                                                color: Qt.darker(accent, 1.2)
                                                radius: 6
                                                samples: 12
                                                verticalOffset: 2
                                            }
                                            border.color: Qt.lighter(accent, 1.2)
                                            border.width: 1
                                            Column {
                                                anchors.centerIn: parent
                                                spacing: 2
                                                Text {
                                                    text: modelData
                                                    color: "#fff"
                                                    font.pixelSize: 14
                                                    font.bold: true
                                                    horizontalAlignment: Text.AlignHCenter
                                                    anchors.horizontalCenter: parent.horizontalCenter
                                                }
                                                Text {
                                                    text: "Ort: " + (selectedFlightStats[modelData] ? selectedFlightStats[modelData].avg.toFixed(2) : "N/A")
                                                    color: "#fff"
                                                    font.pixelSize: 11
                                                    horizontalAlignment: Text.AlignHCenter
                                                    anchors.horizontalCenter: parent.horizontalCenter
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Helper functions
    function updatePacketStats(status) {
        packetStats.total++
        if (status === "success") {
            packetStats.success++
        } else {
            packetStats.failed++
        }
        packetStats.successRate = packetStats.total > 0 ? Math.round((packetStats.success / packetStats.total) * 100) : 0
    }

    // Durum mesajı ekleme fonksiyonu
    function addStatusMessage(text, type) {
        var now = new Date();
        var time = now.toLocaleTimeString();
        var arr = statusMessages.slice(); // Kopyasını al
        arr.unshift({ text: text, type: type || "info", time: time });
        if (arr.length > 13) arr.pop();
        statusMessages = arr; // Referansı değiştir, QML binding tetiklensin
    }

    // Tam ekran video oynatıcı
        Rectangle {
        id: order66Overlay
            anchors.fill: parent
        color: "black"
        visible: false
        z: 1000
        Video {
            id: order66Video
            anchors.fill: parent
            source: "assets/video/p.mp4"
            autoPlay: false
            fillMode: VideoOutput.PreserveAspectCrop
            onStopped: order66Overlay.visible = false
        }
        Timer {
            interval: 500
            running: order66Overlay.visible
            repeat: true
            onTriggered: {
                if (order66Video.error !== 0) {
                    order66Overlay.visible = false
                    running = false
                }
            }
        }
        Keys.onEscapePressed: order66Overlay.visible = false
        MouseArea {
            anchors.fill: parent
            onClicked: order66Overlay.visible = false
        }
    }

    // Durum Mesajları Kutusu
    Rectangle {
        id: bekirOverlay
        anchors.fill: parent
        color: "black"
        opacity: 0.85
        visible: bekirVisible && currentTab === 0
        z: 1000
        Video {
            id: bekirVideo
            anchors.centerIn: parent
            width: parent.width * 0.5
            height: parent.height * 0.5
            source: "assets/video/bekir.mp4"
            autoPlay: false
            fillMode: VideoOutput.PreserveAspectFit
            onStopped: bekirVisible = false
        }
        MouseArea {
            anchors.fill: parent
            onClicked: {
                bekirVideo.stop();
                bekirVisible = false;
            }
        }
    }

    Rectangle {
        id: splashScreen
        anchors.fill: parent
        color: "#181a20" // veya mainBg
        visible: splashVisible
        z: 10000
        Column {
            anchors.centerIn: parent
            spacing: 32
            Image {
                source: "../assets/images/LOGO.PNG"
                width: 180
                height: 180
                fillMode: Image.PreserveAspectFit
            }
            Text {
                text: "Humbaba Yer İstasyonu"
                font.pixelSize: 32
                color: "#fff"
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
            }
        }
        Timer {
            interval: 2000
            running: splashVisible
            repeat: false
            onTriggered: splashVisible = false
        }
    }

    Item {
        visible: !splashVisible
        anchors.fill: parent
        // ... mevcut ana arayüz kodları buraya taşınacak ...
    }
}