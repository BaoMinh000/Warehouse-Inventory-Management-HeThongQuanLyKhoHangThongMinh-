from PyQt6.QtWidgets import QDialog, QComboBox
from .ui_item_form import Ui_ItemFormDialog  # Nhập class UI ở trên

class ItemFormDialog(QDialog):
    """
    Controller xử lý logic của Form.
    Giao diện được tách hoàn toàn sang Ui_ItemFormDialog.
    """
    def __init__(self, data: dict, mode: str = "view", api_client=None, parent=None):
        super().__init__(parent)
        self.original_data = data
        self.mode = mode
        self.updated_data = {}
        self.api_client = api_client
 
        # 1. Khởi tạo và thiết lập UI
        self.ui = Ui_ItemFormDialog()
        self.ui.setup_ui(self, data, mode)

        # 2. Liên kết các sự kiện (Signals & Slots)
        self._connect_signals()

    def _connect_signals(self):
        """Khớp các nút bấm bên UI với các hàm logic."""
        if self.mode == "view":
            if self.ui.close_btn:
                self.ui.close_btn.clicked.connect(self.reject)
        else:
            if self.ui.cancel_btn:
                self.ui.cancel_btn.clicked.connect(self.reject)
            if self.ui.save_btn:
                self.ui.save_btn.clicked.connect(self.handle_save)

    def get_updated_data(self) -> dict:
        """Trích xuất dữ liệu từ các widget nhập liệu trên UI."""
        updated_data = {}
        for key, widget in self.ui.fields.items():
            original_val = self.original_data.get(key, "")

            if key == "status":
                updated_data[key] = original_val
                continue

            if isinstance(widget, QComboBox):
                current_text = widget.currentText()
            else:
                current_text = widget.text()

            if isinstance(original_val, tuple):
                updated_data[key] = (current_text, original_val[1])
            else:
                updated_data[key] = current_text

        return updated_data
    
    def handle_save(self):
        """Xử lý khi bấm nút Lưu thay đổi."""
        self.updated_data = self.get_updated_data()
        # Gọi API để lưu dữ liệu mới vào cơ sở dữ liệu hoặc thực hiện các thao tác cần thiết khác
        result = self.api_client.update_product(
                    barcode=self.original_data.get("barcode"),
                    name=self.updated_data.get("product_name"),
                    strategy=self.updated_data.get("strategy_type"),
                    category=self.updated_data.get("category")
                )
        if result:
            self.accept()  # Đóng dialog và trả về trạng thái thành công
        elif not result:
            # Hiển thị thông báo lỗi nếu cần
            print("Cập nhật sản phẩm thất bại.")