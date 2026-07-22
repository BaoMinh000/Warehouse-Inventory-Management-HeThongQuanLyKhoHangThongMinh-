# app/dsa/stack.py
from typing import Any, Optional

class Stack:
    """Cấu trúc dữ liệu Ngăn xếp (LIFO) ứng dụng quản lý lô hàng nhập sau - xuất trước"""
    def __init__(self):
        self._storage: list = []

    def push(self, item: Any) -> None:
        """Đẩy một lô hàng mới lên đỉnh ngăn xếp"""
        self._storage.append(item)

    def pop(self) -> Optional[Any]:
        """Lấy và loại bỏ lô hàng ở đỉnh (mới nhất) ra khỏi ngăn xếp"""
        if self.is_empty():
            return None
        return self._storage.pop()

    def peek(self) -> Optional[Any]:
        """Xem thông tin lô hàng ở đỉnh ngăn xếp mà không loại bỏ"""
        if self.is_empty():
            return None
        return self._storage[-1]

    def is_empty(self) -> bool:
        """Kiểm tra ngăn xếp có trống hay không"""
        return len(self._storage) == 0

    def __len__(self) -> int:
        return len(self._storage)

    def get_all(self) -> list:
        """Trả về danh sách tất cả các lô hàng (từ đáy đến đỉnh)"""
        return self._storage