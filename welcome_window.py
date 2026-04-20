from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QLinearGradient, QColor, QPalette, QPixmap, QPainterPath


class WelcomeWindow(QFrame):
    closed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutomaticHening")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(900, 650)
        self.setup_ui()
        self.center_on_screen()
        
    def center_on_screen(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            qr = self.frameGeometry()
            cp = screen.availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        
        main_frame = QFrame(self)
        main_frame.setObjectName("mainFrame")
        main_frame.setStyleSheet("""
            QFrame#mainFrame {
                background-color: #ffffff;
                border-radius: 15px;
            }
        """)
        
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setStyleSheet("""
            QFrame {
                background: transparent;
            }
        """)
        
        title_label = QLabel("AutomaticHening")
        title_font = QFont("Segoe UI", 42, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1a237e; background: transparent; padding-top: 80px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        subtitle_label = QLabel("Program do projektowania plandek")
        subtitle_font = QFont("Segoe UI", 18)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #5c6bc0; background: transparent; padding-bottom: 40px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.open_button = QPushButton("  Otwórz plik STEP  ")
        self.open_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: #1E88E5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 40px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        
        button_layout.addWidget(self.open_button)
        button_layout.addStretch()
        
        info_label = QLabel("Kliknij, aby otworzyć plik STEP")
        info_label.setStyleSheet("color: #9e9e9e; background: transparent; padding-top: 30px; font-size: 12px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        version_label = QLabel("Wersja 1.0")
        version_label.setStyleSheet("color: #bdbdbd; background: transparent; padding-top: 80px; font-size: 10px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        frame_layout.addWidget(title_label)
        frame_layout.addWidget(subtitle_label)
        frame_layout.addLayout(button_layout)
        frame_layout.addWidget(info_label)
        frame_layout.addStretch()
        frame_layout.addWidget(version_label)
        
        layout.addWidget(main_frame)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.closed.emit()
            self.close()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(26, 35, 126))
        gradient.setColorAt(0.4, QColor(40, 53, 147))
        gradient.setColorAt(0.7, QColor(57, 73, 171))
        gradient.setColorAt(1, QColor(255, 255, 255))
        painter.setBrush(gradient)
        painter.drawRect(self.rect())
