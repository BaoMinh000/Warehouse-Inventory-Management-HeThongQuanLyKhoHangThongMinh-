# table_ui.py
import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QPushButton,
    QFrame
)
from PyQt6.QtCore import Qt, QRectF, QByteArray
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer

from ui.components.badge import Badge
from ui.utils.theme import Theme 

SVG_VIEW = os.getenv("SVG_VIEW", "")
SVG_EDIT = os.getenv("SVG_EDIT", "")

class _TableActionButton(QPushButton):
    """Nút thao tác nhỏ (Xem/Sửa) nằm trong ô cuối cùng của mỗi dòng.
    Tự render mã nguồn SVG vector để có thể đổi màu động khi hover chuột[cite: 1]."""

    def __init__(self, svg_str: str, action_type: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24) 
        self.setCursor(Qt.CursorShape.PointingHandCursor) 
        
        self.raw_svg = svg_str
        self.action_type = action_type 
        self._hovered = False    # Dòng trạng thái hover chuột, dùng để đổi màu icon       

    def enterEvent(self, event):
        self._hovered = True
        self.update() 
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update() 
        super().leaveEvent(event)

    def _get_current_color(self) -> str:
        if self._hovered:
            return Theme.COLOR_HOVER_LIGHT 
        return Theme.COLOR_PRIMARY if self.action_type == "edit" else Theme.TEXT_NORMAL

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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) 

        w, h = self.width(), self.height()
        current_color = self._get_current_color()

        if self._hovered:
            painter.setBrush(QColor(Theme.BG_BTN_HOVER))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(0, 0, w, h, 4, 4)

        renderer = self._render_svg(self.raw_svg, current_color)
        if renderer:
            icon_size = 14
            icon_rect = QRectF((w - icon_size) / 2, (h - icon_size) / 2, icon_size, icon_size)
            renderer.render(painter, icon_rect)

        painter.end()


class DataTableUI(QWidget):
    """Lớp dựng khung giao diện chuẩn cho DataTable"""
    
    def __init__(self, columns: list[str], filters: list[str] | None = None, parent=None):
        super().__init__(parent)
        self._columns = columns
        self._filter_btns_dict: dict[str, QPushButton] = {} # Lưu trữ tab phân loại để logic sử dụng

        # Thiết lập Layout chính[cite: 1]
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(10)

        # --- DỰNG KHU VỰC THANH CÔNG CỤ PHÍA TRÊN ---
        top = QHBoxLayout()
        top.setSpacing(8)

        search_frame = QFrame()
        search_frame.setStyleSheet(
            f"QFrame {{ background: {Theme.BG_INPUT}; border: 1px solid {Theme.BORDER_INPUT}; border-radius: 6px; }}"
        )
        sf_lay = QHBoxLayout(search_frame)
        sf_lay.setContentsMargins(10, 0, 10, 0)
        sf_lay.setSpacing(6)
        
        search_icon = QLabel("⌕") 
        search_icon.setStyleSheet(f"color: {Theme.TEXT_NORMAL}; font-size: 14px; border: none;")
        
        self._search = QLineEdit()
        self._search.setPlaceholderText("Tìm kiếm...")
        self._search.setStyleSheet(
            f"background: transparent; border: none; color: {Theme.TEXT_MAIN}; font-size: 12px; padding: 6px 0;"
        )
        sf_lay.addWidget(search_icon)
        sf_lay.addWidget(self._search, 1)

        top.addWidget(search_frame, 1) 

        # Tạo danh sách bộ lọc
        if filters:
            pills = QHBoxLayout()
            pills.setSpacing(5)
            for f in filters:
                btn = QPushButton(f)
                btn.setCheckable(True)
                btn.setChecked(f == "Tất cả")
                btn.setStyleSheet(self._pill_style(f == "Tất cả"))
                pills.addWidget(btn)
                self._filter_btns_dict[f] = btn 
            top.addLayout(pills)

        main.addLayout(top)

        # --- CẤU HÌNH BẢNG QTABLEWIDGET HIỂN THỊ ---
        self._table = QTableWidget()
        self._table.setColumnCount(len(columns))
        self._table.setHorizontalHeaderLabels(columns)
        
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        for i in range(len(columns)):
            if i == 0:
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
                self._table.setColumnWidth(i, 130)
                
        self._table.verticalHeader().setVisible(False) 
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) 
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)       
        self._table.setShowGrid(False) 
        self._table.setStyleSheet(
            f"QTableWidget {{ background-color: {Theme.BG_PANEL_DARK}; border: none; color: {Theme.TEXT_MAIN}; }}"
            f"QHeaderView::section {{ background-color: {Theme.BORDER_PANEL_DARK}; color: {Theme.TEXT_NORMAL}; border: none; padding: 6px; }}"
        )
        main.addWidget(self._table)

        # --- DỰNG THANH ĐIỀU KHIỂN PHÂN TRANG PHÍA DƯỚI BẢNG ---
        self._pagination_layout = QHBoxLayout()
        self._pagination_layout.setContentsMargins(5, 5, 5, 5)
        self._pagination_layout.setSpacing(10)

        self._btn_prev = QPushButton("‹ Trước")
        self._btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_prev.setStyleSheet(self._pill_style(False))

        self._page_label = QLabel("Trang 1 / 1")
        self._page_label.setStyleSheet(f"color: {Theme.TEXT_NORMAL}; font-size: 12px;")
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._btn_next = QPushButton("Sau ›")
        self._btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_next.setStyleSheet(self._pill_style(False))

        self._pagination_layout.addStretch()
        self._pagination_layout.addWidget(self._btn_prev)
        self._pagination_layout.addWidget(self._page_label)
        self._pagination_layout.addWidget(self._btn_next)
        self._pagination_layout.addStretch()

        main.addLayout(self._pagination_layout)

    # --- CÁC HÀM HỖ TRỢ VẼ UI ---
    def _create_method_cell(self, text: str) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(text)
        if text == "FIFO":
            bg_color = "#1E293B"      
            border_color = "#38BDF8"  
            text_color = "#38BDF8"
        else:  
            bg_color = "#1E293B"      
            border_color = "#F59E0B"  
            text_color = "#F59E0B"
            
        label.setStyleSheet(
            f"QLabel {{"
            f"  background-color: {bg_color};"
            f"  border: 1px solid {border_color};"
            f"  color: {text_color};"
            f"  padding: 2px 6px;"
            f"  border-radius: 4px;"
            f"  font-weight: bold;"
            f"  font-size: 11px;"
            f"}}"
        )
        layout.addWidget(label)
        return container

    def _create_badge_cell(self, text: str, variant: str) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge = Badge(text, variant) 
        layout.addWidget(badge)
        return container
    
    def _create_text_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return item    

    def _pill_style(self, active: bool) -> str:
        if active:
            return f"QPushButton {{ font-size:10px; padding:4px 9px; border-radius:10px; background:{Theme.BG_BTN_ACTIVE}; color:{Theme.COLOR_PRIMARY}; border:1px solid {Theme.BORDER_ACTIVE}; }}"
        return f"QPushButton {{ font-size:10px; padding:4px 9px; border-radius:10px; background:transparent; color:{Theme.TEXT_NORMAL}; border:1px solid {Theme.BORDER_NEUTRAL}; }} QPushButton:hover {{ color:{Theme.TEXT_MUTED}; border-color:{Theme.BORDER_HOVER}; }}"