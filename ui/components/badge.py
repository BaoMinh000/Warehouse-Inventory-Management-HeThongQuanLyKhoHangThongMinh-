from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


BADGE_STYLES = {
    "fifo":    ("background:#0f2a1e; color:#2fd89c; border:1px solid #1a4033;"),
    "lifo":    ("background:#1a1a3a; color:#9898e8; border:1px solid #2a2a5a;"),
    "ok":      ("background:#0f2a1e; color:#2fd89c; border:1px solid #1a4033;"),
    "low":     ("background:#2a1215; color:#f07070; border:1px solid #4a1e20;"),
    "warn":    ("background:#2a1f0a; color:#e8a042; border:1px solid #4a3312;"),
    "exp":     ("background:#2a1215; color:#f07070; border:1px solid #4a1e20;"),
    "normal":  ("background:#1e2740; color:#8899b4; border:1px solid #2a3347;"),
    "critical":("background:#2a1215; color:#f07070; border:1px solid #4a1e20;"),
    "info":    ("background:#1a2e4a; color:#5b9cf6; border:1px solid #2a4a6e;"),
}


class Badge(QLabel):
    """Reusable status badge."""

    def __init__(self, text: str, variant: str = "normal", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_variant(variant)

    def set_variant(self, variant: str):
        style = BADGE_STYLES.get(variant, BADGE_STYLES["normal"])
        self.setStyleSheet(
            f"{style} border-radius:3px; padding:2px 7px;"
            f" font-size:10px; font-weight:500;"
        )