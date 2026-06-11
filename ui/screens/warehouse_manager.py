# ui/screens/warehouse_manager.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QFrame
from PyQt6.QtCore import Qt
from ui.screens.stock_in import StockInScreen
from ui.screens.stock_out import StockOutScreen
from ui.components.history_view import HistoryView

class WarehouseManagerScreen(QWidget):
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        self.api_client = api_client

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
        self.btn_nav_in = QPushButton("📥   Nhập kho")
        self.btn_nav_out = QPushButton("📤   Xuất kho")
        
        # Kết nối sự kiện click nút menu nghiệp vụ
        self.btn_nav_in.clicked.connect(self.switch_to_stock_in)
        self.btn_nav_out.clicked.connect(self.switch_to_stock_out)
        
        nav_layout.addWidget(self.btn_nav_in)
        nav_layout.addWidget(self.btn_nav_out)
        
        # Thêm khoảng trống stretch để đẩy nút lịch sử về góc phải thanh tab
        nav_layout.addStretch() 
        
        # NÚT LỊCH SỬ TỔNG HỢP (Đặt ở góc phải thanh Tab)
        self.btn_nav_history = QPushButton("🕒   Lịch sử tổng hợp")
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
        
        # 3. Khởi tạo Lịch sử tổng hợp (Tham số gọn gàng hơn vì cột & filter đã gom vào trong)
        self.history_widget = HistoryView(
            title="🔄 Nhật ký Kho tổng hợp",
            subtitle="Xem toàn bộ lịch sử biến động dữ liệu thời gian thực từ cơ sở dữ liệu",
            back_btn_text="← Quay lại Form xử lý",
            on_back_clicked=self.go_back_to_previous_form,
            parent=self
        )
        
        # Đưa các Phân hệ vào trong Stack
        self.stack.addWidget(self.form_stock_in)
        self.stack.addWidget(self.form_stock_out)
        self.stack.addWidget(self.history_widget)
        
        # Thiết lập trạng thái mặc định ban đầu là form nhập kho
        self.previous_form = self.form_stock_in
        self.set_nav_button_active(self.btn_nav_in, True)
        self.set_nav_button_active(self.btn_nav_out, False)
        self.set_nav_button_active(self.btn_nav_history, False)
        self.stack.setCurrentWidget(self.form_stock_in)

    def toggle_history_view(self):
        if self.stack.currentWidget() == self.history_widget:
            self.go_back_to_previous_form()
        else:
            self.show_history_view()

    def switch_to_stock_in(self):
        self.set_nav_button_active(self.btn_nav_in, True)
        self.set_nav_button_active(self.btn_nav_out, False)
        self.set_nav_button_active(self.btn_nav_history, False)
        self.stack.setCurrentWidget(self.form_stock_in)
        self.previous_form = self.form_stock_in

    def switch_to_stock_out(self):
        self.set_nav_button_active(self.btn_nav_in, False)
        self.set_nav_button_active(self.btn_nav_out, True)
        self.set_nav_button_active(self.btn_nav_history, False)
        self.stack.setCurrentWidget(self.form_stock_out)
        self.previous_form = self.form_stock_out

    def show_history_view(self):
        """Mở màn hình lịch sử và ủy quyền cho Component tự tải/hiển thị dữ liệu thực tế"""
        self.previous_form = self.stack.currentWidget() 
        
        self.set_nav_button_active(self.btn_nav_in, False)
        self.set_nav_button_active(self.btn_nav_out, False)
        self.set_nav_button_active(self.btn_nav_history, True)
        
        # Gọi hàm xử lý dữ liệu đã được di chuyển biệt lập sang HistoryView
        if hasattr(self.history_widget, 'fetch_and_refresh_history'):
            self.history_widget.fetch_and_refresh_history(self.api_client)
            
        self.stack.setCurrentWidget(self.history_widget)

    def go_back_to_previous_form(self):
        if hasattr(self, 'previous_form') and self.previous_form == self.form_stock_out:
            self.switch_to_stock_out()
        else:
            self.switch_to_stock_in()

    def set_nav_button_active(self, button: QPushButton, active: bool):
        if active:
            button.setStyleSheet("""
                background: #1a2e4a; color: #5b9cf6; border: 1px solid #2a4a6e; 
                padding: 10px 20px; font-size: 13px; font-weight: bold; border-radius: 6px;
            """)
        else:
            if button == self.btn_nav_history:
                button.setStyleSheet("""
                    QPushButton { background: #161b26; border: 1px solid #2a3347; color: #8899b4; 
                                  padding: 10px 20px; font-size: 13px; font-weight: bold; border-radius: 6px; }
                    QPushButton:hover { background: #1e2740; border-color: #3a4560; color: #e2e8f0; }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton { background: transparent; color: #8899b4; border: none; 
                                  padding: 10px 20px; font-size: 13px; font-weight: bold; border-radius: 6px; }
                    QPushButton:hover { background: #161b26; color: #e2e8f0; }
                """)