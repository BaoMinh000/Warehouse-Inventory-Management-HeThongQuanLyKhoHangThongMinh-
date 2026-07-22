# app/dsa/bst.py
from typing import Optional, List, Tuple
from dsa.queue import Queue
from dsa.stack import Stack

class Batch: # Lô hàng
    """Đại diện cho một lô hàng cụ thể trong kho"""
    def __init__(self, batch_id: str, barcode: str, quantity: int, expiry_date, import_date):
        self.batch_id = batch_id
        self.barcode = barcode
        self.quantity = quantity
        self.expiry_date = expiry_date
        self.import_date = import_date
     
class ProductNode: 
    """Đại diện cho một Node sản phẩm trên cây tìm kiếm nhị phân (BST)"""
    def __init__(self, barcode: str, product_name: str, strategy_type: str, category: str = "Thực phẩm"):
        self.barcode: str = barcode               
        self.product_name: str = product_name     
        self.category: str = category
        self.strategy_type: str = strategy_type   # Chiến lược xuất kho: "FIFO" hoặc "LIFO"  

        if strategy_type == "FIFO":
            self.stock_collection = Queue()
        elif strategy_type == "LIFO":
            self.stock_collection = Stack()
        else:
            raise ValueError("Chiến lược xuất kho phải là 'FIFO' hoặc 'LIFO'")

        self.left: Optional[ProductNode] = None
        self.right: Optional[ProductNode] = None


class BinarySearchTree: 
    """Cây tìm kiếm nhị phân quản lý danh mục toàn bộ sản phẩm in-memory"""
    def __init__(self):
        self.root: Optional[ProductNode] = None

    def insert(self, barcode: str, product_name: str, strategy_type: str, category: str = "Thực phẩm") -> None:
        """Thêm một sản phẩm mới vào danh mục cây BST"""
        new_node = ProductNode(barcode, product_name, strategy_type, category)
        if self.root is None:
            self.root = new_node
            return

        current = self.root
        while True:
            if barcode < current.barcode:
                if current.left is None:
                    current.left = new_node
                    break
                current = current.left
            elif barcode > current.barcode:
                if current.right is None:
                    current.right = new_node
                    break
                current = current.right
            else:
                # Trường hợp trùng mã vạch (Barcode đã tồn tại)
                raise ValueError(f"Mã vạch {barcode} đã tồn tại trong danh mục kho.")

    def search(self, barcode: str) -> Optional[ProductNode]:
        """Tìm kiếm sản phẩm theo mã vạch với độ phức tạp trung bình O(log n)"""
        current = self.root
        while current is not None:
            if barcode == current.barcode:
                return current
            elif barcode < current.barcode:
                current = current.left
            else:
                current = current.right
        return None

    def get_all_products(self) -> List[Tuple[str, str, str, str]]:
        """Duyệt cây theo thứ tự In-Order để lấy toàn bộ danh mục sắp xếp theo Barcode tăng dần"""
        products = []
        self._in_order(self.root, products)
        return products

    def _in_order(self, node: Optional[ProductNode], products: list):
        if node is not None:
            self._in_order(node.left, products)
            products.append((node.barcode, node.product_name, node.category, node.strategy_type))
            self._in_order(node.right, products)

    def delete(self, barcode: str) -> bool:
        """Xóa một sản phẩm khỏi cây danh mục (Xử lý đủ 3 trường hợp xóa cấu trúc)"""
        if self.search(barcode) is None:
            return False
        self.root = self._delete_node(self.root, barcode)
        return True

    def _delete_node(self, root: Optional[ProductNode], barcode: str) -> Optional[ProductNode]:
        if root is None:
            return root

        if barcode < root.barcode:
            root.left = self._delete_node(root.left, barcode)
        elif barcode > root.barcode:
            root.right = self._delete_node(root.right, barcode)
        else:
            # Trường hợp 1: Node lá (không có con) hoặc Trường hợp 2: Node chỉ có 1 con
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left

            # Trường hợp 3: Node có cả 2 con
            # Tìm node nhỏ nhất ở nhánh bên phải (In-order Successor) để thế mạng
            temp = self._min_value_node(root.right)
            root.barcode = temp.barcode
            root.product_name = temp.product_name
            root.category = temp.category
            root.strategy_type = temp.strategy_type
            root.stock_collection = temp.stock_collection
            
            # Xóa node thế mạng cũ ở nhánh phải
            root.right = self._delete_node(root.right, temp.barcode)

        return root

    def _min_value_node(self, node: ProductNode) -> ProductNode:
        current = node
        while current.left is not None:
            current = current.left
        return current
    
    def get_product_batches(self, barcode: str) -> Optional[List[Batch]]:
        """Lấy danh sách các lô hàng của sản phẩm theo mã vạch"""
        product_node = self.search(barcode)
        if product_node is None:
            return None
        
        # Trích xuất danh sách lô hàng từ cấu trúc lưu trữ (Queue hoặc Stack)
        batches = []
        if isinstance(product_node.stock_collection, Queue):
            temp_queue = Queue()
            while not product_node.stock_collection.is_empty():
                batch = product_node.stock_collection.dequeue()
                batches.append(batch)
                temp_queue.enqueue(batch)
            # Khôi phục lại trạng thái ban đầu của Queue
            while not temp_queue.is_empty():
                product_node.stock_collection.enqueue(temp_queue.dequeue())
        elif isinstance(product_node.stock_collection, Stack):
            temp_stack = Stack()
            while not product_node.stock_collection.is_empty():
                batch = product_node.stock_collection.pop()
                batches.append(batch)
                temp_stack.push(batch)
            # Khôi phục lại trạng thái ban đầu của Stack
            while not temp_stack.is_empty():
                product_node.stock_collection.push(temp_stack.pop())
        
        return batches
    