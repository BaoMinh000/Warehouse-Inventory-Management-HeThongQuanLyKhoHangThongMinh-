

import os
import re
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QRect, QByteArray, QRectF
from PyQt6.QtSvg import QSvgRenderer

from ui.utils.theme import Theme


class BarChart(QWidget):
    """
    Biểu đồ cột dọc đôi (Nhập - Xuất) bằng QPainter.
    Tự động hiển thị trạng thái trống kèm Icon SVG (đổi màu động) nếu không có dữ liệu.
    """

    def __init__(self, data: list[tuple[str, float, float]] | None = None, parent=None):
        super().__init__(parent)
        
        self._data = data 
        self.setMinimumHeight(110)

        # Lấy chuỗi SVG raw từ môi trường hoặc sử dụng chuỗi mặc định
        self.raw_svg_str = os.getenv("SVG_EMPTY_BOX") or """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640">
            <path d="M560.3 301.2C570.7 313 588.6 315.6 602.1 306.7C616.8 296.9 620.8 277 611 262.3L563 190.3C560.2 186.1 556.4 182.6 551.9 180.1L351.4 68.7C332.1 58 308.6 58 289.2 68.7L88.8 180C83.4 183 79.1 187.4 76.2 192.8L27.7 282.7C15.1 306.1 23.9 335.2 47.3 347.8L80.3 365.5L80.3 418.8C80.3 441.8 92.7 463.1 112.7 474.5L288.7 574.2C308.3 585.3 332.2 585.3 351.8 574.2L527.8 474.5C547.9 463.1 560.2 441.9 560.2 418.8L560.2 301.3zM320.3 291.4L170.2 208L320.3 124.6L470.4 208L320.3 291.4zM278.8 341.6L257.5 387.8L91.7 299L117.1 251.8L278.8 341.6z"/>
        </svg>
        """
        
        self.svg_renderer = self._init_svg_renderer(self.raw_svg_str, Theme.TEXT_SUB)

    def _init_svg_renderer(self, svg_str: str, color_hex: str) -> QSvgRenderer | None:
        """Hàm hỗ trợ nhuộm màu mã Hex vào chuỗi SVG và nạp vào QSvgRenderer"""
        if not svg_str.strip():
            return None
            
        if "fill=" not in svg_str:
            svg_str = svg_str.replace('<svg', f'<svg fill="{color_hex}"')
        else:
            svg_str = re.sub(r'fill="[^"]+"', f'fill="{color_hex}"', svg_str)

        byte_array = QByteArray(svg_str.strip().encode('utf-8'))
        renderer = QSvgRenderer(byte_array)
        
        return renderer if renderer.isValid() else None

    def set_data(self, data: list[tuple[str, float, float]]):
        self._data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # --- TRƯỜNG HỢP KHÔNG CÓ DỮ LIỆU ---
        if not self._data:
            self._draw_empty_state(painter, w, h)
            painter.end()
            return

        # --- TRƯỜNG HỢP CÓ DỮ LIỆU ---
        padding_h = 12
        label_h = 18
        chart_h = h - label_h - padding_h

        n = len(self._data)
        group_gap = 12  # Khoảng cách giữa các ngày
        intra_gap = 2   # Khoảng cách giữa cột Nhập và Xuất trong cùng 1 ngày

        # Tính toán độ rộng cho một cụm ngày, sau đó chia đôi trừ đi khoảng cách intra_gap
        group_w = max(16, (w - padding_h * 2 - group_gap * (n - 1)) // n)
        bar_w = max(6, (group_w - intra_gap) // 2)

        # Tìm giá trị lớn nhất trong toàn bộ dữ liệu để scale chiều cao chuẩn xác
        max_val = 1
        for _, val_in, val_out in self._data:
            max_val = max(max_val, val_in, val_out)

        painter.setFont(QFont("Segoe UI", 8))

        for i, (label, val_in, val_out) in enumerate(self._data):
            # Tọa độ X gốc của cụm ngày thứ i
            group_x = padding_h + i * (group_w + group_gap)

            # --- 1. VẼ CỘT NHẬP KHO (Bên trái cụm) ---
            bar_in_h = int((val_in / max_val) * chart_h) if val_in > 0 else 0
            x_in = group_x
            y_in = padding_h + chart_h - bar_in_h
            if bar_in_h > 0:
                painter.setBrush(QColor(Theme.BTN_MINT_SUCCESS))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRect(x_in, y_in, bar_w, bar_in_h), 2, 2)

            # --- 2. VẼ CỘT XUẤT KHO (Bên phải cụm) ---
            bar_out_h = int((val_out / max_val) * chart_h) if val_out > 0 else 0
            x_out = group_x + bar_w + intra_gap
            y_out = padding_h + chart_h - bar_out_h
            if bar_out_h > 0:
                painter.setBrush(QColor(Theme.COLOR_PRIMARY))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRect(x_out, y_out, bar_w, bar_out_h), 2, 2)

            # --- 3. VẼ NHÃN NGÀY (Căn giữa cả cụm cột đôi) ---
            painter.setPen(QColor(Theme.TEXT_SUB))
            painter.drawText(
                QRect(group_x - 4, h - label_h, group_w + 8, label_h),
                Qt.AlignmentFlag.AlignCenter,
                label,
            )

        painter.end()

    def _draw_empty_state(self, painter: QPainter, w: int, h: int):
        svg_size = 40  
        text_height = 20
        spacing = 6    
        
        total_content_h = svg_size + spacing + text_height
        start_y = (h - total_content_h) // 2

        if self.svg_renderer and self.svg_renderer.isValid():
            svg_rect = QRectF((w - svg_size) / 2, start_y, svg_size, svg_size) 
            self.svg_renderer.render(painter, svg_rect)
            text_y = start_y + svg_size + spacing
        else:
            text_y = (h - text_height) // 2

        painter.setPen(QColor(Theme.TEXT_SUB))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        
        text_rect = QRect(0, text_y, w, text_height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "Không có dữ liệu")
        
        
