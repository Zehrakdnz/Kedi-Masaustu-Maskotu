import sys
import time
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl, QPoint, QProcess
from PySide6.QtGui import QDesktopServices, QPixmap, QPainter, QColor, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMenu,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)


class PatiIkonu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 20)

    def paintEvent(self, event):
        firca = QPainter(self)
        firca.setRenderHint(QPainter.RenderHint.Antialiasing)
        firca.setPen(Qt.PenStyle.NoPen)
        firca.setBrush(QColor("#d9a8cc"))

        firca.drawEllipse(2, 5, 5, 5)
        firca.drawEllipse(7, 2, 5, 5)
        firca.drawEllipse(13, 3, 5, 5)
        firca.drawEllipse(17, 7, 4, 4)
        firca.drawEllipse(6, 9, 12, 9)


class KucukMenu(QWidget):
    def __init__(self, maskot):
        super().__init__(maskot)
        self.maskot = maskot

        self.setObjectName("menuPanel")
        self.setFixedWidth(165)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(8, 7, 8, 8)
        duzen.setSpacing(5)

        baslik = QHBoxLayout()
        baslik.setSpacing(7)
        baslik.addWidget(PatiIkonu())

        yazi = QLabel("KISA YOLLAR")
        yazi.setObjectName("menuTitle")
        baslik.addWidget(yazi)
        baslik.addStretch()
        baslik.addWidget(PatiIkonu())
        duzen.addLayout(baslik)

        chatgpt = QPushButton("ChatGPT'yi aç")
        chatgpt.clicked.connect(self.chatgpt_ac)
        duzen.addWidget(chatgpt)

        not_defteri = QPushButton("Not Defteri aç")
        not_defteri.clicked.connect(self.not_defteri_ac)
        duzen.addWidget(not_defteri)

        ekran = QPushButton("Ekran görüntüsü al")
        ekran.clicked.connect(self.ekran_goruntusu_al)
        duzen.addWidget(ekran)

        kapat = QPushButton("Menüyü kapat")
        kapat.clicked.connect(self.hide)
        duzen.addWidget(kapat)

        self.setStyleSheet("""
            QWidget#menuPanel {
                background-color: #211d24;
                border: 1px solid #80677d;
                border-radius: 12px;
            }
            QLabel#menuTitle {
                color: #fff7fc;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
                border: none;
            }
            QPushButton {
                background-color: #39313d;
                color: #fff8fc;
                font-size: 11px;
                font-weight: bold;
                text-align: left;
                padding: 6px 6px;
                border: 1px solid #66566a;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #514154;
                border: 1px solid #d9a8cc;
            }
            QPushButton:pressed {
                background-color: #72556e;
            }
        """)

    def chatgpt_ac(self):
        QDesktopServices.openUrl(QUrl("https://chatgpt.com"))
        self.hide()

    def not_defteri_ac(self):
        QProcess.startDetached("notepad.exe")
        self.hide()

    def ekran_goruntusu_al(self):
        self.hide()
        QTimer.singleShot(300, self.maskot.ekran_goruntusu_cek)


