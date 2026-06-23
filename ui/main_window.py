import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from ui.components.sidebar import Sidebar
from ui.screens.warehouse_manager import WarehouseManagerScreen
from ui.screens.dashboard import DashboardScreen
from ui.screens.products import ProductsScreen
from ui.screens.stock_in import StockInScreen
from ui.screens.stock_out import StockOutScreen
from ui.screens.expiry import ExpiryScreen

class MainWindow(QMainWindow):
    def __init__(self, api_client=None, parent=None):
        super().__init__()
        self.api_client = api_client

        # 1: Cấu hình chung cho cửa sổ chính (Title, kích thước, layout cơ bản)
        self.setWindowTitle("Warehouse Management System")
        self.resize(1100, 680)

        # 2: Đặt icon cho ứng dụng
        self.setWindowIcon(QIcon("ui/assets/Icon/boxes-stacked-solid-full.svg"))
        self

        # Widget gốc nền ứng dụng
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Sắp xếp ngang: Sidebar bên trái | Nội dung chính bên phải
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Khởi tạo Sidebar điều hướng
        self.sidebar = Sidebar(self)
        main_layout.addWidget(self.sidebar)

        # 2. Ngăn chứa các màn hình xếp chồng (Stacked Widget)
        self.stacked_widget = QStackedWidget(self)
        main_layout.addWidget(self.stacked_widget, 1)

        # 3. Đăng ký khởi tạo các màn hình chức năng
        self.screens = {
            "dashboard": DashboardScreen(self, api_client=self.api_client),
            "products":  ProductsScreen(self, api_client=self.api_client),
            "warehouse_manager": WarehouseManagerScreen(self, api_client=self.api_client), # Màn hình Quản lý kho
            "stockin":   StockInScreen(self, api_client=self.api_client),
            "stockout":  StockOutScreen(self, api_client=self.api_client),
            # "expiry":    ExpiryScreen(self, api_client=self.api_client),
            # "reports":   QWidget(self), # Khung chờ trang Báo cáo nếu cần làm thêm
        }

        # Nạp tất cả màn hình vào StackedWidget
        for key, widget in self.screens.items():
            self.stacked_widget.addWidget(widget)

        # 4. Kết nối tín hiệu chuyển tab từ Sidebar sang StackedWidget
        self.sidebar.navigate.connect(self._switch_screen)

        # 5. Nạp cấu trúc thiết kế từ file styles.qss
        self._load_stylesheet()

    def _switch_screen(self, key: str):
        if key in self.screens:
            target_widget = self.screens[key]
            
            # 1. Thực hiện chuyển giao diện sang màn hình được chọn (ví dụ: products)
            self.stacked_widget.setCurrentWidget(target_widget)
            
            # 2. Đón đầu: Nếu màn hình vừa mở là ProductsScreen (hoặc bất kỳ màn hình nào có hàm load API)
            # Hệ thống sẽ tự động ra lệnh gọi API cập nhật dữ liệu ngay lập tức!
            if hasattr(target_widget, "load_products_from_api"):
                target_widget.load_products_from_api()
                
            # (Tùy chọn) Nếu sau này bạn có viết thêm hàm refresh cho các màn hình khác như Dashboard, Expiry...
            elif hasattr(target_widget, "refresh_data"):
                target_widget.refresh_data()

    def _load_stylesheet(self):
        # Định vị đường dẫn file styles.qss tương đối từ thư mục chạy dự án
        qss_path = os.path.join(os.path.dirname(__file__), "assets", "styles.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Không tìm thấy file định dạng CSS tại: {qss_path}")

# Khối chạy thử độc lập ứng dụng kiểm tra thành phẩm
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())