# backend/app/main_api.py
import os
import sys
import time
import multiprocessing
import uvicorn
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Import engine và SessionLocal từ file database độc lập
from database import engine, SessionLocal
from models.db_models import Base
from api.routes import router as inventory_router
from services.inventory_service import InventoryService

# Biến toàn cục để share queue trong cùng tiến trình backend FastAPI
_backend_queue = None

# =========================================================================
# 1. CẤU HÌNH TIẾN TRÌNH LIFESPAN (QUẢN LÝ QUA BOOTSTRAP_SYSTEM)
# =========================================================================
@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    global _backend_queue
    
    if _backend_queue:
        _backend_queue.put(("START", "Đang kết nối Cơ sở dữ liệu và khởi tạo cấu trúc bảng..."))
        
    Base.metadata.create_all(bind=engine)

    if _backend_queue:
        _backend_queue.put(("DB_READY", "Đang nạp dữ liệu từ SQL lên RAM..."))

    db = SessionLocal()
    try:
        service = InventoryService(db)
        # Truyền _backend_queue vào đây: Hàm bootstrap_system sẽ chịu trách nhiệm báo SUCCESS hoặc ERROR nội bộ
        service.bootstrap_system(queue=_backend_queue)
        
    except Exception as e:
        if _backend_queue:
            _backend_queue.put(("ERROR", f"Lỗi khởi động hệ thống: {str(e)}"))
    finally:
        db.close()
    
    yield
    print("[SYSTEM] Đang tắt hệ thống giải phóng bộ nhớ...")


# =========================================================================
# 2. KHỞI TẠO FASTAPI VÀ CẤU HÌNH MIDDLEWARE
# =========================================================================
app = FastAPI(
    title="Smart Warehouse Inventory Management System",
    description="Hệ thống Quản lý Kho sử dụng cấu trúc dữ liệu BST, Queue, Stack kết hợp SQL DB",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn router từ routes.py vào FastAPI app
app.include_router(inventory_router)


# =========================================================================
# 3. ĐIỀU HƯỚNG KHỞI CHẠY ĐA TIẾN TRÌNH (UI + BACKEND)
# =========================================================================
def start_backend(q: multiprocessing.Queue):
    """Hàm chạy máy chủ FastAPI ngầm trên cổng 8000"""
    global _backend_queue
    _backend_queue = q  # Lưu queue vào biến toàn cục của tiến trình backend
    
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)), reload=False, log_level="info")

def start_frontend(q: multiprocessing.Queue):
    """Hàm khởi chạy cửa sổ giao diện PyQt6 kết hợp nhận tín hiệu từ Queue"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    
    # SỬA TẠI ĐÂY: Import từ thư mục `ui` (gọi tuyệt đối từ thư mục gốc)
    from ui.main_window import MainWindow
    from ui.screens.splash_screen import SplashScreen
    from services.api_client import InventoryAPIClient
    
    qt_app = QApplication(sys.argv)
    qt_app.setQuitOnLastWindowClosed(True)
    
    splash = SplashScreen()
    splash.show()
    
    api_client = InventoryAPIClient()

    print("⏳ [UI] Đang chờ tín hiệu sẵn sàng từ Backend...")

    def check_queue():
        """Hàm lặp kiểm tra trạng thái tiến trình backend gửi về qua Queue"""
        while not q.empty():
            status, message = q.get()
            print(f"🔹 [UI Nhận Tín Hiệu] {status}: {message}")
            
            # PHÂN CHIA PHẦN TRĂM THEO TỪNG TRẠNG THÁI NHẬN ĐƯỢC
            if status == "START":
                splash.set_progress(20, message)

            elif status == "DB_READY":
                splash.set_progress(60, message)

            elif status == "ERROR":
                print(f"❌ Khởi động thất bại: {message}")
                splash.set_progress(0, f"❌ Lỗi: {message}")
                timer.stop()
                QTimer.singleShot(2000, qt_app.quit)
                return

            elif status == "SUCCESS":
                print("🚀 Backend đã load xong dữ liệu lên BST! Đang hiển thị giao diện...")
                
                # Đẩy thanh tiến trình lên 100% cùng thông báo thành công
                splash.set_progress(100, f"🚀 {message}")
                
                # Ép giao diện render lại thanh 100% và đứng đợi một chút để người dùng kịp nhìn
                qt_app.processEvents()
                time.sleep(0.8)

                # Khởi tạo và hiển thị cửa sổ chính WMS
                ui_window = MainWindow(api_client=api_client)
                ui_window.show()
                
                qt_app.main_window = ui_window 
                splash.close()
                
                timer.stop()
                return

    timer = QTimer()
    timer.timeout.connect(check_queue)
    timer.start(100)

    exit_code = qt_app.exec()
    sys.exit(exit_code)