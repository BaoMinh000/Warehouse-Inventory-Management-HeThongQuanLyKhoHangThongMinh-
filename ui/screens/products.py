# ui/screens/products_screen.py
# File Frontend UI, định nghĩa màn hình quản lý danh mục sản phẩm, có nhiệm vụ gọi API Client để lấy dữ liệu từ Server Backend và hiển thị lên bảng, cũng như gửi yêu cầu tạo mới sản phẩm xuống Server khi người dùng nhập liệu và bấm nút lưu
from PyQt6.QtWidgets import (
    QMessageBox, QTableWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFrame, QStackedWidget, QTextEdit
)
from PyQt6.QtCore import Qt, QSize
from ui.components.data_table import DataTable

class ProductsScreen(QWidget):
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        self.api_client = api_client
        self.products_catalog = []  # Khởi tạo mảng rỗng ban đầu

        # Quản lý trạng thái chuyển đổi màn hình
        self.stack = QStackedWidget(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)
        
        # Khởi tạo 2 view giao diện
        self.init_list_view()
        self.init_add_form_view()
        
        # Thêm vào stack (Mặc định hiển thị danh sách trước)
        self.stack.addWidget(self.list_widget)
        self.stack.addWidget(self.add_widget)
        self.stack.setCurrentWidget(self.list_widget)

        # Tiến hành nạp dữ liệu từ API lên bảng lần đầu tiên
        self.load_products_from_api()

    def load_products_from_api(self):
        """Hàm UI: Gọi API Client để lấy danh mục sản phẩm từ Server Backend và cập nhật lên bảng hiển thị"""
        try:
            # Gọi hàm thông qua lớp logic api_client để lấy danh mục từ Backend Server
            self.products_catalog = self.api_client.get_catalog()
            
            # Đổ dữ liệu mới nhất vừa quét từ Server vào bảng hiển thị
            self.table.load_data(self.products_catalog, status=True, action=True)
            print(f"[UI] Đã tải và làm mới thành công {len(self.products_catalog)} sản phẩm trên bảng.")
            print(f"[UI] Dữ liệu sản phẩm mẫu: {self.products_catalog[:2]}")  # In ra 2 sản phẩm đầu tiên để kiểm tra định dạng dữ liệu
            return self.products_catalog
        except ConnectionError as e:
            QMessageBox.critical(self, "Lỗi kết nối", str(e))
            return []
        except Exception as e:
            QMessageBox.critical(self, "Lỗi không xác định", f"Đã có lỗi xảy ra: {str(e)}")
            return []

    def init_list_view(self):
        """Màn hình con 1: Bảng danh sách sản phẩm (Mặc định gốc)"""
        self.list_widget = QWidget()
        layout = QVBoxLayout(self.list_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header bar
        header = QHBoxLayout()
        title_lay = QVBoxLayout()
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        title = QLabel("Danh mục sản phẩm")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e2e8f0;")

        self.btn_refresh = QPushButton("↻")
        self.btn_refresh.setFixedSize(28, 28)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.load_products_from_api)

        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #2a3347;
                border-radius: 14px;
                color: #8899b4;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1a2233;
                border-color: #378ADD;
                color: #378ADD;
            }
            QPushButton:pressed {
                background: #111827;
            }
        """)

        title_row.addWidget(title)
        title_row.addWidget(self.btn_refresh)
        title_row.addStretch()

        subtitle = QLabel("Quản lý danh sách mã hàng, vị trí và định mức tồn kho")
        subtitle.setStyleSheet("font-size: 11px; color: #8899b4;")

        title_lay.addLayout(title_row)
        title_lay.addWidget(subtitle)
            
        add_btn = QPushButton("+ Thêm sản phẩm")
        add_btn.setObjectName("action_btn")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton#action_btn {
                background-color: transparent; color: white; 
                border: 1px solid #4c4e4f; border-radius:6px;
                padding:6px 12px; font-size: 14px; font-weight: bold;
            }
            QPushButton#action_btn:hover { background-color: rgba(76, 78, 79, 0.8); }
        """)
        # Kích hoạt lật trang khi bấm nút thêm
        add_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.add_widget))
        
        header.addLayout(title_lay)
        header.addStretch()
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Cấu hình DataTable
        columns = ["Sản phẩm", "Barcode", "Danh mục",  "Loại", "Trạng thái", "Thao tác"] #"Tồn kho", 
        filters = ["Tất cả", "Thực phẩm", "Hóa mỹ phẩm", "Đồ uống", "Vật tư"]
        
        self.table = DataTable(columns, filters, self)
        layout.addWidget(self.table)
        
        self.setStyleSheet("""
            QTableWidget { background: transparent; gridline-color: #2a3347; }
            QHeaderView::section {
                background: transparent; color: #4a5a78;
                font-size: 12px; font-weight: bold; border: none; padding: 4px;
            }
        """)

    def init_add_form_view(self):
        """Màn hình con 2: Form Thêm sản phẩm mới"""
        self.add_widget = QWidget()
        layout = QVBoxLayout(self.add_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Stylesheet đồng bộ Theme Tối cho form nhập liệu
        self.add_widget.setStyleSheet("""
            QLabel { color: #8899b4; font-size: 12px; }
            QLineEdit, QComboBox, QTextEdit {
                background: #161b26; border: 1px solid #2a3347; border-radius: 6px;
                color: #e2e8f0; padding: 8px 12px; font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border-color: #378ADD; }
            QComboBox::drop-down { border: none; padding-right: 10px; }
        """)

        # --- HEADER BAR ---
        header = QHBoxLayout()
        title_lay = QVBoxLayout()
        title = QLabel("Thêm sản phẩm mới")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e2e8f0;")
        subtitle = QLabel("Khai báo mã hàng, định mức lưu kho và chiến lược phân phối")
        subtitle.setStyleSheet("font-size: 11px; color: #8899b4;")
        title_lay.addWidget(title)
        title_lay.addWidget(subtitle)
        
        back_btn = QPushButton("← Quay lại danh sách")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton { background: #1a2e4a; border: 1px solid #2a4a6e; color: #5b9cf6; 
                          padding: 8px 14px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #24426b; }
        """)
        back_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.list_widget))
        
        header.addLayout(title_lay)
        header.addStretch()
        header.addWidget(back_btn)
        layout.addLayout(header)

        # --- BODY CONTENT ---
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        # CỘT TRÁI: THÔNG TIN CƠ BẢN CỦA SẢN PHẨM
        left_box = QFrame()
        left_box.setStyleSheet("QFrame { background: #0f131a; border: 1px solid #1e2530; border-radius: 8px; }")
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)

        lbl_left_title = QLabel("📝 Thông tin cơ bản")
        lbl_left_title.setStyleSheet("color: #5b9cf6; font-weight: bold; font-size: 13px; border: none;")
        left_layout.addWidget(lbl_left_title)

        left_layout.addWidget(QLabel("Tên sản phẩm"))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ví dụ: Sữa TH True Milk 1L...")
        left_layout.addWidget(self.input_name)

        left_layout.addWidget(QLabel("Mã vạch / Barcode"))
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("Nhập hoặc quét mã barcode sản phẩm...")
        left_layout.addWidget(self.input_barcode)

        # Layout hàng ngang cho Danh mục & Đơn vị tính
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

        body_layout.addWidget(left_box, 1)

        # CỘT PHẢI: THIẾT LẬP QUẢN TRỊ KHO
        right_box = QFrame()
        right_box.setStyleSheet("QFrame { background: #0f131a; border: 1px solid #1e2530; border-radius: 8px; }")
        right_layout = QVBoxLayout(right_box)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        lbl_right_title = QLabel("⚙ Cấu hình quản trị kho")
        lbl_right_title.setStyleSheet("color: #e2e8f0; font-weight: bold; font-size: 13px; border: none;")
        right_layout.addWidget(lbl_right_title)

        right_layout.addWidget(QLabel("Chiến lược luân chuyển hàng hóa"))
        self.cbo_strategy = QComboBox()
        self.cbo_strategy.addItems(["FIFO — Ưu tiên xuất hàng nhập trước", "LIFO — Ưu tiên xuất hàng nhập sau"])
        right_layout.addWidget(self.cbo_strategy)

        # Hàng ngang cấu hình định mức cảnh báo tồn kho
        row_limit = QHBoxLayout()
        col_min = QVBoxLayout(); col_min.addWidget(QLabel("Định mức tối thiểu (Min)")); self.input_min = QLineEdit("10"); col_min.addWidget(self.input_min); row_limit.addLayout(col_min, 1)
        col_max = QVBoxLayout(); col_max.addWidget(QLabel("Định mức tối đa (Max)")); self.input_max = QLineEdit("5000"); col_max.addWidget(self.input_max); row_limit.addLayout(col_max, 1)
        right_layout.addLayout(row_limit)

        right_layout.addWidget(QLabel("Vị trí lưu trữ mặc định (Kệ/Dãy)"))
        self.input_loc = QLineEdit()
        self.input_loc.setPlaceholderText("Ví dụ: Khu A, Kệ A-01-02...")
        right_layout.addWidget(self.input_loc)

        note_panel = QFrame()
        note_panel.setStyleSheet("QFrame { background: #11151f; border-radius: 6px; border: none; }")
        np_lay = QVBoxLayout(note_panel)
        np_lay.setContentsMargins(12, 10, 12, 10)
        np_lay.setSpacing(4)
        
        lbl_np_t = QLabel("📌 Lưu ý hệ thống")
        lbl_np_t.setStyleSheet("color: #5b9cf6; font-weight: bold; border: none;")
        lbl_np_c = QLabel("Mã sản phẩm tự động sinh nếu để trống.\nChiến lược FIFO được áp dụng mặc định cho thực phẩm.")
        lbl_np_c.setStyleSheet("color: #6c7a9c; font-size: 11px; border: none; line-height: 14px;")
        np_lay.addWidget(lbl_np_t)
        np_lay.addWidget(lbl_np_c)
        right_layout.addWidget(note_panel)

        btn_save = QPushButton("Lưu sản phẩm mới")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton { background: #1dd1a1; border: none; color: #0f131a; 
                          padding: 10px; border-radius: 6px; font-weight: bold; font-size: 13px; }
            QPushButton:hover { background: #10ac84; }
        """)
        btn_save.clicked.connect(self._on_save_clicked)

        right_layout.addWidget(btn_save)
        right_layout.addStretch()
        body_layout.addWidget(right_box, 1)
        layout.addLayout(body_layout)
    
    def _on_save_clicked(self):
        """Hàm thu thập dữ liệu từ các ô Input và gửi yêu cầu tạo sản phẩm mới"""
        barcode = self.input_barcode.text().strip()
        name = self.input_name.text().strip()
        category = self.cbo_category.currentText()
        
        strategy_raw = self.cbo_strategy.currentText()
        strategy = "FIFO" if "FIFO" in strategy_raw else "LIFO"

        if not barcode or not name:
            QMessageBox.warning(
                self, "Dữ liệu không hợp lệ", "Vui lòng điền đầy đủ thông tin Tên sản phẩm và Mã vạch!"
            )
            return

        try:
            # 1. Gửi lệnh tạo sản phẩm xuống Server Backend thông qua API Client
            success = self.api_client.create_product(barcode, name, strategy, category)
            
            if success:
                QMessageBox.information(
                    self, "Thành công", f"Đã lưu sản phẩm '{name}' vào danh mục kho thành công."
                )
                
                # 2. Gọi hàm đồng bộ tải lại dữ liệu từ Server tới UI để làm mới bảng hiển thị
                self.load_products_from_api()
                
                # Làm sạch form nhập liệu
                self.input_barcode.clear()
                self.input_name.clear()
                self.input_desc.clear()
                self.input_loc.clear()
                
                # Lật trang quay về màn hình danh sách chính
                if hasattr(self, 'stack') and hasattr(self, 'list_widget'):
                    self.stack.setCurrentWidget(self.list_widget)
                    
        except ValueError as e:
            QMessageBox.critical(self, "Lỗi Nghiệp Vụ", str(e))
        except ConnectionError as e:
            QMessageBox.critical(self, "Lỗi Kết Nối", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Hệ Thống", f"Đã xảy ra sự cố: {str(e)}")