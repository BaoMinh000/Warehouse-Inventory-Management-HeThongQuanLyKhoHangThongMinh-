import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt

from ui.components.stat_card import StatCard
from ui.components.expiry_item import ExpiryItem

# Gọi file theme tập trung của hệ thống
from ui.utils.theme import Theme 


class ExpiryScreen(QWidget):
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        self.api_client = api_client
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # --- HEADER ---
        title_lay = QVBoxLayout()
        title = QLabel("Theo dõi Hạn sử dụng (FeFO)")
        title.setStyleSheet(f"background: transparent; font-size: 16px; font-weight: bold; color: {Theme.TEXT_MAIN};")
        
        subtitle = QLabel("Hệ thống giám sát thời gian thực các lô hàng sắp hết hạn dùng")
        subtitle.setStyleSheet(f"background: transparent; font-size: 11px; color: {Theme.TEXT_MUTED};")
        
        title_lay.addWidget(title)
        title_lay.addWidget(subtitle)
        layout.addLayout(title_lay)

        # --- HÀNG THẺ THỐNG KÊ (STAT CARDS) ---
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        
        # Đồng bộ màu sắc hiển thị động của các con số qua Theme hệ thống
        card_expired = StatCard("ĐÃ QUÁ HẠN", "2 lô", "Cần tiêu hủy ngay", value_color=Theme.COLOR_DANGER)
        card_near = StatCard("HẾT HẠN < 30 NGÀY", "5 lô", "Khuyến nghị xuất trước", value_color=Theme.TEXT_BANNER_SUCCESS)
        card_status = StatCard("TÌNH TRẠNG CHUNG", "An toàn", "98.2% lô hàng ổn định", value_color=Theme.COLOR_SUCCESS)
        
        # Áp dụng cơ chế Qss Selector lồng để triệt tiêu vệt nền đen của các QLabel nội bộ bên trong StatCard
        for card in [card_expired, card_near, card_status]:
            card.setStyleSheet(f"""
                StatCard {{
                    background: {Theme.BG_PANEL_DARK};
                    border: 1px solid {Theme.BORDER_PANEL_DARK};
                    border-radius: 6px;
                }}
                QLabel {{
                    background: transparent; /* Ép chữ trong suốt để lộ màu nền tối gốc của thẻ */
                }}
            """)
            stats_layout.addWidget(card)
            
        layout.addLayout(stats_layout)

        # --- DANH SÁCH TIMELINE ---
        list_title = QLabel("Dòng thời gian & Mức độ rủi ro của lô hàng")
        list_title.setStyleSheet(f"background: transparent; color: {Theme.TEXT_MUTED}; font-size: 12px; font-weight: 500; margin-top: 5px;")
        layout.addWidget(list_title)

        # Vùng cuộn chứa danh sách ExpiryItems
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        
        list_container = QWidget()
        list_container.setStyleSheet("QWidget { background: transparent; }")
        
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(8)

        # Nạp dữ liệu vào các hàng ExpiryItem
        items_data = [
            ("Sữa tươi tiệt trùng TH True Milk 1L", "Lô #B2404-12 · SL: 140 thùng · Vị trí: A-01-02", -3, "critical"),
            ("Sữa chua Vinamilk có đường", "Lô #VNM-991 · SL: 50 thùng · Vị trí: A-04-05", 2, "critical"),
            ("Mì ăn liền Hảo Hảo Tôm chua cay", "Lô #HH-781 · SL: 85 thùng · Vị trí: B-04-11", 12, "warning"),
            ("Nước khoáng thiên nhiên Lavie 500ml", "Lô #LV-092 · SL: 500 chai · Vị trí: C-02-05", 25, "warning"),
            ("Dầu ăn Neptune Light 1L", "Lô #NEP-442 · SL: 1,200 chai · Vị trí: A-03-02", 90, "safe"),
            ("Bột giặt Ariel Cửa trên 5kg", "Lô #AR-112 · SL: 230 túi · Vị trí: D-02-03", 180, "safe"),
        ]

        for name, batch, days, severity in items_data:
            item_widget = ExpiryItem(name, batch, days, severity, max_days=180)
            list_layout.addWidget(item_widget)
            
        list_layout.addStretch()
        scroll.setWidget(list_container)
        layout.addWidget(scroll, 1)