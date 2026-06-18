# ui/controllers/stock_in_controller.py
from PyQt6.QtWidgets import QMessageBox

class StockInController:
    """Controller chịu trách nhiệm xử lý logic nghiệp vụ cho màn hình Nhập kho."""
    
    def __init__(self, view, api_client):
        self.view = view
        self.api_client = api_client

    def handle_barcode_scanned(self):
        """Xử lý sự kiện khi quét hoặc nhập mã vạch sản phẩm."""
        barcode = self.view.txt_barcode.text().strip()
        if not barcode:
            return
            
        try:
            if hasattr(self.api_client, 'search_product'):
                prod_data = self.api_client.search_product(barcode)
            else:
                print("[CONTROLLER ERROR] API Client chưa hỗ trợ search_product.")
                return

            if prod_data:
                product_name = prod_data.get('product_name', '')
                strategy_info = "FIFO" if "FIFO" in prod_data.get('strategy_type', 'FIFO') else "LIFO"
                
                # Cập nhật thông tin lên giao diện
                self.view.txt_name.setText(product_name)
                self.view.lbl_batch_title.setText(f"Lô mới — {product_name}")
                self.view.lbl_batch_sub.setText(f"Sẵn sàng nạp kho theo chiến lược: {strategy_info}")
                
        except Exception:
            self.view.txt_name.setText("")
            self.view.lbl_batch_title.setText("Sản phẩm mới")
            self.view.lbl_batch_sub.setText("Mã vạch lạ, hệ thống sẽ tự động tạo mới danh mục khi xác nhận.")

    def handle_confirm_stock_in(self):
        """Thu thập dữ liệu, kiểm tra tính hợp lệ và thực hiện gọi API nhập kho."""
        try:
            # 1. Thu thập dữ liệu thô từ View
            barcode = self.view.txt_barcode.text().strip()
            product_name = self.view.txt_name.text().strip()
            qty_text = self.view.txt_qty.text().strip()
            unit = self.view.cbo_unit.currentText()
            location = self.view.txt_location.text().strip()
            expiry_date_str = self.view.dt_expiry.date().toString("yyyy-MM-dd")

            # 2. Kiểm tra tính hợp lệ (Validation)
            if not barcode:
                raise ValueError("Mã vạch / Barcode không được để trống.")
            if not product_name:
                raise ValueError("Tên sản phẩm không được để trống.")
            if not qty_text.isdigit() or int(qty_text) <= 0:
                raise ValueError("Số lượng nhập kho phải là số nguyên dương lớn hơn 0.")
                
            quantity = int(qty_text)

            # 3. Gọi API xử lý lưu xuống Database
            result = self.api_client.stock_in(
                barcode=barcode,
                quantity=quantity,
                expiry_date=expiry_date_str
            )
            
            # 4. Phản hồi kết quả lên giao diện
            batch_id = result.get("batch_id", "Không rõ")
            msg = f"Nhập kho thành công!\n- Mã lô phát sinh: {batch_id}\n- Vị trí lưu trữ: Kệ {location}"
            QMessageBox.information(self.view, "Thành công", msg)
            
            display_expiry = self.view.dt_expiry.date().toString('dd/MM/yyyy')
            self.view.lbl_batch_title.setText(f"Lô {batch_id} — {product_name}")
            self.view.lbl_batch_sub.setText(f"{quantity} {unit} · Lưu tại kệ: {location} · Hạn: {display_expiry}")
            
        except ValueError as e:
            QMessageBox.warning(self.view, "Lỗi Nghiệp Vụ", str(e))
        except ConnectionError as e:
            QMessageBox.critical(self.view, "Lỗi Kết Nối", str(e))
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi Hệ Thống", f"Đã xảy ra sự cố ngoài ý muốn:\n{str(e)}")