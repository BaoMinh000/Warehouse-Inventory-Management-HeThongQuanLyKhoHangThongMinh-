# ui/controllers/products_controller.py
import os
from PyQt6.QtWidgets import QMessageBox

class ProductsController:
    """Controller chịu trách nhiệm điều phối dữ liệu và logic nghiệp vụ cho ProductsScreen."""
    
    def __init__(self, view, api_client):
        self.view = view
        self.api_client = api_client

    def handle_load_products(self):
        """Gọi API lấy danh mục sản phẩm và đồng bộ hiển thị lên bảng dữ liệu."""
        try:
            if not self.api_client:
                print("[CONTROLLER ERROR] API Client chưa được cấu hình.")
                return []
                
            products_catalog = self.api_client.get_catalog()
            
            # Cập nhật dữ liệu sạch xuống DataTable thông qua View
            if hasattr(self.view, 'table'):
                self.view.table.load_data(products_catalog, status=True, action=True)
                
            print(f"[CONTROLLER] Đã làm mới thành công {len(products_catalog)} sản phẩm.")
            return products_catalog
            
        except ConnectionError as e:
            QMessageBox.critical(self.view, "Lỗi kết nối", str(e))
            return []
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi không xác định", f"Đã có lỗi xảy ra: {str(e)}")
            return []

    def handle_save_product(self):
        """Thu thập dữ liệu thô từ Form, kiểm tra tính hợp lệ và gửi yêu cầu tạo sản phẩm."""
        # 1. Thu thập dữ liệu từ các trường nhập liệu của View
        barcode = self.view.input_barcode.text().strip()
        name = self.view.input_name.text().strip()
        category = self.view.cbo_category.currentText()
        
        strategy_raw = self.view.cbo_strategy.currentText()
        strategy = "FIFO" if "FIFO" in strategy_raw else "LIFO"

        # 2. Kiểm tra tính hợp lệ dữ liệu (Validation)
        if not barcode or not name:
            QMessageBox.warning(
                self.view, "Dữ liệu không hợp lệ", "Vui lòng điền đầy đủ thông tin Tên sản phẩm và Mã vạch!"
            )
            return

        # 3. Thực thi gọi tầng dữ liệu
        try:
            if not self.api_client:
                raise Exception("API Client không khả dụng.")
                
            success = self.api_client.create_product(barcode, name, strategy, category)
            
            if success:
                QMessageBox.information(
                    self.view, "Thành công", f"Đã lưu sản phẩm '{name}' vào danh mục kho thành công."
                )
                
                # Làm mới lại danh sách bảng sau khi thêm mới thành công
                self.handle_load_products()
                
                # Clear trống Form nhập liệu
                self.view.clear_form_inputs()
                
                # Quay trở lại màn hình danh sách chính
                self.view.switch_to_list_view()
                    
        except ValueError as e:
            QMessageBox.critical(self.view, "Lỗi Nghiệp Vụ", str(e))
        except ConnectionError as e:
            QMessageBox.critical(self.view, "Lỗi Kết Nối", str(e))
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi Hệ Thống", f"Đã xảy ra sự cố: {str(e)}")