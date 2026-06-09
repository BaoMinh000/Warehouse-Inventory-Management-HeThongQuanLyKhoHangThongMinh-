from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt


ICON_MAP = {
    "in":   ("↑", "#0f2a1e", "#2fd89c"),
    "out":  ("↓", "#2a1215", "#f07070"),
    "warn": ("!", "#2a1f0a", "#e8a042"),
}


class _ActivityItem(QFrame):
    def __init__(self, kind: str, title: str, subtitle: str, qty: str, parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        self.setStyleSheet(
            "QFrame { background:#161b26; border:none;"
            " border-radius:6px; padding:0; }"
        )

        icon_char, icon_bg, icon_fg = ICON_MAP.get(kind, ICON_MAP["warn"])
        row = QHBoxLayout(self)
        row.setContentsMargins(10, 7, 10, 7)
        row.setSpacing(10)

        icon = QLabel(icon_char)
        icon.setFixedSize(28, 28)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"background:{icon_bg}; color:{icon_fg};"
            f" border-radius:6px; font-size:13px; font-weight:500;"
        )

        body = QVBoxLayout()
        body.setSpacing(1)
        t = QLabel(title)
        t.setStyleSheet("color:#e2e8f0; font-size:11px;")
        s = QLabel(subtitle)
        s.setStyleSheet("color:#4a5a78; font-size:10px;")
        body.addWidget(t)
        body.addWidget(s)

        qty_lbl = QLabel(qty)
        qty_lbl.setStyleSheet(
            f"color:{icon_fg}; font-size:11px; font-weight:500;"
        )
        qty_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        row.addWidget(icon)
        row.addLayout(body, 1)
        row.addWidget(qty_lbl)


class ActivityFeed(QWidget):
    """
    Vertical list of recent inventory activity items.

    Call add_item() to append, or load_items() to replace all.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self._list_layout = QVBoxLayout()
        self._list_layout.setSpacing(5)
        layout.addLayout(self._list_layout)
        layout.addStretch()

        self.load_items(self._default_items())

    def _default_items(self):
        return [
            ("in",   "Nhập lô — Sữa TH True Milk 1L",
             "09:42 — Lô #B2406-01 · 240 thùng", "+240"),
            ("out",  "Xuất kho — Mì Hảo Hảo tôm chua cay",
             "08:15 — Đơn #ORD-7821 · FIFO tự động", "−120"),
            ("warn", "Cảnh báo hết hạn — Nước Lavie 500ml",
             "Hệ thống · Còn 7 ngày · Lô #B2405-12", "7 ngày"),
        ]

    def load_items(self, items: list[tuple[str, str, str, str]]):
        self._clear()
        for kind, title, subtitle, qty in items:
            self._list_layout.addWidget(
                _ActivityItem(kind, title, subtitle, qty)
            )

    def add_item(self, kind: str, title: str, subtitle: str, qty: str):
        self._list_layout.insertWidget(0, _ActivityItem(kind, title, subtitle, qty))

    def _clear(self):
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()