# import os
# import re
# from PyQt6.QtWidgets import QWidget
# from PyQt6.QtGui import QPainter, QColor, QFont
# from PyQt6.QtCore import Qt, QRect, QByteArray, QRectF
# from PyQt6.QtSvg import QSvgRenderer  # Dùng để render SVG dạng vector nguyên bản

# from ui.utils.theme import Theme  # Import bảng màu tập trung hệ thống


# class BarChart(QWidget):
#     """
#     Biểu đồ cột dọc đơn giản bằng QPainter.
#     Tự động hiển thị trạng thái trống kèm Icon SVG (đổi màu động) nếu không có dữ liệu.
#     """

#     def __init__(self, data: list[tuple[str, float]] | None = None, parent=None):
#         super().__init__(parent)
        
#         # Nếu data truyền vào là None -> Dùng dữ liệu demo
#         self._data = data 
#         self.setMinimumHeight(110)

#         # Lấy chuỗi SVG raw từ môi trường hoặc sử dụng chuỗi mặc định
#         self.raw_svg_str = os.getenv("SVG_EMPTY_BOX") or """
#         <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640">
#             <path d="M560.3 301.2C570.7 313 588.6 315.6 602.1 306.7C616.8 296.9 620.8 277 611 262.3L563 190.3C560.2 186.1 556.4 182.6 551.9 180.1L351.4 68.7C332.1 58 308.6 58 289.2 68.7L88.8 180C83.4 183 79.1 187.4 76.2 192.8L27.7 282.7C15.1 306.1 23.9 335.2 47.3 347.8L80.3 365.5L80.3 418.8C80.3 441.8 92.7 463.1 112.7 474.5L288.7 574.2C308.3 585.3 332.2 585.3 351.8 574.2L527.8 474.5C547.9 463.1 560.2 441.9 560.2 418.8L560.2 301.3zM320.3 291.4L170.2 208L320.3 124.6L470.4 208L320.3 291.4zM278.8 341.6L257.5 387.8L91.7 299L117.1 251.8L278.8 341.6z"/>
#         </svg>
#         """
        
