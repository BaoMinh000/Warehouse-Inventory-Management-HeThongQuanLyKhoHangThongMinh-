import os
import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QByteArray, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtSvg import QSvgRenderer  # Dùng để render SVG vector trực tiếp cho nút bấm

from ui.utils.theme import Theme  # Khai báo sử dụng bảng màu tập trung hệ thống

# Load SVG icons từ .env
SVG_DASHBOARD = os.getenv("SVG_DASHBOARD", "")
SVG_BOX = os.getenv("SVG_BOX", "")
SVG_WAREHOUSE = os.getenv("SVG_WAREHOUSE", "")
SVG_CLOCK = os.getenv("SVG_CLOCK", "")
SVG_CHART = os.getenv("SVG_CHART", "")

NAV_ITEMS = [
    ("dashboard", SVG_DASHBOARD,  "Dashboard",     False),
    ("products",  SVG_BOX,        "Sản phẩm",      False),
    ("warehouse_manager", SVG_WAREHOUSE, "Quản lý kho", False),
    # ("expiry",    SVG_CLOCK,      "Hết hạn",       True),
    # ("reports",   SVG_CHART,      "Báo cáo",       False),
]

class _NavButton(QPushButton):
    """Nút bấm Sidebar tự vẽ Icon SVG bằng QSvgRenderer để đổi màu động"""

    def __init__(self, svg_str: str, tooltip: str, has_badge: bool = False, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Hiệu ứng bàn tay khi hover
        
        self.raw_svg = svg_str
        self._active = False
        self._hovered = False

    def set_active(self, active: bool):
        self._active = active
        self.update()  # Yêu cầu nút vẽ lại giao diện khi đổi trạng thái

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def _get_current_color(self) -> str:
        """Trả về mã màu Hex từ Theme dựa trên trạng thái hiện tại của nút"""
        if self._active:
            return Theme.COLOR_PRIMARY
        if self._hovered:
            return Theme.TEXT_WHITE_HOVER
        return Theme.TEXT_SUB

    def _render_svg(self, svg_str: str, color_hex: str) -> QSvgRenderer | None:
        if not svg_str.strip():
            return None
        if "fill=" not in svg_str:
            svg_str = svg_str.replace('<svg', f'<svg fill="{color_hex}"')
        else:
            svg_str = re.sub(r'fill="[^"]+"', f'fill="{color_hex}"', svg_str)
        
        byte_array = QByteArray(svg_str.strip().encode('utf-8'))
        renderer = QSvgRenderer(byte_array)
        return renderer if renderer.isValid() else None

    def paintEvent(self, event):
        """Hàm tự vẽ toàn bộ nút bấm kết nối với dữ liệu Theme màu chung"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        current_color = self._get_current_color()

        # Thay thế BG_NAV_ACTIVE bằng BG_BTN_ACTIVE, BG_NAV_HOVER bằng BG_BTN_HOVER
        if self._active:
            painter.setBrush(QColor(Theme.BG_BTN_ACTIVE)) # Dùng chung với nút active hệ thống
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(0, 0, w, h, 8, 8)
        elif self._hovered:
            painter.setBrush(QColor(Theme.BG_BTN_HOVER))  # Dùng chung với nút hover hệ thống
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(0, 0, w, h, 8, 8)

        # 2. Vẽ Icon SVG trực tiếp bằng Renderer
        renderer = self._render_svg(self.raw_svg, current_color)
        if renderer:
            icon_size = 20
            icon_rect = QRectF((w - icon_size) / 2, (h - icon_size) / 2, icon_size, icon_size)
            renderer.render(painter, icon_rect)

        painter.end()


class Sidebar(QWidget):
    """Thanh Sidebar quản lý các nút bấm vector đồng bộ cấu trúc màu từ Theme"""
    navigate = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(52)
        # Đồng bộ màu nền Sidebar và màu viền phân tách sang Theme chung
        self.setStyleSheet(
            f"QWidget {{ background: {Theme.BG_SIDEBAR}; border-right: 1px solid {Theme.BORDER_SIDEBAR}; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._buttons: dict[str, _NavButton] = {}

        for key, icon, tip, badge in NAV_ITEMS:
            if key == "expiry":
                divider = QFrame()
                divider.setFixedHeight(1)
                divider.setStyleSheet(f"background: {Theme.BORDER_SIDEBAR}; border: none; margin: 4px 0;")
                layout.addWidget(divider)

            btn = _NavButton(icon, tip, badge)
            btn.clicked.connect(lambda _, k=key: self._on_click(k))
            self._buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()
        
        # Phần nút cài đặt vạch phân tách thứ 2
        divider2 = QFrame()
        divider2.setFixedHeight(1)
        divider2.setStyleSheet(f"background: {Theme.BORDER_SIDEBAR}; border: none; margin: 4px 0;")
        layout.addWidget(divider2)

        self.settings_btn = _NavButton("", "Cài đặt") 
        layout.addWidget(self.settings_btn)

        self._active_key = "dashboard"
        self._buttons["dashboard"].set_active(True)

    def _on_click(self, key: str):
        if key in self._buttons:
            if self._active_key in self._buttons:
                self._buttons[self._active_key].set_active(False)
            self._active_key = key
            self._buttons[key].set_active(True)
        self.navigate.emit(key)