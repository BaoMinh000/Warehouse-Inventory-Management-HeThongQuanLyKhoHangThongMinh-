<h1>Smart Warehouse Inventory Management System</h1>
<h2>(Hệ Thống Quản Lý Kho Hàng Thông Minh)</h2>

<p style="line-height: 1.25;">
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/PyQt-6%20%2F%20PySide6-green.svg?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt">
    <img src="https://img.shields.io/badge/SQLite-Database-003B57.svg?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
</p>

<p style="line-height: 1.25;">Hệ thống Quản lý Kho hàng Thông minh (Smart Warehouse Inventory Management System) là một giải pháp phần mềm dạng ứng dụng máy tính (Desktop Application) trực quan và mạnh mẽ được phát triển hoàn toàn bằng ngôn ngữ <strong>Python</strong> kết hợp giao diện đồ họa hiện đại <strong>PyQt/PySide</strong>[cite: 1]. Hệ thống tích hợp sâu các cấu trúc dữ liệu tối ưu nhằm giải quyết triệt để bài toán quản lý danh mục hàng hóa, điều phối quy trình xuất nhập kho và theo dõi nghiêm ngặt thời hạn sử dụng của sản phẩm theo thời gian thực[cite: 1].</p>

<h2>🚀 Tính Năng Chính</h2>
<ul>
    <li><strong>Bảng điều khiển tổng quan (Dashboard):</strong> Tích hợp các cấu trúc biểu đồ trực quan (Biểu đồ cột, biểu đồ tròn/donut) hỗ trợ thống kê nhanh số lượng hàng tồn, dòng sản phẩm biến động và các chỉ số vận hành kho[cite: 1].</li>
    <li><strong>Quản lý sản phẩm (Products Management):</strong> Hỗ trợ thiết lập thông tin hàng hóa chi tiết bao gồm danh mục phân loại, giá cả, mã hóa và định vị khu vực lưu kho[cite: 1].</li>
    <li><strong>Quy trình xuất nhập kho (Stock In / Stock Out):</strong> Xử lý và kiểm soát chặt chẽ luồng tạo lập phiếu nhập, xuất hàng thông qua các bộ điều khiển logic (Controllers) độc lập[cite: 1].</li>
    <li><strong>Giám sát và cảnh báo hạn sử dụng (Expiry Service):</strong> Tự động tính toán và theo dõi sát sao ngày hết hạn của từng lô hàng, hiển thị danh sách cảnh báo trực quan nhằm giảm thiểu tối đa thiệt hại do hàng hóa quá hạn[cite: 1].</li>
    <li><strong>Lịch sử hoạt động (Activity Feed / History View):</strong> Ghi nhận và lưu vết toàn bộ biến động kho hàng cùng lịch sử thao tác của nhân viên vận hành[cite: 1].</li>
</ul>

<h2>🧠 Cấu Trúc Dữ Liệu &amp; Giải Thuật (DSA) Tích Hợp</h2>
<p style="line-height: 1.25;">Điểm nhấn kỹ thuật cốt lõi của dự án nằm ở thư mục <code>app/dsa/</code>, nơi các cấu trúc dữ liệu nền tảng được tự xây dựng và tối ưu hóa nhằm tăng tốc hiệu năng xử lý hệ thống[cite: 1]:</p>
<table border="1" cellpadding="6" style="border-collapse: collapse; line-height: 1.25; border-color: #ddd;">
    <thead>
        <tr style="background-color: #f2f2f2;">
            <th align="left">Cấu Trúc Dữ Liệu</th>
            <th align="left">Mục Đích Ứng Dụng Trong Thực Tế Của Dự Án</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Binary Search Tree (BST)</strong></td>
            <td>Tối ưu hóa tốc độ tìm kiếm, truy xuất thông tin sản phẩm dựa trên mã định danh ID, đồng thời duy trì việc sắp xếp cấu trúc hàng hóa có thứ tự một cách tự động[cite: 1].</td>
        </tr>
        <tr>
            <td><strong>Queue (Hàng đợi)</strong></td>
            <td>Hỗ trợ điều phối luồng xuất/nhập kho theo mô hình hàng đợi. Đặc biệt ứng dụng hiệu quả trong việc xử lý xuất hàng theo nguyên tắc <strong>FIFO (First In, First Out)</strong> đối với các mặt hàng có hạn sử dụng ngắn[cite: 1].</td>
        </tr>
        <tr>
            <td><strong>Stack (Ngăn xếp)</strong></td>
            <td>Quản lý danh sách các hành động gần nhất của hệ thống, hỗ trợ cơ chế lưu vết lịch sử thao tác (Activity Feed), phục vụ tốt cho các tính năng Undo/Redo hoặc xem lại nhanh tác vụ vừa thực hiện[cite: 1].</td>
        </tr>
    </tbody>
</table>

