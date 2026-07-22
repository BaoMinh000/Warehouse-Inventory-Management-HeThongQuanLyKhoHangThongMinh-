# tests/test_bst.py
import pytest
from dsa.bst import BinarySearchTree

def test_insert_and_search_product():
    """Kiểm tra xem thêm sản phẩm vào cây thì có tìm lại được đúng sản phẩm đó không"""
    # 1. Arrange: Chuẩn bị dữ liệu mẫu
    tree = BinarySearchTree()
    
    # 2. Act: Thực hiện hành động thêm và tìm kiếm
    tree.insert(barcode="893001", product_name="Mì Tôm", strategy_type="FIFO")
    found_node = tree.search("893001")
    
    # 3. Assert: Xác minh kết quả xem có đúng như kỳ vọng không
    assert found_node is not None
    assert found_node.product_name == "Mì Tôm"
    assert found_node.strategy_type == "FIFO"

def test_insert_duplicate_barcode_should_fail():
    """Kiểm tra xem nếu cố tình nhập trùng mã vạch thì hệ thống có chặn lại và báo lỗi không"""
    tree = BinarySearchTree()
    tree.insert(barcode="893001", product_name="Mì Tôm", strategy_type="FIFO")
    
    # Kỳ vọng hệ thống phải tung ra lỗi ValueError khi trùng mã vạch
    with pytest.raises(ValueError):
        tree.insert(barcode="893001", product_name="Sữa Tươi", strategy_type="LIFO")