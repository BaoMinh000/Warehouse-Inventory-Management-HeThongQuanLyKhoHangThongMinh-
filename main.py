# main.py
import os
from dotenv import load_dotenv
load_dotenv()
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import multiprocessing
import sys
import time

# Import engine và SessionLocal từ file database độc lập
from app.database import engine, SessionLocal
from app.models.db_models import Base
from app.api.routes import router as inventory_router
from app.services.inventory_service import InventoryService

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
    
    # SỬA TẠI ĐÂY: Truyền trực tiếp đối tượng app thay vì chuỗi "main:app"
    uvicorn.run(app, host=os.getenv("HOST"), port=int(os.getenv("PORT")), reload=False, log_level="info")

def start_frontend(q: multiprocessing.Queue):
    """Hàm khởi chạy cửa sổ giao diện PyQt6 kết hợp nhận tín hiệu từ Queue"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from ui.main_window import MainWindow
    from ui.screens.splash_screen import SplashScreen
    from app.services.api_client import InventoryAPIClient
    
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
  
if __name__ == "__main__":
    # Hỗ trợ chạy đa tiến trình an toàn trên môi trường Windows/macOS
    multiprocessing.freeze_support()

    print("📦 [DỰ ÁN KHO] Đang khởi động đồng thời Backend FastAPI và Giao diện PyQt6...")

    # Khởi tạo Queue dùng chung giữa các tiến trình
    status_queue = multiprocessing.Queue()

    # Khởi tạo 2 tiến trình độc lập và truyền chung instance status_queue
    backend_process = multiprocessing.Process(target=start_backend, args=(status_queue,), name="FastAPI_Backend")
    frontend_process = multiprocessing.Process(target=start_frontend, args=(status_queue,), name="PyQt6_Frontend")

    # Bật tiến trình
    backend_process.start()
    frontend_process.start()

    try:
        # Giữ ứng dụng chạy cho đến khi người dùng tắt cửa sổ UI (Frontend kết thúc)
        frontend_process.join()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Nhận tín hiệu tắt hệ thống từ bàn phím...")
    finally:
        # Khi UI đóng, tự động hủy tiến trình Backend để giải phóng cổng 8000
        if backend_process.is_alive():
            print("[SYSTEM] Đang dọn dẹp và giải phóng cổng Server ngầm...")
            backend_process.terminate()
            backend_process.join()
        print("[SYSTEM] Hệ thống đã đóng an toàn.")

# # main.py
# import os
# from dotenv import load_dotenv
# load_dotenv()
# from contextlib import asynccontextmanager
# import uvicorn
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# import multiprocessing
# import sys
# import time

# # Import engine và SessionLocal từ file database độc lập
# from app.database import engine, SessionLocal
# from app.models.db_models import Base
# from app.api.routes import router as inventory_router
# from app.services.inventory_service import InventoryService

# # =========================================================================
# # 1. CẤU HÌNH TIẾN TRÌNH LIFESPAN (GIỮ NGUYÊN LOGIC CŨ)
# # =========================================================================
# @asynccontextmanager
# async def lifespan(app_instance: FastAPI):
#     print("[SYSTEM] Đang kết nối Cơ sở dữ liệu và khởi tạo các cấu trúc bảng...")
#     Base.metadata.create_all(bind=engine)

#     db = SessionLocal()
#     try:
#         service = InventoryService(db)
#         loaded_count = service.bootstrap_system()
#         print(f"[SYSTEM] Khởi động thành công! Đã nạp {loaded_count} sản phẩm lên Cây BST trên RAM.")
#     except Exception as e:
#         print(f"[SYSTEM] Lỗi khi nạp dữ liệu lên RAM: {str(e)}")
#     finally:
#         db.close()
    
#     yield
#     print("[SYSTEM] Đang tắt hệ thống giải phóng bộ nhớ...")


# # =========================================================================
# # 2. KHỞI TẠO FASTAPI VÀ CẤU HÌNH MIDDLEWARE
# # =========================================================================
# app = FastAPI(
#     title="Smart Warehouse Inventory Management System",
#     description="Hệ thống Quản lý Kho sử dụng cấu trúc dữ liệu BST, Queue, Stack kết hợp SQL DB",
#     version="2.0.0",
#     lifespan=lifespan
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(inventory_router)


# # =========================================================================
# # 3. ĐIỀU HƯỚNG KHỞI CHẠY ĐA TIẾN TRÌNH (UI + BACKEND)
# # =========================================================================
# def start_backend():
#     """Hàm chạy máy chủ FastAPI ngầm trên cổng 8000"""
#     # Tắt tính năng reload khi chạy đa tiến trình đóng gói để tránh xung đột luồng UI
#     uvicorn.run("main:app", host=os.getenv("HOST"), port=int(os.getenv("PORT")), reload=False, log_level="info")

# def start_frontend():
#     """Hàm khởi chạy cửa sổ giao diện PyQt6"""
#     # Import đặt bên trong hàm để tránh vòng lặp import (Circular Import) nếu có
#     from PyQt6.QtWidgets import QApplication
#     from ui.main_window import MainWindow
#     from app.services.api_client import InventoryAPIClient
#     # 1. Chờ 1.5 giây để máy chủ Backend kịp hoàn tất tiến trình bootstrap dữ liệu lên RAM
#     time.sleep(1.5)
    
#     # 2. Khởi tạo ứng dụng Qt
#     qt_app = QApplication(sys.argv)
#     #    Khỏi tạo API Client để UI có thể gọi API ngay khi cần (ví dụ: nạp danh mục sản phẩm)
#     api_client = InventoryAPIClient()

#     # 3. Đảm bảo ứng dụng đóng sạch sẽ, không bị treo tiến trình ngầm khi bấm [X]
#     qt_app.setQuitOnLastWindowClosed(True)
    
#     # 4. Khởi tạo và hiển thị cửa sổ chính WMS 2.0
#     ui_window = MainWindow(api_client=api_client)
#     ui_window.show()
    
#     # 5. Chạy vòng lặp sự kiện của Qt và bắt mã lỗi khi thoát
#     exit_code = qt_app.exec()
    
#     # Thực hiện dọn dẹp backend tại đây nếu cần (ví dụ: đóng kết nối DB, ngắt kết nối socket...)
#     # print("Đang tắt hệ thống quản lý kho...")
    
#     sys.exit(exit_code)


# if __name__ == "__main__":
#     # Hỗ trợ chạy đa tiến trình an toàn trên môi trường Windows/macOS
#     multiprocessing.freeze_support()

#     print("📦 [DỰ ÁN KHO] Đang khởi động đồng thời Backend FastAPI và Giao diện PyQt6...")

#     # Khởi tạo 2 tiến trình độc lập
#     backend_process = multiprocessing.Process(target=start_backend, name="FastAPI_Backend")
#     frontend_process = multiprocessing.Process(target=start_frontend, name="PyQt6_Frontend")

#     # Bật tiến trình
#     backend_process.start()
#     frontend_process.start()

#     try:
#         # Giữ ứng dụng chạy cho đến khi người dùng tắt cửa sổ UI (Frontend kết thúc)
#         frontend_process.join()
#     except KeyboardInterrupt:
#         print("\n[SYSTEM] Nhận tín hiệu tắt hệ thống từ bàn phím...")
#     finally:
#         # Khi UI đóng, tự động hủy tiến trình Backend để giải phóng cổng 8000
#         if backend_process.is_alive():
#             print("[SYSTEM] Đang dọn dẹp và giải phóng cổng Server ngầm...")
#             backend_process.terminate()
#             backend_process.join()
#         print("[SYSTEM] Hệ thống đã đóng an toàn.")