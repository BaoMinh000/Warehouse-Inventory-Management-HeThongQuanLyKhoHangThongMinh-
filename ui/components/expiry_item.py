from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar
)
from PyQt6.QtCore import Qt

from ui.components.badge import Badge
from ui.utils.theme import Theme  # Khai báo đường dẫn import file theme của bạn


class ExpiryItem(QFrame):
    """
    Single row in the expiry timeline with cleaned label borders.

    Parameters
    ----------
    name     : str   — product + batch label
    batch    : str   — subtitle (received, qty, shelf)
    days     : int   — days until expiry (negative = already expired)
    severity : str   — "critical" | "warning" | "safe"
    """

    _CARD_STYLES = {
        "critical": f"background: {Theme.EXPIRY_BG_CRITICAL}; border: 1px solid {Theme.EXPIRY_BORDER_CRITICAL};",
        "warning":  f"background: {Theme.EXPIRY_BG_WARNING}; border: 1px solid {Theme.EXPIRY_BORDER_WARNING};",
        "safe":     f"background: {Theme.BG_INPUT}; border: 1px solid {Theme.BORDER_INPUT};",
    }
    _DAY_COLORS = {
        "critical": Theme.COLOR_DANGER,
        "warning":  Theme.EXPIRY_TEXT_WARNING,
        "safe":     Theme.TEXT_MUTED,
    }
    _BAR_IDS = {
        "critical": "progress_danger",
        "warning": "progress_warning",
        "safe": "",
    }
    _BADGE_VARIANTS = {
        "critical": ("Hết hạn", "exp"),
        "warning":  ("Sắp hết", "warn"),
        "safe":     ("Theo dõi", "normal"),
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
        name_lbl.setStyleSheet(f"background: transparent; border: none; color: {Theme.TEXT_MAIN}; font-size: 12px; font-weight: 500;")
        
        batch_lbl = QLabel(batch)
        batch_lbl.setStyleSheet(f"background: transparent; border: none; color: {Theme.TEXT_SUB}; font-size: 10px;")
        
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
        color = self._DAY_COLORS.get(severity, Theme.TEXT_MUTED)
        day_text = f"−{abs(days)} ngày" if days < 0 else f"{days} ngày"
        days_lbl = QLabel(day_text)
        days_lbl.setStyleSheet(f"background: transparent; border: 1px solid {Theme.BORDER_NEUTRAL}; color: {color}; font-size: 12px; font-weight: 500;")
        days_lbl.setFixedWidth(62)
        days_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(days_lbl)

        # Badge
        badge_text, badge_var = self._BADGE_VARIANTS.get(severity, ("", "normal"))
        row.addWidget(Badge(badge_text, badge_var))