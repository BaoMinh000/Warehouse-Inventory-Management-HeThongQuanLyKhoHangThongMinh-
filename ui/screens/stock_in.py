import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QDate
from backend.app.services.api_client import InventoryAPIClient
from ui.utils.theme import Theme 
# Import lớp điều phối nghiệp vụ vừa tách
from ui.controllers.stock_in_controller import StockInController


class StockInScreen(QWidget):
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        
        # Khởi tạo API Client và Controller điều phối
        active_api = api_client or getattr(parent, 'api_client', InventoryAPIClient())
        self.controller = StockInController(self, active_api)
        
        self.stack = QStackedWidget(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)
        
        self.init_form_view()
        
        self.stack.addWidget(self.form_widget)
        self.stack.setCurrentWidget(self.form_widget)

    def init_form_view(self):
        """Màn hình chính: Form tạo lô nhập kho mới"""
        self.form_widget = QWidget()
        layout = QVBoxLayout(self.form_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        self.form_widget.setStyleSheet(f"""
            QLabel {{ color: {Theme.TEXT_MUTED}; font-size: 12px; }}
            QLineEdit, QComboBox, QDateEdit, QTextEdit {{
                background: {Theme.BG_INPUT};
                border: 1px solid {Theme.BORDER_INPUT};
                border-radius: 6px;
                color: {Theme.TEXT_MAIN};
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
                border-color: {Theme.COLOR_PRIMARY};
            }}
            QComboBox::drop-down {{ border: none; padding-right: 10px; }}
        """)

        # --- HEADER BAR ---
        header = QHBoxLayout()
        title_lay = QVBoxLayout()
        title = QLabel("Nhập kho")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Theme.TEXT_MAIN};")
        subtitle = QLabel("Tạo lô nhập mới · FIFO / LIFO tự động")
        subtitle.setStyleSheet(f"font-size: 11px; color: {Theme.TEXT_MUTED};")
        title_lay.addWidget(title)
        title_lay.addWidget(subtitle)
        
        header.addLayout(title_lay)
        header.addStretch()
        layout.addLayout(header)

        # --- BOX THÔNG TIN LÔ HÀNG ---
        info_box = QFrame()
        info_box.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_DARK}; border: 1px solid {Theme.BORDER_PANEL_DARK}; border-radius: 8px; }}")
        box_layout = QVBoxLayout(info_box)
        box_layout.setContentsMargins(16, 16, 16, 16)
        box_layout.setSpacing(12)

        group_title = QLabel("📦   Thông tin lô hàng")
        group_title.setStyleSheet(f"color: {Theme.TEXT_BLUE_ACCENT}; font-weight: bold; font-size: 13px; border: none;")
        box_layout.addWidget(group_title)

        # Hàng 1: Mã sản phẩm & Tên sản phẩm
        row1 = QHBoxLayout()
        col1_1 = QVBoxLayout()
        lbl_barcode = QLabel("Mã sản phẩm / Barcode")
        lbl_barcode.setStyleSheet("border: none; background: transparent;")
        col1_1.addWidget(lbl_barcode)
        
        self.txt_barcode = QLineEdit()
        self.txt_barcode.setPlaceholderText("📷 Quét hoặc nhập barcode...")
        # SỰ KIỆN: Ủy quyền khi nhấn Enter ở ô vạch cho Controller xử lý
        self.txt_barcode.returnPressed.connect(self.controller.handle_barcode_scanned)
        col1_1.addWidget(self.txt_barcode)
        row1.addLayout(col1_1, 1)
        
        col1_2 = QVBoxLayout()
        lbl_name = QLabel("Tên sản phẩm")
        lbl_name.setStyleSheet("border: none; background: transparent;")
        col1_2.addWidget(lbl_name)
        
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Tự động điền sau khi quét...")
        col1_2.addWidget(self.txt_name)
        row1.addLayout(col1_2, 1)
        box_layout.addLayout(row1)

        # Hàng 2: Số lượng nhập & Đơn vị
        row2 = QHBoxLayout()
        col2_1 = QVBoxLayout()
        lbl_qty = QLabel("Số lượng nhập")
        lbl_qty.setStyleSheet("border: none; background: transparent;")
        col2_1.addWidget(lbl_qty)
        
        self.txt_qty = QLineEdit("240")
        col2_1.addWidget(self.txt_qty)
        row2.addLayout(col2_1, 1)
        
        col2_2 = QVBoxLayout()
        lbl_unit = QLabel("Đơn vị")
        lbl_unit.setStyleSheet("border: none; background: transparent;")
        col2_2.addWidget(lbl_unit)
        
        self.cbo_unit = QComboBox()
        self.cbo_unit.addItems(["Thùng", "Chai", "Hộp", "Can", "Túi"])
        col2_2.addWidget(self.cbo_unit)
        row2.addLayout(col2_2, 1)
        box_layout.addLayout(row2)

        # Hàng 3: Ngày nhận & Ngày hết hạn
        row3 = QHBoxLayout()
        col3_1 = QVBoxLayout()
        lbl_receive = QLabel("Ngày nhận")
        lbl_receive.setStyleSheet("border: none; background: transparent;")
        col3_1.addWidget(lbl_receive)
        
        self.dt_receive = QDateEdit(QDate.currentDate())
        self.dt_receive.setCalendarPopup(True)
        col3_1.addWidget(self.dt_receive)
        row3.addLayout(col3_1, 1)
        
        col3_2 = QVBoxLayout()
        lbl_expiry = QLabel("Ngày hết hạn")
        lbl_expiry.setStyleSheet("border: none; background: transparent;")
        col3_2.addWidget(lbl_expiry)
        
        self.dt_expiry = QDateEdit(QDate.currentDate().addMonths(6))
        self.dt_expiry.setCalendarPopup(True)
        col3_2.addWidget(self.dt_expiry)
        row3.addLayout(col3_2, 1)
        box_layout.addLayout(row3)

        # Hàng 4: Phương thức xuất kho & Vị trí kệ
        row4 = QHBoxLayout()
        col4_1 = QVBoxLayout()
        lbl_strategy = QLabel("Phương thức xuất kho")
        lbl_strategy.setStyleSheet("border: none; background: transparent;")
        col4_1.addWidget(lbl_strategy)
        
        self.cbo_strategy = QComboBox()
        self.cbo_strategy.addItems(["FIFO — First In First Out", "LIFO — Last In First Out"])
        col4_1.addWidget(self.cbo_strategy)
        row4.addLayout(col4_1, 1)
        
        col4_2 = QVBoxLayout()
        lbl_location = QLabel("Vị trí kệ")
        lbl_location.setStyleSheet("border: none; background: transparent;")
        col4_2.addWidget(lbl_location)
        
        self.txt_location = QLineEdit("A-03-02")
        col4_2.addWidget(self.txt_location)
        row4.addLayout(col4_2, 1)
        box_layout.addLayout(row4)

        # Hàng 5: Ghi chú
        col_note = QVBoxLayout()
        lbl_note = QLabel("Ghi chú lô hàng")
        lbl_note.setStyleSheet("border: none; background: transparent;")
        col_note.addWidget(lbl_note)
        
        self.txt_note = QTextEdit()
        self.txt_note.setPlaceholderText("Ghi chú tùy chọn...")
        self.txt_note.setMaximumHeight(60)
        col_note.addWidget(self.txt_note)
        box_layout.addLayout(col_note)
        
        layout.addWidget(info_box)

        # --- SECTION XÁC NHẬN LÔ NHẬP ---
        confirm_box = QFrame()
        confirm_box.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_DARK}; border: 1px solid {Theme.BORDER_PANEL_DARK}; border-radius: 8px; }}")
        conf_layout = QVBoxLayout(confirm_box)
        conf_layout.setContentsMargins(16, 16, 16, 16)
        
        conf_title = QLabel("✓   Xác nhận lô nhập")
        conf_title.setStyleSheet(f"color: {Theme.TEXT_BANNER_SUCCESS}; font-weight: bold; font-size: 13px; border: none; margin-bottom: 4px;")
        conf_layout.addWidget(conf_title)

        alert_banner = QFrame()
        alert_banner.setStyleSheet(f"QFrame {{ background: {Theme.BG_BANNER_SUCCESS}; border: 1px solid {Theme.BORDER_BANNER_SUCCESS}; border-radius: 6px; }}")
        alert_layout = QHBoxLayout(alert_banner)
        alert_layout.setContentsMargins(16, 12, 16, 12)

        info_text_layout = QVBoxLayout()
        self.lbl_batch_title = QLabel("Lô mới — Chờ kiểm tra thông tin")
        self.lbl_batch_title.setStyleSheet(f"color: {Theme.TEXT_BANNER_SUCCESS}; font-weight: bold; font-size: 14px; border:none;")
        self.lbl_batch_sub = QLabel("Vui lòng nhập đầy đủ các thông tin của sản phẩm ở phía trên")
        self.lbl_batch_sub.setStyleSheet(f"color: {Theme.TEXT_NORMAL}; font-size: 11px; border:none;")
        info_text_layout.addWidget(self.lbl_batch_title)
        info_text_layout.addWidget(self.lbl_batch_sub)
        
        btn_submit = QPushButton("Xác nhận nhập kho")
        btn_submit.setStyleSheet(f"""
            QPushButton {{ 
                background: {Theme.BTN_MINT_SUCCESS}; 
                border: none; 
                color: {Theme.BG_PANEL_DARK}; 
                padding: 10px 20px; 
                border-radius: 6px; 
                font-weight: bold; 
                font-size: 13px;
            }}
            QPushButton:hover {{ background: {Theme.BTN_MINT_HOVER}; }}
        """)
        
        # SỰ KIỆN: Ủy quyền thực thi nghiệp vụ nhập kho sang cho Controller điều phối
        btn_submit.clicked.connect(self.controller.handle_confirm_stock_in)
        
        alert_layout.addLayout(info_text_layout)
        alert_layout.addStretch()
        alert_layout.addWidget(btn_submit)
        
        conf_layout.addWidget(alert_banner)
        layout.addWidget(confirm_box)
        layout.addStretch()