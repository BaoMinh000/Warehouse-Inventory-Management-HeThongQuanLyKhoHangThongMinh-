# 📦 Warehouse Inventory Management System (Hệ thống Quản lý Kho hàng Thông minh)

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/Language-Python%203.10+-blue.svg)
![DSA](https://img.shields.io/badge/DSA-BST%20%7C%20Queue%20%7C%20Stack-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Hệ thống Quản lý Kho hàng Thông minh là giải pháp quản trị kho in-memory được tối ưu bằng ngôn ngữ **Python**. Hệ thống áp dụng các cấu trúc dữ liệu và giải thuật (DSA) chuyên biệt để tăng tốc độ truy xuất danh mục hàng hóa và tự động hóa quy trình phân phối xuất hàng dựa trên thời hạn sử dụng hoặc thứ tự nhập kho.

---

## 🏗️ Kiến trúc Cấu trúc Dữ liệu Cốt lõi (Core DSA)

Dự án không phụ thuộc hoàn toàn vào truy vấn cơ sở dữ liệu truyền thống cho mỗi giao dịch. Thay vào đó, hệ thống nạp và quản lý dữ liệu trực tiếp trên bộ nhớ đệm (RAM) bằng các cấu trúc dữ liệu tự định nghĩa:

1. **Binary Search Tree (BST - Cây Tìm Kiếm Nhị Phân)**: Quản lý và định danh danh mục hàng hóa toàn kho. Mỗi sản phẩm là một Node, phân nhánh dựa trên mã vạch (`Barcode`) giúp tối ưu thời gian tìm kiếm sản phẩm về mức $O(\log n)$.
2. **Queue (Hàng đợi - FIFO)**: Áp dụng cho các nhóm sản phẩm cấu hình chiến lược "Nhập trước - Xuất trước". Hệ thống tự động trích xuất các lô hàng cũ nhất nằm ở đầu hàng đợi để xuất kho (áp dụng cho hàng có hạn dùng ngắn).
3. **Stack (Ngăn xếp - LIFO)**: Áp dụng cho các nhóm sản phẩm cấu hình chiến lược "Nhập sau - Xuất trước". Lô hàng mới nhập gần đây nhất nằm ở đỉnh ngăn xếp sẽ được ưu tiên xuất trước (áp dụng cho hàng hóa dạng pallet xếp chồng).

---

## 📂 Cấu trúc Thư mục Dự án (Project Directory Structure)

Dự án được tổ chức theo mô hình chuẩn hóa lớp (Layered Architecture) trong hệ sinh thái Python nhằm tách biệt rõ ràng giữa logic thuật toán, định nghĩa dữ liệu và giao diện lập trình (APIs).

```text
warehouse_management/
│
├── app/
│   ├── __init__.py
│   │
│   ├── dsa/
│   │   ├── __init__.py
│   │   ├── bst.py
│   │   ├── queue.py
│   │   └── stack.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db_models.py
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── inventory_service.py
│   │   └── expiry_service.py
│   │
│   └── api/
│       ├── __init__.py
│       └── routes.py
│
├── tests/
│   ├── test_bst.py
│   ├── test_inventory.py
│   └── conftest.py
│
├── .env
├── requirements.txt
├── README.md
└── main.py
🔍 Tác dụng và Ý nghĩa của từng Folder:
app/: Thư mục gốc chứa toàn bộ mã nguồn lõi của ứng dụng.

dsa/ (Data Structures & Algorithms): Nơi hiện thực các cấu trúc dữ liệu thuần túy bằng Python (Cây BST, cấu trúc điều hướng Hàng đợi và Ngăn xếp). Đây là "trái tim" xử lý thuật toán in-memory của hệ thống, hoàn toàn không chứa mã nguồn liên quan đến giao diện hay database.

models/: Định nghĩa cấu trúc thực thể dữ liệu. Bao gồm db_models.py (Ánh xạ cấu trúc xuống database thông qua ORM SQLAlchemy) và schemas.py (Định dạng dữ liệu đầu vào/đầu ra Pydantic cho APIs).

services/: Nơi chứa các lớp xử lý nghiệp vụ kho (Business Logic Layer). Kết nối giữa cấu trúc dữ liệu dsa/ và cơ sở dữ liệu models/. Nhận lệnh từ thủ kho, gọi thuật toán trừ kho lũy tiến, sau đó ra lệnh đồng bộ xuống database.

api/: Chứa các router và endpoint (giao diện kết nối). Nhận các request HTTP (JSON) từ máy quét mã vạch hoặc giao diện UI của thủ kho và chuyển tiếp xuống tầng service.

tests/: Chứa toàn bộ các kịch bản kiểm thử tự động (Unit Test & Integration Test) sử dụng thư viện pytest nhằm đảm bảo thuật toán phân nhánh cây và trừ kho lũy tiến chạy chính xác ở mọi điều kiện biên.

main.py: Tệp khởi chạy (Entry point) của toàn bộ hệ thống. Chịu trách nhiệm khởi tạo server, thiết lập kết nối CSDL và kích hoạt tiến trình nạp dữ liệu từ kho lên cây BST trên RAM khi hệ thống bắt đầu chạy.

🚀 Các Tính năng của Hệ thống (Core Modules)
Module Quản lý Danh mục (Product Catalogue): Cho phép thêm mới sản phẩm, tra cứu nhanh thông tin sản phẩm qua mã quét mã vạch, và xóa sản phẩm khỏi hệ thống kho. Danh mục tự động được sắp xếp theo thứ tự mã vạch tăng dần nhờ cơ chế duyệt cây nhị phân.

Module Nhập kho theo Lô (Batch Stock-In): Hỗ trợ thủ kho nhập hàng theo từng lô riêng biệt. Mỗi lô hàng lưu giữ rõ thông tin: Mã lô, Số lượng, Ngày nhập kho và Hạn sử dụng.

Module Tự động xuất kho lũy tiến (Automated Stock-Out): Hệ thống tự động tính toán tổng số lượng cần xuất, sau đó áp dụng chiến lược (FIFO hoặc LIFO) cấu hình riêng cho từng sản phẩm để tự động bóc tách và trừ số lượng của các lô hàng tương ứng. Hỗ trợ cơ chế hủy đơn (Rollback) nếu tổng lượng tồn của tất cả các lô không đủ.

Module Cảnh báo Hạn sử dụng (Expiry Warning System): Tiến trình chạy ngầm thực hiện duyệt toàn bộ các lô hàng trong kho, tự động lọc và thông báo các lô hàng sắp hết hạn (dưới 30 ngày) để thủ kho có phương án xử lý hoặc cách ly kịp thời.

Module Nhật ký vận hành (Audit Logs): Ghi lại toàn bộ lịch sử biến động kho (Ai nhập, Ai xuất, Lô nào bị trừ số lượng, Vào thời gian nào) nhằm đảm bảo tính minh bạch dữ liệu.

💻 Hướng dẫn Cài đặt & Triển khai (Installation)
1. Yêu cầu Hệ thống (Prerequisites)
Ngôn ngữ: Python 3.10 hoặc phiên bản cao hơn.

Hệ quản trị cơ sở dữ liệu: PostgreSQL, MySQL hoặc SQLite (Mặc định).

2. Các bước triển khai chi tiết
Bước 2.1: Tải mã nguồn về máy cục bộ

Bash
git clone [https://github.com/YourUsername/Warehouse-Inventory-Management.git](https://github.com/YourUsername/Warehouse-Inventory-Management.git)
cd Warehouse-Inventory-Management
Bước 2.2: Khởi tạo và kích hoạt môi trường ảo (Virtual Environment)
Việc sử dụng môi trường ảo giúp cô lập các thư viện của dự án, tránh xung đột với hệ thống.

Trên hệ điều hành Windows:

Bash
python -m venv venv
venv\Scripts\activate
Trên hệ điều hành macOS / Linux:

Bash
python3 -m venv venv
source venv/bin/activate
Bước 2.3: Cài đặt các thư viện phụ thuộc (Dependencies)
Cài đặt toàn bộ các thư viện bổ trợ cấu trúc dữ liệu, ORM Database và API framework:

Bash
pip install -r requirements.txt
Bước 2.4: Thiết lập biến môi trường
Tạo một tệp tin tên là .env tại thư mục gốc của dự án và cấu hình thông tin kết nối CSDL (Mẫu cấu hình sử dụng SQLite phục vụ kiểm thử nhanh):

Đoạn mã
DATABASE_URL=sqlite:///./warehouse.db
ENVIRONMENT=development
DEBUG=True
Bước 2.5: Khởi chạy và vận hành hệ thống
Khởi chạy tệp tin cấu hình chính để nạp dữ liệu lên RAM và mở cổng dịch vụ API:

Bash
python main.py
Sau khi khởi chạy thành công, hệ thống sẽ mở cổng dịch vụ tại địa chỉ http://127.0.0.1:8000. Bạn có thể truy cập đường dẫn http://127.0.0.1:8000/docs để kiểm tra và thử nghiệm trực quan các tính năng của hệ thống kho thông qua giao diện tài liệu API tự động.