class MasaustuKedisi(QLabel):
    def __init__(self):
        super().__init__()

        self.resim_dizini = Path(__file__).resolve().parent / "images"
        self.son_etkilesim = time.monotonic()
        self.gecici_durum_bitis = 0
        self.surukleme_baslangici = None
        self.ilk_pencere_konumu = None
        self.surukleme_ekrani = None
        self.suruklendi = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resim_yukle("moskott")
        self.panel = KucukMenu(self)

        self.zamanlayici = QTimer(self)
        self.zamanlayici.timeout.connect(self.durum_kontrol)
        self.zamanlayici.start(500)

    def resim_yukle(self, isim):
        dosya = self.resim_dizini / f"{isim}.png"
        resim = QPixmap(str(dosya))

        if resim.isNull():
            print("Resim yüklenemedi:", dosya)
            return

        self.durum = isim
        self.setPixmap(
            resim.scaled(
                180,
                180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.adjustSize()

    def etkilesim(self, durum="moskott", sure=0):
        self.son_etkilesim = time.monotonic()
        self.resim_yukle(durum)
        self.gecici_durum_bitis = (
            time.monotonic() + sure if sure else 0
        )

    def durum_kontrol(self):
        simdi = time.monotonic()

        if simdi - self.son_etkilesim >= 30:
            if self.durum != "sleep":
                self.resim_yukle("sleep")
        elif self.gecici_durum_bitis and simdi >= self.gecici_durum_bitis:
            self.gecici_durum_bitis = 0
            self.resim_yukle("moskott")

    def panel_konumla(self):
        self.panel.adjustSize()

        kedi_alani = self.frameGeometry()
        ekran = QGuiApplication.screenAt(kedi_alani.center())
        if ekran is None:
            ekran = QApplication.primaryScreen()
        if ekran is None:
            return

        ekran_alani = ekran.availableGeometry()
        bosluk = 6
        panel_genislik = self.panel.width()
        panel_yukseklik = self.panel.height()

        sag_x = kedi_alani.right() + 1 + bosluk
        sol_x = kedi_alani.left() - panel_genislik - bosluk

        if sag_x + panel_genislik <= ekran_alani.right() + 1:
            x = sag_x
        elif sol_x >= ekran_alani.left():
            x = sol_x
        else:
            x = max(
                ekran_alani.left(),
                min(sag_x, ekran_alani.right() - panel_genislik + 1),
            )

        y = max(
            ekran_alani.top(),
            min(kedi_alani.top(), ekran_alani.bottom() - panel_yukseklik + 1),
        )
        self.panel.move(x, y)

    def kedi_konumunu_sinirla(self, hedef_konum):
        ekran = self.surukleme_ekrani
        if ekran is None:
            ekran = QGuiApplication.screenAt(self.frameGeometry().center())
        if ekran is None:
            ekran = QApplication.primaryScreen()
        if ekran is None:
            return hedef_konum

        alan = ekran.availableGeometry()
        en_kucuk_x = alan.left()
        en_buyuk_x = max(en_kucuk_x, alan.right() - self.width() + 1)
        en_kucuk_y = alan.top()
        en_buyuk_y = max(en_kucuk_y, alan.bottom() - self.height() + 1)

        return QPoint(
            max(en_kucuk_x, min(hedef_konum.x(), en_buyuk_x)),
            max(en_kucuk_y, min(hedef_konum.y(), en_buyuk_y)),
        )

    def enterEvent(self, event):
        self.etkilesim("blink", 1)
        super().enterEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.surukleme_baslangici = event.globalPosition().toPoint()
            self.ilk_pencere_konumu = self.frameGeometry().topLeft()
            self.surukleme_ekrani = (
                QGuiApplication.screenAt(self.frameGeometry().center())
                or QApplication.primaryScreen()
            )
            self.suruklendi = False

        elif event.button() == Qt.MouseButton.RightButton:
            menu = QMenu(self)

            for isim, etiket in [
                ("moskott", "Normal"),
                ("ukala", "Ukala"),
                ("angry", "Kızgın"),
                ("suprised", "Şaşkın"),
                ("sleep", "Uyu"),
            ]:
                menu.addAction(
                    etiket,
                    lambda secilen=isim: self.etkilesim(secilen),
                )

            menu.addSeparator()
            menu.addAction("Kapat", QApplication.quit)
            menu.exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if (
            self.surukleme_baslangici is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            simdiki_nokta = event.globalPosition().toPoint()
            fark = simdiki_nokta - self.surukleme_baslangici

            if fark.manhattanLength() >= QApplication.startDragDistance():
                self.suruklendi = True
                imlecin_ekrani = QGuiApplication.screenAt(simdiki_nokta)
                if imlecin_ekrani is not None:
                    self.surukleme_ekrani = imlecin_ekrani

                hedef_konum = self.kedi_konumunu_sinirla(
                    self.ilk_pencere_konumu + fark
                )
                self.move(hedef_konum)

                if self.panel.isVisible():
                    self.panel_konumla()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.suruklendi:
                self.son_etkilesim = time.monotonic()

                if self.panel.isVisible():
                    self.panel.hide()
                else:
                    self.panel_konumla()
                    self.panel.show()
                    self.panel.raise_()

            self.surukleme_baslangici = None
            self.surukleme_ekrani = None

    def ekran_goruntusu_cek(self):
        ekran = QApplication.primaryScreen()

        if ekran is None:
            print("Ekran bulunamadı.")
            return

        klasor = Path(__file__).resolve().parent / "screenshots"
        klasor.mkdir(exist_ok=True)

        zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
        dosya = klasor / f"ekran_{zaman}.png"

        kaydedildi = ekran.grabWindow(0).save(str(dosya), "PNG")

        if kaydedildi:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(dosya)))
            print("Ekran görüntüsü kaydedildi:", dosya)
        else:
            print("Ekran görüntüsü kaydedilemedi.")


uygulama = QApplication(sys.argv)
kedi = MasaustuKedisi()
kedi.move(1000, 500)
kedi.show()
sys.exit(uygulama.exec())
