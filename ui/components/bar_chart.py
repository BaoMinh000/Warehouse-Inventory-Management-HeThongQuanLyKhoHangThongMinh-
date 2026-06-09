from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QRect


class BarChart(QWidget):
    """
    Simple vertical bar chart widget drawn with QPainter.

    Parameters
    ----------
    data   : list[tuple[str, float]]  — (label, value) pairs
    accent : str  — hex color for highlighted bars
    """

    ACCENT     = "#378ADD"
    NEUTRAL    = "#243050"
    LABEL_CLR  = "#4a5a78"
    BG_CLR     = "#161b26"

    def __init__(self, data: list[tuple[str, float]] | None = None, parent=None):
        super().__init__(parent)
        self._data = data or [
            ("T2", 45), ("T3", 62), ("T4", 38),
            ("T5", 78), ("T6", 90), ("T7", 55), ("CN", 70),
        ]
        self.setMinimumHeight(110)

    def set_data(self, data: list[tuple[str, float]]):
        self._data = data
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        padding_h = 8
        label_h = 18
        chart_h = h - label_h - padding_h

        n = len(self._data)
        bar_gap = 5
        bar_w = max(8, (w - padding_h * 2 - bar_gap * (n - 1)) // n)
        max_val = max(v for _, v in self._data) or 1

        # Find peak value index for accent color
        peak_idx = max(range(n), key=lambda i: self._data[i][1])

        font = QFont("Segoe UI", 8)
        painter.setFont(font)

        for i, (label, value) in enumerate(self._data):
            x = padding_h + i * (bar_w + bar_gap)
            bar_height = int((value / max_val) * chart_h)
            y = padding_h + chart_h - bar_height

            color = self.ACCENT if i == peak_idx else self.NEUTRAL
            painter.setBrush(QColor(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRect(x, y, bar_w, bar_height), 2, 2)

            painter.setPen(QColor(self.LABEL_CLR))
            painter.drawText(
                QRect(x - 4, h - label_h, bar_w + 8, label_h),
                Qt.AlignmentFlag.AlignCenter,
                label,
            )

        painter.end()