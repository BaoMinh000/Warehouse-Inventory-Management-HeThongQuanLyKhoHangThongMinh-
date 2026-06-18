import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFrame, QStackedWidget, QProgressBar
)
from PyQt6.QtCore import Qt
from ui.utils.theme import Theme 
# Import bộ điều phối MVC vừa tách
from ui.controllers.stock_out_controller import StockOutController


class StockOutScreen(QWidget):
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        
        # Khởi tạo API Client và gán Controller xử lý sự kiện
        active_api = api_client or getattr(parent, 'api_client', None)
        self.controller = StockOutController(self, active_api)
        
        self.stack = QStackedWidget(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)
        
        self.init_form_view()
        
        self.stack.addWidget(self.form_widget)
        self.stack.setCurrentWidget(self.form_widget)

    def update_status_badge(self, success: bool):
        """Cập nhật Badge trạng thái nghiệp vụ dưới panel tóm tắt."""
        if success:
            self.lbl_badge.setText("Đã xuất")
            self.lbl_badge.setStyleSheet(
                f"background: {Theme.BG_BANNER_SUCCESS}; color: {Theme.TEXT_BANNER_SUCCESS}; "
                f"font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; border: none;"
            )
        else:
            self.lbl_badge.setText("Thất bại")
            self.lbl_badge.setStyleSheet(
                f"background: {Theme.BG_BADGE_DANGER}; color: {Theme.TEXT_BADGE_DANGER}; "
                f"font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; border: none;"
            )

    def update_allocation_progress(self, batch_id: str, order_id: str, qty_deducted: int, total_qty: int):
        """Cập nhật thông tin phân bổ lô hàng và hiển thị tiến trình QProgressBar."""
        self.lbl_ba_title.setText(f"Lô {batch_id} (Đã trừ kho)")
        self.lbl_ba_info.setText(f"Mã đơn: {order_id} · Trừ lũy tiến thành công: {qty_deducted}")
        
        self.bar.setRange(0, total_qty)
        self.bar.setValue(qty_deducted)
        self.lbl_progress_num.setText(f"{qty_deducted}/{total_qty}")

    def init_form_view(self):
        """Khởi tạo toàn bộ giao diện Form xuất kho định dạng Theme hệ thống."""
        self.form_widget = QWidget()
        layout = QVBoxLayout(self.form_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        self.form_widget.setStyleSheet(f"""
            QLabel {{ 
                color: {Theme.TEXT_MUTED}; 
                font-size: 12px; 
                border: none; 
                background: transparent; 
            }}
            QLineEdit, QComboBox {{
                background: {Theme.BG_INPUT};
                border: 1px solid {Theme.BORDER_INPUT};
                border-radius: 6px;
                color: {Theme.TEXT_MAIN};
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {Theme.COLOR_PRIMARY};
            }}
            QComboBox::drop-down {{ border: none; padding-right: 10px; }}
        """)

        # --- HEADER BAR ---
        header = QHBoxLayout()
        title_lay = QVBoxLayout()
        title = QLabel("Xuất kho")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Theme.TEXT_MAIN}; border: none; background: transparent;")
        subtitle = QLabel("Tự động phân bổ FIFO / LIFO · Rollback khi không đủ hàng")
        subtitle.setStyleSheet(f"font-size: 11px; color: {Theme.TEXT_MUTED}; border: none; background: transparent;")
        title_lay.addWidget(title)
        title_lay.addWidget(subtitle)
        
        header.addLayout(title_lay)
        header.addStretch()
        layout.addLayout(header)

        # --- BODY CONTENT (Cột Trái - Phải) ---
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        # --- CỘT TRÁI: THÔNG TIN ĐƠN XUẤT ---
        left_box = QFrame()
        left_box.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_DARK}; border: 1px solid {Theme.BORDER_PANEL_DARK}; border-radius: 8px; }}")
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)

        lbl_left_title = QLabel("📥   Thông tin đơn xuất")
        lbl_left_title.setStyleSheet(f"color: {Theme.TEXT_BLUE_ACCENT}; font-weight: bold; font-size: 13px; border: none; background: transparent;")
        left_layout.addWidget(lbl_left_title)

        left_layout.addWidget(QLabel("Mã đơn hàng"))
        self.txt_order_id = QLineEdit("ORD-7830")
        left_layout.addWidget(self.txt_order_id)

        left_layout.addWidget(QLabel("Mã vạch sản phẩm (Barcode)"))
        self.txt_product = QLineEdit("Mã vạch sản phẩm...") 
        left_layout.addWidget(self.txt_product)

        left_layout.addWidget(QLabel("Số lượng yêu cầu"))
        self.txt_qty = QLineEdit("200") 
        left_layout.addWidget(self.txt_qty)

        left_layout.addWidget(QLabel("Phương thức"))
        self.cbo_method = QComboBox()
        self.cbo_method.addItems(["FIFO — tự động (khuyến nghị)", "LIFO — tự động", "Chỉ định thủ công"])
        left_layout.addWidget(self.cbo_method)
        left_layout.addStretch()

        body_layout.addWidget(left_box, 1)

        # --- CỘT PHẢI: PHÂN BỔ TỰ ĐỘNG & TÓM TẮT ---
        right_box = QFrame()
        right_box.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_DARK}; border: 1px solid {Theme.BORDER_PANEL_DARK}; border-radius: 8px; }}")
        right_layout = QVBoxLayout(right_box)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        lbl_right_title = QLabel("Phân bổ tự động")
        lbl_right_title.setStyleSheet(f"color: {Theme.TEXT_MAIN}; font-weight: bold; font-size: 13px; border: none; background: transparent;")
        lbl_right_sub = QLabel("Hệ thống chọn lô theo quy tắc")
        lbl_right_sub.setStyleSheet(f"color: {Theme.TEXT_SUB}; font-size: 11px; border: none; background: transparent; margin-bottom: 4px;")
        right_layout.addWidget(lbl_right_title)
        right_layout.addWidget(lbl_right_sub)

        # Khung lô đề xuất chủ động
        batch_active = QFrame()
        batch_active.setStyleSheet(f"QFrame {{ background: {Theme.BG_BANNER_SUCCESS}; border: 1px solid {Theme.BORDER_BANNER_SUCCESS}; border-radius: 6px; }}")
        ba_lay = QVBoxLayout(batch_active)
        ba_lay.setContentsMargins(12, 10, 12, 10)
        ba_lay.setSpacing(6)
        
        self.lbl_ba_title = QLabel("Lô hệ thống đề xuất")
        self.lbl_ba_title.setStyleSheet(f"color: {Theme.TEXT_BANNER_SUCCESS}; font-weight: bold; border: none; background: transparent;")
        self.lbl_ba_info = QLabel("Thông tin phân bổ lũy tiến sẽ hiển thị tại đây")
        self.lbl_ba_info.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 11px; border: none; background: transparent;")
        
        progress_layout = QHBoxLayout()
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        self.bar.setStyleSheet(f"QProgressBar {{ background: {Theme.BG_INPUT}; border: none; border-radius: 3px; }}"
                               f"QProgressBar::chunk {{ background: {Theme.BTN_MINT_SUCCESS}; border-radius: 3px; }}")
        self.lbl_progress_num = QLabel("0/0")
        self.lbl_progress_num.setStyleSheet(f"color: {Theme.TEXT_BANNER_SUCCESS}; font-weight: bold; font-size: 11px; border: none; background: transparent;")
        progress_layout.addWidget(self.bar)
        progress_layout.addWidget(self.lbl_progress_num)

        ba_lay.addWidget(self.lbl_ba_title)
        ba_lay.addWidget(self.lbl_ba_info)
        ba_lay.addLayout(progress_layout)
        right_layout.addWidget(batch_active)

        # Khung lô dự phòng
        batch_backup = QFrame()
        batch_backup.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_BACKUP}; border: 1px solid {Theme.BORDER_PANEL_BACKUP}; border-radius: 6px; }}")
        bb_lay = QVBoxLayout(batch_backup)
        bb_lay.setContentsMargins(12, 10, 12, 10)
        bb_lay.setSpacing(2)
        lbl_bb_title = QLabel("Lô dự phòng hệ thống")
        lbl_bb_title.setStyleSheet(f"color: {Theme.TEXT_SUB}; font-weight: bold; border: none; background: transparent;")
        lbl_bb_info = QLabel("Tồn kho gối đầu — Chờ sử dụng")
        lbl_bb_info.setStyleSheet(f"color: {Theme.BORDER_HOVER}; font-size: 11px; border: none; background: transparent;")
        bb_lay.addWidget(lbl_bb_title)
        bb_lay.addWidget(lbl_bb_info)
        right_layout.addWidget(batch_backup)

        # Bảng tóm tắt số liệu dưới cùng
        summary_panel = QFrame()
        summary_panel.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_SUMMARY}; border-radius: 6px; border: none; }}")
        sm_lay = QVBoxLayout(summary_panel)
        sm_lay.setContentsMargins(12, 10, 12, 10)
        sm_lay.setSpacing(6)
        
        # Hàm tiện ích tạo hàng tóm tắt với nhãn và giá trị có thể tùy chỉnh màu sắc
        def make_summary_row(label, val, val_color=Theme.TEXT_MAIN):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {Theme.TEXT_LABEL_SUMMARY}; border: none; background: transparent;")
            v = QLabel(val)
            v.setStyleSheet(f"color: {val_color}; font-weight: bold; border: none; background: transparent;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(v)
            return row

        sm_lay.addLayout(make_summary_row("Nghiệp vụ", "Xuất kho tự động"))
        
        status_row = QHBoxLayout()
        lbl_st = QLabel("Trạng thái")
        lbl_st.setStyleSheet(f"color: {Theme.TEXT_LABEL_SUMMARY}; border: none; background: transparent;")
        self.lbl_badge = QLabel("Chờ lệnh")
        self.lbl_badge.setStyleSheet(f"background: {Theme.BG_INPUT}; color: {Theme.TEXT_MUTED}; font-size: 11px; "
                                     f"padding: 2px 8px; border-radius: 4px; font-weight: bold; border: none;")
        status_row.addWidget(lbl_st)
        status_row.addStretch()
        status_row.addWidget(self.lbl_badge)
        sm_lay.addLayout(status_row)
        
        right_layout.addWidget(summary_panel)

        # NÚT XÁC NHẬN KẾT NỐI API XUẤT KHO
        self.btn_submit = QPushButton("Xác nhận xuất kho")
        self.btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_submit.setStyleSheet(f"""
            QPushButton {{ 
                background: transparent; 
                border: 1px solid {Theme.BORDER_HOVER}; 
                color: {Theme.TEXT_MAIN}; 
                padding: 10px; 
                border-radius: 6px; 
                font-weight: bold; 
                font-size: 13px; 
            }}
            QPushButton:hover {{ 
                background: {Theme.BG_INPUT}; 
                border-color: {Theme.TEXT_BLUE_ACCENT}; 
            }}
        """)
        
        # SỰ KIỆN: Ủy quyền thực thi cho Controller
        self.btn_submit.clicked.connect(self.controller.handle_confirm_stock_out)
        
        right_layout.addWidget(self.btn_submit)
        right_layout.addStretch()

        body_layout.addWidget(right_box, 1)
        layout.addLayout(body_layout)