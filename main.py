# main.py
import multiprocessing
import sys
import os

# Thêm thư mục backend/app vào sys.path để các module bên trong nó 
# có thể gọi qua lại lẫn nhau (ví dụ: `from database import engine`)
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_app_dir = os.path.join(current_dir, "backend", "app")
if backend_app_dir not in sys.path:
    sys.path.insert(0, backend_app_dir)

# Import 2 hàm khởi chạy từ main_api.py
from backend.app.main_api import start_backend, start_frontend

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