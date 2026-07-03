# table_logic.py
import math
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

# Import giao diện đã tách
from .table_ui import DataTableUI, _TableActionButton, SVG_VIEW, SVG_EDIT

class DataTable(DataTableUI):
    """Lớp xử lý Logic bao gồm: Lọc dữ liệu, phân trang và bắn tín hiệu"""
    
    # Định nghĩa 2 tín hiệu (Signal)
    row_selected = pyqtSignal(int)       # (index của dòng được chọn trong danh sách gốc)    
    action_clicked = pyqtSignal(str, int)    # (action_type, row_index)

    def __init__(self, columns: list[str], filters: list[str] | None = None, parent=None):
        super().__init__(columns, filters, parent)
        
        self._all_data: list[dict] = []     
        self._active_filter = "Tất cả"      
        
        self._with_status = False  
        self._with_actions = False

        self.current_page = 1               
        self.page_size = 20                 
        self._filtered_data: list[dict] = []

        self._connect_signals() # Lắng nghe thao tác của người dùng trên giao diện.

    def _connect_signals(self):
        """Kết nối các sự kiện trên UI tới hàm xử lý Logic"""
        self._search.textChanged.connect(self._on_search_changed) 
        self._table.cellClicked.connect(self._on_cell_clicked) 
        self._btn_prev.clicked.connect(self._prev_page)
        self._btn_next.clicked.connect(self._next_page)

        # Kết nối sự kiện cho tab phân loại
        for name, btn in self._filter_btns_dict.items():
            btn.clicked.connect(lambda _, n=name, b=btn: self._on_filter(n, b))

    def load_data(self, data_list: list[dict], status: bool = False, action: bool = False):
        self._all_data = data_list
        self._with_status = status   
        self._with_actions = action  
        self.current_page = 1
        # print(f"[DEBUG]: load_data called with {len(data_list)} items, status={status}, action={action}")        
        self._apply_filter()         

    def _on_search_changed(self):
        self.current_page = 1        
        self._apply_filter()

    def _apply_filter(self):
        query = self._search.text().lower()
        self._filtered_data = []
        
        # --- BƯỚC 1: LỌC DỮ LIỆU ---
        for data_dict in self._all_data:
            if self._with_status:
                status_val = data_dict.get('status', 'Thành công')
                status_text = status_val[0] if isinstance(status_val, tuple) else status_val
                if status_text in ["Ẩn", "Khóa", "inactive"]:
                    continue  

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
                
            self._filtered_data.append(data_dict)

        # --- BƯỚC 2: TÍNH TOÁN SỐ TRANG ---[cite: 1]
        total_items = len(self._filtered_data)
        total_pages = math.ceil(total_items / self.page_size) if total_items > 0 else 1
        
        if self.current_page > total_pages:
            self.current_page = total_pages
            
        self._page_label.setText(f"Trang {self.current_page} / {total_pages}")
        self._btn_prev.setEnabled(self.current_page > 1)
        self._btn_next.setEnabled(self.current_page < total_pages)

        # --- BƯỚC 3: CẮT LÁT DỮ LIỆU ĐỔ VÀO BẢNG ---
        self._table.setRowCount(0) 
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_data = self._filtered_data[start_idx:end_idx] 

        # --- BƯỚC 4: ĐỔ DỮ LIỆU VÀO BẢNG QTABLEWIDGET ---
        for data_dict in page_data:
            self._insert_row(data_dict)

    def _insert_row(self, data_dict: dict):
        """Xử lý đẩy cấu trúc một dòng dữ liệu vào QTableWidget"""
        r = self._table.rowCount()
        self._table.insertRow(r)
        self._table.setRowHeight(r, 38) 
        
        # Đoạn này xác định thứ tự các cột dựa trên key của dict, bỏ qua cột 'status' và cột hành động nếu có
        dict_keys = []
        for k in data_dict.keys():
            if k != 'status':
                dict_keys.append(k)
        
        # print (f"[DEBUG]: dict_keys = {dict_keys}, data_dict = {data_dict}")
                
        total_cols = self._table.columnCount()

        # Nếu có không có cột hành động, thì chỉ cần đổ dữ liệu theo số cột thực tế
        if self._with_actions:
            content_cols_count = total_cols - 1
        else:
            content_cols_count = total_cols

        # print(f"[DEBUG]: content_cols_count = {content_cols_count}")
        # print(f"[DEBUG]: total_cols = {total_cols}")
        for col_idx in range(content_cols_count):  # lặp theo số cột thực tế (không tính cột hành động)
            if col_idx < len(dict_keys):
                key = dict_keys[col_idx]
                val = data_dict.get(key, "")
                
                if isinstance(val, tuple):
                    badge_text = val[0] # VD: 
                    badge_variant = val[1]
                    self._table.setCellWidget(r, col_idx, self._create_badge_cell(badge_text, badge_variant))
                
                elif str(val).strip() in ("LIFO", "FIFO"):
                    method_widget = self._create_method_cell(str(val).strip())
                    self._table.setCellWidget(r, col_idx, method_widget)
                
                else:
                    self._table.setItem(r, col_idx, self._create_text_item(str(val)))
            else:
                self._table.setItem(r, col_idx, self._create_text_item(""))

        # print(f"[DEBUG]: self._with_actions = {self._with_actions}, total_cols = {total_cols}, content_cols_count = {content_cols_count}")
        
        if self._with_actions:
            action_col_idx = total_cols - 1
            actions_list = [("view", SVG_VIEW), ("edit", SVG_EDIT)]
            action_widget = self._create_action_cell(actions_list, r)
            self._table.setCellWidget(r, action_col_idx, action_widget)

    def _create_action_cell(self, actions_list: list, row_index: int) -> QWidget:
        """Tạo widget hành động và gán trực tiếp sự kiện logic"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container) # Hiển thị các nút hành động theo chiều ngang
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        for action_type, svg_str in actions_list:
            btn = _TableActionButton(svg_str, action_type)
            #Hàm lambda ở đây sẽ "nhớ" biến act và biến r (row_index)
            btn.clicked.connect(lambda _, act=action_type, r=row_index: self._on_action_triggered(act, r))
            layout.addWidget(btn)
            
        return container

    def _on_cell_clicked(self, row: int, col: int):
        if not self._filtered_data:
            return
        target_filtered_item = self._filtered_data[(self.current_page - 1) * self.page_size + row]
        try:
            actual_global_idx = self._all_data.index(target_filtered_item)
            self.row_selected.emit(actual_global_idx) 
        except ValueError:
            self.row_selected.emit(row) 

    def _on_action_triggered(self, action_type: str, row_index: int):
        """Xử lý khi người dùng bấm nút hành động (view/edit) trên một dòng"""
        """Xác định index thực tế trong danh sách gốc và phát tín hiệu action_clicked"""
        if not self._filtered_data:
            return
        # Lấy ra dict dữ liệu thực tế dựa trên số trang và dòng màn hình
        target_filtered_item = self._filtered_data[(self.current_page - 1) * self.page_size + row_index]
        try:
            # Dò tìm vị trí (index) của dict này trong danh sách dữ liệu gốc (_all_data)
            actual_global_idx = self._all_data.index(target_filtered_item)
            # Phát tín hiệu action_clicked với action_type và index thực tế
            self.action_clicked.emit(action_type, actual_global_idx)
        except ValueError:
            self.action_clicked.emit(action_type, row_index)

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._apply_filter() 

    def _next_page(self):
        total_items = len(self._filtered_data)
        total_pages = math.ceil(total_items / self.page_size) if total_items > 0 else 1
        if self.current_page < total_pages:
            self.current_page += 1
            self._apply_filter() 

    def _on_filter(self, name: str, btn: QPushButton):
        self._active_filter = name
        self.current_page = 1  
        for b in self._filter_btns_dict.values():
            active = b.text() == name
            b.setChecked(active)
            b.setStyleSheet(self._pill_style(active)) 
        self._apply_filter()