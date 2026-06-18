import os
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QPushButton,
    QFrame
)
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QRectF, QByteArray
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtSvg import QSvgRenderer

from ui.components.badge import Badge
from ui.utils.theme import Theme 

# Load SVG icons từ môi trường
SVG_VIEW = os.getenv("SVG_VIEW", "")
SVG_EDIT = os.getenv("SVG_EDIT", "")


class _TableActionButton(QPushButton):
    """Nút thao tác nhỏ trong ô bảng dữ liệu, tự vẽ SVG Vector để đổi màu động"""

    def __init__(self, svg_str: str, action_type: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.raw_svg = svg_str
        self.action_type = action_type
        self._hovered = False

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def _get_current_color(self) -> str:
        """Định hình màu sắc của Icon khi hover hoặc bình thường dựa theo vai trò"""
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
        """Tự vẽ nền hover và icon vector"""
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


class DataTable(QWidget):
    row_selected = pyqtSignal(int)
    action_clicked = pyqtSignal(str, int)

    def __init__(self, columns: list[str], filters: list[str] | None = None, parent=None):
        super().__init__(parent)
        self._columns = columns
        self._all_data: list[dict] = [] 
        self._active_filter = "Tất cả"
        
        self._with_status = False  # Đóng vai trò kích hoạt bộ lọc trạng thái ẩn/hiện logic
        self._with_actions = False

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(10)

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
        search_icon.setStyleSheet(f"color: {Theme.TEXT_NORMAL}; font-size: 14px;")
        
        self._search = QLineEdit()
        self._search.setPlaceholderText("Tìm kiếm...")
        self._search.setStyleSheet(
            f"background: transparent; border: none; color: {Theme.TEXT_MAIN}; font-size: 12px; padding: 6px 0;"
        )
        self._search.textChanged.connect(self._apply_filter)
        sf_lay.addWidget(search_icon)
        sf_lay.addWidget(self._search, 1)

        top.addWidget(search_frame, 1)

        if filters:
            pills = QHBoxLayout()
            pills.setSpacing(5)
            self._filter_btns: list[QPushButton] = []
            for f in filters:
                btn = QPushButton(f)
                btn.setCheckable(True)
                btn.setChecked(f == "Tất cả")
                btn.setStyleSheet(self._pill_style(f == "Tất cả"))
                btn.clicked.connect(lambda _, name=f, b=btn: self._on_filter(name, b))
                pills.addWidget(btn)
                self._filter_btns.append(btn)
            top.addLayout(pills)

        main.addLayout(top)

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
        self._table.cellClicked.connect(lambda r, _: self.row_selected.emit(r))
        
        self._table.setStyleSheet(
            f"QTableWidget {{ background-color: {Theme.BG_PANEL_DARK}; border: none; color: {Theme.TEXT_MAIN}; }}"
            f"QHeaderView::section {{ background-color: {Theme.BORDER_PANEL_DARK}; color: {Theme.TEXT_NORMAL}; border: none; padding: 6px; }}"
        )
        main.addWidget(self._table)

    def load_data(self, data_list: list[dict], status: bool = False, action: bool = False):
        self._all_data = data_list
        self._with_status = status
        self._with_actions = action
        self._apply_filter()

    def _apply_filter(self):
        query = self._search.text().lower()
        self._table.setRowCount(0)
        
        for data_dict in self._all_data:
            # 1. KIỂM TRA TRẠNG THÁI (STATUS LOGIC) ĐỂ ẨN/HIỆN DÒNG
            if self._with_status:
                status_val = data_dict.get('status', 'Thành công')
                status_text = status_val[0] if isinstance(status_val, tuple) else status_val
                
                # Bỏ qua không dựng dòng này nếu trạng thái thuộc danh sách cần ẩn
                if status_text in ["Ẩn", "Khóa", "inactive"]:
                    continue  

            # 2. XỬ LÝ SEARCH & FILTER THEO TỪ KHÓA
            searchable_values = []
            for k, v in data_dict.items():
                if k == "status":
                    continue
                if isinstance(v, tuple): 
                    searchable_values.append(str(v[0]))
                else:
                    searchable_values.append(str(v))
                    
            searchable_text = " ".join(searchable_values).lower()

            if query and query not in searchable_text:
                continue
            if self._active_filter not in ("Tất cả", "") and self._active_filter not in searchable_text:
                continue
                
            # Đạt điều kiện -> Tiến hành dựng dòng
            self._insert_row(data_dict)

    def _insert_row(self, data_dict: dict):
        r = self._table.rowCount()
        # print(f"[DATA TABLE LOG] Đang dựng dòng thứ #{r} | Dữ liệu ô: {data_dict}")

        self._table.insertRow(r)
        self._table.setRowHeight(r, 38)
        
        # Khôi phục nguyên trạng: lấy danh sách các key tự động theo thứ tự trong data_dict
        dict_keys = [k for k in data_dict.keys() if k != 'status']
        total_cols = self._table.columnCount()

        content_cols_count = total_cols
        if self._with_actions:
            content_cols_count -= 1

        # Lặp điền dữ liệu tự động dựa theo thứ tự dict_keys ban đầu
        for col_idx in range(content_cols_count): 
            if col_idx < len(dict_keys):
                key = dict_keys[col_idx]
                val = data_dict.get(key, "")
                
                if isinstance(val, tuple):
                    badge_text = val[0]
                    badge_variant = val[1]
                    self._table.setCellWidget(r, col_idx, self._create_badge_cell(badge_text, badge_variant))
                else:
                    self._table.setItem(r, col_idx, self._create_text_item(str(val)))
            else:
                self._table.setItem(r, col_idx, self._create_text_item(""))

        # Dựng cột hành động (Thao tác) ở cuối cùng bảng nếu có bật
        if self._with_actions:
            action_col_idx = total_cols - 1
            actions_list = [("view", SVG_VIEW), ("edit", SVG_EDIT)]
            action_widget = self._create_action_cell(actions_list, r)
            
            self._table.setCellWidget(r, action_col_idx, action_widget)

    def _create_text_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        return item

    def _create_badge_cell(self, text: str, variant: str) -> QWidget:
        badge = Badge(text, variant)
        cell = QWidget()
        lay = QHBoxLayout(cell)
        lay.setContentsMargins(6, 0, 6, 0)
        lay.addWidget(badge)
        lay.addStretch()
        return cell

    def _create_action_cell(self, actions_list: list, row_index: int) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        for action_type, svg_str in actions_list:
            btn = _TableActionButton(svg_str, action_type)
            btn.clicked.connect(lambda _, act=action_type, r=row_index: self.action_clicked.emit(act, r))
            layout.addWidget(btn)
            
        return container

    def _on_filter(self, name: str, btn: QPushButton):
        self._active_filter = name
        for b in self._filter_btns:
            active = b.text() == name
            b.setChecked(active)
            b.setStyleSheet(self._pill_style(active))
        self._apply_filter()

    @staticmethod
    def _pill_style(active: bool) -> str:
        if active:
            return f"QPushButton {{ font-size:10px; padding:4px 9px; border-radius:10px; background:{Theme.BG_BTN_ACTIVE}; color:{Theme.COLOR_PRIMARY}; border:1px solid {Theme.BORDER_ACTIVE}; }}"
        return f"QPushButton {{ font-size:10px; padding:4px 9px; border-radius:10px; background:transparent; color:{Theme.TEXT_NORMAL}; border:1px solid {Theme.BORDER_NEUTRAL}; }} QPushButton:hover {{ color:{Theme.TEXT_MUTED}; border-color:{Theme.BORDER_HOVER}; }}"