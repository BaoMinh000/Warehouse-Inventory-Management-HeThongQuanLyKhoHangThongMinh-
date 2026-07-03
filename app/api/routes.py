# app/api/routes.py
# Đây là file định nghĩa các đường link API (Endpoints) của FastAPI, xử lý logic nghiệp vụ và tương tác với DB Models thông qua InventoryService. Các API này sẽ được gọi từ UI thông qua lớp API Client.
# File ở Server Backend
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.services.inventory_service import InventoryService
from app.models.db_models import ProductModel

# Khởi tạo router của FastAPI
router = APIRouter(prefix="/api/inventory", tags=["Inventory Management"])

# --- ĐỊNH NGHĨA CÁC PYDANTIC SCHEMAS (ÉP KIỂU ĐẦU VÀO) ---

class ProductCreateSchema(BaseModel):
    barcode: str = Field(..., description="Mã vạch duy nhất của sản phẩm")
    product_name: str = Field(..., description="Tên sản phẩm")
    category: str = Field(default="Thực phẩm", description="Danh mục sản phẩm")
    strategy_type: str = Field(..., description="Chiến lược xuất kho: 'FIFO' hoặc 'LIFO'")

class StockInSchema(BaseModel):
    barcode: str = Field(..., description="Mã vạch sản phẩm nhập kho")
    quantity: int = Field(..., gt=0, description="Số lượng nhập kho, phải lớn hơn 0")
    expiry_date: str = Field(..., description="Hạn sử dụng (Định dạng: YYYY-MM-DD)")

class StockOutSchema(BaseModel):
    barcode: str = Field(..., description="Mã vạch sản phẩm xuất kho")
    quantity: int = Field(..., gt=0, description="Số lượng cần xuất, phải lớn hơn 0")

class ProductResponseSchema(BaseModel):
    barcode: str
    product_name: str
    category: str
    strategy_type: str
# --- HÀM TRỢ GIÚP LẤY KẾT NỐI DATABASE (DEPENDENCY) ---
from app.database import SessionLocal 

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
    service.bootstrap_system()
    
    try:
        # 1. Lưu xuống SQL DB trước
        new_product = ProductModel(
            barcode=payload.barcode,
            product_name=payload.product_name,
            category=payload.category,
            strategy_type=payload.strategy_type
        )
        db.add(new_product)
        db.commit()
        
        # 2. Đồng bộ thêm node vào cây BST trên RAM
        service.bst.insert(
            barcode=payload.barcode, 
            product_name=payload.product_name, 
            strategy_type=payload.strategy_type,
            category=payload.category
        )
        
        return {"message": f"Tạo danh mục sản phẩm '{payload.product_name}' thành công."}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        # Giữ lại logic phân tích lỗi trùng khóa hoặc lỗi hệ thống tổng quát
        if "UNIQUE" in str(e) or "Mã vạch" in str(e):
            raise HTTPException(status_code=400, detail=f"Mã vạch {payload.barcode} đã tồn tại trong cơ sở dữ liệu.")
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi tạo sản phẩm: {str(e)}")

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi nhập kho: {str(e)}")

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
            "details": exported_batches # Trả về danh sách chi tiết các lô bị trừ số lượng
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi xuất kho: {str(e)}")

@router.get("/products")
def get_catalog(db: Session = Depends(get_db)):
    """API 4: Lấy toàn bộ danh mục sản phẩm (Duyệt cây nhị phân In-Order sắp xếp theo mã vạch)"""
    service = InventoryService(db)
    service.bootstrap_system()
    
    # Chạy thuật toán duyệt cây để lấy danh sách sắp xếp tăng dần theo mã vạch
    sorted_products = service.bst.get_all_products()
    
    result = []
    for prod in sorted_products:
        result.append({
            "product_name": prod[1],
            "barcode": prod[0],
            "category": prod[2],
            "strategy_type": prod[3]
        })
    return {"total_products": len(result), "catalog": result}

@router.get("/product/{barcode}")
def search_product(barcode: str, db: Session = Depends(get_db)):
    """API 5: Tìm kiếm sản phẩm theo mã vạch (Tìm kiếm trên cây BST trên RAM)"""
    service = InventoryService(db)
    service.bootstrap_system()
    
    product_node = service.bst.search(barcode)
    if not product_node:
        raise HTTPException(status_code=404, detail=f"Sản phẩm có mã vạch {barcode} không tồn tại.")
    
    return {
        "barcode": product_node.barcode,
        "product_name": product_node.product_name,
        "category": product_node.category,
        "strategy_type": product_node.strategy_type
    }
    
@router.get("/history")
def history_view(db: Session = Depends(get_db)):
    """API 6: Lấy toàn bộ lịch sử biến động kho (Dữ liệu mẫu tĩnh cho UI)"""
    # Lấy dữ liệu từ SQL DB
    service = InventoryService(db)
    HISTORY_DATA = service.get_inventory_history()
    return {"history": HISTORY_DATA}

@router.get("/product-stock/{barcode}")
def get_product_stock(barcode: str, db: Session = Depends(get_db)):
    """API 7: Lấy thông tin tồn kho hiện tại của một sản phẩm theo mã vạch"""
    service = InventoryService(db)
    service.bootstrap_system()
    
    stock_info = service.get_product_stock(barcode)
    return stock_info

@router.get("/batch-details/{batch_id}")
def get_batch_details(batch_id: int, db: Session = Depends(get_db)):
    """API 8: Lấy thông tin chi tiết của một lô hàng theo batch_id"""
    service = InventoryService(db)
    service.bootstrap_system()
    
    batch_details = service.get_batch_details(batch_id)
    if not batch_details:
        raise HTTPException(status_code=404, detail=f"Lô hàng với batch_id {batch_id} không tồn tại.")
    
    return batch_details

@router.post("/update-product/{barcode}")
def update_product(barcode: str, payload: ProductCreateSchema, db: Session = Depends(get_db)):
    """API 9: Cập nhật thông tin sản phẩm theo mã vạch"""
    service = InventoryService(db)
    service.bootstrap_system()
    
    try:
        updated_product = service.update_product_info(
            barcode=barcode,
            product_name=payload.product_name,
            category=payload.category,
            strategy_type=payload.strategy_type
        )
        return {
            "message": f"Cập nhật thông tin sản phẩm '{barcode}' thành công.",
            "updated_product": updated_product
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi cập nhật sản phẩm: {str(e)}")