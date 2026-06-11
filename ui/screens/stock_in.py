from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QFrame, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from app.services.api_client import InventoryAPIClient

class StockInScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Đảm bảo giữ lại api_client truyền từ MainWindow xuống nếu có, hoặc tạo mới
        self.api_client = getattr(parent, 'api_client', InventoryAPIClient())
        
        self.stack = QStackedWidget(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)
        
        # Khởi tạo màn hình con
        self.init_form_view()
        
        # Thêm vào stack (Bây giờ chỉ quản lý form_widget, lịch sử đã gộp ra ngoài)
        self.stack.addWidget(self.form_widget)
        self.stack.setCurrentWidget(self.form_widget)

    def init_form_view(self):
        """Màn hình 1: Form Nhập kho theo chuẩn ảnh Mockup"""
        self.form_widget = QWidget()
        layout = QVBoxLayout(self.form_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        self.form_widget.setStyleSheet("""
            QLabel { color: #8899b4; font-size: 12px; }
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                background: #161b26;
                border: 1px solid #2a3347;
                border-radius: 6px;
                color: #e2e8f0;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border-color: #378ADD;
            }
            QComboBox::drop-down { border: none; padding-right: 10px; }
        """)

        # --- HEADER BAR ---
        header = QHBoxLayout()
        title_lay = QVBoxLayout()
        title = QLabel("Nhập kho")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e2e8f0;")
        subtitle = QLabel("Tạo lô nhập mới · FIFO / LIFO tự động")
        subtitle.setStyleSheet("font-size: 11px; color: #8899b4;")
        title_lay.addWidget(title)
        title_lay.addWidget(subtitle)
        
        # Tạo biến lớp để WarehouseManagerScreen có thể tìm thấy nút và bind sự kiện mở lịch sử tổng hợp
        # self.history_btn = QPushButton("🕒 Lịch sử nhập")
        # self.history_btn.setStyleSheet("""
        #     QPushButton { background: #161b26; border: 1px solid #2a3347; color: #e2e8f0; 
        #                   padding: 8px 14px; border-radius: 6px; font-weight: bold; }
        #     QPushButton:hover { background: #1e2740; border-color: #3a4560; }
        # """)
        
        header.addLayout(title_lay)
        header.addStretch()
        # header.addWidget(self.history_btn)
        layout.addLayout(header)

        # --- BOX THÔNG TIN LÔ HÀNG ---
        info_box = QFrame()
        info_box.setStyleSheet("QFrame { background: #0f131a; border: 1px solid #1e2530; border-radius: 8px; }")
        box_layout = QVBoxLayout(info_box)
        box_layout.setContentsMargins(16, 16, 16, 16)
        box_layout.setSpacing(12)

        group_title = QLabel("📦  Thông tin lô hàng")
        group_title.setStyleSheet("color: #5b9cf6; font-weight: bold; font-size: 13px; border: none;")
        box_layout.addWidget(group_title)

        # Hàng 1: Mã sản phẩm & Tên sản phẩm
        row1 = QHBoxLayout()
        col1_1 = QVBoxLayout()
        col1_1.addWidget(QLabel("Mã sản phẩm / Barcode"))
        self.txt_barcode = QLineEdit()
        self.txt_barcode.setPlaceholderText("📷 Quét hoặc nhập barcode...")
        # Khi người dùng nhập xong mã vạch và nhấn Enter, tự động tra cứu tên sản phẩm từ hệ thống
        self.txt_barcode.returnPressed.connect(self.on_barcode_scanned)
        col1_1.addWidget(self.txt_barcode)
        row1.addLayout(col1_1, 1)
        
        col1_2 = QVBoxLayout()
        col1_2.addWidget(QLabel("Tên sản phẩm"))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Tự động điền sau khi quét...")
        col1_2.addWidget(self.txt_name)
        row1.addLayout(col1_2, 1)
        box_layout.addLayout(row1)

        # Hàng 2: Số lượng nhập & Đơn vị
        row2 = QHBoxLayout()
        col2_1 = QVBoxLayout()
        col2_1.addWidget(QLabel("Số lượng nhập"))
        self.txt_qty = QLineEdit("240")
        col2_1.addWidget(self.txt_qty)
        row2.addLayout(col2_1, 1)
        
        col2_2 = QVBoxLayout()
        col2_2.addWidget(QLabel("Đơn vị"))
        self.cbo_unit = QComboBox()
        self.cbo_unit.addItems(["Thùng", "Chai", "Hộp", "Can", "Túi"])
        col2_2.addWidget(self.cbo_unit)
        row2.addLayout(col2_2, 1)
        box_layout.addLayout(row2)

        # Hàng 3: Ngày nhận & Ngày hết hạn
        row3 = QHBoxLayout()
        col3_1 = QVBoxLayout()
        col3_1.addWidget(QLabel("Ngày nhận"))
        self.dt_receive = QDateEdit(QDate.currentDate())
        self.dt_receive.setCalendarPopup(True)
        col3_1.addWidget(self.dt_receive)
        row3.addLayout(col3_1, 1)
        
        col3_2 = QVBoxLayout()
        col3_2.addWidget(QLabel("Ngày hết hạn"))
        self.dt_expiry = QDateEdit(QDate.currentDate().addMonths(6))
        self.dt_expiry.setCalendarPopup(True)
        col3_2.addWidget(self.dt_expiry)
        row3.addLayout(col3_2, 1)
        box_layout.addLayout(row3)

        # Hàng 4: Phương thức xuất kho & Vị trí kệ
        row4 = QHBoxLayout()
        col4_1 = QVBoxLayout()
        col4_1.addWidget(QLabel("Phương thức xuất kho"))
        self.cbo_strategy = QComboBox()
        self.cbo_strategy.addItems(["FIFO — First In First Out", "LIFO — Last In First Out"])
        col4_1.addWidget(self.cbo_strategy)
        row4.addLayout(col4_1, 1)
        
        col4_2 = QVBoxLayout()
        col4_2.addWidget(QLabel("Vị trí kệ"))
        self.txt_location = QLineEdit("A-03-02")
        col4_2.addWidget(self.txt_location)
        row4.addLayout(col4_2, 1)
        box_layout.addLayout(row4)

        # Hàng 5: Ghi chú
        col_note = QVBoxLayout()
        col_note.addWidget(QLabel("Ghi chú lô hàng"))
        self.txt_note = QTextEdit()
        self.txt_note.setPlaceholderText("Ghi chú tùy chọn...")
        self.txt_note.setMaximumHeight(60)
        col_note.addWidget(self.txt_note)
        box_layout.addLayout(col_note)

        layout.addWidget(info_box)

        # --- SECTION XÁC NHẬN LÔ NHẬP (Thanh Màu Xanh Lá Bên Dưới) ---
        confirm_box = QFrame()
        confirm_box.setStyleSheet("QFrame { background: #0f131a; border: 1px solid #1e2530; border-radius: 8px; }")
        conf_layout = QVBoxLayout(confirm_box)
        conf_layout.setContentsMargins(16, 16, 16, 16)
        
        conf_title = QLabel("✓  Xác nhận lô nhập")
        conf_title.setStyleSheet("color: #2ec4b6; font-weight: bold; font-size: 13px; border: none; margin-bottom: 4px;")
        conf_layout.addWidget(conf_title)

        alert_banner = QFrame()
        alert_banner.setStyleSheet("QFrame { background: #06261a; border: 1px solid #0f4d34; border-radius: 6px; }")
        alert_layout = QHBoxLayout(alert_banner)
        alert_layout.setContentsMargins(16, 12, 16, 12)

        info_text_layout = QVBoxLayout()
        self.lbl_batch_title = QLabel("Lô mới — Chờ kiểm tra thông tin")
        self.lbl_batch_title.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 14px; border:none;")
        self.lbl_batch_sub = QLabel("Vui lòng nhập đầy đủ các thông tin của sản phẩm ở phía trên")
        self.lbl_batch_sub.setStyleSheet("color: #a3b8cc; font-size: 11px; border:none;")
        info_text_layout.addWidget(self.lbl_batch_title)
        info_text_layout.addWidget(self.lbl_batch_sub)
        
        btn_submit = QPushButton("Xác nhận nhập kho")
        btn_submit.setStyleSheet("""
            QPushButton { background: #1dd1a1; border: none; color: #0f131a; padding: 10px 20px; 
                          border-radius: 6px; font-weight: bold; font-size: 13px;}
            QPushButton:hover { background: #10ac84; }
        """)
        btn_submit.clicked.connect(self.on_click_confirm_stock_in)
        
        alert_layout.addLayout(info_text_layout)
        alert_layout.addStretch()
        alert_layout.addWidget(btn_submit)
        
        conf_layout.addWidget(alert_banner)
        layout.addWidget(confirm_box)
        layout.addStretch()

    # --- LOGIC XỬ LÝ SỰ KIỆN VÀ THU THẬP THAM SỐ API ---

    def on_barcode_scanned(self):
        """Tự động gọi API tìm kiếm sản phẩm khi quét hoặc gõ xong Barcode"""
        barcode = self.txt_barcode.text().strip()
        if not barcode:
            return
        try:
            # Giả định Backend hỗ trợ API search_product qua Client
            if hasattr(self.api_client, 'search_product'): # Nếu API Client đã map endpoint này, gọi trực tiếp
                prod_data = self.api_client.search_product(barcode)
            else:
                # Nếu client chưa map endpoint này, gọi tạm bằng requests/fallback hoặc bỏ qua
                print("API Client chưa hỗ trợ search_product, bỏ qua bước tự động điền tên sản phẩm.")
                return

            if prod_data:
                self.txt_name.setText(prod_data.get('product_name', ''))
                # Đồng bộ hiển thị xuống khung thông báo xanh bên dưới để người dùng kiểm chứng
                self.lbl_batch_title.setText(f"Lô mới — {prod_data.get('product_name')}")
                strategy_info = "FIFO" if "FIFO" in prod_data.get('strategy_type', 'FIFO') else "LIFO"
                self.lbl_batch_sub.setText(f"Sẵn sàng nạp kho theo chiến lược: {strategy_info}")
        except Exception:
            self.txt_name.setText("")
            self.lbl_batch_title.setText("Sản phẩm mới")
            self.lbl_batch_sub.setText("Mã vạch lạ, hệ thống sẽ tự động tạo mới danh mục khi xác nhận.")

    def on_click_confirm_stock_in(self):
        """Thu thập đầy đủ toàn bộ tham số từ UI để đẩy qua API Client"""
        try:
            # 1. Lấy dữ liệu thô và ép kiểu an toàn
            barcode = self.txt_barcode.text().strip()
            product_name = self.txt_name.text().strip()
            qty_text = self.txt_qty.text().strip()
            unit = self.cbo_unit.currentText()
            location = self.txt_location.text().strip()
            note = self.txt_note.toPlainText().strip()
            
            # Chuẩn hóa ngày hết hạn sang định dạng chuỗi "YYYY-MM-DD" chuẩn ISO theo Backend nhận
            expiry_date_str = self.dt_expiry.date().toString("yyyy-MM-dd")
            
            # Tách chuỗi lấy giá trị "FIFO" hoặc "LIFO" tinh khiết từ combobox
            strategy_raw = self.cbo_strategy.currentText()
            strategy = "FIFO" if "FIFO" in strategy_raw else "LIFO"

            # 2. Validate dữ liệu đầu vào phía client tránh gửi payload rác
            if not barcode:
                raise ValueError("Mã vạch / Barcode không được để trống.")
            if not product_name:
                raise ValueError("Tên sản phẩm không được để trống.")
            if not qty_text.isdigit() or int(qty_text) <= 0:
                raise ValueError("Số lượng nhập kho phải là số nguyên dương lớn hơn 0.")
                
            quantity = int(qty_text)

            # # 3. Tự động kiểm tra / tạo danh mục sản phẩm trước nếu chưa tồn tại
            # # (Phòng trường hợp quét sản phẩm hoàn toàn mới chưa có trong cây BST)
            # try:
            #     self.api_client.create_product(
            #         barcode=barcode, 
            #         name=product_name, 
            #         strategy=strategy, 
            #         category="Thực phẩm"
            #     )
            # except ValueError:
            #     # Nếu sản phẩm đã tồn tại từ trước, API tạo danh mục sẽ báo lỗi trùng. 
            #     # Chúng ta bỏ qua bước này để tiếp tục ghi nhận phiếu nhập kho lô hàng.
            #     pass

            # 4. Gửi tín hiệu xử lý Nhập Kho sang Server Backend FastAPI
            result = self.api_client.stock_in(
                barcode=barcode,
                quantity=quantity,
                expiry_date=expiry_date_str
            )
            
            # 5. Hiển thị thông báo kết quả trả về từ server lên màn hình dạng Dialog
            batch_id = result.get("batch_id", "Không rõ")
            msg = f"Nhập kho thành công!\n- Mã lô phát sinh: {batch_id}\n- Vị trí lưu trữ: Kệ {location}"
            QMessageBox.information(self, "Thành công", msg)
            
            # Cập nhật thông tin hiển thị lên nhãn trạng thái trực quan
            self.lbl_batch_title.setText(f"Lô {batch_id} — {product_name}")
            self.lbl_batch_sub.setText(f"{quantity} {unit} · Lưu tại kệ: {location} · Hạn: {self.dt_expiry.date().toString('dd/MM/yyyy')}")
            
        except ValueError as e:
            QMessageBox.warning(self, "Lỗi Nghiệp Vụ", str(e))
        except ConnectionError as e:
            QMessageBox.critical(self, "Lỗi Kết Nối", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Hệ Thống", f"Đã xảy ra sự cố ngoài ý muốn:\n{str(e)}")

    def show_error_dialog(self, message: str):
        """Hàm helper bổ trợ hiển thị hộp thoại cảnh báo lỗi"""
        QMessageBox.warning(self, "Cảnh báo", message)