import os
import re
import math  
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QPushButton,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QByteArray
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer

from ui.components.badge import Badge
from ui.utils.theme import Theme 

# Đọc các chuỗi mã nguồn SVG từ biến môi trường để vẽ các icon View/Edit
SVG_VIEW = os.getenv("SVG_VIEW", "")
SVG_EDIT = os.getenv("SVG_EDIT", "")


class _TableActionButton(QPushButton):
    """Nút thao tác nhỏ (Xem/Sửa) nằm trong ô cuối cùng của mỗi dòng.
    Tự render mã nguồn SVG vector để có thể đổi màu động khi hover chuột."""

    def __init__(self, svg_str: str, action_type: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24) # Kích thước nút vuông 24x24 px
        self.setCursor(Qt.CursorShape.PointingHandCursor) # Đổi con trỏ chuột thành hình bàn tay
        
        self.raw_svg = svg_str
        self.action_type = action_type # Loại hành động: "view" hoặc "edit"
        self._hovered = False          # Trạng thái di chuột vào nút

    def enterEvent(self, event):
        """Sự kiện kích hoạt khi con trỏ chuột bắt đầu đi vào vùng của nút"""
        self._hovered = True
        self.update() # Yêu cầu nút vẽ lại giao diện (kích hoạt paintEvent)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Sự kiện kích hoạt khi con trỏ chuột rời khỏi vùng của nút"""
        self._hovered = False
        self.update() # Yêu cầu nút vẽ lại giao diện (kích hoạt paintEvent)
        super().leaveEvent(event)

    def _get_current_color(self) -> str:
        """Xác định màu sắc của Icon dựa trên trạng thái chuột và loại hành động"""
        if self._hovered:
            return Theme.COLOR_HOVER_LIGHT # Màu khi hover chung
        # Nếu bình thường: nút edit có màu Primary, nút view có màu chữ mặc định
        return Theme.COLOR_PRIMARY if self.action_type == "edit" else Theme.TEXT_NORMAL

    def _render_svg(self, svg_str: str, color_hex: str) -> QSvgRenderer | None:
        """Thay đổi thuộc tính 'fill' trong chuỗi SVG gốc để đổi màu Icon theo Theme"""
        if not svg_str.strip():
            return None
        # Thực hiện Regex tìm thuộc tính fill="..." để thay thế bằng mã màu mới
        if "fill=" not in svg_str:
            svg_str = svg_str.replace('<svg', f'<svg fill="{color_hex}"')
        else:
            svg_str = re.sub(r'fill="[^"]+"', f'fill="{color_hex}"', svg_str)
        
        # Chuyển đổi chuỗi SVG sang mảng byte để nạp vào bộ dựng hình của Qt (QSvgRenderer)
        byte_array = QByteArray(svg_str.strip().encode('utf-8'))
        renderer = QSvgRenderer(byte_array)
        return renderer if renderer.isValid() else None

    def paintEvent(self, event):
        """Hàm tự vẽ giao diện nút: Tạo nền bo góc khi hover và vẽ icon SVG vào tâm"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) # Bật khử răng cưa giúp nét vẽ mịn hơn

        w, h = self.width(), self.height()
        current_color = self._get_current_color()

        # Nếu đang hover, vẽ một hình chữ nhật bo góc làm nền mờ phía sau nút
        if self._hovered:
            painter.setBrush(QColor(Theme.BG_BTN_HOVER))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(0, 0, w, h, 4, 4)

        # Tiến hành căn chỉnh và vẽ Icon SVG vào chính giữa nút
        renderer = self._render_svg(self.raw_svg, current_color)
        if renderer:
            icon_size = 14
            icon_rect = QRectF((w - icon_size) / 2, (h - icon_size) / 2, icon_size, icon_size)
            renderer.render(painter, icon_rect)

        painter.end()


class DataTable(QWidget):
    # Định nghĩa 2 tín hiệu (Signal) để truyền dữ liệu ra màn hình cha khi người dùng tương tác
    row_selected = pyqtSignal(int)          # Bắn ra Index gốc khi click đúp/click dòng
    action_clicked = pyqtSignal(str, int)   # Bắn ra tên hành động ("view"/"edit") và Index gốc tương ứng

    def __init__(self, columns: list[str], filters: list[str] | None = None, parent=None):
        super().__init__(parent)
        self._columns = columns
        self._all_data: list[dict] = []     # Nơi lưu trữ bản sao dữ liệu gốc do backend đổ vào
        self._active_filter = "Tất cả"      # Tên tab phân loại đang được chọn mặc định
        
        self._with_status = False  
        self._with_actions = False

        # --- KHỞI TẠO CÁC BIẾN QUẢN LÝ PHÂN TRANG ---
        self.current_page = 1               # Trang hiện tại bắt đầu từ 1
        self.page_size = 20                 # Giới hạn hiển thị tối đa 20 sản phẩm/trang
        self._filtered_data: list[dict] = []# Lưu trữ tập dữ liệu tạm thời sau khi lọc (dùng tính tổng số trang)

        # Thiết lập Layout chính theo chiều dọc
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(10)

        # --- DỰNG KHU VỰC THANH CÔNG CỤ PHÍA TRÊN (SEARCH + PILLS FILTER) ---
        top = QHBoxLayout()
        top.setSpacing(8)

        # Khung bọc ô Tìm kiếm (Search Bar)
        search_frame = QFrame()
        search_frame.setStyleSheet(
            f"QFrame {{ background: {Theme.BG_INPUT}; border: 1px solid {Theme.BORDER_INPUT}; border-radius: 6px; }}"
        )
        sf_lay = QHBoxLayout(search_frame)
        sf_lay.setContentsMargins(10, 0, 10, 0)
        sf_lay.setSpacing(6)
        
        search_icon = QLabel("⌕") # Ký tự icon kính lúp tạm thời
        search_icon.setStyleSheet(f"color: {Theme.TEXT_NORMAL}; font-size: 14px;")
        
        self._search = QLineEdit()
        self._search.setPlaceholderText("Tìm kiếm...")
        self._search.setStyleSheet(
            f"background: transparent; border: none; color: {Theme.TEXT_MAIN}; font-size: 12px; padding: 6px 0;"
        )
        self._search.textChanged.connect(self._on_search_changed) # Gõ chữ là tự động kích hoạt lọc lại dữ liệu
        sf_lay.addWidget(search_icon)
        sf_lay.addWidget(self._search, 1)

        top.addWidget(search_frame, 1) # Cho Search Bar chiếm diện tích lớn nhất thanh top

        # Nếu màn hình cha có truyền danh sách bộ lọc (ví dụ: ["Tất cả", "Hết hàng", "Sắp hết hàng"])
        if filters:
            pills = QHBoxLayout()
            pills.setSpacing(5)
            self._filter_btns: list[QPushButton] = []
            for f in filters:
                btn = QPushButton(f)
                btn.setCheckable(True)
                btn.setChecked(f == "Tất cả")
                btn.setStyleSheet(self._pill_style(f == "Tất cả"))
                # Khi click tab, đổi trạng thái và thực hiện chạy lại bộ lọc
                btn.clicked.connect(lambda _, name=f, b=btn: self._on_filter(name, b))
                pills.addWidget(btn)
                self._filter_btns.append(btn)
            top.addLayout(pills)

        main.addLayout(top)

        # --- CẤU HÌNH BẢNG QTABLEWIDGET HIỂN THỊ ---
        self._table = QTableWidget()
        self._table.setColumnCount(len(columns))
        self._table.setHorizontalHeaderLabels(columns)
        
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Cấu hình độ rộng: Cột đầu tiên (thường là Tên sản phẩm) tự giãn, các cột sau cố định 130px
        for i in range(len(columns)):
            if i == 0:
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
                self._table.setColumnWidth(i, 130)
                
        self._table.verticalHeader().setVisible(False) # Ẩn cột số thứ tự mặc định của Qt
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) # Bấm vào là chọn nguyên cả dòng
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)       # Không cho người dùng sửa trực tiếp trên ô
        self._table.setShowGrid(False) # Ẩn đường lưới viền ô nhằm tối ưu hóa giao diện phẳng phẳng sạch sẽ
        
        self._table.cellClicked.connect(self._on_cell_clicked) # Đăng ký sự kiện click chuột vào ô dữ liệu
        
        self._table.setStyleSheet(
            f"QTableWidget {{ background-color: {Theme.BG_PANEL_DARK}; border: none; color: {Theme.TEXT_MAIN}; }}"
            f"QHeaderView::section {{ background-color: {Theme.BORDER_PANEL_DARK}; color: {Theme.TEXT_NORMAL}; border: none; padding: 6px; }}"
        )
        main.addWidget(self._table)

        # --- DỰNG THANH ĐIỀU KHIỂN PHÂN TRANG PHÍA DƯỚI BẢNG (PAGINATION BAR) ---
        self._pagination_layout = QHBoxLayout()
        self._pagination_layout.setContentsMargins(5, 5, 5, 5)
        self._pagination_layout.setSpacing(10)

        # Nút chuyển về trang trước
        self._btn_prev = QPushButton("‹ Trước")
        self._btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_prev.setStyleSheet(self._pill_style(False))
        self._btn_prev.clicked.connect(self._prev_page)

        # Nhãn hiển thị vị trí trang hiện tại (ví dụ: "Trang 2 / 10")
        self._page_label = QLabel("Trang 1 / 1")
        self._page_label.setStyleSheet(f"color: {Theme.TEXT_NORMAL}; font-size: 12px;")
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Nút tiến tới trang kế tiếp
        self._btn_next = QPushButton("Sau ›")
        self._btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_next.setStyleSheet(self._pill_style(False))
        self._btn_next.clicked.connect(self._next_page)

        # Sử dụng Stretch dồn cụm nút phân trang vào chính giữa thanh đáy
        self._pagination_layout.addStretch()
        self._pagination_layout.addWidget(self._btn_prev)
        self._pagination_layout.addWidget(self._page_label)
        self._pagination_layout.addWidget(self._btn_next)
        self._pagination_layout.addStretch()

        main.addLayout(self._pagination_layout)

    def load_data(self, data_list: list[dict], status: bool = False, action: bool = False):
        """Hàm công khai (Public) để màn hình cha đẩy cục dữ liệu thô từ API/DB vào bảng"""
        self._all_data = data_list
        self._with_status = status   # Xác định xem bảng có hiển thị Badge trạng thái ẩn/hiện hay không
        self._with_actions = action  # Xác định xem có cột chức năng (Xem/Sửa) ở cuối không
        self.current_page = 1        # Reset trang hiện tại về 1 bất cứ khi nào nạp cục dữ liệu mới
        self._apply_filter()         # Kích hoạt tính toán lọc dữ liệu và hiển thị lên UI

    def _on_search_changed(self):
        """Xử lý sự kiện khi chuỗi ký tự ô tìm kiếm thay đổi"""
        self.current_page = 1        # Khi gõ tìm kiếm, ép trang quay về trang đầu tiên
        self._apply_filter()

    def _apply_filter(self):
        """Hàm xử lý LÝ THUYẾT TRỌNG TÂM: Lọc dữ liệu, tính số trang và cắt lát data đưa lên UI"""
        query = self._search.text().lower()
        self._filtered_data = []
        
        # --- BƯỚC 1: LỌC DỮ LIỆU THÔ DỰA THEO TỪ KHÓA TÌM KIẾM VÀ TAB PHÂN LOẠI ---
        for data_dict in self._all_data:
            # Nếu có cấu hình trạng thái, bỏ qua các bản ghi bị ẩn hoặc khóa ngầm định
            if self._with_status:
                status_val = data_dict.get('status', 'Thành công')
                status_text = status_val[0] if isinstance(status_val, tuple) else status_val
                if status_text in ["Ẩn", "Khóa", "inactive"]:
                    continue  

            # Hợp nhất toàn bộ các trường text trong dict thành chuỗi dài để so khớp từ khóa (Search Full-text)
            searchable_values = []
            for k, v in data_dict.items():
                if k == "status":
                    continue
                if isinstance(v, tuple): 
                    searchable_values.append(str(v[0]))
                else:
                    searchable_values.append(str(v))
                    
            searchable_text = " ".join(searchable_values).lower()

            # Kiểm tra xem chuỗi dữ liệu có khớp từ khóa và tab phân loại không, đạt yêu cầu thì giữ lại
            if query and query not in searchable_text:
                continue
            if self._active_filter not in ("Tất cả", "") and self._active_filter not in searchable_text:
                continue
                
            self._filtered_data.append(data_dict)

        # --- BƯỚC 2: TÍNH TOÁN SỐ TRANG (LOGIC PHÂN TRANG) ---
        total_items = len(self._filtered_data)
        # Sử dụng math.ceil để làm tròn lên tổng số trang (Ví dụ: 21 item / 20 = 1.05 -> Làm tròn thành 2 trang)
        total_pages = math.ceil(total_items / self.page_size) if total_items > 0 else 1
        
        # Phòng vệ: Nếu số trang hiện tại vô tình lớn hơn tổng số trang vừa tính, ép về trang cuối hợp lệ
        if self.current_page > total_pages:
            self.current_page = total_pages
            
        # Cập nhật thông tin chữ hiển thị trên thanh điều hướng phân trang
        self._page_label.setText(f"Trang {self.current_page} / {total_pages}")
        # Ẩn/Hiện nút Trở trước hoặc Trang kế dựa trên việc có đang đứng ở trang biên hay không
        self._btn_prev.setEnabled(self.current_page > 1)
        self._btn_next.setEnabled(self.current_page < total_pages)

        # --- BƯỚC 3: CẮT LÁT DỮ LIỆU THEO TRANG VÀ ĐỔ VÀO BẢNG HÀNG loạt ---
        self._table.setRowCount(0) # Xóa sạch các dòng giao diện của trang cũ
        # Công thức tính Index cắt mảng dữ liệu theo trang hiện tại
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_data = self._filtered_data[start_idx:end_idx] # Chỉ lấy tối đa đúng 20 bản ghi phục vụ trang này

        # Tiến hành duyệt 20 bản ghi này dựng dòng đưa lên QTableWidget
        for data_dict in page_data:
            self._insert_row(data_dict)

    def _insert_row(self, data_dict: dict):
        """Hàm nội bộ thực hiện dựng và đẩy cấu trúc một dòng dữ liệu mới vào QTableWidget"""
        r = self._table.rowCount()
        self._table.insertRow(r)
        self._table.setRowHeight(r, 38) # Định cấu hình độ cao mỗi dòng đồng đều 38px
        
        # Tách bỏ khóa trường 'status' chuyên biệt ra để lọc các cột thông tin thuần túy
        dict_keys = [k for k in data_dict.keys() if k != 'status']
        total_cols = self._table.columnCount()

        # Tính toán số lượng cột chứa nội dung chữ (Nếu có cột action cuối thì trừ bớt đi 1)
        content_cols_count = total_cols
        if self._with_actions:
            content_cols_count -= 1

        # Đổ dữ liệu vào từng ô (Cell) trên dòng tương ứng
        for col_idx in range(content_cols_count): 
            if col_idx < len(dict_keys):
                key = dict_keys[col_idx]
                val = data_dict.get(key, "")
                
                # Nếu dữ liệu trường đó là Tuple dạng ("Thành công", "success") -> Vẽ ô hiển thị dạng Badge màu
                if isinstance(val, tuple):
                    badge_text = val[0] #
                    badge_variant = val[1]
                    self._table.setCellWidget(r, col_idx, self._create_badge_cell(badge_text, badge_variant))
                else:
                    # Ngược lại, đổ chữ thông thường vào ô bảng dữ liệu
                    self._table.setItem(r, col_idx, self._create_text_item(str(val)))
            else:
                self._table.setItem(r, col_idx, self._create_text_item(""))

        # Nếu bảng yêu cầu bật cột hành động Xem/Sửa ở cuối bảng
        if self._with_actions:
            action_col_idx = total_cols - 1
            actions_list = [("view", SVG_VIEW), ("edit", SVG_EDIT)]
            # Tạo cụm widget chứa 2 nút hành động nhỏ và truyền chỉ số dòng hiện tại vào để định danh
            action_widget = self._create_action_cell(actions_list, r)
            self._table.setCellWidget(r, action_col_idx, action_widget)

    def _on_cell_clicked(self, row: int, col: int):
        """Ánh xạ dòng giao diện ngược lại mảng dữ liệu gốc khi click vào một dòng bất kỳ"""
        if not self._filtered_data:
            return
        # Tính toán ngược vị trí chuẩn xác: Lấy số trang hiện tại nhân 20 rồi cộng dồn với hàng được click
        target_filtered_item = self._filtered_data[(self.current_page - 1) * self.page_size + row]
        try:
            # Dò tìm vị trí index tuyệt đối của phần tử này nằm ở đâu trong mảng thô _all_data ban đầu
            actual_global_idx = self._all_data.index(target_filtered_item)
            self.row_selected.emit(actual_global_idx) # Phát tín hiệu Index gốc ra ngoài
        except ValueError:
            self.row_selected.emit(row) # Dự phòng phát chỉ số hàng hiện tại nếu mảng lỗi

    def _create_action_cell(self, actions_list: list, row_index: int) -> QWidget:
        """Tạo một widget container nằm bên trong ô cột cuối chứa cụm nút Xem/Sửa"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # Căn cụm nút nằm chính giữa ô
        
        for action_type, svg_str in actions_list:
            btn = _TableActionButton(svg_str, action_type)
            # Sử dụng lambda để gom tên hành động kèm vị trí dòng truyền trực tiếp vào hàm kích hoạt
            btn.clicked.connect(lambda _, act=action_type, r=row_index: self._on_action_triggered(act, r))
            layout.addWidget(btn)
            
        return container

    def _on_action_triggered(self, action_type: str, row_index: int):
        """Xử lý tính toán vị trí index gốc tương tự khi người dùng click vào các nút nhỏ View/Edit"""
        if not self._filtered_data:
            return
        # Ánh xạ dòng UI dòng (0-19) sang chỉ số dòng thực tế trong mảng danh sách đã lọc
        target_filtered_item = self._filtered_data[(self.current_page - 1) * self.page_size + row_index]
        try:
            # Tìm vị trí chính xác trong mảng dữ liệu tổng _all_data để bắn ra ngoài
            actual_global_idx = self._all_data.index(target_filtered_item)
            self.action_clicked.emit(action_type, actual_global_idx)
        except ValueError:
            self.action_clicked.emit(action_type, row_index)

    def _prev_page(self):
        """Chức năng lùi lại 1 trang khi click nút 'Trước'"""
        if self.current_page > 1:
            self.current_page -= 1
            self._apply_filter() # Render lại bảng theo trang mới

    def _next_page(self):
        """Chức năng tiến lên 1 trang khi click nút 'Sau'"""
        total_items = len(self._filtered_data)
        total_pages = math.ceil(total_items / self.page_size) if total_items > 0 else 1
        if self.current_page < total_pages:
            self.current_page += 1
            self._apply_filter() # Render lại bảng theo trang mới

    def _on_filter(self, name: str, btn: QPushButton):
        """Xử lý logic khi người dùng nhấn chuyển đổi qua lại giữa các Tab phân loại sản phẩm"""
        self._active_filter = name
        self.current_page = 1  # Đổi tab phân loại là phải ép trang quay về trang 1
        for b in self._filter_btns:
            active = b.text() == name
            b.setChecked(active)
            b.setStyleSheet(self._pill_style(active)) # Đổi style sáng/tối dựa theo trạng thái active
        self._apply_filter()

    def _create_badge_cell(self, text: str, variant: str) -> QWidget:
        """Tạo ô đặc biệt chứa thành phần Badge màu bo góc (Dùng hiển thị trạng thái)"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge = Badge(text, variant) 
        layout.addWidget(badge)
        return container
    
    def _create_text_item(self, text: str) -> QTableWidgetItem:
        """Tạo một ô text chuẩn mực cho QTableWidget, cấu hình căn lề chữ bên trái và ở giữa theo chiều dọc"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return item    

    def _pill_style(self, active: bool) -> str:
        """Trả về mã CSS StyleSheet định hình màu sắc cho các nút điều hướng và tab phân loại"""
        if active:
            # Màu rực rỡ nổi bật khi nút đang ở trạng thái được chọn (Active)
            return f"QPushButton {{ font-size:10px; padding:4px 9px; border-radius:10px; background:{Theme.BG_BTN_ACTIVE}; color:{Theme.COLOR_PRIMARY}; border:1px solid {Theme.BORDER_ACTIVE}; }}"
        # Màu trung tính, mờ khi nút ở trạng thái thường
        return f"QPushButton {{ font-size:10px; padding:4px 9px; border-radius:10px; background:transparent; color:{Theme.TEXT_NORMAL}; border:1px solid {Theme.BORDER_NEUTRAL}; }} QPushButton:hover {{ color:{Theme.TEXT_MUTED}; border-color:{Theme.BORDER_HOVER}; }}"