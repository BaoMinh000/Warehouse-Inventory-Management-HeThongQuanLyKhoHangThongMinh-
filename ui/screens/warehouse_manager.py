# ui/screens/warehouse_manager.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QFrame
from PyQt6.QtCore import Qt
from ui.screens.stock_in import StockInScreen
from ui.screens.stock_out import StockOutScreen
from ui.components.history_view import HistoryView

class WarehouseManagerScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout chính của toàn bộ trang (Dạng dọc)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # 1. KHỞI TẠO THANH ĐIỀU HƯỚNG (NAVIGATION BAR) Ở TRÊN CÙNG
        self.nav_bar = QFrame()
        self.nav_bar.setStyleSheet("""
            QFrame { background: #0f131a; border: 1px solid #1e2530; border-radius: 8px; }
            QPushButton { 
                background: transparent; border: none; color: #8899b4; 
                padding: 10px 20px; font-size: 13px; font-weight: bold; border-radius: 6px;
            }
            QPushButton:hover { background: #161b26; color: #e2e8f0; }
        """)
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(10)
        
        # Tạo 2 nút chuyển đổi nghiệp vụ ở bên trái
        self.btn_nav_in = QPushButton("📥  Nhập kho")
        self.btn_nav_out = QPushButton("📤  Xuất kho")
        
        # Thiết lập hiệu ứng sáng nút khi đang active (Mặc định ở trang Nhập)
        self.set_nav_button_active(self.btn_nav_in, True)
        
        # Kết nối sự kiện click nút menu nghiệp vụ
        self.btn_nav_in.clicked.connect(self.switch_to_stock_in)
        self.btn_nav_out.clicked.connect(self.switch_to_stock_out)
        
        nav_layout.addWidget(self.btn_nav_in)
        nav_layout.addWidget(self.btn_nav_out)
        
        # LƯU Ý: Thêm khoảng trống stretch để đẩy nút tiếp theo về góc phải thanh tab
        nav_layout.addStretch() 
        
        # NÚT LỊCH SỬ TỔNG HỢP (Đặt ở góc phải thanh Tab)
        self.btn_nav_history = QPushButton("🕒  Lịch sử tổng hợp")
        self.btn_nav_history.setStyleSheet("""
            QPushButton { background: #161b26; border: 1px solid #2a3347; color: #e2e8f0; 
                          padding: 8px 14px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #1e2740; border-color: #3a4560; }
        """)
        # Kết nối nút lịch sử này với hàm xử lý Bật/Tắt (Toggle)
        self.btn_nav_history.clicked.connect(self.toggle_history_view)
        nav_layout.addWidget(self.btn_nav_history)
        
        # Thêm thanh menu điều hướng vào giao diện tổng
        main_layout.addWidget(self.nav_bar)
        
        # 2. KHỞI TẠO STACKED WIDGET QUẢN LÝ CÁC PHÂN HỆ
        self.stack = QStackedWidget(self)
        main_layout.addWidget(self.stack, 1)
        
        # Khởi tạo các màn hình đơn lẻ
        self.stock_in_screen = StockInScreen(self)
        self.stock_out_screen = StockOutScreen(self)
        
        self.form_stock_in = self.stock_in_screen.form_widget
        self.form_stock_out = self.stock_out_screen.form_widget
        
        # Khởi tạo Lịch sử gộp chung
        self.init_global_history_view()
        
        # Đưa các Form và Lịch sử vào trong Stack
        self.stack.addWidget(self.form_stock_in)
        self.stack.addWidget(self.form_stock_out)
        self.stack.addWidget(self.history_widget)
        
        # 3. ĐIỀU HƯỚNG NÚT LỊCH SỬ TỪ CÁC FORM LẺ VỀ ĐÂY (NẾU CÓ)
        self.bind_history_buttons()
        
        # Lưu vết form mặc định ban đầu là form nhập kho
        self.previous_form = self.form_stock_in
        self.stack.setCurrentWidget(self.form_stock_in)

    def bind_history_buttons(self):
        """Bắt sự kiện từ nút lịch sử phụ bên trong các form lẻ nếu có bấm vào"""
        if hasattr(self.stock_in_screen, 'history_btn'):
            try: self.stock_in_screen.history_btn.clicked.disconnect()
            except TypeError: pass
            self.stock_in_screen.history_btn.clicked.connect(self.show_history_view)
            
        if hasattr(self.stock_out_screen, 'history_btn'):
            try: self.stock_out_screen.history_btn.clicked.disconnect()
            except TypeError: pass
            self.stock_out_screen.history_btn.clicked.connect(self.show_history_view)

    def init_global_history_view(self):
        columns = ["Sản phẩm / Đối tác", "Mã chứng từ", "Nghiệp vụ", "Số lượng", "Chiến lược", "Trạng thái", "Thao tác"]
        filters = ["Tất cả", "Nhập kho", "Xuất kho"]
        
        global_sample_data = [
            {"product_name": "Sữa TH True Milk 1L (TH Group)", "barcode": "#B2406-01", "category": "Nhập kho", "stock": "240 Thùng", "strategy_type": ("FIFO", "fifo"), "status": ("Đã hoàn thành", "success")},
            {"product_name": "Đại lý WinMart+ Quận 1", "barcode": "#ORD-7821", "category": "Xuất kho", "stock": "5 mặt hàng", "strategy_type": ("FIFO tự động", "info"), "status": ("Đã xuất", "success")},
            {"product_name": "Nước khoáng Lavie 500ml", "barcode": "#B2406-02", "category": "Nhập kho", "stock": "1,500 Chai", "strategy_type": ("FIFO", "fifo"), "status": ("Đã hoàn thành", "success")},
            {"product_name": "Kho bán sỉ Bình Dương", "barcode": "#ORD-7822", "category": "Xuất kho", "stock": "12 mặt hàng", "strategy_type": ("FIFO tự động", "info"), "status": ("Đang lấy hàng", "warning")},
            {"product_name": "Bột giặt Ariel 5kg (P&G)", "barcode": "#B2405-99", "category": "Nhập kho", "stock": "100 Túi", "strategy_type": ("LIFO", "lifo"), "status": ("Chờ xếp kho", "normal")},
            {"product_name": "Cửa hàng Co.op Food Q3", "barcode": "#ORD-7823", "category": "Xuất kho", "stock": "2 mặt hàng", "strategy_type": ("Lập lịch", "normal"), "status": ("Chờ xử lý", "normal")}
        ]
        
        # Truyền chính hàm go_back_to_previous_form vào nút Back của HistoryView
        self.history_widget = HistoryView(
            title="🔄 Nhật ký Kho tổng hợp",
            subtitle="Xem toàn bộ lịch sử biến động · Bộ lọc Nhập / Xuất thông minh",
            back_btn_text="← Quay lại Form xử lý",
            columns=columns,
            filters=filters,
            sample_data=global_sample_data,
            on_back_clicked=self.go_back_to_previous_form,
            parent=self
        )

    # --- HÀM TOGGLE (BẬT/TẮT) LỊCH SỬ BẰNG NÚT TAB PHẢI ---
    def toggle_history_view(self):
        """Nếu đang ở lịch sử thì đóng (quay lại form cũ), ngược lại thì mở lịch sử"""
        if self.stack.currentWidget() == self.history_widget:
            self.go_back_to_previous_form()
        else:
            self.show_history_view()

    def switch_to_stock_in(self):
        self.set_nav_button_active(self.btn_nav_in, True)
        self.set_nav_button_active(self.btn_nav_out, False)
        self.btn_nav_history.setStyleSheet("background: #161b26; border: 1px solid #2a3347; color: #e2e8f0; padding: 8px 14px; border-radius: 6px; font-weight: bold;")
        self.stack.setCurrentWidget(self.form_stock_in)
        self.previous_form = self.form_stock_in # Ghi nhận form hiện tại

    def switch_to_stock_out(self):
        self.set_nav_button_active(self.btn_nav_in, False)
        self.set_nav_button_active(self.btn_nav_out, True)
        self.btn_nav_history.setStyleSheet("background: #161b26; border: 1px solid #2a3347; color: #e2e8f0; padding: 8px 14px; border-radius: 6px; font-weight: bold;")
        self.stack.setCurrentWidget(self.form_stock_out)
        self.previous_form = self.form_stock_out # Ghi nhận form hiện tại

    def show_history_view(self):
        """Mở màn hình lịch sử và highlight nút Lịch sử tổng hợp"""
        self.previous_form = self.stack.currentWidget() # Lưu lại form trước khi mở lịch sử
        
        # Trả trạng thái màu 2 nút tab nghiệp vụ về bình thường
        self.set_nav_button_active(self.btn_nav_in, False)
        self.set_nav_button_active(self.btn_nav_out, False)
        
        # Làm sáng nút lịch sử lên (Màu xanh dương giống nút back)
        self.btn_nav_history.setStyleSheet("background: #1a2e4a; color: #5b9cf6; border: 1px solid #2a4a6e; padding: 8px 14px; border-radius: 6px; font-weight: bold;")
        self.stack.setCurrentWidget(self.history_widget)

    def go_back_to_previous_form(self):
        """Đóng màn hình lịch sử, quay lại form cũ và khôi phục màu sắc tab menu"""
        if hasattr(self, 'previous_form') and self.previous_form == self.form_stock_out:
            self.switch_to_stock_out()
        else:
            self.switch_to_stock_in()

    def set_nav_button_active(self, button: QPushButton, active: bool):
        if active:
            button.setStyleSheet("background: #1a2e4a; color: #5b9cf6; border: 1px solid #2a4a6e; padding: 10px 20px; font-size: 13px; font-weight: bold; border-radius: 6px;")
        else:
            button.setStyleSheet("background: transparent; color: #8899b4; border: none; padding: 10px 20px; font-size: 13px; font-weight: bold; border-radius: 6px;")