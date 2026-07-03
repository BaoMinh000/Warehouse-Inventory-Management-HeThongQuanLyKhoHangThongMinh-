import os
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFrame, QStackedWidget, QTextEdit
)
from PyQt6.QtCore import Qt
from ui.components.datatable.table_logic import DataTable
from ui.components.item_form.item_form_dialog import ItemFormDialog
from ui.utils.theme import Theme 
# Import lớp điều phối nghiệp vụ vừa tách
from ui.controllers.products_controller import ProductsController


class ProductsScreen(QWidget):
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        
        # Khởi tạo Controller điều phối hành vi
        self.controller = ProductsController(self, api_client)
        self.api_client = api_client
        # Quản lý trạng thái chuyển đổi màn hình dạng Stack
        self.stack = QStackedWidget(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)
        
        # Khởi tạo 2 View con
        self.init_list_view()
        self.init_add_form_view()
        
        self.stack.addWidget(self.list_widget)
        self.stack.addWidget(self.add_widget)
        self.switch_to_list_view()

        # Ủy quyền cho controller nạp dữ liệu lần đầu
        self.controller.handle_load_products()

    # =========================================================
    # CÁC HÀM XỬ LÝ SỰ KIỆN & ĐIỀU HƯỚNG
    # =========================================================

    def switch_to_list_view(self):
        """Chuyển đổi giao diện về màn hình danh sách chính."""
        if hasattr(self, 'stack') and hasattr(self, 'list_widget'):
            self.stack.setCurrentWidget(self.list_widget)

    def switch_to_add_view(self):
        """Chuyển đổi giao diện sang Form thêm sản phẩm."""
        if hasattr(self, 'stack') and hasattr(self, 'add_widget'):
            self.stack.setCurrentWidget(self.add_widget)

    def clear_form_inputs(self):
        """Dọn dẹp sạch dữ liệu cũ trong các ô Form nhập liệu."""
        self.input_barcode.clear()
        self.input_name.clear()
        self.input_desc.clear()
        self.input_loc.clear()

    def handle_table_action(self, action_type: str, index: int):
        """Xử lý khi người dùng bấm nút view/edit trên DataTable"""
        try:
            row_data = self.table._all_data[index]
        except IndexError:
            return

        dialog = ItemFormDialog(data=row_data, mode=action_type, api_client=self.api_client, parent=self)
        result = dialog.exec()
        
        if action_type == "edit" and result == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_updated_data()
            # self.controller.handle_update_product(index, updated_data)

    # =========================================================
    # GIAO DIỆN 1: MÀN HÌNH DANH SÁCH (LIST VIEW)
    # =========================================================

    def init_list_view(self):
        """Khởi tạo container cho màn hình danh sách sản phẩm"""
        self.list_widget = QWidget()
        layout = QVBoxLayout(self.list_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Lắp ráp các thành phần Header và Bảng dữ liệu
        layout.addLayout(self._build_list_header())
        layout.addWidget(self._build_list_table())

        # Style áp dụng chung cho Table nằm trong màn hình này
        self.setStyleSheet(f"""
            QTableWidget {{ background: transparent; gridline-color: {Theme.BORDER_SIDEBAR}; }}
            QHeaderView::section {{
                background: transparent; color: {Theme.TEXT_SUB};
                font-size: 12px; font-weight: bold; border: none; padding: 4px;
            }}
        """)

    def _build_list_header(self) -> QHBoxLayout:
        """Xây dựng thanh công cụ Header của danh sách"""
        header = QHBoxLayout()
        title_lay = QVBoxLayout()
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        # Tiêu đề
        title = QLabel("Danh mục sản phẩm")
        title.setStyleSheet(f"background: transparent; font-size: 16px; font-weight: bold; color: {Theme.TEXT_MAIN};")

        # Nút Refresh
        self.btn_refresh = QPushButton("↻")
        self.btn_refresh.setFixedSize(28, 28)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.controller.handle_load_products)
        self.btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {Theme.BORDER_SIDEBAR};
                border-radius: 14px;
                color: {Theme.TEXT_MUTED};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {Theme.BG_NAV_HOVER if hasattr(Theme, 'BG_NAV_HOVER') else Theme.BG_BTN_HOVER};
                border-color: {Theme.COLOR_PRIMARY};
                color: {Theme.COLOR_PRIMARY};
            }}
            QPushButton:pressed {{ background: {Theme.BG_PANEL_DARK}; }}
        """)

        title_row.addWidget(title)
        title_row.addWidget(self.btn_refresh)
        title_row.addStretch()

        # Phụ đề
        subtitle = QLabel("Quản lý danh sách mã hàng, vị trí và định mức tồn kho")
        subtitle.setStyleSheet(f"background: transparent; font-size: 11px; color: {Theme.TEXT_MUTED};")

        title_lay.addLayout(title_row)
        title_lay.addWidget(subtitle)
            
        # Nút thêm mới
        add_btn = QPushButton("+ Thêm sản phẩm")
        add_btn.setObjectName("action_btn")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton#action_btn {{
                background-color: transparent; color: {Theme.TEXT_MAIN}; 
                border: 1px solid {Theme.BORDER_NEUTRAL}; border-radius:6px;
                padding:6px 12px; font-size: 14px; font-weight: bold;
            }}
            QPushButton#action_btn:hover {{ background-color: {Theme.BG_BTN_HOVER}; }}
        """)
        add_btn.clicked.connect(self.switch_to_add_view)
        
        header.addLayout(title_lay)
        header.addStretch()
        header.addWidget(add_btn)
        
        return header

    def _build_list_table(self) -> DataTable:
        """Khởi tạo và cấu hình DataTable"""
        columns = ["Sản phẩm", "Barcode", "Danh mục",  "Loại", "Thao tác"]
        filters = ["Tất cả", "Thực phẩm", "Hóa mỹ phẩm", "Đồ uống", "Vật tư"]
        
        self.table = DataTable(columns, filters, self) 
        self.table.action_clicked.connect(self.handle_table_action)
        return self.table

    # =========================================================
    # GIAO DIỆN 2: MÀN HÌNH FORM THÊM MỚI (ADD FORM VIEW)
    # =========================================================

    def init_add_form_view(self):
        """Khởi tạo container cho Form thêm sản phẩm"""
        self.add_widget = QWidget()
        layout = QVBoxLayout(self.add_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Style mặc định cho các input trong Form
        self.add_widget.setStyleSheet(f"""
            QLabel {{ color: {Theme.TEXT_MUTED}; font-size: 12px; background: transparent; }}
            QLineEdit, QComboBox, QTextEdit {{
                background: {Theme.BG_INPUT}; border: 1px solid {Theme.BORDER_INPUT}; border-radius: 6px;
                color: {Theme.TEXT_MAIN}; padding: 8px 12px; font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{ border-color: {Theme.COLOR_PRIMARY}; }}
            QComboBox::drop-down {{ border: none; padding-right: 10px; }}
        """)

        # Lắp ráp Header và Body của Form
        layout.addLayout(self._build_add_header())
        
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)
        body_layout.addWidget(self._build_add_left_panel(), 1)
        body_layout.addWidget(self._build_add_right_panel(), 1)
        
        layout.addLayout(body_layout)

    def _build_add_header(self) -> QHBoxLayout:
        """Xây dựng Header cho Form thêm mới"""
        header = QHBoxLayout()
        title_lay = QVBoxLayout()
        title = QLabel("Thêm sản phẩm mới")
        title.setStyleSheet(f"background: transparent; font-size: 18px; font-weight: bold; color: {Theme.TEXT_MAIN};")
        subtitle = QLabel("Khai báo mã hàng, định mức lưu kho và chiến lược phân phối")
        subtitle.setStyleSheet(f"background: transparent; font-size: 11px; color: {Theme.TEXT_MUTED};")
        title_lay.addWidget(title)
        title_lay.addWidget(subtitle)
        
        back_btn = QPushButton("← Quay lại danh sách")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: {Theme.BG_NAV_ACTIVE if hasattr(Theme, 'BG_NAV_ACTIVE') else Theme.BG_BTN_ACTIVE}; 
                border: 1px solid {Theme.BORDER_ACTIVE}; 
                color: {Theme.TEXT_BLUE_ACCENT}; 
                padding: 8px 14px; border-radius: 6px; font-weight: bold; 
            }}
            QPushButton:hover {{ background: {Theme.BORDER_HOVER}; }}
        """)
        back_btn.clicked.connect(self.switch_to_list_view)
        
        header.addLayout(title_lay)
        header.addStretch()
        header.addWidget(back_btn)
        
        return header

    def _build_add_left_panel(self) -> QFrame:
        """Xây dựng Cột Trái: Thông tin cơ bản"""
        left_box = QFrame()
        left_box.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_DARK}; border: 1px solid {Theme.BORDER_PANEL_DARK}; border-radius: 8px; }}")
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)

        lbl_left_title = QLabel("📝 Thông tin cơ bản")
        lbl_left_title.setStyleSheet(f"color: {Theme.TEXT_BLUE_ACCENT}; font-weight: bold; font-size: 13px; border: none; background: transparent;")
        left_layout.addWidget(lbl_left_title)

        left_layout.addWidget(QLabel("Tên sản phẩm"))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ví dụ: Sữa TH True Milk 1L...")
        left_layout.addWidget(self.input_name)

        left_layout.addWidget(QLabel("Mã vạch / Barcode"))
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("Nhập hoặc quét mã barcode sản phẩm...")
        left_layout.addWidget(self.input_barcode)

        row_cate = QHBoxLayout()
        col_cat = QVBoxLayout()
        col_cat.addWidget(QLabel("Danh mục"))
        self.cbo_category = QComboBox()
        self.cbo_category.addItems(["Thực phẩm", "Hóa mỹ phẩm", "Đồ uống", "Vật tư"])
        col_cat.addWidget(self.cbo_category)
        row_cate.addLayout(col_cat, 1)

        col_unit = QVBoxLayout()
        col_unit.addWidget(QLabel("Đơn vị tính"))
        self.cbo_unit = QComboBox()
        self.cbo_unit.addItems(["Thùng", "Chai", "Hộp", "Can", "Túi", "Cái"])
        col_unit.addWidget(self.cbo_unit)
        row_cate.addLayout(col_unit, 1)
        left_layout.addLayout(row_cate)

        left_layout.addWidget(QLabel("Mô tả chi tiết"))
        self.input_desc = QTextEdit()
        self.input_desc.setPlaceholderText("Nhập mô tả sản phẩm (không bắt buộc)...")
        self.input_desc.setMaximumHeight(80)
        left_layout.addWidget(self.input_desc)
        left_layout.addStretch()

        return left_box

    def _build_add_right_panel(self) -> QFrame:
        """Xây dựng Cột Phải: Cấu hình quản trị kho"""
        right_box = QFrame()
        right_box.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_DARK}; border: 1px solid {Theme.BORDER_PANEL_DARK}; border-radius: 8px; }}")
        right_layout = QVBoxLayout(right_box)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        lbl_right_title = QLabel("⚙ Cấu hình quản trị kho")
        lbl_right_title.setStyleSheet(f"color: {Theme.TEXT_MAIN}; font-weight: bold; font-size: 13px; border: none; background: transparent;")
        right_layout.addWidget(lbl_right_title)

        right_layout.addWidget(QLabel("Chiến lược luân chuyển hàng hóa"))
        self.cbo_strategy = QComboBox()
        self.cbo_strategy.addItems(["FIFO — Ưu tiên xuất hàng nhập trước", "LIFO — Ưu tiên xuất hàng nhập sau"])
        right_layout.addWidget(self.cbo_strategy)

        row_limit = QHBoxLayout()
        col_min = QVBoxLayout()
        col_min.addWidget(QLabel("Định mức tối thiểu (Min)"))
        self.input_min = QLineEdit("10")
        col_min.addWidget(self.input_min)
        row_limit.addLayout(col_min, 1)
        
        col_max = QVBoxLayout()
        col_max.addWidget(QLabel("Định mức tối đa (Max)"))
        self.input_max = QLineEdit("5000")
        col_max.addWidget(self.input_max)
        row_limit.addLayout(col_max, 1)
        right_layout.addLayout(row_limit)

        right_layout.addWidget(QLabel("Vị trí lưu trữ mặc định (Kệ/Dãy)"))
        self.input_loc = QLineEdit()
        self.input_loc.setPlaceholderText("Ví dụ: Khu A, Kệ A-01-02...")
        right_layout.addWidget(self.input_loc)

        # Panel ghi chú
        note_panel = QFrame()
        note_panel.setStyleSheet(f"QFrame {{ background: {Theme.BG_PANEL_SUMMARY}; border-radius: 6px; border: none; }}")
        np_lay = QVBoxLayout(note_panel)
        np_lay.setContentsMargins(12, 10, 12, 10)
        np_lay.setSpacing(4)
        
        lbl_np_t = QLabel("📌 Lưu ý hệ thống")
        lbl_np_t.setStyleSheet(f"color: {Theme.TEXT_BLUE_ACCENT}; font-weight: bold; border: none; background: transparent;")
        lbl_np_c = QLabel("Mã sản phẩm tự động sinh nếu để trống.\nChiến lược FIFO được áp dụng mặc định cho thực phẩm.")
        lbl_np_c.setStyleSheet(f"color: {Theme.TEXT_LABEL_SUMMARY}; font-size: 11px; border: none; line-height: 14px; background: transparent;")
        np_lay.addWidget(lbl_np_t)
        np_lay.addWidget(lbl_np_c)
        right_layout.addWidget(note_panel)

        # Nút Lưu
        btn_save = QPushButton("Lưu sản phẩm mới")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{ 
                background: {Theme.BTN_MINT_SUCCESS}; 
                border: none; 
                color: {Theme.BG_PANEL_DARK}; 
                padding: 10px; 
                border-radius: 6px; 
                font-weight: bold; 
                font-size: 13px; 
            }}
            QPushButton:hover {{ background: {Theme.BTN_MINT_HOVER}; }}
        """)
        btn_save.clicked.connect(self.controller.handle_save_product)

        right_layout.addWidget(btn_save)
        right_layout.addStretch()
        
        return right_box