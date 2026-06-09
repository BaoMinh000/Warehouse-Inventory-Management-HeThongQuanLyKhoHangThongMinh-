from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt

from ui.components.stat_card import StatCard
from ui.components.bar_chart import BarChart
from ui.components.donut_chart import DonutChart
from ui.components.activity_feed import ActivityFeed


def _panel(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("panel")
    return f


def _section_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("color:#8899b4; font-size:12px; font-weight:500;")
    return lbl


class DashboardScreen(QScrollArea):
    """Dashboard — tổng quan hệ thống."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self.setWidget(container)
        root = QVBoxLayout(container)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        title = QLabel("Dashboard tổng quan")
        title.setStyleSheet("color:#e2e8f0; font-size:15px; font-weight:500;")
        sub = QLabel("Thứ Hai, 08/06/2026 — Kho Hà Nội")
        sub.setStyleSheet("color:#4a5a78; font-size:11px;")
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header.addLayout(title_block, 1)

        btn_period = QPushButton("🗓  Tuần này")
        btn_export = QPushButton("↓  Xuất báo cáo")
        header.addWidget(btn_period)
        header.addWidget(btn_export)
        root.addLayout(header)

        # Stat cards
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        stats_row.addWidget(StatCard("⬛  Tổng SKU",    "1,248", "+34 tháng này"))
        stats_row.addWidget(StatCard("↑  Nhập hôm nay", "+2,840", "12 lô hàng",
                                     value_color="#2fd89c"))
        stats_row.addWidget(StatCard("↓  Xuất hôm nay", "−1,560", "8 đơn hàng",
                                     value_color="#378ADD"))
        stats_row.addWidget(StatCard("⚠  Cảnh báo",    "23",    "7 sắp hết hạn",
                                     value_color="#f07070"))
        root.addLayout(stats_row)

        # Mid row: bar chart + donut
        mid = QHBoxLayout()
        mid.setSpacing(10)

        # Bar chart panel
        chart_panel = _panel()
        cp_lay = QVBoxLayout(chart_panel)
        cp_lay.setContentsMargins(14, 14, 14, 14)
        cp_lay.setSpacing(8)
        cp_title_row = QHBoxLayout()
        cp_title_row.addWidget(_section_title("Biến động tồn kho 7 ngày"))
        cp_more = QLabel("Xem chi tiết")
        cp_more.setStyleSheet(
            "color:#378ADD; font-size:10px; font-weight:500;"
        )
        cp_title_row.addWidget(cp_more, 0, Qt.AlignmentFlag.AlignRight)
        cp_lay.addLayout(cp_title_row)
        bar = BarChart()
        bar.setMinimumHeight(100)
        cp_lay.addWidget(bar, 1)

        legend_row = QHBoxLayout()
        for color, label in [("#378ADD", "Nhập kho"), ("#243050", "Xuất kho")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color}; font-size:10px;")
            lbl = QLabel(label)
            lbl.setStyleSheet("color:#4a5a78; font-size:10px;")
            legend_row.addWidget(dot)
            legend_row.addWidget(lbl)
            legend_row.addSpacing(8)
        legend_row.addStretch()
        cp_lay.addLayout(legend_row)

        # Donut panel
        donut_panel = _panel()
        donut_panel.setFixedWidth(200)
        dp_lay = QVBoxLayout(donut_panel)
        dp_lay.setContentsMargins(14, 14, 14, 14)
        dp_lay.setSpacing(6)
        dp_lay.addWidget(_section_title("Phân loại lưu trữ"))
        donut = DonutChart()
        donut.setFixedHeight(130)
        dp_lay.addWidget(donut)

        for color, label, pct in [
            ("#378ADD", "FIFO",  "53%"),
            ("#9898e8", "LIFO",  "37%"),
            ("#e8a042", "Mixed", "10%"),
        ]:
            leg = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color}; font-size:9px;")
            lbl = QLabel(label)
            lbl.setStyleSheet("color:#8899b4; font-size:10px;")
            val = QLabel(pct)
            val.setStyleSheet("color:#e2e8f0; font-size:10px; font-weight:500;")
            leg.addWidget(dot)
            leg.addWidget(lbl, 1)
            leg.addWidget(val)
            dp_lay.addLayout(leg)

        mid.addWidget(chart_panel, 1)
        mid.addWidget(donut_panel)
        root.addLayout(mid)

        # Activity feed panel
        act_panel = _panel()
        ap_lay = QVBoxLayout(act_panel)
        ap_lay.setContentsMargins(14, 14, 14, 14)
        ap_lay.setSpacing(8)
        act_title_row = QHBoxLayout()
        act_title_row.addWidget(_section_title("Hoạt động gần đây"))
        act_more = QLabel("Xem tất cả")
        act_more.setStyleSheet("color:#378ADD; font-size:10px;")
        act_title_row.addWidget(act_more, 0, Qt.AlignmentFlag.AlignRight)
        ap_lay.addLayout(act_title_row)
        ap_lay.addWidget(ActivityFeed())
        root.addWidget(act_panel)

        root.addStretch()