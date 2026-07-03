import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QButtonGroup
)
from PyQt6.QtCore import Qt

from ui.components.stat_card import StatCard
from ui.components.bar_chart import BarChart
from ui.components.donut_chart import DonutChart
from ui.components.activity_feed import ActivityFeed
from ui.utils.theme import Theme 
from ui.controllers.dashboard_controller import DashboardDataController


def _panel(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("panel")
    return f


def _section_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"background: transparent; color:{Theme.TEXT_MUTED}; font-size:12px; font-weight:500; border: none;")
    return lbl


class DashboardScreen(QScrollArea):
    """Dashboard — Giao diện tổng quan hệ thống."""

    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        
        # UI khởi tạo Controller để xử lý logic và gọi API
        self.controller = DashboardDataController(api_client)
        self.current_filter_days = 7 

        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self.setWidget(container)
        root = QVBoxLayout(container)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Khởi tạo các thành phần giao diện qua các hàm riêng biệt
        root.addLayout(self._build_header())
        root.addLayout(self._build_stat_cards())
        root.addLayout(self._build_middle_row())
        root.addWidget(self._build_activity_panel())

        root.addStretch()
        
        # Khởi động lần đầu: Gọi hàm tổng hợp dữ liệu
        self.load_dashboard_data()


    def refresh_data(self):
        """Hàm chuẩn hóa để main.py tự động gọi khi chuyển trang"""
        self.load_dashboard_data()

    # --- HÀM TÁCH BIỆT XÂY DỰNG UI ---

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("Dashboard tổng quan")
        title.setStyleSheet(f"background: transparent; color:{Theme.TEXT_MAIN}; font-size:15px; font-weight:500; border: none;")
        
        sub = QLabel("Thứ Tư, 17/06/2026 — Kho Hà Nội")
        sub.setStyleSheet(f"background: transparent; color:{Theme.TEXT_SUB}; font-size:11px; border: none;")
        
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header.addLayout(title_block, 1)

        # Khởi tạo nút Refresh với biểu tượng (Icon text)
        self.btn_refresh = QPushButton("⟳")
        self.btn_refresh.setFixedSize(28, 28) # Đặt kích thước 28x28 để tạo hình tròn chuẩn với border-radius: 14px
        
        # Gắn style bạn cung cấp
        self.btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {Theme.BORDER_SIDEBAR};
                border-radius: 14px;
                color: {Theme.TEXT_MUTED};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {Theme.BG_NAV_HOVER if hasattr(Theme, 'BG_NAV_HOVER') else Theme.BG_BTN_HOVER};
                border-color: {Theme.COLOR_PRIMARY};
                color: {Theme.COLOR_PRIMARY};
            }}
            QPushButton:pressed {{
                background: {Theme.BG_PANEL_DARK};
            }}
        """)
        
        # Bắt sự kiện click để tải lại dữ liệu Dashboard
        if hasattr(self, "load_dashboard_data"):
            self.btn_refresh.clicked.connect(self.load_dashboard_data)

        # Các nút hiện có
        btn_period = QPushButton("🗓  Tuần này")
        btn_export = QPushButton("↓  Xuất báo cáo")
        
        # Thêm các nút vào Header (thêm nút refresh vào trước nút period)
        header.addWidget(self.btn_refresh)
        header.addWidget(btn_period)
        header.addWidget(btn_export)
        
        return header

    def _build_stat_cards(self) -> QHBoxLayout:
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        
        self.card_sku = StatCard("⬛  Tổng SKU", "0", "Đang tải...")
        self.card_in = StatCard("↑  Nhập hôm nay", "0", "0 lô hàng", value_color=Theme.COLOR_SUCCESS)
        self.card_out = StatCard("↓  Xuất hôm nay", "0", "0 đơn hàng", value_color=Theme.COLOR_PRIMARY)
        self.card_warn = StatCard("⚠  Cảnh báo", "0", "0 sắp hết hạn", value_color=Theme.COLOR_DANGER)

        for card in [self.card_sku, self.card_in, self.card_out, self.card_warn]:
            card.setStyleSheet(f"""
                StatCard {{
                    border: 1px solid {Theme.BORDER_PANEL_DARK};
                    border-radius: 8px;
                }}
                QLabel {{
                    background: transparent;
                    border: none;
                }}
            """)
            stats_row.addWidget(card)
            
        return stats_row

    def _build_middle_row(self) -> QHBoxLayout:
        mid = QHBoxLayout()
        mid.setSpacing(10)

        mid.addWidget(self._build_bar_chart_panel(), 1)
        mid.addWidget(self._build_donut_chart_panel())
        
        return mid

    def _build_bar_chart_panel(self) -> QFrame:
        chart_panel = _panel()
        cp_lay = QVBoxLayout(chart_panel)
        cp_lay.setContentsMargins(14, 14, 14, 14)
        cp_lay.setSpacing(8)
        
        cp_title_row = QHBoxLayout()
        cp_title_row.addWidget(_section_title("Biến động tồn kho"))
        
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(2)
        
        self.btn_group = QButtonGroup(self)
        filters = [("1 Ngày", 1), ("7 Ngày", 7), ("1 Tháng", 30), ("Tất cả", -1)]
        
        filter_btn_style = f"""
            QPushButton {{
                background: transparent;
                color: {Theme.TEXT_MUTED};
                font-size: 10px;
                font-weight: 500;
                padding: 2px 6px;
                border: 1px solid transparent;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                color: {Theme.TEXT_MAIN};
                background: {Theme.BORDER_PANEL_DARK};
            }}
            QPushButton:checked {{
                color: {Theme.COLOR_PRIMARY};
                background: {Theme.BORDER_PANEL_DARK};
                border: 1px solid {Theme.COLOR_PRIMARY};
            }}
        """
        for text, days in filters:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setStyleSheet(filter_btn_style)
            if days == 7:  
                btn.setChecked(True)
                
            filter_layout.addWidget(btn)
            self.btn_group.addButton(btn, days) 
            
        # Gắn sự kiện UI gọi hàm cập nhật
        self.btn_group.idClicked.connect(self.on_filter_changed)
        cp_title_row.addLayout(filter_layout)
 
        cp_title_row.addStretch() 
        cp_more = QLabel("Xem chi tiết")
        cp_more.setStyleSheet(f"background: transparent; color:{Theme.TEXT_LINK}; font-size:10px; font-weight:500; border: none;")
        cp_title_row.addWidget(cp_more, 0, Qt.AlignmentFlag.AlignRight)
        cp_lay.addLayout(cp_title_row)
        
        self.bar_chart_widget = BarChart()
        self.bar_chart_widget.setMinimumHeight(100)
        cp_lay.addWidget(self.bar_chart_widget, 1)

        legend_row = QHBoxLayout()
        for color, label in [(Theme.BTN_MINT_SUCCESS, "Nhập kho"), (Theme.COLOR_PRIMARY, "Xuất kho")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"background: transparent; color:{color}; font-size:10px; border: none;")
            lbl = QLabel(label)
            lbl.setStyleSheet(f"background: transparent; color:{Theme.TEXT_SUB}; font-size:10px; border: none;")
            legend_row.addWidget(dot)
            legend_row.addWidget(lbl)
            legend_row.addSpacing(8)
        legend_row.addStretch()
        cp_lay.addLayout(legend_row)
        
        return chart_panel

    def _build_donut_chart_panel(self) -> QFrame:
        donut_panel = _panel()
        donut_panel.setFixedWidth(200)
        dp_lay = QVBoxLayout(donut_panel)
        dp_lay.setContentsMargins(14, 14, 14, 14)
        dp_lay.setSpacing(6)
        dp_lay.addWidget(_section_title("Phân loại lưu trữ"))
        
        self.donut = DonutChart()
        self.donut.setFixedHeight(130)
        dp_lay.addWidget(self.donut)

        self.lbl_pct_fifo = None
        self.lbl_pct_lifo = None
        self.lbl_pct_mixed = None

        for color, label, pct in [
            (Theme.COLOR_PRIMARY, "FIFO",  "0%"),
            (Theme.TEXT_MUTED,    "LIFO",  "0%"), 
            (Theme.TEXT_BLUE_ACCENT, "Mixed", "0%"), 
        ]:
            leg = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"background: transparent; color:{color}; font-size:9px; border: none;")
            lbl = QLabel(label)
            lbl.setStyleSheet(f"background: transparent; color:{Theme.TEXT_MUTED}; font-size:10px; border: none;")
            val = QLabel(pct)
            val.setStyleSheet(f"background: transparent; color:{Theme.TEXT_MAIN}; font-size:10px; font-weight:500; border: none;")
            
            if label == "FIFO": self.lbl_pct_fifo = val
            elif label == "LIFO": self.lbl_pct_lifo = val
            elif label == "Mixed": self.lbl_pct_mixed = val

            leg.addWidget(dot)
            leg.addWidget(lbl, 1)
            leg.addWidget(val)
            dp_lay.addLayout(leg)
            
        return donut_panel

    def _build_activity_panel(self) -> QFrame:
        act_panel = _panel()
        ap_lay = QVBoxLayout(act_panel)
        ap_lay.setContentsMargins(14, 14, 14, 14)
        ap_lay.setSpacing(8)
        act_title_row = QHBoxLayout()
        act_title_row.addWidget(_section_title("Hoạt động gần đây"))
        
        act_more = QLabel("Xem tất cả")
        act_more.setStyleSheet(f"background: transparent; color:{Theme.TEXT_LINK}; font-size:10px; border: none;")
        act_title_row.addWidget(act_more, 0, Qt.AlignmentFlag.AlignRight)
        ap_lay.addLayout(act_title_row)
        
        self.activity_feed = ActivityFeed()
        ap_lay.addWidget(self.activity_feed)
        
        return act_panel

    # --- CÁC HÀM XỬ LÝ SỰ KIỆN GIAO DIỆN & CẬP NHẬT UI ---

    def on_filter_changed(self, days_id):
        """Kích hoạt khi người dùng nhấn chuyển đổi Tab bộ lọc thời gian."""
        self.current_filter_days = days_id
        self.render_bar_chart()

    def load_dashboard_data(self):
        """Yêu cầu Controller lấy dữ liệu và kích hoạt cập nhật giao diện."""
        # Gọi xuống lớp Controller để thực hiện logic API
        success = self.controller.fetch_dashboard_data()
        
        if success:
            self.render_bar_chart()
            self.render_donut_chart()
            self.render_stat_cards()
            self.render_recent_activities()

    def render_recent_activities(self): 
        """Nhận dữ liệu từ Controller và hiển thị lên ActivityFeed."""
        try:
            formatted_tuples = self.controller.get_recent_activities()

            if hasattr(self.activity_feed, 'load_items'):
                self.activity_feed.load_items(formatted_tuples)
            else:
                print("[ACTIVITY ERROR] Không tìm thấy hàm load_items trên component ActivityFeed.")

        except Exception as e:
            print(f"[UI ERROR] Gặp lỗi khi render feed: {str(e)}")

    def render_stat_cards(self):
        """Lấy chỉ số thống kê từ Controller và hiển thị lên StatCards."""
        try:
            stats = self.controller.get_stat_cards_data()

            self.card_sku.update_value(f"{stats['total_skus']:,}")
            self.card_sku.update_subtext("Đã đồng bộ từ danh mục")

            self.card_in.update_value(f"+{stats['total_in_qty']:,}" if stats['total_in_qty'] > 0 else "0")
            self.card_in.update_subtext(f"{stats['count_in_batches']} lô hàng")
            
            self.card_out.update_value(f"-{stats['total_out_qty']:,}" if stats['total_out_qty'] > 0 else "0")
            self.card_out.update_subtext(f"{stats['count_out_orders']} đơn hàng")

            self.card_warn.update_value(f"{stats['count_warnings']}")
            self.card_warn.update_subtext(f"{stats['count_expired_soon']} sắp hết hạn")

        except Exception as e:
            print(f"[UI ERROR] Lỗi khi render thẻ thống kê: {str(e)}")

    def render_bar_chart(self):
        """Nhận dữ liệu biểu đồ cột từ Controller theo bộ lọc và cập nhật BarChart."""
        try:
            chart_data_tuples = self.controller.get_chart_data(self.current_filter_days)

            if hasattr(self.bar_chart_widget, 'set_data'):
                self.bar_chart_widget.set_data(chart_data_tuples)
            elif hasattr(self.bar_chart_widget, 'setData'):
                self.bar_chart_widget.setData(chart_data_tuples)
                
            if hasattr(self.bar_chart_widget, 'update'):
                self.bar_chart_widget.update()
                    
        except Exception as e:
            print(f"[UI ERROR] Gặp lỗi khi render biểu đồ cột: {str(e)}")

    def render_donut_chart(self):
        """Lấy phần trăm phân loại từ Controller và cập nhật DonutChart."""
        try:
            pct_fifo, pct_lifo, pct_mixed, total_products = self.controller.get_donut_chart_data()

            if hasattr(self, 'donut') and self.donut:
                if hasattr(self.donut, 'set_segments'):
                    self.donut.set_segments([
                        ("FIFO", pct_fifo, Theme.COLOR_PRIMARY),
                        ("LIFO", pct_lifo, Theme.TEXT_MUTED),
                        ("Mixed", pct_mixed, Theme.TEXT_BLUE_ACCENT)
                    ], total_skus=total_products)
                elif hasattr(self.donut, 'set_data'):
                    self.donut.set_data({
                        'FIFO': pct_fifo,
                        'LIFO': pct_lifo,
                        'Mixed': pct_mixed
                    })

            if self.lbl_pct_fifo: self.lbl_pct_fifo.setText(f"{pct_fifo}%")
            if self.lbl_pct_lifo: self.lbl_pct_lifo.setText(f"{pct_lifo}%")
            if self.lbl_pct_mixed: self.lbl_pct_mixed.setText(f"{pct_mixed}%")

        except Exception as e:
            print(f"[UI ERROR] Gặp lỗi khi render biểu đồ tròn: {str(e)}")