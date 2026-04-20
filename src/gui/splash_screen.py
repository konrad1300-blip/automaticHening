from PySide6.QtWidgets import QSplashScreen
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt


class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(500, 300)
        pixmap.fill(Qt.darkBlue)
        super().__init__(pixmap)
        self.setFont(QFont("Arial", 16, QFont.Bold))
        self.showMessage("AutomaticHening\nŁadowanie...",
                         Qt.AlignCenter, Qt.white)