from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QByteArray, QSize
from PyQt6.QtGui import QIcon, QPixmap
from ui.utils.image_utils import create_svg_icon

SVG_DASHBOARD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path fill="currentColor" d="M341.8 72.6C329.5 61.2 310.5 61.2 298.3 72.6L74.3 280.6C64.7 289.6 61.5 303.5 66.3 315.7C71.1 327.9 82.8 336 96 336L112 336L112 512C112 547.3 140.7 576 176 576L464 576C499.3 576 528 547.3 528 512L528 336L544 336C557.2 336 569 327.9 573.8 315.7C578.6 303.5 575.4 289.5 565.8 280.6L341.8 72.6zM304 384L336 384C362.5 384 384 405.5 384 432L384 528L256 528L256 432C256 405.5 277.5 384 304 384z"/></svg>"""
SVG_BOX = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M465.4 192L431.1 144L209 144L174.7 192L465.4 192zM96 212.5C96 199.2 100.2 186.2 107.9 175.3L156.9 106.8C168.9 90 188.3 80 208.9 80L431 80C451.7 80 471.1 90 483.1 106.8L532 175.3C539.8 186.2 543.9 199.2 543.9 212.5L544 480C544 515.3 515.3 544 480 544L160 544C124.7 544 96 515.3 96 480L96 212.5z"/></svg>"""
SVG_ARROW_UP = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M342.6 73.4C330.1 60.9 309.8 60.9 297.3 73.4L169.3 201.4C156.8 213.9 156.8 234.2 169.3 246.7C181.8 259.2 202.1 259.2 214.6 246.7L288 173.3L288 384C288 401.7 302.3 416 320 416C337.7 416 352 401.7 352 384L352 173.3L425.4 246.7C437.9 259.2 458.2 259.2 470.7 246.7C483.2 234.2 483.2 213.9 470.7 201.4L342.7 73.4zM160 416C160 398.3 145.7 384 128 384C110.3 384 96 398.3 96 416L96 480C96 533 139 576 192 576L448 576C501 576 544 533 544 480L544 416C544 398.3 529.7 384 512 384C494.3 384 480 398.3 480 416L480 480C480 497.7 465.7 512 448 512L192 512C174.3 512 160 497.7 160 480L160 416z"/></svg>"""
SVG_ARROW_DOWN = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M297.4 566.6C309.9 579.1 330.2 579.1 342.7 566.6L502.7 406.6C515.2 394.1 515.2 373.8 502.7 361.3C490.2 348.8 469.9 348.8 457.4 361.3L352 466.7L352 96C352 78.3 337.7 64 320 64C302.3 64 288 78.3 288 96L288 466.7L182.6 361.3C170.1 348.8 149.8 348.8 137.3 361.3C124.8 373.8 124.8 394.1 137.3 406.6L297.3 566.6z"/></svg>"""
SVG_CLOCK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M320 64C461.4 64 576 178.6 576 320C576 461.4 461.4 576 320 576C178.6 576 64 461.4 64 320C64 178.6 178.6 64 320 64zM296 184L296 320C296 328 300 335.5 306.7 340L402.7 404C413.7 411.4 428.6 408.4 436 397.3C443.4 386.2 440.4 371.4 429.3 364L344 307.2L344 184C344 170.7 333.3 160 320 160C306.7 160 296 170.7 296 184z"/></svg>"""
SVG_CHART = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M96 96C113.7 96 128 110.3 128 128L128 464C128 472.8 135.2 480 144 480L544 480C561.7 480 576 494.3 576 512C576 529.7 561.7 544 544 544L144 544C99.8 544 64 508.2 64 464L64 128C64 110.3 78.3 96 96 96zM192 160C192 142.3 206.3 128 224 128L416 128C433.7 128 448 142.3 448 160C448 177.7 433.7 192 416 192L224 192C206.3 192 192 177.7 192 160zM224 240L352 240C369.7 240 384 254.3 384 272C384 289.7 369.7 304 352 304L224 304C206.3 304 192 289.7 192 272C192 254.3 206.3 240 224 240zM224 352L480 352C497.7 352 512 366.3 512 384C512 401.7 497.7 416 480 416L224 416C206.3 416 192 401.7 192 384C192 366.3 206.3 352 224 352z"/></svg>"""
SVG_WAREHOUSE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M32 206.1L32 544C32 561.7 46.3 576 64 576C81.7 576 96 561.7 96 544L96 304C96 286.3 110.3 272 128 272L512 272C529.7 272 544 286.3 544 304L544 544C544 561.7 558.3 576 576 576C593.7 576 608 561.7 608 544L608 206.1C608 178.6 590.4 154.1 564.2 145.4L335.2 69.1C325.3 65.8 314.7 65.8 304.8 69.1L75.8 145.4C49.6 154.1 32 178.6 32 206.1zM496 320L144 320L144 384L496 384L496 320zM144 480L496 480L496 416L144 416L144 480zM496 512L144 512L144 576L496 576L496 512z"/></svg>"""

