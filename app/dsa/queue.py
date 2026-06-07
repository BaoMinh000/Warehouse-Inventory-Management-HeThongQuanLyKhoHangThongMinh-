# app/dsa/queue.py
from collections import deque
from typing import Any, Optional

class Queue:
    """Cấu trúc dữ liệu Hàng đợi (FIFO) ứng dụng quản lý lô hàng nhập trước - xuất trước"""
    def __init__(self):
        # Sử dụng deque thay vì list thuần để các thao tác popleft() đạt độ phức tạp O(1)
        self._storage: deque = deque()

    def enqueue(self, item: Any) -> None:
        """Thêm một lô hàng mới vào cuối hàng đợi"""
        self._storage.append(item)

    def dequeue(self) -> Optional[Any]:
        """Lấy và loại bỏ lô hàng đầu tiên (cũ nhất) ra khỏi hàng đợi"""
        if self.is_empty():
            return None
        return self._storage.popleft()

    def peek(self) -> Optional[Any]:
        """Xem thông tin lô hàng đầu chuỗi mà không loại bỏ khỏi hàng đợi"""
        if self.is_empty():
            return None
        return self._storage[0]

    def is_empty(self) -> bool:
        """Kiểm tra hàng đợi có trống hay không"""
        return len(self._storage) == 0

    def __len__(self) -> int:
        return len(self._storage)

    def get_all(self) -> list:
        """Trả về danh sách tất cả các lô hàng hiện tại để phục vụ việc duyệt/quét dữ liệu"""
        return list(self._storage)