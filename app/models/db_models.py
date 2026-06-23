# app/models/db_models.py
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import declarative_base, relationship

# Lớp nền tảng của SQLAlchemy để các model khác kế thừa
Base = declarative_base()

class ProductModel(Base):
    """
    Ánh xạ xuống bảng 'products' trong SQL.
    Lưu thông tin danh mục sản phẩm (Tương ứng với dữ liệu của một Node trên cây BST).
    """
    __tablename__ = 'products'

    # barcode đóng vai trò là Khóa chính dưới DB và là Key điều hướng trên cây BST
    product_name = Column(String(255), nullable=False)
    barcode = Column(String(50), primary_key=True)
    
    #Trường danh mục sản phẩm để đồng bộ với BST Node và API
    category = Column(String(100), nullable=False, default="Thực phẩm")
    
    # Chiến lược xuất kho: Chỉ cho phép nhận giá trị 'FIFO' hoặc 'LIFO'
    strategy_type = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Mối quan hệ 1-Nhiều: Một sản phẩm có thể có nhiều lô hàng trong kho
    batches = relationship("BatchModel", back_populates="product", cascade="all, delete-orphan")

    # Ràng buộc điều kiện dưới SQL: strategy_type bắt buộc phải là FIFO hoặc LIFO
    __table_args__ = (
        CheckConstraint("strategy_type IN ('FIFO', 'LIFO')", name="check_product_strategy_type"),
    )


class BatchModel(Base):
    """
    Ánh xạ xuống bảng 'batches' trong SQL.
    Lưu chi tiết từng lô hàng nhập vào (Tương ứng với các phần tử nằm trong Queue/Stack trên RAM).
    """
    __tablename__ = 'batches'

    batch_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    barcode = Column(String(50), ForeignKey('products.barcode', ondelete='CASCADE'), nullable=False)
    
    # Số lượng tồn kho của lô hàng đó (Bắt buộc phải >= 0)
    quantity = Column(Integer, nullable=False)
    expiry_date = Column(DateTime, nullable=False)   # Hạn sử dụng
    import_date = Column(DateTime, nullable=False, default=datetime.utcnow)   # Ngày nhập kho để phân tách FIFO/LIFO

    # Mối quan hệ ngược lại với bảng ProductModel
    product = relationship("ProductModel", back_populates="batches")

    # Ràng buộc điều kiện dưới SQL: Số lượng hàng trong lô không bao giờ được âm
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='check_batch_quantity_positive'),
    )


class InventoryLogModel(Base):
    """
    Ánh xạ xuống bảng 'inventory_logs' trong SQL.
    Lưu nhật ký vận hành (Audit Logs) phục vụ việc đối soát, kiểm tra xem ai đã nhập/xuất lô nào.
    """
    __tablename__ = 'inventory_logs'

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    barcode = Column(String(50), nullable=False)
    batch_id = Column(String(50), nullable=False)
    
    # Loại hành động: 'IMPORT' (Nhập kho) hoặc 'EXPORT' (Xuất kho)
    action_type = Column(String(20), nullable=False)
    
    # Số lượng biến động
    quantity_changed = Column(Integer, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow)

    # Ràng buộc điều kiện dưới SQL: hành động phải là IMPORT hoặc EXPORT
    __table_args__ = (
        CheckConstraint("action_type IN ('IMPORT', 'EXPORT')", name="check_log_action_type"),
    )