# ui/controllers/stock_in_controller.py
from PyQt6.QtWidgets import QMessageBox

class StockOutController:
    """Controller chịu trách nhiệm xử lý logic nghiệp vụ cho màn hình Xuất kho."""
    
    def __init__(self, view, api_client):
        self.view = view
        self.api_client = api_client

    def handle_confirm_stock_out(self):
        """Thu thập dữ liệu đơn hàng, kiểm tra hợp lệ và thực hiện gọi mạng xuất kho."""
        try:
            # 1. Thu thập dữ liệu thô từ View
            order_id = self.view.txt_order_id.text().strip()
            barcode = self.view.txt_product.text().strip()      
            qty_raw = self.view.txt_qty.text().strip()
            
            # Làm sạch chuỗi dữ liệu số lượng
            qty_clean = "".join([char for char in qty_raw if char.isdigit()])

            # 2. Kiểm tra tính hợp lệ dữ liệu (Validation)
            if not barcode or "..." in barcode:
                raise ValueError("Vui lòng nhập Mã vạch (Barcode) sản phẩm cần xuất kho.")
            if not qty_clean or int(qty_clean) <= 0:
                raise ValueError("Số lượng yêu cầu xuất kho phải là một số nguyên dương lớn hơn 0.")
            
            quantity = int(qty_clean)
            
            # 3. Thực thi gọi API xuất kho từ Backend
            result = self.api_client.stock_out(barcode=barcode, quantity=quantity)
            
            message = result.get("message", "Xuất kho thành công.")
            details = result.get("details", []) 
            
            # 4. Phản hồi trạng thái thành công lên giao diện (View)
            QMessageBox.information(self.view, "Thành Công", f"Đơn hàng {order_id} xử lý thành công!\n\n{message}")
            self.view.update_status_badge(success=True)
            
            if details:
                first_batch = details[0]
                batch_id = first_batch.get("batch_id", "N/A")
                qty_deducted = first_batch.get("quantity_deducted", quantity)
                
                # Cập nhật thanh tiến trình phân bổ lũy tiến
                self.view.update_allocation_progress(batch_id, order_id, qty_deducted, quantity)
            
        except ValueError as e:
            self.view.update_status_badge(success=False)
            QMessageBox.warning(self.view, "Lỗi Nghiệp Vụ", str(e))
            
        except ConnectionError as e:
            QMessageBox.critical(self.view, "Lỗi Kết Nối", str(e))
            
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi Hệ Thống", f"Đã xảy ra sự cố không xác định:\n{str(e)}")