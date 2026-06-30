import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFrame, QStackedWidget, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from ui.utils.theme import Theme 

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

    def update_allocation_progress(self, allocated_batches: list, qty_deducted: int, total_qty: int, explanation: str):
        """
        Cập nhật thông tin bảng phân bổ lô hàng động và hiển thị tiến trình tổng quát.
        :param allocated_batches: List các dict/tuple chứa thông tin lô, ví dụ: 
                                  [{"id": "LOT-004", "date": "25-06-2026", "stock": "50", "qty_out": "50 (Hết hàng)", "is_depleted": True}]
        """
        # 1. Cập nhật thanh tiến trình tổng quan
        self.bar.setRange(0, total_qty)
        self.bar.setValue(qty_deducted)
        self.lbl_progress_num.setText(f"{qty_deducted}/{total_qty}")
        
        # 2. Làm mới và nạp lại dữ liệu cho bảng phân bổ
        self.tbl_allocation.setRowCount(0)
        self.tbl_allocation.setRowCount(len(allocated_batches))
        
        for row_idx, batch in enumerate(allocated_batches):
            self.tbl_allocation.setItem(row_idx, 0, QTableWidgetItem(str(batch.get('id'))))
            self.tbl_allocation.setItem(row_idx, 1, QTableWidgetItem(str(batch.get('date'))))
            self.tbl_allocation.setItem(row_idx, 2, QTableWidgetItem(str(batch.get('stock'))))
            
            # Cột số lượng xuất thực tế
            qty_item = QTableWidgetItem(str(batch.get('qty_out')))
            # Nếu hết hàng thì tô màu cảnh báo nhẹ, nếu còn dư hoặc bình thường thì tô màu xanh
            if batch.get('is_depleted', False):
                qty_item.setForeground(Qt.GlobalColor.red)
            else:
                qty_item.setForeground(Qt.GlobalColor.green)
            self.tbl_allocation.setItem(row_idx, 3, qty_item)
            
        # 3. Cập nhật chuỗi văn bản giải trình thuật toán gối lô
        self.lbl_algo_explanation.setText(f"💡 Giải trình: {explanation}")

    def init_left_form(self) -> QFrame:
        """--- CỘT TRÁI: THÔNG TIN ĐƠN XUẤT ---"""
        left_box = QFrame()
        left_box.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_DARK}; border: 1px solid {Theme.BORDER_PANEL_DARK}; border-radius: 8px; }}")
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)

        lbl_left_title = QLabel("📥   Thông tin đơn xuất")
        lbl_left_title.setStyleSheet(f"color: {Theme.TEXT_BLUE_ACCENT}; font-weight: bold; font-size: 13px; border: none; background: transparent;")
        left_layout.addWidget(lbl_left_title)

        left_layout.addWidget(QLabel("Mã đơn hàng"))
        self.txt_order_id = QLineEdit("55c65694-65cc-43d2-b92e-9ae7311571ed")
        left_layout.addWidget(self.txt_order_id)

        left_layout.addWidget(QLabel("Mã vạch sản phẩm (Barcode)"))
        self.txt_product = QLineEdit("0021200534521") 
        left_layout.addWidget(self.txt_product)

        left_layout.addWidget(QLabel("Số lượng yêu cầu"))
        self.txt_qty = QLineEdit("100") 
        left_layout.addWidget(self.txt_qty)

        left_layout.addWidget(QLabel("Phương thức"))
        self.cbo_method = QComboBox()
        self.cbo_method.addItems(["FIFO — tự động (khuyến nghị)", "LIFO — tự động", "Chỉ định thủ công"])
        left_layout.addWidget(self.cbo_method)
        
        # NÚT KIỂM TRA THÔNG TIN (MỚI THÊM)
        self.btn_check_allocation = QPushButton("🔍 Kiểm tra phân bổ")
        self.btn_check_allocation.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_allocation.setStyleSheet(f"""
            QPushButton {{ 
                background: {Theme.BG_INPUT}; 
                border: 1px solid {Theme.COLOR_PRIMARY}; 
                color: {Theme.COLOR_PRIMARY}; 
                padding: 10px; 
                border-radius: 6px; 
                font-weight: bold; 
                font-size: 13px; 
            }}
            QPushButton:hover {{ 
                background: {Theme.COLOR_PRIMARY}; 
                color: {Theme.TEXT_MAIN}; 
            }}
        """)
        # Kết nối sự kiện click tới hàm xử lý trong Controller
        self.btn_check_allocation.clicked.connect(self.controller.handle_check_allocation)
        left_layout.addWidget(self.btn_check_allocation)
        
        left_layout.addStretch()
        return left_box

    def init_right_allocation(self) -> QFrame:
        """--- CỘT PHẢI: BẢNG PHÂN BỔ TỰ ĐỘNG LÔ HÀNG & TÓM TẮT ---"""
        right_box = QFrame()
        right_box.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_DARK}; border: 1px solid {Theme.BORDER_PANEL_DARK}; border-radius: 8px; }}")
        right_layout = QVBoxLayout(right_box)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        # Tiêu đề & tiêu đề phụ của bảng phân bổ
        lbl_right_title = QLabel("📊   Bảng phân bổ lô hàng dự kiến")
        lbl_right_title.setStyleSheet(f"color: {Theme.TEXT_MAIN}; font-weight: bold; font-size: 13px; border: none; background: transparent;")
        lbl_right_sub = QLabel("Hệ thống tự động tính toán gối lô theo thuật toán")
        lbl_right_sub.setStyleSheet(f"color: {Theme.TEXT_SUB}; font-size: 11px; border: none; background: transparent; margin-bottom: 2px;")
        right_layout.addWidget(lbl_right_title)
        right_layout.addWidget(lbl_right_sub)

        # Thanh tổng tiến trình gom hàng kết hợp số liệu lũy tiến
        progress_container = QFrame()
        progress_container.setStyleSheet(f"QFrame {{ background: {Theme.BG_INPUT}; border-radius: 6px; border: 1px solid {Theme.BORDER_INPUT}; }}")
        prog_lay = QVBoxLayout(progress_container)
        prog_lay.setContentsMargins(12, 8, 12, 8)
        
        prog_header = QHBoxLayout()
        lbl_prog_title = QLabel("Tổng tiến trình phân bổ:")
        lbl_prog_title.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.lbl_progress_num = QLabel("0/0")
        self.lbl_progress_num.setStyleSheet(f"color: {Theme.TEXT_BLUE_ACCENT}; font-weight: bold; font-size: 12px;")
        prog_header.addWidget(lbl_prog_title)
        prog_header.addStretch()
        prog_header.addWidget(self.lbl_progress_num)
        
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)
        self.bar.setStyleSheet(f"QProgressBar {{ background: {Theme.BG_PANEL_DARK}; border: none; border-radius: 4px; }}"
                               f"QProgressBar::chunk {{ background: {Theme.TEXT_BLUE_ACCENT}; border-radius: 4px; }}")
        
        prog_lay.addLayout(prog_header)
        prog_lay.addWidget(self.bar)
        right_layout.addWidget(progress_container)

        # Bảng lưới chi tiết QTableWidget hiển thị trạng thái phân bổ
        self.tbl_allocation = QTableWidget()
        self.tbl_allocation.setColumnCount(4)
        self.tbl_allocation.setHorizontalHeaderLabels(["Mã Lô", "Ngày Nhập", "Tồn Lô", "Xuất Thực Tế"])
        self.tbl_allocation.verticalHeader().setVisible(False)
        self.tbl_allocation.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tbl_allocation.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_allocation.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)        
        self.tbl_allocation.setStyleSheet(f"""
            QTableWidget {{
                background: {Theme.BG_INPUT};
                border: 1px solid {Theme.BORDER_INPUT};
                border-radius: 6px;
                gridline-color: {Theme.BORDER_PANEL_DARK};
                color: {Theme.TEXT_MAIN};
                font-size: 12px;
            }}
            QHeaderView::section {{
                background: {Theme.BG_PANEL_DARK};
                color: {Theme.TEXT_SUB};
                padding: 6px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid {Theme.BORDER_INPUT};
            }}
        """)
        
        # Nạp dữ liệu mô phỏng ban đầu theo đúng thiết kế đã chốt để xem trước layout
        mock_data = []
        self.tbl_allocation.setRowCount(len(mock_data))
        for row_idx, (lot, date, stock, allocation) in enumerate(mock_data):
            self.tbl_allocation.setItem(row_idx, 0, QTableWidgetItem(lot))
            self.tbl_allocation.setItem(row_idx, 1, QTableWidgetItem(date))
            self.tbl_allocation.setItem(row_idx, 2, QTableWidgetItem(stock))
            
            alloc_item = QTableWidgetItem(allocation)
            alloc_item.setForeground(Qt.GlobalColor.red if "Hết hàng" in allocation else Qt.GlobalColor.green)
            self.tbl_allocation.setItem(row_idx, 3, alloc_item)
            
        right_layout.addWidget(self.tbl_allocation)

        # Khung văn bản hiển thị nhật ký giải trình thuật toán gối lô
        self.lbl_algo_explanation = QLabel("💡 Giải trình: Hệ thống đã lấy hết 50 sp từ LOT-004 và tự động gối tiếp sang 50 sp từ LOT-003.")
        self.lbl_algo_explanation.setWordWrap(True)
        self.lbl_algo_explanation.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 11px; font-style: italic; border: none; background: transparent;")
        right_layout.addWidget(self.lbl_algo_explanation)

        # Panel tóm tắt nghiệp vụ & trạng thái
        summary_panel = QFrame()
        summary_panel.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_SUMMARY}; border-radius: 6px; border: none; }}")
        sm_lay = QVBoxLayout(summary_panel)
        sm_lay.setContentsMargins(12, 10, 12, 10)
        sm_lay.setSpacing(6)
        
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
        self.btn_submit.clicked.connect(self.controller.handle_confirm_stock_out)
        right_layout.addWidget(self.btn_submit)
        
        return right_box

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

        # --- BODY CONTENT (Gộp cột Trái và cột Phải) ---
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        # Gọi tách biệt 2 hàm UI để lắp ráp bố cục
        left_box = self.init_left_form()
        right_box = self.init_right_allocation()

        body_layout.addWidget(left_box, 1)
        body_layout.addWidget(right_box, 1)
        
        layout.addLayout(body_layout)
