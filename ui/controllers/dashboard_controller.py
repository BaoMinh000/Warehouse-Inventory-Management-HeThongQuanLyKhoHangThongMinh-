# ui/controllers/dashboard_controller.py
from datetime import datetime

class DashboardDataController:
    """Service chuyên trách xử lý, chuyển đổi, gọi API và chuẩn hóa dữ liệu cho Dashboard."""
    
    def __init__(self, api_client=None):
        self.api_client = api_client
        # Bộ nhớ đệm dữ liệu gốc được chuyển từ UI sang Controller
        self.raw_history_cached = [] 
        self.products_catalog_cached = []  
        
    def fetch_inventory_history(self) -> bool:
        """
        Gọi API kết nối để chỉ nạp dữ liệu lịch sử thô (log).
        Có thể gọi lại hàm này khi muốn làm mới bảng hoạt động gần đây mà không cần tải lại danh mục.
        """
        if not self.api_client:
            print("[CONTROLLER ERROR] API Client chưa được cấu hình khi lấy lịch sử.")
            return False
            
        try:
            raw_history = self.api_client.get_inventory_history()
            
            if raw_history:
                self.raw_history_cached = raw_history
                print(f"[CONTROLLER LOG] Đã tải thành công {len(self.raw_history_cached)} bản ghi lịch sử.")
            else:
                self.raw_history_cached = []
                print("[CONTROLLER LOG] Không có dữ liệu lịch sử từ mạng.")
                
            return True
            
        except Exception as e:
            print(f"[CONTROLLER ERROR] Gặp sự cố khi nạp dữ liệu lịch sử từ API: {str(e)}")
            return False

    def fetch_product_catalog(self) -> bool:
        """
        Gọi API kết nối để chỉ nạp danh mục sản phẩm.
        Có thể gọi lại hàm này khi có thay đổi về tổng số SKU hoặc thông tin sản phẩm.
        """
        if not self.api_client:
            print("[CONTROLLER ERROR] API Client chưa được cấu hình khi lấy danh mục.")
            return False
            
        try:
            if hasattr(self.api_client, 'get_catalog'):
                catalog_data = self.api_client.get_catalog()
                
                if catalog_data:
                    self.products_catalog_cached = catalog_data
                    print(f"[CONTROLLER LOG] Đã làm mới thành công {len(self.products_catalog_cached)} sản phẩm.")
                else:
                    self.products_catalog_cached = []
                    print("[CONTROLLER LOG] Danh mục sản phẩm hiện đang trống.")
                    
                return True
            else:
                print("[CONTROLLER ERROR] API Client không có phương thức 'get_catalog'.")
                return False
                
        except Exception as e:
            print(f"[CONTROLLER ERROR] Gặp sự cố khi nạp dữ liệu danh mục từ API: {str(e)}")
            return False

    def fetch_dashboard_data(self) -> bool:
        """
        Hàm tổng hợp để nạp toàn bộ dữ liệu cho Dashboard khi khởi động lần đầu.
        Sẽ gọi tuần tự các hàm nạp lịch sử và danh mục.
        """
        # Gọi riêng lẻ từng hàm lấy dữ liệu
        history_success = self.fetch_inventory_history()
        catalog_success = self.fetch_product_catalog()
        
        # Trả về True nếu cả hai quá trình nạp dữ liệu đều không xảy ra lỗi nghiêm trọng
        if history_success and catalog_success:
            return True
        else:
            print("[CONTROLLER WARN] Có một phần dữ liệu không được tải xuống trọn vẹn.")
            return False

    def get_chart_data(self, filter_days: int) -> list[tuple[str, float, float]]:
        """Gom nhóm dữ liệu từ cache và chuyển đổi thành cấu trúc cột đôi (DD/MM, nhập, xuất)."""
        if not self.raw_history_cached:
            return []

        daily_summary = {}
        for log in self.raw_history_cached:
            date_str = log.get("timestamp", "").split(" ")[0]
            if not date_str:
                continue
                
            action = str(log.get("action_type", "")).upper().strip()
            qty = abs(int(log.get("quantity_changed", 0)))
            
            if date_str not in daily_summary:
                daily_summary[date_str] = {"stock_in": 0, "stock_out": 0}
                
            if action in ("IMPORT", "NHẬP"):
                daily_summary[date_str]["stock_in"] += qty
            elif action in ("EXPORT", "XUẤT"):
                daily_summary[date_str]["stock_out"] += qty

        sorted_dates = sorted(daily_summary.keys())
        if filter_days > 0:
            sorted_dates = sorted_dates[-filter_days:]
    
        chart_data_tuples = []
        for d in sorted_dates:
            stock_in_val = float(daily_summary[d]["stock_in"])
            stock_out_val = float(daily_summary[d]["stock_out"])
            
            try:
                display_date = datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m")
            except ValueError:
                display_date = d
                
            chart_data_tuples.append((display_date, stock_in_val, stock_out_val))

        return chart_data_tuples

    def get_recent_activities(self) -> list[tuple[str, str, str, str]]:
        """Lọc, định dạng và xây dựng cấu trúc tuple cho danh sách hoạt động gần đây."""
        if not self.raw_history_cached:
            return []

        search_product_fn = getattr(self.api_client, 'search_product', None) if self.api_client else None

        try:
            sorted_history = sorted(
                self.raw_history_cached, 
                key=lambda x: x.get('timestamp', ''), 
                reverse=True
            )
        except Exception:
            sorted_history = self.raw_history_cached

        recent_records = sorted_history[:5]
        formatted_tuples = []

        for record in recent_records:
            barcode = record.get('barcode') or "N/A"
            qty = int(record.get('quantity_changed') or record.get('quantity') or record.get('qty') or 0)
            raw_date = record.get('timestamp') or record.get('date') or ""
            action_type = str(record.get('action_type') or record.get('type') or '').upper()
            
            prod_name = ""
            if barcode != "N/A" and search_product_fn:
                try:
                    prod_data = search_product_fn(barcode)
                    if prod_data:
                        prod_name = prod_data.get('product_name') or prod_data.get('name')
                except Exception:
                    pass
            
            if not prod_name:
                prod_name = f"Sản phẩm ({barcode})"

            time_str = raw_date
            if " " in raw_date:
                time_str = raw_date.split(" ")[1][:5]
            elif "T" in raw_date:
                time_str = raw_date.split("T")[1][:5]

            if "IMPORT" in action_type or "IN" in action_type:
                kind = "in"
                title = f"Nhập kho — {prod_name}"
                subtitle = f"{time_str} · Barcode: {barcode}"
                qty_str = f"+{qty:,}"
            elif "EXPORT" in action_type or "OUT" in action_type:
                kind = "out"
                title = f"Xuất kho — {prod_name}"
                subtitle = f"{time_str} · Barcode: {barcode}"
                qty_str = f"−{qty:,}"
            else:
                kind = "warn"
                title = f"Điều chỉnh — {prod_name}"
                subtitle = f"{time_str} · Hành động: {action_type}"
                qty_str = f"{qty:+,}"

            formatted_tuples.append((kind, title, subtitle, qty_str))

        return formatted_tuples

    def get_stat_cards_data(self) -> dict:
        """Tính toán các chỉ số thực tế phục vụ hiển thị trên Stat Cards."""
        total_skus = len(self.products_catalog_cached)

        today_str = datetime.now().strftime("%Y-%m-%d")
        total_in_qty = 0
        count_in_batches = 0
        total_out_qty = 0
        count_out_orders = 0
        
        for record in self.raw_history_cached:
            record_date = record.get('date', '') or record.get('timestamp', '')
            if today_str in record_date:
                record_type = str(record.get('type', record.get('action_type', ''))).upper()
                qty = int(record.get('quantity') or record.get('qty') or record.get('quantity_changed') or 0)
                
                if "IN" in record_type or "IMPORT" in record_type:
                    total_in_qty += qty
                    count_in_batches += 1
                elif "OUT" in record_type or "EXPORT" in record_type:
                    total_out_qty += qty
                    count_out_orders += 1

        count_warnings = 0
        count_expired_soon = 0
        
        for prod in self.products_catalog_cached:
            if prod.get('is_warning') or prod.get('status') == 'warning' or prod.get('warn'):
                count_warnings += 1
            if prod.get('is_expired_soon') or 'EXPIRED' in str(prod.get('expiry_status', '')).upper():
                count_expired_soon += 1
        
        if count_warnings == 0 and total_skus > 0:
            count_warnings = sum(1 for p in self.products_catalog_cached if int(p.get('stock', 0)) < int(p.get('min_stock', 10)))

        return {
            "total_skus": total_skus,
            "total_in_qty": total_in_qty,
            "count_in_batches": count_in_batches,
            "total_out_qty": total_out_qty,
            "count_out_orders": count_out_orders,
            "count_warnings": count_warnings,
            "count_expired_soon": count_expired_soon
        }

    def get_donut_chart_data(self) -> tuple[int, int, int, int]:
        """Phân tách và tính toán phần trăm theo chiến lược phân loại lưu trữ (FIFO/LIFO/Mixed)."""
        count_fifo = 0
        count_lifo = 0
        count_mixed = 0
        total_products = len(self.products_catalog_cached)

        for prod in self.products_catalog_cached:
            inv_type = prod.get('strategy_type') or prod.get('inventory_type') or prod.get('type') or 'FIFO'
            method = str(inv_type).upper()
            
            if "FIFO" in method:
                count_fifo += 1
            elif "LIFO" in method:
                count_lifo += 1
            else:
                count_mixed += 1

        if total_products > 0:
            pct_fifo = round((count_fifo / total_products) * 100)
            pct_lifo = round((count_lifo / total_products) * 100)
            pct_mixed = max(0, 100 - pct_fifo - pct_lifo)
        else:
            pct_fifo, pct_lifo, pct_mixed = 0, 0, 0

        return pct_fifo, pct_lifo, pct_mixed, total_products