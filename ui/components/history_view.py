# ui/components/history_view.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from ui.components.datatable.table_logic import DataTable

class HistoryView(QWidget):
    def __init__(self, title, subtitle, back_btn_text, on_back_clicked, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # --- HEADER BAR ---
        header = QHBoxLayout()
        title_lay = QVBoxLayout()
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e2e8f0;")
        lbl_subtitle = QLabel(subtitle)
        lbl_subtitle.setStyleSheet("font-size: 11px; color: #8899b4;")
        
        title_lay.addWidget(lbl_title)
        title_lay.addWidget(lbl_subtitle)
        
        back_btn = QPushButton(back_btn_text)
        back_btn.setStyleSheet("""
            QPushButton { background: #1a2e4a; border: 1px solid #2a4a6e; color: #5b9cf6; 
                          padding: 8px 14px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #24426b; }
        """)
        back_btn.clicked.connect(on_back_clicked)
        
        header.addLayout(title_lay)
        header.addStretch()
        header.addWidget(back_btn)
        layout.addLayout(header)

        # --- DATA TABLE ---
        # Tự đóng gói cấu trúc cột và bộ lọc cố định của lịch sử kho tại đây
        columns = ["📦 Sản phẩm (Barcode)", "Mã lô / Chứng từ", "Nghiệp vụ", "Số lượng thay đổi", "Thời gian hệ thống"]
        filters = ["Tất cả", "Nhập kho", "Xuất kho"]
        
        self.table = DataTable(columns, filters, self)
        layout.addWidget(self.table)

        # Khởi tạo bảng trống ban đầu
        # self.table.load_data([], status=True, action=True)
        self.table.load_data([], status=True, action=False)  # Đặt status=True để hiển thị cột trạng thái, action=True để hiển thị cột hành động

    def fetch_and_refresh_history(self, api_client):
        """Tự gọi API lấy dữ liệu, biến đổi cấu trúc và nạp trực tiếp lên bảng hiển thị"""
        if not api_client:
            return
            
        try:
            raw_history_list = api_client.get_inventory_history()
            
            if isinstance(raw_history_list, list):
                # Thực hiện ánh xạ dữ liệu ngay tại đây
                formatted_history = self._map_api_to_ui_format(raw_history_list)
                
                # Nạp dữ liệu vào bảng
                self.table.load_data(formatted_history, status=True, action=False)
                
                # Tự động căn chỉnh độ rộng các cột vừa vặn với nội dung văn bản dữ liệu thật
                if hasattr(self.table, 'view') and self.table.view:
                    self.table.view.resizeColumnsToContents()
                elif hasattr(self.table, 'resizeColumnsToContents'):
                    self.table.resizeColumnsToContents()
        except Exception as e:
            print(f"[UI ERROR] Thất bại khi đồng bộ lịch sử bên trong Component: {str(e)}")

    def _map_api_to_ui_format(self, raw_logs: list) -> list:
        """Hàm nội bộ chuyển đổi cấu trúc dữ liệu từ API sang cấu trúc DataTable UI nhận diện"""
        formatted_list = []
        for log in raw_logs:
            action = log.get("action_type", "IMPORT").upper()
            
            if action == "IMPORT":
                category = "Nhập kho"
                qty_display = f"+{log.get('quantity_changed', 0)} SP"
            elif action == "EXPORT":
                category = "Xuất kho"
                qty_display = f"-{log.get('quantity_changed', 0)} SP"
            else:
                category = "Nhập kho" if action in ["IN", "NHẬP KHO", "NHAP_KHO"] else "Xuất kho"
                qty_display = f"{log.get('quantity_changed', 0)} SP"
            
            raw_batch_id = log.get("batch_id", "00000000")
            # short_batch_id = raw_batch_id[:8] if len(raw_batch_id) > 8 else raw_batch_id
            
            formatted_item = {
                "product_name": f"{log.get('barcode', 'N/A')}", # 
                "barcode": f"{raw_batch_id}", # Hiển thị mã lô hàng dưới dạng rút gọn để dễ nhìn, đồng thời giữ lại dấu # để phân biệt với cột mã vạch sản phẩm
                "category": category, # Hiển thị loại nghiệp vụ (Nhập/Xuất) ngay trong cột này để dễ phân biệt
                "stock": qty_display, # Hiển thị số lượng thay đổi với dấu +/- để dễ nhận biết ngay lập tức
                "strategy_type": (log.get("timestamp", "N/A"), "normal"),
                "status": ("Thành công", "success") 
            }
            formatted_list.append(formatted_item)
            
        return formatted_list