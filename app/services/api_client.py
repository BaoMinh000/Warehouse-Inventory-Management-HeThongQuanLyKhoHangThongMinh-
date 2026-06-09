# ui/services/api_client.py
# Flide ở Frontend UI, nhiệm vụ là gửi tín hiệu HTTP POST/GET sang cho Backend và nhận kết quả trả về
# nhiệm vụ là gửi tín hiệu HTTP POST/GET sang cho Backend và nhận kết quả trả về
# Đây là lớp API Client đơn giản để UI có thể gọi API của Backend một cách dễ dàng mà không cần quan tâm đến chi tiết URL hay cấu trúc payload, gọi đến file routes.py để xử lý logic nghiệp vụ và tương tác với DB Models
import os
import requests


class InventoryAPIClient:
    def __init__(self, base_url: str = os.getenv("BASE_URL")):
        self.base_url = base_url

    def get_catalog(self) -> list:
        """Gọi API GET để lấy toàn bộ danh mục sản phẩm từ Server Backend và trả về dưới dạng list of dicts"""

        if not self.base_url:
            raise ValueError("BASE_URL chưa được cấu hình. Vui lòng kiểm tra biến môi trường.")
        url = f"{self.base_url}/products"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get("catalog", [])
            else:
                print(f"[API ERROR] Status code: {response.status_code}")
                return []
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Mất kết nối tới máy chủ Backend FastAPI.")

    def create_product(self, barcode: str, name: str, strategy: str, category: str) -> bool:
        """Gọi API POST để tạo mới một sản phẩm trong danh mục trên Server Backend. Trả về True nếu thành công, False nếu thất bại."""
        if not self.base_url:
            raise ValueError("BASE_URL chưa được cấu hình. Vui lòng kiểm tra biến môi trường.")
        url = f"{self.base_url}/products"
        payload = {
            "barcode": barcode,
            "product_name": name,
            "category": category,
            "strategy_type": strategy
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 201:
                error_msg = response.json().get("detail", "Lỗi không xác định từ hệ thống.")
                raise ValueError(error_msg)
            return True
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Mất kết nối tới máy chủ Backend.")

    def stock_in(self, barcode: str, quantity: int, expiry_date: str) -> dict:
        """
        Gọi API POST để tạo lô nhập kho mới.
        Tham số:
        --------
        barcode     : Chuỗi mã vạch định danh của sản phẩm cần nhập kho.
        quantity    : Số lượng nhập kho (phải lớn hơn 0).
        expiry_date : Chuỗi ngày hết hạn định dạng dạng "YYYY-MM-DD".
        
        Trả về:
        -------
        dict: Bản ghi kết quả bao gồm trạng thái thông báo và mã lô hàng `batch_id` từ Server.
        """
        url = f"{self.base_url}/stock-in"
               
        payload = {
            "barcode": barcode,
            "quantity": quantity,
            "expiry_date": expiry_date  # Gửi chuỗi ngày sang để Backend tự parse datetime
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.json().get("detail", "Lỗi không xác định khi nhập kho.")
                raise ValueError(error_msg)
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Mất kết nối tới máy chủ Backend khi thực hiện nhập kho.")

    def stock_out(self, barcode: str, quantity: int) -> dict:
        """
        Gọi API POST để chạy thuật toán trừ kho tự động lũy tiến (FIFO/LIFO).
        Tham số:
        --------
        barcode  : Chuỗi mã vạch sản phẩm yêu cầu xuất kho.
        quantity : Tổng số lượng cần bốc dỡ ra khỏi kho.
        
        Trả về:
        -------
        dict: Trả về kết quả và danh sách chi tiết các lô hàng (`details`) bị trừ số lượng.
        """
        url = f"{self.base_url}/stock-out"
        payload = {
            "barcode": barcode,
            "quantity": quantity
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.json().get("detail", "Lỗi không xác định khi xuất kho.")
                raise ValueError(error_msg)
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Mất kết nối tới máy chủ Backend khi thực hiện xuất kho.")