<h2>📐 Cấu Trúc Thư Mục Dự Án</h2>
<p style="line-height: 1.25;">Dự án được tổ chức khoa học theo mô hình MVC tách biệt rõ ràng giữa giao diện hiển thị, logic nghiệp vụ và tầng dữ liệu[cite: 1]:</p>
<pre style="background-color: #f8f9fa; padding: 10px; border-left: 3px solid #007bff; line-height: 1.25;">
├── app/                  # Tầng xử lý logic nghiệp vụ và dữ liệu gốc
│   ├── api/              # Quản lý các luồng định tuyến và kết nối API nội bộ[cite: 1]
│   ├── dsa/              # Cấu trúc dữ liệu tự định nghĩa (bst, queue, stack)[cite: 1]
│   ├── models/           # Định nghĩa cấu trúc Database Models &amp; Schemas hệ thống[cite: 1]
│   ├── services/         # Dịch vụ nghiệp vụ chính (inventory_service, expiry_service...)[cite: 1]
│   └── database.py       # Thiết lập kết nối và cấu hình Cơ sở dữ liệu[cite: 1]
├── ui/                   # Tầng giao diện người dùng (User Interface)
│   ├── assets/           # Chứa tài nguyên icon định dạng SVG và stylesheet ứng dụng (styles.qss)[cite: 1]
│   ├── components/       # Các Widget đồ họa tái sử dụng (charts, tables, sidebars, stat_cards...)[cite: 1]
│   ├── controllers/      # Bộ điều khiển trung gian kết nối giữa UI và lớp Services nghiệp vụ[cite: 1]
│   └── screens/          # Các màn hình tính năng lớn (dashboard, products, expiry, stock_in...)[cite: 1]
├── tests/                # Thư mục chứa mã nguồn kiểm thử tự động (test_bst.py, test_inventory.py)[cite: 1]
├── main.py               # Điểm khởi chạy chính của toàn bộ ứng dụng (Main Entry Point)[cite: 1]
├── warehouse.sqbpro      # Cơ sở dữ liệu lưu trữ cục bộ dạng SQLite[cite: 1]
└── requirements.txt      # Danh sách tệp tin chứa các thư viện phụ thuộc của dự án[cite: 1]
</pre>

<h2>💻 Hướng Dẫn Cài Đặt &amp; Khởi Chạy</h2>

<h3>1. Yêu cầu hệ thống</h3>
<ul>
    <li>Máy tính đã cài đặt sẵn môi trường <strong>Python 3.10+</strong>.</li>
</ul>

<h3>2. Các bước triển khai chi tiết</h3>
<p style="line-height: 1.25;">Mở terminal hoặc command prompt của bạn và thực thi tuần tự các câu lệnh sau[cite: 1]:</p>
<pre style="background-color: #f8f9fa; padding: 10px; border-left: 3px solid #28a745; line-height: 1.25;">
# 1. Tải mã nguồn dự án về máy cục bộ
git clone https://github.com/BaoMinh000/Warehouse-Inventory-Management-HeThongQuanLyKhoHangThongMinh-.git

# 2. Di chuyển quyền điều khiển vào thư mục dự án
cd Warehouse-Inventory-Management-HeThongQuanLyKhoHangThongMinh-

# 3. Khởi tạo một môi trường ảo độc lập (Khuyến khích)
python -m venv venv

# 4. Kích hoạt môi trường ảo vừa tạo
# Dành cho hệ điều hành macOS/Linux:
source venv/bin/activate
# Dành cho hệ điều hành Windows:
venv\Scripts\activate

# 5. Cài đặt toàn bộ các thư viện phụ thuộc bắt buộc
pip install -r requirements.txt
</pre>

<h3>3. Cấu hình tệp môi trường</h3>
<p style="line-height: 1.25;">Sao chép hoặc khởi tạo tệp tin mang tên <code>.env</code> nằm tại thư mục gốc của dự án và khai báo các hằng số cấu hình cơ bản[cite: 1]:</p>
<pre style="background-color: #f8f9fa; padding: 10px; line-height: 1.25;">
DB_PATH=warehouse.sqbpro
DEBUG=True
</pre>

<h3>4. Khởi chạy phần mềm</h3>
<p style="line-height: 1.25;">Thực hiện lệnh sau từ thư mục gốc để kích hoạt ứng dụng giao diện Desktop[cite: 1]:</p>
<pre style="background-color: #f8f9fa; padding: 10px; line-height: 1.25;">
python main.py
</pre>

<h3>5. Kiểm thử hệ thống (Testing)</h3>
<p style="line-height: 1.25;">Để chạy bộ kiểm thử tự động, xác minh tính ổn định của các cấu trúc cây BST hay logic tồn kho[cite: 1]:</p>
<pre style="background-color: #f8f9fa; padding: 10px; line-height: 1.25;">
pytest
</pre>

<h2>👥 Thành Viên Phát Triển</h2>
<ul>
    <li><strong>Quách Bảo Minh</strong> - <i>Lead Developer &amp; Architect</i> - <a href="https://github.com/BaoMinh000">@BaoMinh000</a></li>
</ul>