#         # Khởi tạo renderer cho trạng thái trống - Đồng bộ lấy màu chữ xám đậm từ Theme
#         self.svg_renderer = self._init_svg_renderer(self.raw_svg_str, Theme.TEXT_SUB)

#     def _init_svg_renderer(self, svg_str: str, color_hex: str) -> QSvgRenderer | None:
#         """Hàm hỗ trợ nhuộm màu mã Hex vào chuỗi SVG và nạp vào QSvgRenderer"""
#         if not svg_str.strip():
#             return None
            
#         # Xử lý đổi màu bằng Regex (Tìm thuộc tính fill hoặc chèn mới vào thẻ <svg>)
#         if "fill=" not in svg_str:
#             svg_str = svg_str.replace('<svg', f'<svg fill="{color_hex}"')
#         else:
#             svg_str = re.sub(r'fill="[^"]+"', f'fill="{color_hex}"', svg_str)

#         # Nạp mảng byte XML của SVG trực tiếp vào Renderer để giữ nguyên chất lượng Vector
#         byte_array = QByteArray(svg_str.strip().encode('utf-8'))
#         renderer = QSvgRenderer(byte_array)
        
#         return renderer if renderer.isValid() else None

#     def set_data(self, data: list[tuple[str, float]]):
#         self._data = data
#         self.update()

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)

#         w = self.width()
#         h = self.height()

#         # --- TRƯỜNG HỢP KHÔNG CÓ DỮ LIỆU ---
#         if not self._data:
#             self._draw_empty_state(painter, w, h)
#             painter.end()
#             return

#         # --- TRƯỜNG HỢP CÓ DỮ LIỆU ---
#         padding_h = 8
#         label_h = 18
#         chart_h = h - label_h - padding_h

#         n = len(self._data)
#         bar_gap = 5
#         bar_w = max(8, (w - padding_h * 2 - bar_gap * (n - 1)) // n)
#         max_val = max(v for _, v in self._data) or 1
#         peak_idx = max(range(n), key=lambda i: self._data[i][1])

#         painter.setFont(QFont("Segoe UI", 8))

#         for i, (label, value) in enumerate(self._data):
#             x = padding_h + i * (bar_w + bar_gap)
#             bar_height = int((value / max_val) * chart_h)
#             y = padding_h + chart_h - bar_height

#             # Đồng bộ màu: Cột cao nhất lấy màu COLOR_PRIMARY, các cột khác lấy màu COLOR_CHART_DARK
#             color = Theme.COLOR_PRIMARY if i == peak_idx else Theme.BORDER_NEUTRAL
#             painter.setBrush(QColor(color))
#             painter.setPen(Qt.PenStyle.NoPen)
#             painter.drawRoundedRect(QRect(x, y, bar_w, bar_height), 2, 2)

#             # Đồng bộ màu chữ nhãn (Label) dưới chân cột sang màu TEXT_SUB
#             painter.setPen(QColor(Theme.TEXT_SUB))
#             painter.drawText(
#                 QRect(x - 4, h - label_h, bar_w + 8, label_h),
#                 Qt.AlignmentFlag.AlignCenter,
#                 label,
#             )

#         painter.end()

#     def _draw_empty_state(self, painter: QPainter, w: int, h: int):
#         """Vẽ giao diện trống gồm Icon SVG đã đổi màu và dòng chữ thông báo"""
#         svg_size = 40  
#         text_height = 20
#         spacing = 6    
        
#         total_content_h = svg_size + spacing + text_height
#         start_y = (h - total_content_h) // 2

#         if self.svg_renderer and self.svg_renderer.isValid():
#             svg_rect = QRectF((w - svg_size) / 2, start_y, svg_size, svg_size) 
#             self.svg_renderer.render(painter, svg_rect)
#             text_y = start_y + svg_size + spacing
#         else:
#             text_y = (h - text_height) // 2

#         # Vẽ chữ "Không có dữ liệu" với màu chữ TEXT_SUB từ Theme chung
#         painter.setPen(QColor(Theme.TEXT_SUB))
#         painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        
#         text_rect = QRect(0, text_y, w, text_height)
#         painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "Không có dữ liệu")