import re
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QByteArray

def create_svg_icon(svg_str: str, color_hex: str = "#FFFFFF") -> QIcon:
    """
    Tạo QIcon trực tiếp từ chuỗi SVG XML và tự động ép màu theo mã Hex.
    
    Parameters:
    -----------
    svg_str (str) : Chuỗi XML cấu trúc của file SVG.
    color_hex (str) : Mã màu mong muốn (Mặc định là màu trắng "#FFFFFF").
    """
    # Xử lý đổi màu triệt để bằng cách thay thế hoặc chèn thuộc tính fill
    if "fill=" not in svg_str:
        # Nếu chưa có thuộc tính fill, chèn thẳng vào thẻ <svg> mở
        svg_str = svg_str.replace('<svg', f'<svg fill="{color_hex}"')
    else:
        # Nếu đã có fill cũ, dùng regex quét sạch và thay bằng màu mới
        svg_str = re.sub(r'fill="[^"]+"', f'fill="{color_hex}"', svg_str)

    # Nạp dữ liệu SVG đã xử lý màu vào QPixmap thông qua QByteArray
    byte_array = QByteArray(svg_str.encode('utf-8'))
    pixmap = QPixmap()
    pixmap.loadFromData(byte_array, "SVG")
    
    return QIcon(pixmap)