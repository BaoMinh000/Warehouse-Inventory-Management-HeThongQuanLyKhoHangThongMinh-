import os
import sys
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QFormLayout, QSpinBox, QComboBox, QDateEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import QDate, Qt

# BASE_URL = "http://127.0.0.1:8000/api/inventory"
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/inventory")
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📦 Warehouse Inventory Management System (PyQt6)")
        self.resize(900, 600)
        
        # Widget trung tâm và Khởi tạo các Tabs
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Khởi tạo các tab thành phần
        self.init_tab_overview()
        self.init_tab_stock_in()
        self.init_tab_stock_out()
        self.init_tab_expiry()

    # -------------------------------------------------------------------------
    # TAB 1: TỔNG QUAN & TÌM KIẾM (Ứng dụng cây BST để tìm kiếm nhanh O(log n))
    # -------------------------------------------------------------------------
    def init_tab_overview(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Vùng Tìm kiếm
        search_layout = QHBoxLayout()
        self.txt_search_barcode = QLineEdit()
        self.txt_search_barcode.setPlaceholderText("Nhập mã Barcode cần tìm kiếm nhanh (O(log n))...")
        btn_search = QPushButton("🔍 Tìm kiếm RAM")
        btn_search.clicked.connect(self.search_product)
        
        search_layout.addWidget(self.txt_search_barcode)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)

        # Nút thêm sản phẩm (ban đầu là "Thêm")
        self.btn_add_toggle = QPushButton("➕ Thêm sản phẩm")
        self.btn_add_toggle.clicked.connect(self.toggle_add_product_form)
        layout.addWidget(self.btn_add_toggle)

        # Form nhập sản phẩm (ẩn mặc định)
        self.add_form = QWidget()
        form_layout = QHBoxLayout(self.add_form)

        self.add_barcode = QLineEdit()
        self.add_barcode.setPlaceholderText("Barcode")
        self.add_name = QLineEdit()
        self.add_name.setPlaceholderText("Tên sản phẩm")
        self.add_strategy = QComboBox()
        self.add_strategy.addItems(["FIFO", "LIFO"])

        form_layout.addWidget(self.add_barcode)
        form_layout.addWidget(self.add_name)
        form_layout.addWidget(self.add_strategy)

        self.add_form.setVisible(False)  # ẩn form ban đầu
        layout.addWidget(self.add_form)
        
        # Nút Tải lại danh sách
        btn_refresh = QPushButton("🔄 Tải lại Danh mục Sản phẩm (In-order Traversal)")
        btn_refresh.clicked.connect(self.load_all_products)
        layout.addWidget(btn_refresh)
        
        # Bảng sản phẩm
        self.table_products = QTableWidget()
        self.table_products.setColumnCount(3)
        self.table_products.setHorizontalHeaderLabels(["Mã Barcode", "Tên Sản phẩm", "Cơ chế xuất kho"])
        self.table_products.horizontalHeader().setStretchLastSection(True)
        self.table_products.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_products)

        self.tabs.addTab(tab, "📊 Tổng quan & Tìm kiếm")

    def toggle_add_product_form(self):
        if not self.add_form.isVisible():
            # Hiện form nhập và đổi nút thành "Lưu"
            self.add_form.setVisible(True)
            self.btn_add_toggle.setText("💾 Lưu sản phẩm")
        else:
            # Khi bấm "Lưu": gọi API thêm sản phẩm
            self.submit_add_product()
            # Reset form: khóa lại và clear input
            self.add_barcode.clear()
            self.add_name.clear()
            self.add_form.setVisible(False)
            self.btn_add_toggle.setText("➕ Thêm sản phẩm")

    def submit_add_product(self):
        if not self.add_barcode.text() or not self.add_name.text():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        payload = {
            "barcode": self.add_barcode.text().strip(),
            "product_name": self.add_name.text().strip(),
            "strategy_type": self.add_strategy.currentText()
        }

        try:
            res = requests.post(f"{BASE_URL}/products", json=payload)
            if res.status_code in [200, 201]:
                QMessageBox.information(self, "Thành công", f"Đã thêm sản phẩm {payload['product_name']}!")
                self.load_all_products()  # refresh bảng
            else:
                QMessageBox.critical(self, "Thất bại", f"Lỗi từ server: {res.text}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi kết nối", str(e))

    def search_product(self):
        barcode = self.txt_search_barcode.text().strip()
        if not barcode:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã Barcode cần tìm!")
            return
        try:
            res = requests.get(f"{BASE_URL}/product/{barcode}")
            if res.status_code == 200:
                prod = res.json()
                QMessageBox.information(self, "Kết quả tìm kiếm trên RAM", f"Tìm thấy sản phẩm:\n- Tên: {prod.get('product_name')}\n- Barcode: {prod.get('barcode')}")
            else:
                QMessageBox.critical(self, "Lỗi", "Không tìm thấy sản phẩm này trên hệ thống cây BST!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi kết nối", f"Không thể kết nối tới Backend: {str(e)}")

    def load_all_products(self):
        try:
            res = requests.get(f"{BASE_URL}/products")
            if res.status_code == 200:
                data = res.json()  # Nhận về đối tượng Dict chứa 'total_products' và 'catalog'
                
                # Bóc tách mảng danh sách sản phẩm từ khóa 'catalog'
                # Nếu không tìm thấy hoặc lỗi, mặc định trả về mảng rỗng [] để tránh crash
                products = data.get("catalog", [])
                
                # Xóa dữ liệu cũ trên bảng để chuẩn bị nạp dữ liệu mới
                self.table_products.setRowCount(0)
                
                # Duyệt qua từng sản phẩm trong mảng 'catalog' để đổ vào bảng
                for row_idx, prod in enumerate(products):
                    self.table_products.insertRow(row_idx)
                    
                    # 1. Lấy và nạp Barcode (Sử dụng đúng từ khóa "barcode")
                    barcode_val = str(prod.get("barcode", ""))
                    self.table_products.setItem(row_idx, 0, QTableWidgetItem(barcode_val))
                    
                    # 2. Lấy và nạp Tên sản phẩm (Sử dụng đúng từ khóa "product_name")
                    name_val = str(prod.get("product_name", ""))
                    self.table_products.setItem(row_idx, 1, name_item := QTableWidgetItem(name_val))
                    
                    # (Tùy chọn) Nếu bảng của bạn có thêm cột thứ 3 hiển thị Cơ chế xuất kho:
                    strategy_val = str(prod.get("strategy_type", ""))
                    self.table_products.setItem(row_idx, 2, QTableWidgetItem(strategy_val))
            else:
                QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách sản phẩm. Mã lỗi: {res.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi kết nối", f"Không thể kết nối tới Backend: {str(e)}")
    
    # -------------------------------------------------------------------------
    # TAB 2: NHẬP KHO (Stock-In) - Lưu SQLite & Cập nhật cây BST
    # -------------------------------------------------------------------------
    def init_tab_stock_in(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.in_barcode = QLineEdit()
        self.in_name = QLineEdit()
        self.in_batch_id = QLineEdit()
        
        self.in_qty = QSpinBox()
        self.in_qty.setMinimum(1)
        self.in_qty.setMaximum(999999)
        
        self.in_expiry = QDateEdit()
        self.in_expiry.setCalendarPopup(True)
        self.in_expiry.setDate(QDate.currentDate().addDays(30))
        
        self.in_strategy = QComboBox()
        self.in_strategy.addItems(["FIFO", "LIFO"])
        
        btn_submit = QPushButton("📥 Xác nhận Nhập kho")
        btn_submit.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 5px;")
        btn_submit.clicked.connect(self.submit_stock_in)
        
        layout.addRow("Mã Barcode *:", self.in_barcode)
        layout.addRow("Tên sản phẩm *:", self.in_name)
        layout.addRow("Mã lô hàng (Batch ID) *:", self.in_batch_id)
        layout.addRow("Số lượng nhập *:", self.in_qty)
        layout.addRow("Ngày hết hạn *:", self.in_expiry)
        layout.addRow("Cơ chế xuất kho áp dụng:", self.in_strategy)
        layout.addRow("", btn_submit)
        
        self.tabs.addTab(tab, "📥 Nhập kho (Stock-In)")

    def submit_stock_in(self):
        if not self.in_barcode.text() or not self.in_name.text() or not self.in_batch_id.text():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ thông tin bắt buộc!")
            return
            
        payload = {
            "barcode": self.in_barcode.text().strip(),
            "name": self.in_name.text().strip(),
            "batch_id": self.in_batch_id.text().strip(),
            "quantity": self.in_qty.value(),
            "expiry_date": self.in_expiry.date().toString("yyyy-MM-dd"),
            "strategy": self.in_strategy.currentText()
        }
        
        try:
            res = requests.post(f"{BASE_URL}/stock-in", json=payload)
            if res.status_code in [200, 201]:
                QMessageBox.information(self, "Thành công", f"Đã nhập kho thành công lô hàng {payload['batch_id']}. Dữ liệu SQLite và RAM đã được đồng bộ!")
                # Reset Form
                self.in_barcode.clear()
                self.in_name.clear()
                self.in_batch_id.clear()
                self.in_qty.setValue(1)
            else:
                QMessageBox.critical(self, "Thất bại", f"Lỗi từ server: {res.text}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi kết nối", str(e))

    # -------------------------------------------------------------------------
    # TAB 3: XUẤT KHO (Stock-Out) - Tự động bốc hàng theo Queue/Stack
    # -------------------------------------------------------------------------
    def init_tab_stock_out(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.out_barcode = QLineEdit()
        self.out_qty = QSpinBox()
        self.out_qty.setMinimum(1)
        self.out_qty.setMaximum(999999)
        
        btn_submit = QPushButton("📤 Xác nhận Xuất kho Tự động")
        btn_submit.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; padding: 5px;")
        btn_submit.clicked.connect(self.submit_stock_out)
        
        self.out_log = QTextEdit()
        self.out_log.setReadOnly(True)
        
        layout.addRow("Nhập mã Barcode:", self.out_barcode)
        layout.addRow("Số lượng cần xuất:", self.out_qty)
        layout.addRow("", btn_submit)
        layout.addRow("Nhật ký bốc hàng:", self.out_log)
        
        self.tabs.addTab(tab, "📤 Xuất kho (Stock-Out)")

    def submit_stock_out(self):
        if not self.out_barcode.text():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã Barcode!")
            return
            
        payload = {
            "barcode": self.out_barcode.text().strip(),
            "quantity": self.out_qty.value()
        }
        try:
            res = requests.post(f"{BASE_URL}/stock-out", json=payload)
            if res.status_code == 200:
                QMessageBox.information(self, "Thành công", "Xuất kho hoàn tất!")
                self.out_log.setText(str(res.json()))
                self.out_barcode.clear()
                self.out_qty.setValue(1)
            else:
                detail = res.json().get('detail', 'Không đủ hàng hoặc sai mã')
                QMessageBox.critical(self, "Thất bại", f"Lỗi xuất kho: {detail}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi kết nối", str(e))

    # -------------------------------------------------------------------------
    # TAB 4: CẢNH BÁO HẾT HẠN
    # -------------------------------------------------------------------------
    def init_tab_expiry(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("Ngưỡng cảnh báo cận date (ngày):"))
        self.spin_threshold = QSpinBox()
        self.spin_threshold.setValue(30)
        self.spin_threshold.setRange(1, 180)
        config_layout.addWidget(self.spin_threshold)
        
        btn_scan = QPushButton("⏰ Chạy quét kiểm tra Cận hạn / Hết hạn")
        btn_scan.clicked.connect(self.scan_expiry)
        config_layout.addWidget(btn_scan)
        layout.addLayout(config_layout)
        
        self.txt_expiry_result = QTextEdit()
        self.txt_expiry_result.setReadOnly(True)
        layout.addWidget(self.txt_expiry_result)
        
        self.tabs.addTab(tab, "⏰ Cảnh báo Hết hạn")

    def scan_expiry(self):
        try:
            res = requests.get(f"{BASE_URL}/expiry-warning?threshold={self.spin_threshold.value()}")
            if res.status_code == 200:
                warnings = res.json()
                if not warnings:
                    self.txt_expiry_result.setText("🍏 Tuyệt vời! Không phát hiện lô hàng nào sắp hết hạn trong ngưỡng cấu hình.")
                else:
                    self.txt_expiry_result.setText(f"⚠️ Phát hiện {len(warnings)} lô hàng cần xử lý:\n\n" + str(warnings))
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể lấy dữ liệu cảnh báo.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi kết nối", str(e))


