from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QPushButton,
    QFrame
)
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

from ui.components.badge import Badge
from ui.utils.image_utils import create_svg_icon

# Định nghĩa sẵn các chuỗi SVG mẫu nếu file utils của bạn cần dùng
SVG_VIEW = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path fill="#8899b4" d="M320 96C239.2 96 174.5 132.8 127.4 176.6C80.6 220.1 49.3 272 34.4 307.7C31.1 315.6 31.1 324.4 34.4 332.3C49.3 368 80.6 420 127.4 463.4C174.5 507.1 239.2 544 320 544C400.8 544 465.5 507.2 512.6 463.4C559.4 419.9 590.7 368 605.6 332.3C608.9 324.4 608.9 315.6 605.6 307.7C590.7 272 559.4 220 512.6 176.6C465.5 132.9 400.8 96 320 96zM176 320C176 240.5 240.5 176 320 176C399.5 176 464 240.5 464 320C464 399.5 399.5 464 320 464C240.5 464 176 399.5 176 320zM320 256C320 291.3 291.3 320 256 320C244.5 320 233.7 317 224.3 311.6C223.3 322.5 224.2 333.7 227.2 344.8C240.9 396 293.6 426.4 344.8 412.7C396 399 426.4 346.3 412.7 295.1C400.5 249.4 357.2 220.3 311.6 224.3C316.9 233.6 320 244.4 320 256z"/></svg>"""
SVG_EDIT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path fill="#378ADD" d="M535.6 85.7C513.7 63.8 478.3 63.8 456.4 85.7L432 110.1L529.9 208L554.3 183.6C576.2 161.7 576.2 126.3 554.3 104.4L535.6 85.7zM236.4 305.7C230.3 311.8 225.6 319.3 222.9 327.6L193.3 416.4C190.4 425 192.7 434.5 199.1 441C205.5 447.5 215 449.7 223.7 446.8L312.5 417.2C320.7 414.5 328.2 409.8 334.4 403.7L496 241.9L398.1 144L236.4 305.7zM160 128C107 128 64 171 64 224L64 480C64 533 107 576 160 576L416 576C469 576 512 533 512 480L512 384C512 366.3 497.7 352 480 352C462.3 352 448 366.3 448 384L448 480C448 497.7 433.7 512 416 512L160 512C142.3 512 128 497.7 128 480L128 224C128 206.3 142.3 192 160 192L256 192C273.7 192 288 177.7 288 160C288 142.3 273.7 128 256 128L160 128z"/></svg>"""

