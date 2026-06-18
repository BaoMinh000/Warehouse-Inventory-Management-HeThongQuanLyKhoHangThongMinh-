from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QFrame
)

from ui.screens.stock_in import StockInScreen
from ui.screens.stock_out import StockOutScreen
# Giả định bạn có hoặc sẽ có màn hình lịch sử, nếu chưa có hãy tạm thời dùng QWidget trống
from ui.components.history_view import HistoryView

class WarehouseManagerScreen(QWidget):

    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)

        self.api_client = api_client

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # ===== NAVIGATION BAR =====
        self.nav_bar = QFrame()
        self.nav_bar.setStyleSheet("""
            QFrame { 
                background: #0f131a; 
                border: 1px solid #1e2530; 
                border-radius: 8px; 
            }
        """)
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(8, 8, 8, 8) # Thêm chút padding cho thanh nav đẹp hơn

        # Tạo các nút điều hướng
        self.btn_nav_in = QPushButton("📥 Nhập kho")
        self.btn_nav_out = QPushButton("📤 Xuất kho")
        self.btn_nav_history = QPushButton("🕒 Lịch sử tổng hợp")

        # Đưa các nút vào layout
        nav_layout.addWidget(self.btn_nav_in)
        nav_layout.addWidget(self.btn_nav_out)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_nav_history)

        main_layout.addWidget(self.nav_bar)

        # ===== STACKED WIDGET (QUẢN LÝ MÀN HÌNH) =====
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Khởi tạo các màn hình con
        self.stock_in_screen = StockInScreen(self, api_client=self.api_client)
        self.stock_out_screen = StockOutScreen(self, api_client=self.api_client)
        self.stock_history_screen = HistoryView(
            title="🔄 Nhật ký Kho tổng hợp",
            subtitle="Xem toàn bộ lịch sử biến động dữ liệu thời gian thực từ cơ sở dữ liệu",
            back_btn_text="← Quay lại",
            on_back_clicked=self.switch_to_stock_in, # Khi bấm nút back trong lịch sử, tự động chuyển về tab nhập kho (tab mặc định)
            parent=self
        )

        # Thêm các màn hình vào stack theo đúng thứ tự
        self.stack.addWidget(self.stock_in_screen)
        self.stack.addWidget(self.stock_out_screen)
        self.stack.addWidget(self.stock_history_screen)

        # ===== KẾT NỐI SỰ KIỆN KHU VỰC TAB =====
        self.btn_nav_in.clicked.connect(self.switch_to_stock_in)
        self.btn_nav_out.clicked.connect(self.switch_to_stock_out)
        self.btn_nav_history.clicked.connect(self.switch_to_stock_history)

        # Thiết lập trạng thái mặc định ban đầu (Màn hình nhập kho)
        self.switch_to_stock_in()


    # ===== CÁC HÀM CHUYỂN ĐỔI TAB =====
    def switch_to_stock_in(self):
        self.stack.setCurrentWidget(self.stock_in_screen)
        self.update_nav_buttons(active_button=self.btn_nav_in)
        self.btn_nav_history.setVisible(True)


    def switch_to_stock_out(self):
        self.stack.setCurrentWidget(self.stock_out_screen)
        self.update_nav_buttons(active_button=self.btn_nav_out)

    def switch_to_stock_history(self): # Khi chuyển sang tab lịch sử, tự động fetch dữ liệu mới nhất từ API để đảm bảo luôn cập nhật

        self.stock_history_screen.fetch_and_refresh_history( self.api_client )

        self.stack.setCurrentWidget(self.stock_history_screen)

        self.update_nav_buttons( active_button=self.btn_nav_history)
        # ẩn nút lịch sử khi đang ở tab lịch sử để tránh nhầm lẫn, chỉ hiển thị khi ở tab nhập/xuất kho
        self.btn_nav_history.setVisible(False)

    # ===== CẬP NHẬT GIAO DIỆN NÚT BẤM (ACTIVE / INACTIVE) =====
    
    def update_nav_buttons(self, active_button: QPushButton):
        """Hàm tự động duyệt qua tất cả các nút để bật/tắt CSS active"""
        buttons = [self.btn_nav_in, self.btn_nav_out, self.btn_nav_history]
        
        for button in buttons:
            if button == active_button:
                # Định dạng khi tab ĐƯỢC CHỌN (Active)
                button.setStyleSheet("""
                    QPushButton {
                        background: #1a2e4a; color: #5b9cf6; border: 1px solid #2a4a6e; 
                        padding: 10px 20px; font-size: 13px; font-weight: bold; border-radius: 6px;
                    }
                """)
            else:
                # Định dạng khi tab KHÔNG ĐƯỢC CHỌN (Normal / Hover)
                if button == self.btn_nav_history:
                    # Thiết kế riêng biệt một chút cho nút lịch sử (nằm bên phải) như code cũ của bạn
                    button.setStyleSheet("""
                        QPushButton { background: #161b26; border: 1px solid #2a3347; color: #8899b4; 
                                      padding: 10px 20px; font-size: 13px; font-weight: bold; border-radius: 6px; }
                        QPushButton:hover { background: #1e2740; border-color: #3a4560; color: #e2e8f0; }
                    """)
                else:
                    # Thiết kế cho các nút mặc định (Nhập / Xuất)
                    button.setStyleSheet("""
                        QPushButton { background: transparent; color: #8899b4; border: none; 
                                      padding: 10px 20px; font-size: 13px; font-weight: bold; border-radius: 6px; }
                        QPushButton:hover { background: #161b26; color: #e2e8f0; }
                    """)