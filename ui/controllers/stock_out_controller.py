# ui/controllers/stock_in_controller.py
from PyQt6.QtWidgets import QMessageBox

class StockOutController:
    """Controller chịu trách nhiệm xử lý logic nghiệp vụ cho màn hình Xuất kho."""
    
    def __init__(self, view, api_client):
        self.view = view
        self.api_client = api_client

    def handle_confirm_stock_out(self):
        """
        Thu thập dữ liệu đơn hàng, kiểm tra hợp lệ và thực hiện gọi mạng xuất kho.
        Cập nhật dữ liệu đồng bộ theo danh sách phân bổ lô hàng thực tế trả về từ API.
        """
        try:
            # 1. Thu thập dữ liệu thô từ View
            order_id = self.view.txt_order_id.text().strip()
            barcode = self.view.txt_product.text().strip()      
            qty_raw = self.view.txt_qty.text().strip() # Lấy dữ liệu số lượng thô từ ô text, có thể chứa ký tự không phải số
            
            # Làm sạch chuỗi dữ liệu số lượng
            qty_clean = "".join([char for char in qty_raw if char.isdigit()])

            # 2. Kiểm tra tính hợp lệ dữ liệu (Validation)
            if not barcode or "..." in barcode:
                raise ValueError("Vui lòng nhập Mã vạch (Barcode) sản phẩm cần xuất kho.")
            if not qty_clean or int(qty_clean) <= 0:
                raise ValueError("Số lượng yêu cầu xuất kho phải là một số nguyên dương lớn hơn 0.")
            
            quantity = int(qty_clean)
            
            # 3. Thực thi gọi API xuất kho từ Backend
            # Backend xử lý trừ kho và trả lời về danh sách các lô thực tế đã bị trừ
            result = self.api_client.stock_out(barcode=barcode, quantity=quantity)
            
            message = result.get("message", "Xuất kho thành công.")
            # details chứa danh sách các lô thực tế bị trừ: [{"batch_id": "...", "quantity_deducted": 50, "is_depleted": True, "import_date": "..."}]
            details = result.get("details", []) 
            
            # 4. Tạo danh sách allocated_result từ kết quả thật của API để đẩy lên Table view bên phải
            allocated_result = []
            qty_deducted = 0
            explanation_logs = []
            
            # Lấy thông tin phương thức xuất hiện tại trên giao diện để hiển thị nhãn (Label)
            strategy_text = "FIFO" if self.view.cbo_method.currentIndex() == 0 else "LIFO"

            for batch_info in details:
                b_id = batch_info.get("batch_id")
                take = batch_info.get("quantity_deducted", 0)
                is_depleted = batch_info.get("is_depleted", False)
                import_date_str = batch_info.get("import_date", "N/A")
                
                qty_deducted += take
                
                # Format đúng cấu trúc cấu hình hiển thị của bảng bên phải QTableWidget
                allocated_result.append({
                    "id": f"{b_id} ({strategy_text})" if len(allocated_result) == 0 else b_id,
                    "date": import_date_str,
                    "stock": "Đã trừ kho", # Trạng thái sau khi xuất thành công
                    "qty_out": f"{take} (Hết hàng)" if is_depleted else f"{take} (Thành công)",
                    "is_depleted": is_depleted
                })
                explanation_logs.append(f"trừ {take} sp từ lô {b_id}")

            # Tạo chuỗi văn bản giải trình thực tế sau khi xuất
            if qty_deducted < quantity:
                explanation = f"Cảnh báo: Chỉ xuất được {qty_deducted}/{quantity} sản phẩm do thiếu hàng tồn."
            else:
                explanation = f"Xuất kho hoàn tất! Hệ thống đã tự động " + " và ".join(explanation_logs) + "."

            # 5. Phản hồi trạng thái thành công lên giao diện (View)
            QMessageBox.information(self.view, "Thành Công", f"Đơn hàng {order_id} xử lý thành công!\n\n{message}")
            self.view.update_status_badge(success=True)
            
            # Đẩy danh sách allocated_result thật lên giao diện bảng lưới
            self.view.update_allocation_progress(
                allocated_batches=allocated_result,
                qty_deducted=qty_deducted,
                total_qty=quantity,
                explanation=explanation
            )
            
        except ValueError as e:
            self.view.update_status_badge(success=False)
            QMessageBox.warning(self.view, "Lỗi Nghiệp Vụ", str(e))
            
        except ConnectionError as e:
            QMessageBox.critical(self.view, "Lỗi Kết Nối", str(e))
            
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi Hệ Thống", f"Đã xảy ra sự cố không xác định:\n{str(e)}")
     
    def handle_get_stock(self):
        """Xử lý sự kiện khi người dùng nhấn nút 'Kiểm tra tồn kho'."""
        try:
            barcode = self.view.txt_product.text().strip()
            if not barcode or "..." in barcode:
                raise ValueError("Vui lòng nhập Mã vạch (Barcode) sản phẩm để kiểm tra tồn kho.")
            
            stock_info = self.api_client.get_product_stock(barcode)
            total_quantity = stock_info.get("total_quantity", 0)
            batches = stock_info.get("batches", [])
            
            # Cập nhật giao diện với thông tin tồn kho
            self.view.display_stock_info(total_quantity, batches)
            
        except ValueError as e:
            QMessageBox.warning(self.view, "Lỗi Nghiệp Vụ", str(e))
            
        except ConnectionError as e:
            QMessageBox.critical(self.view, "Lỗi Kết Nối", str(e))
            
        except Exception as e:
            QMessageBox.critical(self.view, "Lỗi Hệ Thống", f"Đã xảy ra sự cố không xác định:\n{str(e)}")
            
            
    def handle_check_allocation(self):
        import json
        """
        Xử lý kiểm tra thông tin đơn xuất, tự động khóa phương thức theo cấu hình gốc của Sản phẩm 
        và tính toán phân bổ gối lô (FIFO/LIFO) hiển thị kết quả sang bảng bên phải.
        """
        # 1. Thu thập dữ liệu đầu vào từ giao diện (Cột trái)
        order_id = self.view.txt_order_id.text().strip()
        barcode = self.view.txt_product.text().strip() # Lấy từ ô text mã vạch sản phẩm bên màn hình xuất kho

        if not barcode:
            self.view.lbl_algo_explanation.setText("❌ Lỗi: Mã vạch sản phẩm không được để trống!")
            return

        try:
            qty_requested = int(self.view.txt_qty.text().strip())
            if qty_requested <= 0:
                raise ValueError()
        except ValueError:
            self.view.lbl_algo_explanation.setText("❌ Lỗi: Số lượng yêu cầu phải là số nguyên dương!")
            return

        try:
            # 2. LẤY CHIẾN LƯỢC GỐC TỪ SẢN PHẨM BẰNG SEARCH_PRODUCT & KHÓA UI
            if hasattr(self.api_client, 'search_product'):
                prod_data = self.api_client.search_product(barcode)
            else:
                self.view.lbl_algo_explanation.setText("❌ Lỗi: API Client chưa hỗ trợ search_product.")
                return

            if not prod_data:
                self.view.lbl_algo_explanation.setText(f"❌ Lỗi: Sản phẩm có mã vạch {barcode} không tồn tại.")
                return
            
            # Áp dụng logic bóc tách thông tin chiến lược xuất kho của bạn
            strategy_text = "FIFO" if "FIFO" in prod_data.get('strategy_type', 'FIFO') else "LIFO"
            
            # Đồng bộ ngược lại giao diện và KHÓA KHÔNG CHO USER CHỈNH SỬA[cite: 3]
            if strategy_text == "FIFO":
                self.view.cbo_method.setCurrentIndex(0)
            else:
                self.view.cbo_method.setCurrentIndex(1)
                
            self.view.cbo_method.setEnabled(False)  # Khóa cứng ComboBox trên UI không cho chỉnh

            # 3. Lấy danh sách các lô hàng hiện có của sản phẩm từ Backend RAM/DB[cite: 3]
            all_batches = self.api_client.get_product_stock(barcode).get("batches", [])
            
            # In debug danh sách thô nhận được từ Backend
            # formatted_batches = json.dumps(all_batches, indent=4, ensure_ascii=False)
            # print(f"\n[DEBUG] === DANH SÁCH LÔ HÀNG CỦA BARCODE {barcode} ===")
            # print(formatted_batches)
            
            # Sắp xếp các lô hàng dựa trên chiến lược cấu hình chuẩn gốc của sản phẩm[cite: 2]
            if strategy_text == "FIFO":  # Cũ nhất xếp trước (Ngày tăng dần)
                all_batches.sort(key=lambda x: x["import_date"])
            elif strategy_text == "LIFO":  # Mới nhất xếp trước (Ngày giảm dần)
                all_batches.sort(key=lambda x: x["import_date"], reverse=True)

            # In debug danh sách sau khi đã Sort tự động theo thuật toán
            # formatted_batches_sorted = json.dumps(all_batches, indent=4, ensure_ascii=False)
            # print(f"\n[DEBUG] === DANH SÁCH LÔ HÀNG SAU KHI SORT ({strategy_text}) ===")
            # print(formatted_batches_sorted)

            # 4. Thuật toán gối lô (Phân bổ lũy tiến) dựa trên cấu trúc trường RAM[cite: 2]
            allocated_result = []
            remained_qty_needed = qty_requested
            qty_deducted = 0
            explanation_logs = []

            for batch in all_batches:
                current_stock = int(batch.get("quantity", 0)) # Theo định nghĩa biến quantity[cite: 2]
                batch_id = batch.get("batch_id")             # Theo định nghĩa biến batch_id[cite: 2]
                import_date_str = batch.get("import_date", "")
                
                # Nếu lô hàng này đã hết sẵn, bỏ qua
                if current_stock <= 0:
                    continue

                if remained_qty_needed <= 0:
                    # Nếu đã gom đủ số lượng yêu cầu, các lô sau giữ nguyên hiển thị 0
                    allocated_result.append({
                        "id": batch_id,
                        "date": import_date_str,
                        "stock": f"{current_stock} hộp",
                        "qty_out": "0",
                        "is_depleted": False
                    })
                    continue
                    
                if current_stock <= remained_qty_needed:
                    # Trường hợp lô hiện tại không đủ hoặc vừa đủ -> Bào sạch lô này
                    take = current_stock
                    remained_qty_needed -= take
                    qty_deducted += take
                    
                    allocated_result.append({
                        "id": f"{batch_id} ({strategy_text})" if len(allocated_result) == 0 else batch_id,
                        "date": import_date_str,
                        "stock": f"{current_stock} hộp",
                        "qty_out": f"{take} (Hết hàng)",
                        "is_depleted": True
                    })
                    explanation_logs.append(f"lấy hết {take} sp từ lô {batch_id}")
                else:
                    # Trường hợp lô hiện tại dư sức đáp ứng số lượng thiếu còn lại
                    take = remained_qty_needed
                    remained_qty_needed = 0
                    qty_deducted += take
                    
                    allocated_result.append({
                        "id": f"{batch_id} ({strategy_text})" if len(allocated_result) == 0 else batch_id,
                        "date": import_date_str,
                        "stock": f"{current_stock} hộp",
                        "qty_out": f"{take} (Còn lại {current_stock - take})",
                        "is_depleted": False
                    })
                    explanation_logs.append(f"gối tiếp {take} sp từ lô {batch_id}")

            # Tạo chuỗi văn bản giải trình dựa trên tiến trình gối lô thực tế
            if qty_deducted < qty_requested:
                explanation = f"Kho không đủ hàng! Chỉ gom được {qty_deducted}/{qty_requested} sản phẩm."
            else:
                explanation = f"Do sản phẩm mặc định dùng chiến lược {strategy_text}, hệ thống đã " + " và ".join(explanation_logs) + "."

            # 5. Đẩy ngược dữ liệu đã xử lý sang hiển thị ở cột bên phải UI
            self.view.update_allocation_progress(
                allocated_batches=allocated_result,
                qty_deducted=qty_deducted,
                total_qty=qty_requested,
                explanation=explanation
            )

        except Exception as e:
            self.view.lbl_algo_explanation.setText(f"❌ Lỗi hệ thống khi phân bổ lô: {str(e)}")