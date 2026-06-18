# theme.py

class Theme:
    # --- MÀU CHỮ / TEXT COLORS ---
    TEXT_MAIN = "#e2e8f0"         # Trắng sáng (Tiêu đề chính, nội dung nhập liệu)
    TEXT_MUTED = "#8899b4"        # Xám vừa (Tiêu đề phụ, label phụ)
    TEXT_SUB = "#4a5a78"          # Xám đậm (Chú thích ẩn, text phụ mờ)
    TEXT_LINK = "#378ADD"         # Xanh dương (Liên kết, hành động)
    TEXT_NORMAL = "#94a3b8"       # Xám nhạt mặc định (Chữ nút chưa active, header table)
    TEXT_WHITE_HOVER = "#FFFFFF"  # Trắng tinh khi hover chuột qua
    TEXT_BLUE_ACCENT = "#5b9cf6"  # Xanh lam sáng làm điểm nhấn tiêu đề cột

    # --- MÀU NỀN CHUNG / BACKGROUNDS ---
    BG_TABLE = "#1e293b"          # Nền tối chủ đạo của Table, Search Frame
    BG_BTN_HOVER = "#2d3748"      # Nền khi hover chuột lên các nút Action nhỏ (Sửa/Xem)
    BG_BTN_ACTIVE = "#1e3a8a"     # Nền của nút Bộ lọc (Pill button) khi active
    BG_SIDEBAR = "#161b26"        # Nền tối của cột Sidebar

    # --- MÀU ĐƯỜNG VIỀN CHUNG / BORDERS ---
    BORDER_NEUTRAL = "#334155"    # Đường viền mặc định tổng thể
    BORDER_ACTIVE = "#2a4a6e"     # Đường viền khi widget được chọn/active
    BORDER_HOVER = "#3a4560"      # Đường viền khi hover chuột qua
    BORDER_SIDEBAR = "#2a3347"    # Đường viền phân tách sidebar/vạch divider

    # --- MÀU TRẠNG THÁI & BIỂU ĐỒ / STATUS COLORS ---
    COLOR_PRIMARY = "#378ADD"     # Xanh dương chủ đạo
    COLOR_SUCCESS = "#2fd89c"     # Xanh lá cây tươi (Trạng thái thành công)
    COLOR_DANGER = "#f07070"      # Đỏ (Cảnh báo, lỗi nghiệp vụ)
    COLOR_HOVER_LIGHT = "#60a5fa" # Xanh sáng khi hover chuột qua icon SVG
    
    # --- HỆ THỐNG MÀU DÙNG CHUNG CHO CÁC PHÂN HỆ FORM (STOCK IN / STOCK OUT) ---
    BG_INPUT = "#161b26"          # Nền tối của ô nhập liệu (QLineEdit, QComboBox, ...)
    BORDER_INPUT = "#2a3347"      # Viền ô nhập liệu mặc định
    BG_PANEL_DARK = "#0f131a"     # Nền của khung QFrame lớn chứa nhóm thông tin
    BORDER_PANEL_DARK = "#1e2530" # Viền của khung QFrame lớn
    
    # Các thành phần Banner / Khung trạng thái đặc biệt
    BG_BANNER_SUCCESS = "#06261a"      # Nền xanh lục cực tối (Hệ thống đề xuất / Đã xác thực)
    BORDER_BANNER_SUCCESS = "#0f4d34"  # Viền xanh lục của banner thành công
    TEXT_BANNER_SUCCESS = "#2ecc71"    # Chữ xanh lá tươi hiển thị trong banner
    BTN_MINT_SUCCESS = "#1dd1a1"       # Nền nút xác nhận màu xanh mint sáng
    BTN_MINT_HOVER = "#10ac84"         # Nền nút xác nhận khi di chuột qua

    BG_PANEL_BACKUP = "#141923"        # Nền khung lô dự phòng (Xám tối mờ)
    BORDER_PANEL_BACKUP = "#222b3c"    # Viền khung lô dự phòng
    BG_PANEL_SUMMARY = "#11151f"       # Nền bảng tóm tắt gọn dưới cùng
    TEXT_LABEL_SUMMARY = "#6c7a9c"     # Màu chữ nhãn tóm tắt (Xám xanh)

    # Thêm trạng thái lỗi trực quan cho Badge
    BG_BADGE_DANGER = "#2a1414"        # Nền badge khi thất bại
    TEXT_BADGE_DANGER = "#e74c3c"      # Chữ badge khi thất bại 

    # ==========================================
    # --- ĐỒNG BỘ RIÊNG CHO EXPIRY ITEM ---
    # ==========================================
    EXPIRY_BG_CRITICAL = "#2a1215"      # Nền đỏ tối nguy cấp
    EXPIRY_BORDER_CRITICAL = "#4a1e20"  # Viền đỏ tối nguy cấp
    EXPIRY_BG_WARNING = "#2a1f0a"       # Nền cam/vàng tối cảnh báo
    EXPIRY_BORDER_WARNING = "#4a3312"   # Viền cam/vàng tối cảnh báo
    EXPIRY_TEXT_WARNING = "#e8a042"     # Màu chữ số ngày cảnh báo