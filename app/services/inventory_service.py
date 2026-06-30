# app/services/inventory_service.py
# Lớp nghiệp vụ điều phối dữ liệu giữa cây BST trên RAM và Cơ sở dữ liệu SQL (Chỉ chạy ở Backend)
#Kết nối từ main.py -> routes.py -> inventory_service.py để xử lý logic nghiệp vụ đồng bộ RAM & SQL cho server backend
from datetime import datetime
from sqlalchemy.orm import Session
from app.dsa.bst import BinarySearchTree
from app.dsa.bst import Batch as DSABatch  # Alias để phân biệt với Model SQL
from app.models.db_models import ProductModel, BatchModel, InventoryLogModel

class InventoryService:
    """Lớp nghiệp vụ điều phối dữ liệu giữa cây BST trên RAM và Cơ sở dữ liệu SQL (Chỉ chạy ở Backend)"""
    def __init__(self, db_session: Session):
        self.db: Session = db_session
        self.bst = BinarySearchTree()

    def bootstrap_system(self, queue=None) -> int:
        """Nạp toàn bộ dữ liệu từ SQL DB lên cây RAM khi khởi động Server
            Hàm nạp dữ liệu từ DB lên RAM khi khởi động hệ thống.
            Nhận vào tham số queue để cập nhật trạng thái real-time qua UI.
        """
        try:        
            if self.bst.root is not None:
                return 0

            db_products = self.db.query(ProductModel).all()
            count = 0
            
            for db_prod in db_products:
                # 1. Nạp danh mục sản phẩm vào cây BST
                self.insert_product_to_ram(db_prod)
                
                # 2. Tìm Node vừa nạp để đổ các lô hàng tương ứng vào Queue/Stack của nó
                ram_node = self.bst.search(db_prod.barcode)
                
                db_batches = self.db.query(BatchModel)\
                    .filter(BatchModel.barcode == db_prod.barcode)\
                    .order_by(BatchModel.import_date.asc()).all()
                    
                for db_batch in db_batches:
                    ram_batch = DSABatch(
                        batch_id=db_batch.batch_id,
                        barcode=db_batch.barcode,
                        quantity=db_batch.quantity,
                        expiry_date=db_batch.expiry_date,
                        import_date=db_batch.import_date
                    )
                    if ram_node.strategy_type == "FIFO":
                        ram_node.stock_collection.enqueue(ram_batch)
                    else:
                        ram_node.stock_collection.push(ram_batch)
                count += 1
                
            if queue:
                queue.put(("SUCCESS", f"Đã nạp thành công {count} sản phẩm lên RAM!"))
            
        except Exception as e:
            # Bắn lỗi trực tiếp từ trong service nếu quá trình đọc ghi RAM thất bại
            if queue:
                queue.put(("ERROR", f"Lỗi trong quá trình bootstrap: {str(e)}"))
            raise e
        return count

    def insert_product_to_ram(self, db_prod) -> None:
        """Hàm helper bóc tách dữ liệu từ đối tượng DB/Dict nạp vào cây RAM của Backend"""
        barcode = getattr(db_prod, 'barcode', None) or db_prod.get('barcode')
        product_name = getattr(db_prod, 'product_name', None) or db_prod.get('product_name')
        strategy_type = getattr(db_prod, 'strategy_type', None) or db_prod.get('strategy_type')
        category = getattr(db_prod, 'category', 'Thực phẩm') or db_prod.get('category', 'Thực phẩm')

        self.bst.insert(
            barcode=barcode,
            product_name=product_name,
            strategy_type=strategy_type,
            category=category
        )

    def process_stock_in(self, barcode: str, quantity: int, expiry_date: datetime) -> str:
        """Nghiệp vụ NHẬP KHO: Đẩy lô hàng mới vào cuối Queue/Stack trên RAM và thêm vào SQL DB, trả về batch_id của lô hàng mới tạo"""
        ram_node = self.bst.search(barcode)
        if not ram_node:
            raise ValueError(f"Sản phẩm có mã vạch {barcode} chưa tồn tại trong danh mục.")

        import_time = datetime.now()  # Đồng bộ dùng datetime.now thuần Python cho SQLite

        # 1. Lưu vào CSDL SQL trước
        new_db_batch = BatchModel(
            barcode=barcode,
            quantity=quantity,
            expiry_date=expiry_date,
            import_date=import_time
        )
        # Gọi flush() để lấy batch_id tự động sinh ra từ CSDL trước khi commit
        self.db.add(new_db_batch)
        self.db.flush() 

        # 2. Tự động đồng bộ sang cấu trúc dữ liệu RAM Backend tương ứng
        ram_batch = DSABatch(
            barcode=barcode,
            batch_id=new_db_batch.batch_id,
            quantity=quantity,
            expiry_date=expiry_date,
            import_date=import_time
        )
        if ram_node.strategy_type == "FIFO":
            ram_node.stock_collection.enqueue(ram_batch) 
        else:
            ram_node.stock_collection.push(ram_batch)

        # 3. Ghi Nhật ký vận hành & Commit
        log = InventoryLogModel(barcode=barcode, batch_id=new_db_batch.batch_id, action_type="IMPORT", quantity_changed=quantity)
        self.db.add(log)
        self.db.commit() 
        
        return new_db_batch.batch_id

    def process_stock_out(self, barcode: str, quantity_requested: int) -> list:
        """
        NGHIỆP VỤ XUẤT KHO: Kiểm tra tồn kho trên RAM, nếu đủ thì tiến hành trừ dần số lượng từ Queue/Stack tương ứng,
        đồng thời cập nhật lại SQL DB và trả về chi tiết các lô hàng đã trừ bao gồm cả thông tin hỗ trợ UI.
        """
        ram_node = self.bst.search(barcode) 
        if not ram_node or ram_node.stock_collection.is_empty():
            raise ValueError("Sản phẩm không tồn tại hoặc đã hết hàng tồn kho.")

        # Lấy toàn bộ danh sách lô trên RAM để kiểm tra tổng số lượng khả dụng
        all_batches = ram_node.stock_collection.get_all()
        total_available = sum(b.quantity for b in all_batches)
        
        if total_available < quantity_requested:
            raise ValueError(f"Không đủ hàng xuất. Trong kho chỉ còn tổng cộng {total_available} sản phẩm.")

        remaining_request = quantity_requested
        export_details = []

        while remaining_request > 0 and not ram_node.stock_collection.is_empty():
            # Lấy lô hàng hiện tại trên RAM và đối chiếu với bản ghi SQL
            current_ram_batch = ram_node.stock_collection.peek()
            db_batch = self.db.query(BatchModel).filter(BatchModel.batch_id == current_ram_batch.batch_id).first()

            # Lưu lại các thông tin cần thiết trước khi có khả năng xóa đối tượng DB
            batch_id_str = db_batch.batch_id
            import_date_str = db_batch.import_date.strftime("%Y-%m-%d") if db_batch.import_date else "N/A"
            is_depleted = False # Cờ để đánh dấu lô hàng đã cạn kiệt hay chưa

            if current_ram_batch.quantity > remaining_request:
                qty_deducted = remaining_request
                current_ram_batch.quantity -= remaining_request
                db_batch.quantity -= remaining_request
                remaining_request = 0
            else:
                # Trường hợp bào sạch toàn bộ số lượng của lô này
                qty_deducted = current_ram_batch.quantity
                remaining_request -= current_ram_batch.quantity
                is_depleted = True
                
                # Giải phóng lô hàng ra khỏi RAM theo đúng chiến lược tương ứng
                if ram_node.strategy_type == "FIFO":
                    ram_node.stock_collection.dequeue() # Xóa lô hàng đầu tiên ra khỏi Queue
                else:
                    ram_node.stock_collection.pop() # Xóa lô hàng cuối cùng ra khỏi Stack
                
                # Xóa bản ghi lô hàng này ra khỏi Database SQL vì số lượng đã về 0
                self.db.delete(db_batch)

            # Append dữ liệu an toàn bằng các biến chuỗi đã sao lưu trước đó
            export_details.append({
                "batch_id": batch_id_str, 
                "quantity_deducted": qty_deducted,
                "is_depleted": is_depleted,
                "import_date": import_date_str
            })
            
            # Ghi nhận Nhật ký vận hành hệ thống
            log = InventoryLogModel(
                barcode=barcode, 
                batch_id=batch_id_str, 
                action_type="EXPORT", 
                quantity_changed=qty_deducted
            )
            self.db.add(log)

        self.db.commit()
        return export_details    
    
    def get_inventory_history(self) -> list:
        """API 6: Lấy toàn bộ lịch sử biến động kho từ SQL DB, trả về dạng list các dict để UI hiển thị (Có thể thêm tham số filter để lọc theo Nhập/Xuất)"""
        logs = self.db.query(InventoryLogModel).order_by(InventoryLogModel.logged_at.desc()).all()
        history = []
        for log in logs:
            history.append({
                "timestamp": log.logged_at.strftime("%Y-%m-%d %H:%M:%S"),
                "barcode": log.barcode,
                "batch_id": log.batch_id,
                "action_type": log.action_type,
                "quantity_changed": log.quantity_changed
            })
        return history
    
    def get_product_stock(self, barcode: str) -> dict:
        """API 7: Lấy thông tin tồn kho hiện tại của một sản phẩm theo mã vạch từ RAM, trả về dict chứa tổng số lượng và danh sách chi tiết các lô hàng"""
        ram_node = self.bst.search(barcode)
        if not ram_node:
            return {"total_quantity": 0, "batches": []}

        all_batches = ram_node.stock_collection.get_all()
        print(f"[DEBUG] Lấy danh sách lô hàng hiện có cho barcode {barcode}: {all_batches}")
        total_quantity = sum(b.quantity for b in all_batches)
        batch_details = [
            {
                "batch_id": b.batch_id,
                "barcode": b.barcode,
                "quantity": b.quantity, 
                "expiry_date": b.expiry_date.strftime("%Y-%m-%d"), 
                "import_date": b.import_date.strftime("%Y-%m-%d %H:%M:%S")
            } for b in all_batches
            ]

        return {"total_quantity": total_quantity, "batches": batch_details}