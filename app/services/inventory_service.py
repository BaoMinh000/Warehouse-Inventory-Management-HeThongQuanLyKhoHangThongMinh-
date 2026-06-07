# app/services/inventory_service.py
from datetime import datetime
from sqlalchemy.orm import Session
from app.dsa.bst import BinarySearchTree, ProductNode
from app.dsa.bst import Batch as DSABatch  # Alias để phân biệt với Model SQL
from app.models.db_models import ProductModel, BatchModel, InventoryLogModel

class InventoryService:
    """Lớp nghiệp vụ điều phối dữ liệu giữa cây BST trên RAM và Cơ sở dữ liệu SQL"""
    def __init__(self, db_session: Session):
        self.db: Session = db_session
        # Khởi tạo một cây trống trên RAM cho Service này quản lý
        self.bst = BinarySearchTree()

    def bootstrap_system(self) -> int:
        """
        HÀM KHỞI TẠO: Chạy khi bật server.
        Đọc toàn bộ dữ liệu từ SQL DB nạp lên RAM để dựng thành cây BST hoàn chỉnh.
        """
        # 1. Đọc tất cả sản phẩm từ SQL
        db_products = self.db.query(ProductModel).all()
        count = 0
        
        for db_prod in db_products:
            # 2. Thêm sản phẩm vào cây BST trên RAM
            self.bst.insert(
                barcode=db_prod.barcode,
                product_name=db_prod.product_name,
                strategy_type=db_prod.strategy_type
            )
            
            # 3. Tìm lại Node vừa thêm để nạp các lô hàng (Batches) của nó vào Queue/Stack
            ram_node = self.bst.search(db_prod.barcode)
            
            # Sắp xếp các lô hàng theo thời gian nhập kho tăng dần từ SQL
            db_batches = self.db.query(BatchModel)\
                .filter(BatchModel.barcode == db_prod.barcode)\
                .order_by(BatchModel.import_date.asc()).all()
                
            for db_batch in db_batches:
                ram_batch = DSABatch(
                    batch_id=db_batch.batch_id,
                    quantity=db_batch.quantity,
                    expiry_date=db_batch.expiry_date,
                    import_date=db_batch.import_date
                )
                # Nạp lô hàng vào cấu trúc RAM (Hàm tự động Enqueue hoặc Push tùy cấu hình sản phẩm)
                if ram_node.strategy_type == "FIFO":
                    ram_node.stock_collection.enqueue(ram_batch)
                else:
                    ram_node.stock_collection.push(ram_batch)
            count += 1
        return count

    def process_stock_in(self, barcode: str, quantity: int, expiry_date: datetime) -> str:
        """Nghiệp vụ NHẬP KHO: Cập nhật song song cả RAM (DSA) và CSDL (SQL)"""
        # 1. Tìm sản phẩm trên cây RAM
        ram_node = self.bst.search(barcode)
        if not ram_node:
            raise ValueError(f"Sản phẩm có mã vạch {barcode} chưa tồn tại trong danh mục. Hãy tạo danh mục trước.")

        import_time = datetime.utcnow()

        # 2. Lưu vào CSDL SQL trước để lấy một thực thể lưu trữ vĩnh viễn
        new_db_batch = BatchModel(
            barcode=barcode,
            quantity=quantity,
            expiry_date=expiry_date,
            import_date=import_time
        )
        self.db.add(new_db_batch)
        self.db.flush() # Lấy batch_id tự động sinh ra mà chưa commit hẳn xuống ổ cứng

        # 3. Đồng bộ nạp vào cấu trúc dữ liệu trên RAM
        ram_batch = DSABatch(
            batch_id=new_db_batch.batch_id,
            quantity=quantity,
            expiry_date=expiry_date,
            import_date=import_time
        )
        if ram_node.strategy_type == "FIFO":
            ram_node.stock_collection.enqueue(ram_batch)
        else:
            ram_node.stock_collection.push(ram_batch)

        # 4. Ghi Nhật ký vận hành (Audit Log) xuống SQL
        log = InventoryLogModel(barcode=barcode, batch_id=new_db_batch.batch_id, action_type="IMPORT", quantity_changed=quantity)
        self.db.add(log)
        
        self.db.commit() # Xác nhận lưu tất cả thay đổi an toàn xuống ổ cứng
        return new_db_batch.batch_id

    def process_stock_out(self, barcode: str, quantity_requested: int) -> list:
        """
        NGHIỆP VỤ XUẤT KHO (THUẬT TOÁN TRỪ KHO LŨY TIẾN):
        Tìm sản phẩm trên cây BST, bóc tách trừ số lượng ở các lô hàng (Queue/Stack) trên RAM
        và cập nhật lệnh UPDATE/DELETE tương ứng xuống các hàng trong SQL.
        """
        ram_node = self.bst.search(barcode)
        if not ram_node or ram_node.stock_collection.is_empty():
            raise ValueError("Sản phẩm không tồn tại hoặc đã hết hàng tồn kho.")

        # Lấy danh sách lô hàng hiện tại trên RAM để kiểm tra tổng số lượng trước
        all_batches = ram_node.stock_collection.get_all()
        total_available = sum(b.quantity for b in all_batches)
        
        if total_available < quantity_requested:
            raise ValueError(f"Không đủ hàng xuất. Trong kho chỉ còn tổng cộng {total_available} sản phẩm.")

        remaining_request = quantity_requested
        export_details = [] # Lưu vết thông tin các lô bị trừ để báo cáo lên UI

        # Chạy vòng lặp bóc tách trừ kho lũy tiến
        while remaining_request > 0 and not ram_node.stock_collection.is_empty():
            # Xem lô hàng đầu chuỗi (FIFO) hoặc đỉnh ngăn xếp (LIFO)
            current_ram_batch = ram_node.stock_collection.peek()
            
            # Tìm dòng lô hàng tương ứng dưới SQL DB để chuẩn bị update
            db_batch = self.db.query(BatchModel).filter(BatchModel.batch_id == current_ram_batch.batch_id).first()

            if current_ram_batch.quantity > remaining_request:
                # Trường hợp lô hàng hiện tại dư sức đáp ứng đơn hàng
                qty_deducted = remaining_request
                current_ram_batch.quantity -= remaining_request
                db_batch.quantity -= remaining_request
                remaining_request = 0
            else:
                # Trường hợp lô hàng hiện tại thiếu hoặc vừa đủ, xuất sạch lô này và giải phóng
                qty_deducted = current_ram_batch.quantity
                remaining_request -= current_ram_batch.quantity
                
                # Xóa lô hàng đã cạn trên RAM (Dequeue hoặc Pop)
                if ram_node.strategy_type == "FIFO":
                    ram_node.stock_collection.dequeue()
                else:
                    ram_node.stock_collection.pop()
                
                # Xóa dòng lô hàng đã cạn dưới SQL DB
                self.db.delete(db_batch)

            # Ghi vết chi tiết lô xuất
            export_details.append({"batch_id": db_batch.batch_id, "quantity_deducted": qty_deducted})
            
            # Ghi log vận hành xuống SQL
            log = InventoryLogModel(barcode=barcode, batch_id=db_batch.batch_id, action_type="EXPORT", quantity_changed=qty_deducted)
            self.db.add(log)

        self.db.commit() # Lưu toàn bộ kết quả giao dịch xuống ổ cứng SQL
        return export_details