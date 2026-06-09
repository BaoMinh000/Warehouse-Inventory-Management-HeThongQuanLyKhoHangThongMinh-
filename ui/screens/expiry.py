from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
from ui.components.stat_card import StatCard
from ui.components.expiry_item import ExpiryItem

class ExpiryScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Header
        title_lay = QVBoxLayout()
        title = QLabel("Theo dõi Hạn sử dụng (FeFO)")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e2e8f0;")
        subtitle = QLabel("Hệ thống giám sát thời gian thực các lô hàng sắp hết hạn dùng")
        subtitle.setStyleSheet("font-size: 11px; color: #8899b4;")
        title_lay.addWidget(title)
        title_lay.addWidget(subtitle)
        layout.addLayout(title_lay)

        # Hàng Thẻ Thống kê (Stat Cards)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        
        card1 = StatCard("ĐÃ QUÁ HẠN", "2 lô", "Cần tiêu hủy ngay", "#f07070")
        card2 = StatCard("HẾT HẠN < 30 NGÀY", "5 lô", "Khuyến nghị xuất trước", "#e8a042")
        card3 = StatCard("TÌNH TRẠNG CHUNG", "An toàn", "98.2% lô hàng ổn định", "#2fd89c")
        
        stats_layout.addWidget(card1)
        stats_layout.addWidget(card2)
        stats_layout.addWidget(card3)
        layout.addLayout(stats_layout)

        # Danh sách timeline dòng hàng hết hạn
        list_title = QLabel("Dòng thời gian & Mức độ rủi ro của lô hàng")
        list_title.setStyleSheet("color: #8899b4; font-size: 12px; font-weight: 500; margin-top: 5px;")
        layout.addWidget(list_title)

        # Vùng cuộn chứa danh sách ExpiryItems
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(8)

        # Nạp dữ liệu vào ExpiryItem mẫu (tên, thông tin phụ, số ngày còn lại, phân loại nguy cấp)
        items_data = [
            ("Sữa tươi tiệt trùng TH True Milk 1L", "Lô #B2404-12 · SL: 140 thùng · Vị trí: A-01-02", -3, "critical"),
            ("Sữa chua Vinamilk có đường", "Lô #VNM-991 · SL: 50 thùng · Vị trí: A-04-05", 2, "critical"),
            ("Mì ăn liền Hảo Hảo Tôm chua cay", "Lô #HH-781 · SL: 85 thùng · Vị trí: B-04-11", 12, "warning"),
            ("Nước khoáng thiên nhiên Lavie 500ml", "Lô #LV-092 · SL: 500 chai · Vị trí: C-02-05", 25, "warning"),
            ("Dầu ăn Neptune Light 1L", "Lô #NEP-442 · SL: 1,200 chai · Vị trí: A-03-02", 90, "safe"),
            ("Bột giặt Ariel Cửa trên 5kg", "Lô #AR-112 · SL: 230 túi · Vị trí: D-02-03", 180, "safe"),
        ]

        for name, batch, days, severity in items_data:
            # Tham số cuối max_days quy định mốc tính phần trăm thanh tiến trình (ví dụ 180 ngày)
            item_widget = ExpiryItem(name, batch, days, severity, max_days=180)
            list_layout.addWidget(item_widget)
            
        list_layout.addStretch()
        scroll.setWidget(list_container)
        layout.addWidget(scroll, 1)