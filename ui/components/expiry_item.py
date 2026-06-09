from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar
)
from PyQt6.QtCore import Qt

from ui.components.badge import Badge


class ExpiryItem(QFrame):
    """
    Single row in the expiry timeline.

    Parameters
    ----------
    name     : str   — product + batch label
    batch    : str   — subtitle (received, qty, shelf)
    days     : int   — days until expiry (negative = already expired)
    severity : str   — "critical" | "warning" | "safe"
    """

    _CARD_STYLES = {
        "critical": "background:#2a1215; border:1px solid #4a1e20;",
        "warning":  "background:#2a1f0a; border:1px solid #4a3312;",
        "safe":     "background:#161b26; border:1px solid #2a3347;",
    }
    _DAY_COLORS = {
        "critical": "#f07070",
        "warning":  "#e8a042",
        "safe":     "#8899b4",
    }
    _BAR_IDS = {
        "critical": "progress_danger",
        "warning":  "progress_warning",
        "safe":     "",
    }
    _BADGE_VARIANTS = {
        "critical": ("Hết hạn",    "exp"),
        "warning":  ("Sắp hết",    "warn"),
        "safe":     ("Theo dõi",   "normal"),
    }

    def __init__(
        self,
        name: str,
        batch: str,
        days: int,
        severity: str = "safe",
        max_days: int = 30,
        parent=None,
    ):
        super().__init__(parent)
        base = self._CARD_STYLES.get(severity, self._CARD_STYLES["safe"])
        self.setStyleSheet(f"QFrame {{ {base} border-radius:6px; }}")

        row = QHBoxLayout(self)
        row.setContentsMargins(12, 9, 12, 9)
        row.setSpacing(10)

        # Left — names
        left = QVBoxLayout()
        left.setSpacing(2)
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("color:#e2e8f0; font-size:12px; font-weight:500;")
        batch_lbl = QLabel(batch)
        batch_lbl.setStyleSheet("color:#4a5a78; font-size:10px;")
        left.addWidget(name_lbl)
        left.addWidget(batch_lbl)
        row.addLayout(left, 1)

        # Progress bar
        bar = QProgressBar()
        bar.setFixedWidth(80)
        bar.setFixedHeight(5)
        bar.setTextVisible(False)
        bar_id = self._BAR_IDS.get(severity, "")
        if bar_id:
            bar.setObjectName(bar_id)
        pct = max(0, min(100, int(abs(days) / max(max_days, 1) * 100)))
        bar.setValue(100 - pct if days >= 0 else 100)
        row.addWidget(bar, 0, Qt.AlignmentFlag.AlignVCenter)

        # Days label
        color = self._DAY_COLORS.get(severity, "#8899b4")
        day_text = f"−{abs(days)} ngày" if days < 0 else f"{days} ngày"
        days_lbl = QLabel(day_text)
        days_lbl.setStyleSheet(f"color:{color}; font-size:12px; font-weight:500;")
        days_lbl.setFixedWidth(62)
        days_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(days_lbl)

        # Badge
        badge_text, badge_var = self._BADGE_VARIANTS.get(severity, ("", "normal"))
        row.addWidget(Badge(badge_text, badge_var))