from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt


class StatCard(QFrame):
    """
    Metric summary card.

    Parameters
    ----------
    label   : str  — muted label text (top)
    value   : str  — large value (centre)
    trend   : str  — small trend text (bottom, optional)
    value_color : str — hex color for value text
    """

    def __init__(
        self,
        label: str,
        value: str,
        trend: str = "",
        value_color: str = "#e2e8f0",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("stat_card")
        self.setFixedHeight(88)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        lbl = QLabel(label)
        lbl.setStyleSheet("color:#4a5a78; font-size:11px;")

        val = QLabel(value)
        val.setStyleSheet(
            f"color:{value_color}; font-size:20px; font-weight:500;"
        )

        layout.addWidget(lbl)
        layout.addWidget(val)

        if trend:
            t = QLabel(trend)
            t.setStyleSheet("color:#4a5a78; font-size:10px;")
            layout.addWidget(t)

        layout.addStretch()

    def update_value(self, value: str, trend: str = ""):
        """Refresh displayed value and trend at runtime."""
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget():
                w = item.widget()
                if isinstance(w, QLabel) and w.styleSheet().startswith("color:#"):
                    if "font-size:20px" in w.styleSheet():
                        w.setText(value)
                    elif trend and "font-size:10px" in w.styleSheet():
                        w.setText(trend)