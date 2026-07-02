import os
import re
import base64
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QWidget, QScrollArea, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

# Nhập class Theme của bạn
from ui.utils.theme import Theme 

# ĐỌC BIẾN MÔI TRƯỜNG .ENV (Có sẵn fallback đề phòng file .env lỗi)
SVG_ANGLE_DOWN = os.getenv(
    "SVG_ANGLE_DOWN", 
    ""
)

class ItemFormDialog(QDialog):
    """
    Dialog hiển thị Form để Xem (view) hoặc Chỉnh sửa (edit) dữ liệu.
    Tự động tạo các trường nhập liệu dựa trên dictionary được truyền vào.

    Thiết kế: Áp dụng Dark Theme + Dropdown linh hoạt + Icon đồng bộ từ .env
    """

    # Map variant -> (nền, chữ) cho badge trạng thái sử dụng Theme
    STATUS_COLORS = {
        "success": (Theme.BG_BANNER_SUCCESS, Theme.TEXT_BANNER_SUCCESS),
        "danger": (Theme.BG_BADGE_DANGER, Theme.TEXT_BADGE_DANGER),
        "warning": (Theme.EXPIRY_BG_WARNING, Theme.EXPIRY_TEXT_WARNING),
        "info": (Theme.BG_BTN_ACTIVE, Theme.TEXT_LINK),
        "default": (Theme.BG_PANEL_BACKUP, Theme.TEXT_NORMAL),
    }

    FIELD_LABELS = {
        "id": "Mã",
        "name": "Tên",
        "sku": "SKU",
        "quantity": "Số lượng",
        "unit": "Đơn vị",
        "price": "Đơn giá",
        "category": "Danh mục",
        "location": "Vị trí",
        "status": "Trạng thái",
        "strategy_type": "Chiến lược",
        "description": "Mô tả",
        "supplier": "Nhà cung cấp",
        "updated_at": "Cập nhật lúc",
    }

    def __init__(self, data: dict, mode: str = "view", parent=None):
        super().__init__(parent)
        self.original_data = data
        self.mode = mode  
        self.fields = {}  

        self._setup_ui()

    # ------------------------------------------------------------------ #
    # UI SETUP
    # ------------------------------------------------------------------ #
    def _setup_ui(self):
        is_view = self.mode == "view"

        self.setWindowTitle("Chi tiết sản phẩm" if is_view else "Chỉnh sửa sản phẩm")
        self.setMinimumWidth(460)
        self.setModal(True)
        self.setStyleSheet(self._stylesheet())

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ---------------- Header ---------------- #
        header = QWidget(objectName="Header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 18)
        header_layout.setSpacing(2)

        title_text = "Chi tiết sản phẩm" if is_view else "Chỉnh sửa sản phẩm"
        subtitle_text = (
            "Thông tin chi tiết trong kho (chỉ xem)"
            if is_view else
            "Cập nhật thông tin rồi bấm Lưu để áp dụng"
        )

        title_lbl = QLabel(title_text, objectName="TitleLabel")
        subtitle_lbl = QLabel(subtitle_text, objectName="SubtitleLabel")

        header_layout.addWidget(title_lbl)
        header_layout.addWidget(subtitle_lbl)
        outer.addWidget(header)

        # ---------------- Body (scrollable) ---------------- #
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        body = QWidget(objectName="Body")
        form_layout = QFormLayout(body)
        form_layout.setContentsMargins(24, 20, 24, 12)
        form_layout.setHorizontalSpacing(16)
        form_layout.setVerticalSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        for key, value in self.original_data.items():
            label_text = self.FIELD_LABELS.get(key, key.replace("_", " ").capitalize())
            label = QLabel(f"{label_text}:", objectName="FieldLabel")

            display_value = str(value[0]) if isinstance(value, tuple) else str(value)

            if key == "status":
                field_widget = self._build_status_badge(value)
                self.fields[key] = field_widget
                
            elif key in ["strategy_type", "category"] and not is_view:
                # BẬT DROPDOWN: Chỉ hiển thị khi đang ở chế độ CHỈNH SỬA (edit)
                field_widget = QComboBox()
                field_widget.setObjectName("EditableComboBox")
                
                # Ép kích thước giãn dài bằng các ô nhập khác
                field_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                
                if key == "strategy_type":
                    field_widget.addItems(["FIFO", "LIFO"])
                else:
                    field_widget.addItems(["Thực phẩm", "Hóa mỹ phẩm", "Đồ uống", "Vật tư"])
                    
                field_widget.setCurrentText(display_value)
                self.fields[key] = field_widget
                
            else:
                # CHẾ ĐỘ XEM hoặc các ô dữ liệu text thông thường
                field_widget = QLineEdit(display_value)
                field_widget.setObjectName("ReadOnlyInput" if is_view else "EditableInput")
                field_widget.setReadOnly(is_view)
                self.fields[key] = field_widget

            form_layout.addRow(label, field_widget)

        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        # ---------------- Footer / Buttons ---------------- #
        footer = QWidget(objectName="Footer")
        btn_layout = QHBoxLayout(footer)
        btn_layout.setContentsMargins(24, 14, 24, 18)
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        if is_view:
            close_btn = QPushButton("Đóng")
            close_btn.setObjectName("SecondaryButton") # Nút đóng giữ nguyên xám mờ
            close_btn.setMinimumSize(96, 36)
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.clicked.connect(self.reject)
            btn_layout.addWidget(close_btn)
        else:
            cancel_btn = QPushButton("Hủy")
            cancel_btn.setObjectName("CancelButton")  # <--- ĐỔI TÊN Ở ĐÂY
            cancel_btn.setMinimumSize(96, 36)
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.clicked.connect(self.reject)

            save_btn = QPushButton("Lưu thay đổi")
            save_btn.setObjectName("SaveButton")      # <--- ĐỔI TÊN Ở ĐÂY
            save_btn.setMinimumSize(120, 36)
            save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            save_btn.clicked.connect(self.accept)

            btn_layout.addWidget(cancel_btn)
            btn_layout.addWidget(save_btn)

        outer.addWidget(footer)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

    # ------------------------------------------------------------------ #
    # HELPERS
    # ------------------------------------------------------------------ #
    def _build_status_badge(self, value) -> QLabel:
        if isinstance(value, tuple):
            text, variant = value[0], (value[1] if len(value) > 1 else "default")
        else:
            text, variant = value, "default"

        bg, fg = self.STATUS_COLORS.get(str(variant).lower(), self.STATUS_COLORS["default"])

        badge = QLabel(str(text))
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(28)
        badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        border_color = bg if variant.lower() != "default" else Theme.BORDER_PANEL_BACKUP
        
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border_color};
                border-radius: 14px;
                padding: 0 14px;
                font-weight: 600;
                font-size: 12px;
            }}
        """)
        font = badge.font()
        font.setWeight(QFont.Weight.DemiBold)
        badge.setFont(font)
        return badge

    def _stylesheet(self) -> str:
        # Xử lý chuỗi SVG từ .env để ép đổi màu động theo màu Theme
        svg_content = SVG_ANGLE_DOWN
        if "fill=" not in svg_content:
            svg_content = svg_content.replace('<svg', f'<svg fill="{Theme.TEXT_MUTED}"')
        else:
            svg_content = re.sub(r'fill="[^"]+"', f'fill="{Theme.TEXT_MUTED}"', svg_content)
        
        # MÃ HÓA SANG BASE64 ĐỂ FIX LỖI PARSE STYLESHEET
        svg_b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        svg_data_uri = f"data:image/svg+xml;base64,{svg_b64}"

        return f"""
            QDialog {{
                background-color: {Theme.BG_TABLE};
                border: 1px solid {Theme.BORDER_NEUTRAL};
                border-radius: 12px;
            }}
            QWidget#Header {{
                border-bottom: 1px solid {Theme.BORDER_PANEL_DARK};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
            QLabel#TitleLabel {{
                font-size: 17px;
                font-weight: 700;
                color: {Theme.TEXT_MAIN};
            }}
            QLabel#SubtitleLabel {{
                font-size: 12px;
                color: {Theme.TEXT_MUTED};
            }}
            QLabel#FieldLabel {{
                color: {Theme.TEXT_MUTED};
                font-size: 13px;
                font-weight: 500;
            }}
            QLineEdit#EditableInput {{
                background-color: {Theme.BG_INPUT};
                border: 1.5px solid {Theme.BORDER_INPUT};
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
                color: {Theme.TEXT_MAIN};
            }}
            QLineEdit#EditableInput:focus {{
                border: 1.5px solid {Theme.COLOR_PRIMARY};
                background-color: {Theme.BG_SIDEBAR};
            }}
            QLineEdit#ReadOnlyInput {{
                background-color: {Theme.BG_PANEL_BACKUP};
                border: 1px solid {Theme.BORDER_PANEL_BACKUP};
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
                color: {Theme.TEXT_SUB};
            }}
            
            /* -- STYLE CHO DROPDOWN (QCOMBOBOX) -- */
            QComboBox#EditableComboBox {{
                background-color: {Theme.BG_INPUT};
                border: 1.5px solid {Theme.BORDER_INPUT};
                border-radius: 8px;
                padding: 6px 30px 6px 10px; 
                font-size: 13px;
                color: {Theme.TEXT_MAIN};
            }}
            QComboBox#EditableComboBox:focus {{
                border: 1.5px solid {Theme.COLOR_PRIMARY};
                background-color: {Theme.BG_SIDEBAR};
            }}
            QComboBox#EditableComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border: none;
            }}
            QComboBox#EditableComboBox::down-arrow {{
                image: url("{svg_data_uri}"); /* <--- ĐÃ ĐƯỢC MÃ HÓA, SẼ KHÔNG CÒN LỖI */
                width: 16px;
                height: 16px;
            }}
            QComboBox#EditableComboBox QAbstractItemView {{
                background-color: {Theme.BG_PANEL_DARK};
                color: {Theme.TEXT_MAIN};
                selection-background-color: {Theme.BG_BTN_HOVER};
                selection-color: {Theme.TEXT_MAIN};
                border: 1px solid {Theme.BORDER_PANEL_DARK};
                border-radius: 8px;
                outline: none;
                padding: 4px;
            }}

            QWidget#Footer {{
                background-color: {Theme.BG_PANEL_DARK};
                border-top: 1px solid {Theme.BORDER_PANEL_DARK};
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
            
            /* -- NÚT HỦY (CẢNH BÁO ĐỎ) -- */
            QPushButton#CancelButton {{
                background-color: transparent;
                color: {Theme.COLOR_DANGER};
                border: 1px solid {Theme.COLOR_DANGER};
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton#CancelButton:hover {{
                background-color: {Theme.BG_BADGE_DANGER};
            }}
            QPushButton#CancelButton:pressed {{
                background-color: {Theme.EXPIRY_BG_CRITICAL};
            }}

            /* -- NÚT LƯU THAY ĐỔI (XANH MINT) -- */
            QPushButton#SaveButton {{
                background-color: {Theme.BTN_MINT_SUCCESS};
                color: {Theme.BG_PANEL_DARK};
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton#SaveButton:hover {{
                background-color: {Theme.BTN_MINT_HOVER};
            }}
            QPushButton#SaveButton:pressed {{
                background-color: {Theme.COLOR_SUCCESS};
            }}
            
            QPushButton#SecondaryButton {{
                background-color: {Theme.BG_PANEL_DARK};
                color: {Theme.TEXT_MAIN};
                border: 1.5px solid {Theme.BORDER_NEUTRAL};
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton#SecondaryButton:hover {{
                background-color: {Theme.BG_BTN_HOVER};
                border-color: {Theme.BORDER_HOVER};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 4px 0 4px 0;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.BORDER_NEUTRAL};
                border-radius: 4px;
                min-height: 24px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.BORDER_HOVER};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """
        
    # ------------------------------------------------------------------ #
    # DATA SAVING
    # ------------------------------------------------------------------ #
    def get_updated_data(self) -> dict:
        """Hàm lấy dữ liệu mới sau khi người dùng đã chỉnh sửa trên form."""
        updated_data = {}
        for key, widget in self.fields.items():
            original_val = self.original_data.get(key, "")

            if key == "status":
                updated_data[key] = original_val
                continue

            # Phân tách lấy dữ liệu dựa trên loại Widget thực tế đang hiển thị
            if isinstance(widget, QComboBox):
                current_text = widget.currentText()
            else:
                current_text = widget.text()

            if isinstance(original_val, tuple):
                updated_data[key] = (current_text, original_val[1])
            else:
                updated_data[key] = current_text

        return updated_data