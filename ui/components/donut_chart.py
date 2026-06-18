from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF

from ui.utils.theme import Theme


class DonutChart(QWidget):
    """
    Donut chart được tối ưu hóa vẽ bằng QPainter.
    Hỗ trợ cập nhật động từ Dashboard thông qua set_data() hoặc set_segments().
    """

    def __init__(self, segments: list[tuple[str, float, str]] | None = None, parent=None):
        super().__init__(parent)
        # Giá trị mặc định ban đầu đồng bộ màu sắc từ Theme hệ thống
        self._segments = segments or [
            ("FIFO",  0, Theme.COLOR_PRIMARY),
            ("LIFO",  0, Theme.TEXT_MUTED),
            ("Mixed", 0, Theme.TEXT_BLUE_ACCENT),
        ]
        self._total_display = 0  # Lưu trữ số lượng tổng SKU thật để hiển thị ở tâm
        self.setMinimumSize(140, 140)

    def set_segments(self, segments: list[tuple[str, float, str]], total_skus: int = 0):
        """Cập nhật dữ liệu dạng danh mục đầy đủ."""
        self._segments = segments
        self._total_display = total_skus
        self.update()

    def set_data(self, data_dict: dict):
        """
        Hàm Adapter đồng bộ hoàn hảo với dữ liệu truyền từ DashboardScreen.
        Nhận vào dạng: {'FIFO': 53, 'LIFO': 37, 'Mixed': 10}
        """
        # Áp dụng chính xác hệ màu chủ đạo từ file Theme
        color_map = {
            "FIFO": Theme.COLOR_PRIMARY,
            "LIFO": Theme.TEXT_MUTED,
            "Mixed": Theme.TEXT_BLUE_ACCENT
        }
        
        updated_segments = []
        for label, pct in data_dict.items():
            color = color_map.get(label, Theme.TEXT_MAIN)
            updated_segments.append((label, pct, color))
            
        self._segments = updated_segments
        self.update()

    def paintEvent(self, event):
        if not self._segments:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Tính toán kích thước hình học chuẩn, tránh mất viền (clipping)
        side = min(self.width(), self.height())
        margin = 12
        donut_size = side - margin * 2
        
        # Độ dày bánh Donut chiếm 16% đường kính
        thickness = donut_size * 0.16 
        
        # Thu hẹp rect một chút bằng nửa độ dày pen để nét vẽ nằm trọn bên trong Widget
        rect_size = donut_size - thickness
        x0 = (self.width() - rect_size) / 2
        y0 = (self.height() - rect_size) / 2
        rect = QRectF(x0, y0, rect_size, rect_size)

        # 2. Cấu hình bút vẽ (Pen)
        pen = QPen()
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        pen.setWidthF(thickness)

        # Kiểm tra xem tổng data có hợp lệ không, nếu toàn bộ bằng 0 thì vẽ vòng xám trống
        val_sum = sum(v for _, v, _ in self._segments)
        if val_sum == 0:
            segments_to_draw = [("Empty", 100, Theme.BORDER_NEUTRAL)] # Sử dụng viền trung tính tối làm nền rỗng
            total_ratio = 100
        else:
            segments_to_draw = self._segments
            total_ratio = val_sum

        # 3. Tiến hành vẽ các cung tròn (Arcs)
        angle = 90 * 16  # Bắt đầu từ đỉnh 12 giờ
        for label, value, color in segments_to_draw:
            if value <= 0:
                continue
            # Tính toán góc âm để quay theo chiều kim đồng hồ
            span = int(-(value / total_ratio) * 360 * 16)
            
            pen.setColor(QColor(color))
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(rect, angle, span)
            angle += span

        # 4. Vẽ Text ở tâm đối xứng động theo Rect (Không dùng tọa độ cứng để tránh đè chữ)
        center_rect = QRectF(x0 + thickness, y0 + thickness, rect_size - thickness * 2, rect_size - thickness * 2)
        
        # Vẽ Số lượng hiển thị ở trên (Nếu có số liệu SKU thật thì hiển thị, không thì hiện %)
        display_number = str(self._total_display) if self._total_display > 0 else f"{int(val_sum)}"
        
        painter.setPen(QColor(Theme.TEXT_MAIN)) # Đồng bộ màu chữ trắng sáng chính
        font_num = QFont("Segoe UI", 13, QFont.Weight.Bold)
        painter.setFont(font_num)
        
        # Dịch chuyển nhẹ hộp chữ số lên trên một chút để nhường chỗ cho chữ "SKU"
        num_rect = center_rect.translated(0, -6)
        painter.drawText(num_rect, Qt.AlignmentFlag.AlignCenter, display_number)

        # Vẽ chữ phụ "SKU" hoặc "TỶ LỆ" ở dưới
        painter.setPen(QColor(Theme.TEXT_MUTED)) # Đồng bộ màu chữ xám phụ nhạt
        font_sub = QFont("Segoe UI", 8, QFont.Weight.Medium)
        painter.setFont(font_sub)
        
        sub_rect = center_rect.translated(0, 10)
        sub_text = "SKU" if self._total_display > 0 else "TỔNG %"
        painter.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, sub_text)

        painter.end()