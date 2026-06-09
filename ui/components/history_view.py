# ui/components/history_view.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from ui.components.data_table import DataTable

class HistoryView(QWidget):
    def __init__(self, title, subtitle, back_btn_text, columns, filters, sample_data, on_back_clicked, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # --- HEADER BAR ---
        header = QHBoxLayout()
        title_lay = QVBoxLayout()
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e2e8f0;")
        lbl_subtitle = QLabel(subtitle)
        lbl_subtitle.setStyleSheet("font-size: 11px; color: #8899b4;")
        
        title_lay.addWidget(lbl_title)
        title_lay.addWidget(lbl_subtitle)
        
        back_btn = QPushButton(back_btn_text)
        back_btn.setStyleSheet("""
            QPushButton { background: #1a2e4a; border: 1px solid #2a4a6e; color: #5b9cf6; 
                          padding: 8px 14px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #24426b; }
        """)
        back_btn.clicked.connect(on_back_clicked)
        
        header.addLayout(title_lay)
        header.addStretch()
        header.addWidget(back_btn)
        layout.addLayout(header)

        # --- DATA TABLE ---
        self.table = DataTable(columns, filters, self)
        layout.addWidget(self.table)

        # Gọi hàm load_data có sẵn của bạn (Bật cờ status=True và action=True nếu muốn hiện)
        self.table.load_data(sample_data, status=True, action=True)