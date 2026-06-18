from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class StatCard(QFrame):
    """ Thẻ hiển thị chỉ số thống kê tổng quan """

    def __init__(self, label: str, value: str, trend: str = "", value_color: str = "#e2e8f0", parent=None):
        super().__init__(parent)
        self.setObjectName("stat_card")
        self.setFixedHeight(88)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        # Tiêu đề thẻ
        self.lbl_title = QLabel(label)
        self.lbl_title.setStyleSheet("color:#4a5a78; font-size:11px; background: transparent; border: none;")

        # Giá trị số (Nổi bật)
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"color:{value_color}; font-size:20px; font-weight:500; background: transparent; border: none;")

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.val_lbl)

        # Dòng thông tin phụ phía dưới
        self.trend_lbl = QLabel(trend)
        self.trend_lbl.setStyleSheet("color:#4a5a78; font-size:10px; background: transparent; border: none;")
        layout.addWidget(self.trend_lbl)
        
        # Ẩn/Hiện tùy thuộc vào việc có text ban đầu hay không
        self.trend_lbl.setVisible(bool(trend))

        layout.addStretch()

    def update_value(self, value: str):
        """Cập nhật giá trị số lớn ở giữa"""
        self.val_lbl.setText(value)

    def update_subtext(self, trend: str):
        """Cập nhật dòng thông tin phụ phía dưới"""
        self.trend_lbl.setText(trend)
        self.trend_lbl.setVisible(bool(trend))