from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFrame, QStackedWidget, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from app.services.api_client import InventoryAPIClient

class StockOutScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Đảm bảo kế thừa api_client từ cửa sổ chính MainWindow
        self.api_client = getattr(parent, 'api_client', InventoryAPIClient())
        
        # Quản lý trạng thái lật trang bằng QStackedWidget
        self.stack = QStackedWidget(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)
        
        # Khởi tạo phân hệ giao diện Form
        self.init_form_view()
        
        # Đưa vào ngăn xếp (Bây giờ chỉ chứa form_widget, bảng lịch sử đã gộp ra ngoài)
        self.stack.addWidget(self.form_widget)
        self.stack.setCurrentWidget(self.form_widget)

    def init_form_view(self):
        """Màn hình 1: Form xuất kho phân bổ tự động (Tích hợp API)"""
        self.form_widget = QWidget()
        layout = QVBoxLayout(self.form_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Style sheet đồng bộ nước màu nền tối và input border
        self.form_widget.setStyleSheet("""
            QLabel { color: #8899b4; font-size: 12px; }
            QLineEdit, QComboBox {
                background: #161b26;
                border: 1px solid #2a3347;
                border-radius: 6px;
                color: #e2e8f0;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #378ADD;
            }
            QComboBox::drop-down { border: none; padding-right: 10px; }
        """)

        # --- HEADER BAR ---
        header = QHBoxLayout()
        title_lay = QVBoxLayout()
        title = QLabel("Xuất kho")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e2e8f0;")
        subtitle = QLabel("Tự động phân bổ FIFO / LIFO · Rollback khi không đủ hàng")
        subtitle.setStyleSheet("font-size: 11px; color: #8899b4;")
        title_lay.addWidget(title)
        title_lay.addWidget(subtitle)
        
        # Đã mở lại biến lớp self.history_btn để thanh menu bên ngoài liên kết điều hướng
        self.history_btn = QPushButton("🕒 Lịch sử xuất")
        self.history_btn.setStyleSheet("""
            QPushButton { background: #161b26; border: 1px solid #2a3347; color: #e2e8f0; 
                          padding: 8px 14px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #1e2740; border-color: #3a4560; }
        """)
        
        header.addLayout(title_lay)
        header.addStretch()
        header.addWidget(self.history_btn)
        layout.addLayout(header)

        # --- BODY CONTENT (Chia cột Trái - Phải) ---
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        # --- CỘT TRÁI: THÔNG TIN ĐƠN XUẤT ---
        left_box = QFrame()
        left_box.setStyleSheet("QFrame { background: #0f131a; border: 1px solid #1e2530; border-radius: 8px; }")
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)

        lbl_left_title = QLabel("📥  Thông tin đơn xuất")
        lbl_left_title.setStyleSheet("color: #5b9cf6; font-weight: bold; font-size: 13px; border: none;")
        left_layout.addWidget(lbl_left_title)

        left_layout.addWidget(QLabel("Mã đơn hàng"))
        self.txt_order_id = QLineEdit("ORD-7830")
        left_layout.addWidget(self.txt_order_id)

        # MẸO: Thay vì nhập tên sản phẩm, chúng ta sẽ coi đây là ô truyền Mã vạch / Barcode sang Backend
        left_layout.addWidget(QLabel("Mã vạch sản phẩm (Barcode)"))
        self.txt_product = QLineEdit("Mã vạch sản phẩm...") 
        left_layout.addWidget(self.txt_product)

        left_layout.addWidget(QLabel("Số lượng yêu cầu"))
        self.txt_qty = QLineEdit("200")  # Để mặc định số để người dùng dễ thao tác hoặc tự sửa
        left_layout.addWidget(self.txt_qty)

        left_layout.addWidget(QLabel("Phương thức"))
        self.cbo_method = QComboBox()
        self.cbo_method.addItems(["FIFO — tự động (khuyến nghị)", "LIFO — tự động", "Chỉ định thủ công"])
        left_layout.addWidget(self.cbo_method)
        left_layout.addStretch()

        body_layout.addWidget(left_box, 1)

        # --- CỘT PHẢI: PHÂN BỔ TỰ ĐỘNG & TÓM TẮT ---
        right_box = QFrame()
        right_box.setStyleSheet("QFrame { background: #0f131a; border: 1px solid #1e2530; border-radius: 8px; }")
        right_layout = QVBoxLayout(right_box)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        lbl_right_title = QLabel("Phân bổ tự động")
        lbl_right_title.setStyleSheet("color: #e2e8f0; font-weight: bold; font-size: 13px; border: none;")
        lbl_right_sub = QLabel("Hệ thống chọn lô theo quy tắc")
        lbl_right_sub.setStyleSheet("color: #4a5a78; font-size: 11px; border: none; margin-bottom: 4px;")
        right_layout.addWidget(lbl_right_title)
        right_layout.addWidget(lbl_right_sub)

        # Khung lô 1: Được chọn (Màu xanh lá)
        batch_active = QFrame()
        batch_active.setStyleSheet("QFrame { background: #06261a; border: 1px solid #0f4d34; border-radius: 6px; }")
        ba_lay = QVBoxLayout(batch_active)
        ba_lay.setContentsMargins(12, 10, 12, 10)
        ba_lay.setSpacing(6)
        
        self.lbl_ba_title = QLabel("Lô hệ thống đề xuất")
        self.lbl_ba_title.setStyleSheet("color: #2ecc71; font-weight: bold; border: none;")
        self.lbl_ba_info = QLabel("Thông tin phân bổ lũy tiến sẽ hiển thị tại đây")
        self.lbl_ba_info.setStyleSheet("color: #8899b4; font-size: 11px; border: none;")
        
        # Tiến trình phân bổ (Thanh Progress Bar xanh)
        progress_layout = QHBoxLayout()
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        self.bar.setStyleSheet("QProgressBar { background: #161b26; border: none; border-radius: 3px; }"
                               "QProgressBar::chunk { background: #1dd1a1; border-radius: 3px; }")
        self.lbl_progress_num = QLabel("0/0")
        self.lbl_progress_num.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 11px; border: none;")
        progress_layout.addWidget(self.bar)
        progress_layout.addWidget(self.lbl_progress_num)

        ba_lay.addWidget(self.lbl_ba_title)
        ba_lay.addWidget(self.lbl_ba_info)
        ba_lay.addLayout(progress_layout)
        right_layout.addWidget(batch_active)

        # Khung lô 2: Dự phòng (Màu xám tối mờ)
        batch_backup = QFrame()
        batch_backup.setStyleSheet("QFrame { background: #141923; border: 1px solid #222b3c; border-radius: 6px; }")
        bb_lay = QVBoxLayout(batch_backup)
        bb_lay.setContentsMargins(12, 10, 12, 10)
        bb_lay.setSpacing(2)
        lbl_bb_title = QLabel("Lô dự phòng hệ thống")
        lbl_bb_title.setStyleSheet("color: #4a5a78; font-weight: bold; border: none;")
        lbl_bb_info = QLabel("Tồn kho gối đầu — Chờ sử dụng")
        lbl_bb_info.setStyleSheet("color: #3b475e; font-size: 11px; border: none;")
        bb_lay.addWidget(lbl_bb_title)
        bb_lay.addWidget(lbl_bb_info)
        right_layout.addWidget(batch_backup)

        # Bảng tóm tắt gọn thông số xuất kho
        summary_panel = QFrame()
        summary_panel.setStyleSheet("QFrame { background: #11151f; border-radius: 6px; border: none; }")
        sm_lay = QVBoxLayout(summary_panel)
        sm_lay.setContentsMargins(12, 10, 12, 10)
        sm_lay.setSpacing(6)
        
        def make_summary_row(label, val, val_color="#e2e8f0"):
            row = QHBoxLayout()
            lbl = QLabel(label); lbl.setStyleSheet("color: #6c7a9c; border: none;")
            v = QLabel(val); v.setStyleSheet(f"color: {val_color}; font-weight: bold; border: none;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(v)
            return row

        sm_lay.addLayout(make_summary_row("Nghiệp vụ", "Xuất kho tự động"))
        
        # Dòng trạng thái có badge màu xanh lá nền lồng
        status_row = QHBoxLayout()
        lbl_st = QLabel("Trạng thái"); lbl_st.setStyleSheet("color: #6c7a9c;")
        self.lbl_badge = QLabel("Chờ lệnh")
        self.lbl_badge.setStyleSheet("background: #161b26; color: #8899b4; font-size: 11px; "
                               "padding: 2px 8px; border-radius: 4px; font-weight: bold;")
        status_row.addWidget(lbl_st)
        status_row.addStretch()
        status_row.addWidget(self.lbl_badge)
        sm_lay.addLayout(status_row)
        
        right_layout.addWidget(summary_panel)

        # NÚT XÁC NHẬN KẾT NỐI API XUẤT KHO
        self.btn_submit = QPushButton("Xác nhận xuất kho")
        self.btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_submit.setStyleSheet("""
            QPushButton { background: transparent; border: 1px solid #3a4560; color: #e2e8f0; 
                          padding: 10px; border-radius: 6px; font-weight: bold; font-size: 13px; }
            QPushButton:hover { background: #161b26; border-color: #5b9cf6; }
        """)
        # Kết nối sự kiện Click nút bấm xử lý xuất
        self.btn_submit.clicked.connect(self.on_click_confirm_stock_out)
        right_layout.addWidget(self.btn_submit)
        right_layout.addStretch()

        body_layout.addWidget(right_box, 1)
        layout.addLayout(body_layout)

    # --- LOGIC XỬ LÝ SỰ KIỆN VÀ GỌI API XUẤT KHO ---

    def on_click_confirm_stock_out(self):
        """Bóc tách dữ liệu từ các ô nhập liệu UI và gọi API stock_out sang FastAPI"""
        try:
            # 1. Thu thập dữ liệu từ giao diện Frontend
            order_id = self.txt_order_id.text().strip()
            barcode = self.txt_product.text().strip()      # Lấy mã vạch từ ô sản phẩm
            qty_raw = self.txt_qty.text().strip()
            
            # Tách lọc chuỗi phòng trường hợp người dùng nhập chữ (Ví dụ: "200 gói" -> "200")
            qty_clean = "".join([char for char in qty_raw if char.isdigit()])

            # 2. Kiểm tra tính hợp lệ của dữ liệu (Validation)
            if not barcode or "..." in barcode:
                raise ValueError("Vui lòng nhập Mã vạch (Barcode) sản phẩm cần xuất kho.")
            if not qty_clean or int(qty_clean) <= 0:
                raise ValueError("Số lượng yêu cầu xuất kho phải là một số nguyên dương lớn hơn 0.")
            
            quantity = int(qty_clean)

            # 3. GỌI API POST ĐẾN BACKEND FASTAPI (/api/inventory/stock-out)
            result = self.api_client.stock_out(barcode=barcode, quantity=quantity)
            
            # 4. XỬ LÝ KẾT QUẢ KHI BACKEND TRẢ VỀ THÀNH CÔNG (HTTP 200)
            message = result.get("message", "Xuất kho thành công.")
            details = result.get("details", []) # Danh sách các lô bị trừ hàng lũy tiến
            
            # Hiển thị Dialog thông báo thành công cho người dùng
            QMessageBox.information(self, "Thành Công", f"Đơn hàng {order_id} xử lý thành công!\n\n{message}")
            
            # 5. CẬP NHẬT TRỰC QUAN GIAO DIỆN THEO THÔNG TIN LÔ BỊ TRỪ GẦN NHẤT
            self.lbl_badge.setText("Đã xuất")
            self.lbl_badge.setStyleSheet("background: #06261a; color: #2ecc71; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold;")
            
            if details:
                # Lấy thông tin lô hàng đầu tiên trong danh sách phân bổ để hiển thị mẫu lên Progress Bar
                first_batch = details[0]
                batch_id = first_batch.get("batch_id", "N/A")
                qty_deducted = first_batch.get("quantity_deducted", quantity)
                
                self.lbl_ba_title.setText(f"Lô {batch_id} (Đã trừ kho)")
                self.lbl_ba_info.setText(f"Mã đơn: {order_id} · Trừ lũy tiến thành công: {qty_deducted}")
                
                # Cấu hình lại thanh tiến trình Progress Bar
                self.bar.setRange(0, quantity)
                self.bar.setValue(qty_deducted)
                self.lbl_progress_num.setText(f"{qty_deducted}/{quantity}")
            
        except ValueError as e:
            # Lỗi nghiệp vụ (Dữ liệu rỗng hoặc Backend báo thiếu hàng, không tìm thấy sản phẩm)
            self.lbl_badge.setText("Thất bại")
            self.lbl_badge.setStyleSheet("background: #2a1414; color: #e74c3c; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold;")
            QMessageBox.warning(self, "Lỗi Nghiệp Vụ", str(e))
            
        except ConnectionError as e:
            # Lỗi mất kết nối mạng lên server
            QMessageBox.critical(self, "Lỗi Kết Nối", str(e))
            
        except Exception as e:
            # Lỗi hệ thống phát sinh khác
            QMessageBox.critical(self, "Lỗi Hệ Thống", f"Đã xảy ra sự cố không xác định:\n{str(e)}")