NAV_ITEMS = [
    ("dashboard", SVG_DASHBOARD,  "Dashboard",     False),
    ("products",  SVG_BOX,  "Sản phẩm",      False),
    ("warehouse_manager", SVG_WAREHOUSE, "Quản lý kho", False),
    # ("stockin",   SVG_ARROW_UP,  "Nhập kho",      False),
    # ("stockout",  SVG_ARROW_DOWN,  "Xuất kho",      False),
    ("expiry",    SVG_CLOCK, "Hết hạn",       True),   # True = has alert badge
    ("reports",   SVG_CHART, "Báo cáo",       False),
]


class _NavButton(QPushButton):
    """Single icon nav button using inline SVG text."""

    # Mẹo QSS: Để icon SVG tự đổi màu theo state, hãy dùng thuộc tính `qproperty-icon` trong stylesheet!
    STYLE_NORMAL = (
        "QPushButton { background:transparent; border:none; border-radius:8px;"
        " qproperty-iconSize: 20px 20px; }"
        "QPushButton:hover { background:#1e2740; }"
    )
    
    # Bạn có thể dùng 2 bộ icon màu khác nhau hoặc dùng QIcon States. 
    # Nhưng cách nhanh nhất với stylesheet là quản lý đổi màu icon qua QIcon.
    STYLE_ACTIVE = (
        "QPushButton { background:#1a2e4a; border:none; border-radius:8px;"
        " qproperty-iconSize: 20px 20px; }"
    )

    def __init__(self, svg_str: str, tooltip: str, has_badge: bool = False, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.setToolTip(tooltip)
        
        # Chuyển đổi chuỗi SVG sang QIcon
        icon = create_svg_icon(svg_str)
        self.setIcon(icon)
        self.setIconSize(QSize(20, 20)) # Kích thước icon bên trong nút 36x36
        
        self.setStyleSheet(self.STYLE_NORMAL)
        self._active = False

    def set_active(self, active: bool):
        self._active = active
        self.setStyleSheet(self.STYLE_ACTIVE if active else self.STYLE_NORMAL)
        

class Sidebar(QWidget):
    """
    Vertical icon sidebar.

    Signals
    -------
    navigate(str)  : emitted with screen key when a nav button is clicked
    """

    navigate = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(52)
        self.setStyleSheet(
            "QWidget { background:#161b26;"
            " border-right:1px solid #2a3347; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._buttons: dict[str, _NavButton] = {}

        primary_keys  = ["dashboard", "products", "warehouse_manager"]
        secondary_keys = ["expiry", "reports"]

        for key, icon, tip, badge in NAV_ITEMS:
            if key == "expiry":
                divider = QFrame()
                divider.setFixedHeight(1)
                divider.setStyleSheet(
                    "background:#2a3347; border:none; margin:4px 0;"
                )
                layout.addWidget(divider)

            btn = _NavButton(icon, tip, badge)
            btn.clicked.connect(lambda _, k=key: self._on_click(k))
            self._buttons[key] = btn
            layout.addWidget(btn)

        # Settings pinned at bottom
        layout.addStretch()
        divider2 = QFrame()
        divider2.setFixedHeight(1)
        divider2.setStyleSheet("background:#2a3347; border:none; margin:4px 0;")
        layout.addWidget(divider2)

        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(36, 36)
        settings_btn.setToolTip("Cài đặt")
        settings_btn.setStyleSheet(_NavButton.STYLE_NORMAL)
        layout.addWidget(settings_btn)

        # Activate dashboard by default
        self._active_key = "dashboard"
        self._buttons["dashboard"].set_active(True)

    def _on_click(self, key: str):
        if key in self._buttons:
            self._buttons.get(self._active_key, None) and \
                self._buttons[self._active_key].set_active(False)
            self._active_key = key
            self._buttons[key].set_active(True)
        self.navigate.emit(key)

    def set_active(self, key: str):
        """Programmatically activate a nav item without emitting signal."""
        if self._active_key in self._buttons:
            self._buttons[self._active_key].set_active(False)
        self._active_key = key
        if key in self._buttons:
            self._buttons[key].set_active(True)

    