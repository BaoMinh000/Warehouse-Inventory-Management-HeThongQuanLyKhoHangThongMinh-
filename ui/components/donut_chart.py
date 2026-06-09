from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRect, QRectF


class DonutChart(QWidget):
    """
    Donut chart painted with QPainter arcs.

    Parameters
    ----------
    segments : list[tuple[str, float, str]]  — (label, value, hex_color)
    """

    def __init__(
        self,
        segments: list[tuple[str, float, str]] | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._segments = segments or [
            ("FIFO",  53, "#378ADD"),
            ("LIFO",  37, "#9898e8"),
            ("Mixed", 10, "#e8a042"),
        ]
        self.setMinimumSize(140, 140)

    def set_segments(self, segments: list[tuple[str, float, str]]):
        self._segments = segments
        self.update()

    def paintEvent(self, event):
        if not self._segments:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        side = min(self.width(), self.height())
        margin = 10
        donut_size = side - margin * 2
        x0 = (self.width() - donut_size) // 2
        y0 = (self.height() - donut_size) // 2

        rect = QRectF(x0, y0, donut_size, donut_size)
        thickness = donut_size * 0.2
        pen = QPen()
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        pen.setWidthF(thickness)

        total = sum(v for _, v, _ in self._segments)
        angle = 90 * 16  # start at top

        for label, value, color in self._segments:
            span = int(-(value / total) * 360 * 16)
            pen.setColor(QColor(color))
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(rect, angle, span)
            angle += span

        # Centre text — total label
        painter.setPen(QColor("#e2e8f0"))
        f = QFont("Segoe UI", 11)
        f.setWeight(QFont.Weight.Medium)
        painter.setFont(f)
        painter.drawText(
            QRect(x0, y0, donut_size, donut_size - 12),
            Qt.AlignmentFlag.AlignCenter,
            str(int(total)),
        )
        painter.setPen(QColor("#4a5a78"))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(
            QRect(x0, y0 + 14, donut_size, donut_size),
            Qt.AlignmentFlag.AlignCenter,
            "SKU",
        )

        painter.end()