# app/api/routes.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.services.inventory_service import InventoryService
from app.models.db_models import ProductModel
from app.models.schemas import ProductCreateSchema, StockInSchema, StockOutSchema
# Khởi tạo router của FastAPI
router = APIRouter(prefix="/api/inventory", tags=["Inventory Management"])

# --- ĐỊNH NGHĨA CÁC PYDANTIC SCHEMAS (ÉP KIỂU ĐẦU VÀO) ---

class ProductCreateSchema(BaseModel):
    barcode: str = Field(..., description="Mã vạch duy nhất của sản phẩm")
    product_name: str = Field(..., description="Tên sản phẩm")
    strategy_type: str = Field(..., description="Chiến lược xuất kho: 'FIFO' hoặc 'LIFO'")

class StockInSchema(BaseModel):
    barcode: str = Field(..., description="Mã vạch sản phẩm nhập kho")
    quantity: int = Field(..., gt=0, description="Số lượng nhập kho, phải lớn hơn 0")
    expiry_date: str = Field(..., description="Hạn sử dụng (Định dạng: YYYY-MM-DD)")

class StockOutSchema(BaseModel):
    barcode: str = Field(..., description="Mã vạch sản phẩm xuất kho")
    quantity: int = Field(..., gt=0, description="Số lượng cần xuất, phải lớn hơn 0")


# --- HÀM TRỢ GIÚP LẤY KẾT NỐI DATABASE (DEPENDENCY) ---
# Hàm này giả định bạn đã cấu hình kết nối DB trong file app/database.py (sẽ viết ở bước sau)
from app.database import SessionLocal  # CHUẨN

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ĐỊNH NGHĨA CÁC ĐƯỜNG LINK API (ENDPOINTS) ---

@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreateSchema, db: Session = Depends(get_db)):
    """API 1: Tạo danh mục sản phẩm mới (Lưu SQL và Thêm vào cây BST trên RAM)"""
    service = InventoryService(db)
    # Đồng bộ nạp lại trạng thái cây từ DB hiện tại trước khi xử lý
    service.bootstrap_system()
    
    try:
        # 1. Lưu xuống SQL DB trước
        new_product = ProductModel(
            barcode=payload.barcode,
            product_name=payload.product_name,
            strategy_type=payload.strategy_type
        )
        db.add(new_product)
        db.commit()
        
        # 2. Đồng bộ thêm node vào cây BST trên RAM
        service.bst.insert(payload.barcode, payload.product_name, payload.strategy_type)
        
        return {"message": f"Tạo danh mục sản phẩm '{payload.product_name}' thành công."}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Mã vạch sản phẩm đã tồn tại.")

@router.post("/stock-in")
def stock_in(payload: StockInSchema, db: Session = Depends(get_db)):
    """API 2: Nhập kho lô hàng mới (Đẩy vào cuối Queue/Stack trên RAM và thêm vào SQL)"""
    service = InventoryService(db)
    service.bootstrap_system()
    
    try:
        # Chuyển đổi định dạng chuỗi ngày tháng từ UI gửi lên thành đối tượng datetime
        parsed_expiry = datetime.strptime(payload.expiry_date, "%Y-%m-%d")
        
        # Gọi tầng nghiệp vụ để xử lý đồng bộ RAM & SQL
        batch_id = service.process_stock_in(
            barcode=payload.barcode,
            quantity=payload.quantity,
            expiry_date=parsed_expiry
        )
        return {
            "message": "Nhập kho lô hàng mới thành công",
            "batch_id": batch_id,
            "barcode": payload.barcode,
            "quantity": payload.quantity
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stock-out")
def stock_out(payload: StockOutSchema, db: Session = Depends(get_db)):
    """API 3: Xuất kho tự động (Trừ kho lũy tiến trên RAM, xóa/sửa các lô dưới SQL)"""
    service = InventoryService(db)
    service.bootstrap_system()
    
    try:
        # Gọi thuật toán trừ kho lũy tiến lõi của hệ thống
        exported_batches = service.process_stock_out(
            barcode=payload.barcode,
            quantity_requested=payload.quantity
        )
        return {
            "message": f"Xuất kho thành công tổng cộng {payload.quantity} sản phẩm.",
            "barcode": payload.barcode,
            "details": exported_batches # Trả về mảng danh sách chi tiết các lô bị trừ số lượng cho UI hiển thị
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/products")
def get_catalog(db: Session = Depends(get_db)):
    """API 4: Lấy toàn bộ danh mục sản phẩm (Duyệt cây nhị phân In-Order sắp xếp theo mã vạch)"""
    service = InventoryService(db)
    service.bootstrap_system()
    
    # Chạy thuật toán duyệt cây để lấy danh sách sắp xếp tăng dần mà không cần ORDER BY của SQL
    sorted_products = service.bst.get_all_products()
    
    result = []
    for prod in sorted_products:
        result.append({
            "barcode": prod[0],
            "product_name": prod[1],
            "strategy_type": prod[2]
        })
    return {"total_products": len(result), "catalog": result}