class DataTable(QWidget):
    """
    Reusable table với thanh tìm kiếm, bộ lọc pill và các nút hành động tương tác.
    Đã được cập nhật để nhận dữ liệu dạng List[dict].

    Signals
    -------
    row_selected(int)   : Phát ra khi một dòng được click
    action_clicked(str, int) : Phát ra khi nút hành động được click (action_type, row_index)
    """

    row_selected = pyqtSignal(int)
    action_clicked = pyqtSignal(str, int)

    def __init__(
        self,
        columns: list[str],
        filters: list[str] | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._columns = columns
        self._all_data: list[dict] = []  # Thay đổi thành lưu danh sách dict
        self._active_filter = "Tất cả"
        
        # Lưu các cờ cấu hình hiển thị bổ sung
        self._with_status = False
        self._with_actions = False

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(10)

        # Thanh tìm kiếm + bộ lọc
        top = QHBoxLayout()
        top.setSpacing(8)

        search_frame = QFrame()
        search_frame.setStyleSheet(
            "QFrame { background:#161b26; border:1px solid #2a3347;"
            " border-radius:6px; }"
        )
        sf_lay = QHBoxLayout(search_frame)
        sf_lay.setContentsMargins(10, 0, 10, 0)
        sf_lay.setSpacing(6)
        search_icon = QLabel("⌕")
        search_icon.setStyleSheet("color:#4a5a78; font-size:14px;")
        self._search = QLineEdit()
        self._search.setPlaceholderText("Tìm kiếm...")
        self._search.setStyleSheet(
            "background:transparent; border:none; color:#e2e8f0;"
            " font-size:12px; padding:6px 0;"
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

        # Khởi tạo Table
        self._table = QTableWidget()
        self._table.setColumnCount(len(columns))
        self._table.setHorizontalHeaderLabels(columns)
        
        # Đặt chế độ căn chỉnh thủ công
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Độ rộng các cột tương ứng ["Sản phẩm", "Barcode", "Danh mục", "Tồn kho", "Loại", "Trạng thái", "Thao tác"]
        self._table.setColumnWidth(0, 250)  # Sản phẩm
        self._table.setColumnWidth(1, 130)  # Barcode
        self._table.setColumnWidth(2, 100)  # Danh mục
        self._table.setColumnWidth(3, 80)   # Tồn kho
        self._table.setColumnWidth(4, 70)   # Loại FIFO/LIFO
        self._table.setColumnWidth(5, 110)  # Trạng thái
        self._table.setColumnWidth(6, 80)   # Thao tác
        
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
                
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.cellClicked.connect(lambda r, _: self.row_selected.emit(r))
        main.addWidget(self._table)

    # ------------------------------------------------------------------
    def load_data(self, data_list: list[dict], status: bool = False, action: bool = False):
        """
        Nạp dữ liệu mới vào bảng dưới dạng List[dict].
        
        Tham số:
        --------
        data_list: Danh sách các dict (Ví dụ: {'barcode': '123', 'product_name': 'My OmaChi', ...})
        status   : Tự động hiển thị cột trạng thái (Nếu dict không có, sẽ lấy mặc định)
        action   : Tự động thêm cột nút bấm View/Edit vào cuối bảng
        """
        self._all_data = data_list
        self._with_status = status
        self._with_actions = action
        self._apply_filter()

    def _apply_filter(self):
        query = self._search.text().lower()
        self._table.setRowCount(0)
        
        for data_dict in self._all_data:
            # Lấy tất cả giá trị text thô từ dict để tìm kiếm (Bỏ qua cấu hình icon/badge phức tạp)
            # dict.values() sẽ quét qua toàn bộ product_name, barcode, category...
            searchable_values = []
            for v in data_dict.values():
                if isinstance(v, tuple): # Phòng trường hợp loại chiến lược dạng tuple ("FIFO", "fifo")
                    searchable_values.append(str(v[0]))
                else:
                    searchable_values.append(str(v))
                    
            searchable_text = " ".join(searchable_values).lower()

            # Bộ lọc tìm kiếm ô Text
            if query and query not in searchable_text:
                continue
            # Bộ lọc của các nút Pill (Ví dụ: lọc theo loại chiến lược FIFO/LIFO hoặc trạng thái nếu có)
            if self._active_filter not in ("Tất cả", "") and self._active_filter not in searchable_text:
                continue
                
            self._insert_row(data_dict)

    def _insert_row(self, data_dict: dict):
        r = self._table.rowCount()
        self._table.insertRow(r)
        self._table.setRowHeight(r, 38)
        
        # Map dữ liệu từ dict một cách an toàn bằng dict.get(key, giá_trị_mặc_định)
        # Giúp bảng không bị lỗi kể cả khi dữ liệu backend trả về thiếu trường.
        product_name  = data_dict.get('product_name', '')
        barcode       = data_dict.get('barcode', '')
        category      = data_dict.get('category', 'Chưa phân loại')
        stock         = data_dict.get('stock', '0')
        strategy_type = data_dict.get('strategy_type', 'FIFO')
        
        # Xử lý trường hợp strategy_type truyền vào dạng chuỗi đơn "FIFO" hoặc tuple ("FIFO", "fifo")
        strategy_text = strategy_type[0] if isinstance(strategy_type, tuple) else strategy_type
        strategy_variant = strategy_type[1] if isinstance(strategy_type, tuple) else "fifo"

        # Cột 0: Tên sản phẩm
        self._table.setItem(r, 0, self._create_text_item(product_name))
        
        # Cột 1: Barcode
        self._table.setItem(r, 1, self._create_text_item(barcode))
        
        # Cột 2: Danh mục
        self._table.setItem(r, 2, self._create_text_item(category))
        
        # Cột 3: Tồn kho
        self._table.setItem(r, 3, self._create_text_item(str(stock)))
        
        # Cột 4: Loại chiến lược (Badge FIFO/LIFO)
        self._table.setCellWidget(r, 4, self._create_badge_cell(strategy_text, strategy_variant))
        
        # Cột 5: Trạng thái (Phụ thuộc vào biến truyền từ hàm load_data)
        if self._with_status:
            # Lấy trạng thái từ dict, nếu không có mặc định là "Bình thường"
            status_data = data_dict.get('status', ("Bình thường", "success"))
            status_text = status_data[0] if isinstance(status_data, tuple) else status_data
            status_variant = status_data[1] if isinstance(status_data, tuple) else "success"
            self._table.setCellWidget(r, 5, self._create_badge_cell(status_text, status_variant))
        else:
            self._table.setItem(r, 5, self._create_text_item("-"))

        # Cột 6: Thao tác / Actions (Phụ thuộc vào biến truyền từ hàm load_data)
        if self._with_actions:
            # Tự động gán cấu hình View/Edit mặc định nếu cờ `action=True`
            actions_list = [("view", SVG_VIEW), ("edit", SVG_EDIT)]
            action_widget = self._create_action_cell(actions_list, r)
            self._table.setCellWidget(r, 6, action_widget)
        else:
            self._table.setItem(r, 6, self._create_text_item("-"))

    def _create_text_item(self, text: str) -> QTableWidgetItem:
        """Hàm helper tạo nhanh QTableWidgetItem căn giữa lề trái"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        return item

    def _create_badge_cell(self, text: str, variant: str) -> QWidget:
        """Hàm helper bọc Badge vào Layout để hiển thị trong Table Cell"""
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
            btn = QPushButton()
            btn.setFixedSize(24, 24)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton { background: transparent; border: none; border-radius: 4px; }"
                "QPushButton:hover { background: #1e2740; }"
            )
            
            color = "#378ADD" if action_type == "edit" else "#FFFFFF"
            icon = create_svg_icon(svg_str, color)
            
            btn.setIcon(icon)
            btn.setIconSize(QSize(14, 14))
            
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
            return (
                "QPushButton { font-size:10px; padding:4px 9px;"
                " border-radius:10px; background:#1a2e4a; color:#5b9cf6;"
                " border:1px solid #2a4a6e; }"
            )
        return (
            "QPushButton { font-size:10px; padding:4px 9px;"
            " border-radius:10px; background:transparent; color:#4a5a78;"
            " border:1px solid #2a3347; }"
            "QPushButton:hover { color:#8899b4; border-color:#3a4560; }"
        )