# ui/splash_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setFixedSize(QSize(450, 250))
        
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(15)

        self.title_label = QLabel("SMART WAREHOUSE SYSTEM")
        self.title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: #2c3e50;")

        self.status_label = QLabel("Đang khởi động hệ thống...")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100) # Đặt phạm vi cố định từ 0 đến 100
        self.progress_bar.setValue(0)      # Giá trị khởi tạo ban đầu
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #ecf0f1;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)

        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #ffffff; border: none; border-radius: 8px;")

    def set_progress(self, value: int, message: str):
        """Cập nhật giá trị phần trăm và dòng trạng thái thông báo"""
        # Giới hạn giá trị trong khoảng từ 0 đến 100 để tránh lỗi giao diện
        value = max(0, min(100, value))
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

        # Nếu đạt 100% thì đổi style chữ sang màu xanh thành công
        if value >= 100:
            self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: #7f8c8d; font-weight: normal;")