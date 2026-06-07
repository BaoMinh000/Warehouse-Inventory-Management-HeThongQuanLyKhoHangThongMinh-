# main.py
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import engine và SessionLocal từ file database độc lập
from app.database import engine, SessionLocal
from app.models.db_models import Base
from app.api.routes import router as inventory_router
from app.services.inventory_service import InventoryService

# 1. CẤU HÌNH TIẾN TRÌNH LIFESPAN
@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    print("[SYSTEM] Đang kết nối Cơ sở dữ liệu và khởi tạo các cấu trúc bảng...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        service = InventoryService(db)
        loaded_count = service.bootstrap_system()
        print(f"[SYSTEM] Khởi động thành công! Đã nạp {loaded_count} sản phẩm lên Cây BST trên RAM.")
    except Exception as e:
        print(f"[SYSTEM] Lỗi khi nạp dữ liệu lên RAM: {str(e)}")
    finally:
        db.close()

    yield
    print("[SYSTEM] Đang tắt hệ thống giải phóng bộ nhớ...")


# 2. KHỞI TẠO FASTAPI
app = FastAPI(
    title="Smart Warehouse Inventory Management System",
    description="Hệ thống Quản lý Kho sử dụng cấu trúc dữ liệu BST, Queue, Stack kết hợp SQL DB",
    version="2.0.0",
    lifespan=lifespan
)

# 3. CẤU HÌNH CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. ĐĂNG KÝ CỔNG API VÀO HỆ THỐNG SERVER
app.include_router(inventory_router)

# 5. LỆNH CHẠY SERVER
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)