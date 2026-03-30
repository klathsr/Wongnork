"""
WONGNORK - All Queues Page (PySide6)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QApplication, QMainWindow
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette

from shared import (
    BG_DARK, BG_CARD, BG_CARD_HOV, ACCENT_GREEN, ACCENT_RED,
    ACCENT_BLUE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, FONT_FAMILY,
    RESTAURANT_DATA, get_sorted_restaurants, get_waiting_count
)

def _font(size: int, weight=QFont.Weight.Normal) -> QFont:
    return QFont(FONT_FAMILY, size, weight)


# ═══════════════════════════════════════════════════════════════════════════════
# Restaurant Card
# ═══════════════════════════════════════════════════════════════════════════════
class _RestaurantCard(QFrame):
    def __init__(self, name: str, dist: float, queue: int):
        super().__init__()
        self.setFixedHeight(96)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        has_queue  = queue > 0
        left_color = ACCENT_RED if has_queue else "transparent"
        emoji      = RESTAURANT_DATA.get(name, {}).get("emoji", "🍽")
        hours      = RESTAURANT_DATA.get(name, {}).get("hours", "")

        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-radius: 10px;
                border-left: 3px solid {left_color};
            }}
            QFrame:hover {{ background: {BG_CARD_HOV}; }}
        """)

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 0, 20, 0)
        row.setSpacing(14)

        avatar = QLabel(emoji)
        avatar.setFont(_font(26))
        avatar.setFixedSize(56, 56)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"background: {BG_DARK}; border-radius: 28px; color: white;")
        row.addWidget(avatar)

        info = QVBoxLayout(); info.setSpacing(4)

        name_lbl = QLabel(name)
        name_lbl.setFont(_font(13, QFont.Weight.Medium))
        name_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        info.addWidget(name_lbl)

        meta = QHBoxLayout(); meta.setSpacing(16)
        for icon, val in [("📍", f"{dist:.2f} km"), ("⏱", f"~{int(dist*12)} min"), ("🕐", hours)]:
            lbl = QLabel(f"{icon} {val}")
            lbl.setFont(_font(11))
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
            meta.addWidget(lbl)
        meta.addStretch()
        info.addLayout(meta)
        row.addLayout(info)
        row.addStretch()

        q_col = QVBoxLayout(); q_col.setSpacing(2)
        q_col.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        q_color = ACCENT_RED if has_queue else ACCENT_GREEN
        q_num = QLabel(f"{queue} Queue")
        q_num.setFont(_font(15, QFont.Weight.Bold))
        q_num.setAlignment(Qt.AlignmentFlag.AlignRight)
        q_num.setStyleSheet(f"color: {q_color}; background: transparent;")

        q_sub = QLabel("Waiting")
        q_sub.setFont(_font(11))
        q_sub.setAlignment(Qt.AlignmentFlag.AlignRight)
        q_sub.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")

        q_col.addWidget(q_num); q_col.addWidget(q_sub)
        row.addLayout(q_col)


# ═══════════════════════════════════════════════════════════════════════════════
# All Queues Page
# ═══════════════════════════════════════════════════════════════════════════════
class AllQueuesPage(QWidget):
    def __init__(self, user_lat: float = 16.4550, user_lon: float = 102.8240, parent=None):
        super().__init__(parent)
        self.user_lat = user_lat
        self.user_lon = user_lon
        self.setStyleSheet(f"background: {BG_DARK};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(0)

        layout.addLayout(self._build_topbar())
        layout.addSpacing(24)
        layout.addWidget(self._build_subheader())
        layout.addSpacing(14)
        layout.addWidget(self._build_card_list())

    def _build_topbar(self) -> QHBoxLayout:
        topbar = QHBoxLayout()

        title_col = QVBoxLayout(); title_col.setSpacing(2)
        live = QLabel("Live overview")
        live.setFont(_font(12))
        live.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        title = QLabel("Restaurant Queues")
        title.setFont(_font(28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        title_col.addWidget(live); title_col.addWidget(title)
        topbar.addLayout(title_col)
        topbar.addStretch()

        sort_btn = QPushButton("📍  Sort by distance")
        sort_btn.setFont(_font(12, QFont.Weight.Medium))
        sort_btn.setFixedHeight(38)
        sort_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sort_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e2030; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px; padding: 0 16px;
            }}
            QPushButton:hover {{ background: {BG_CARD_HOV}; }}
        """)
        sort_btn.clicked.connect(self._populate_cards)

        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.setFont(_font(12, QFont.Weight.Medium))
        refresh_btn.setFixedHeight(38)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_BLUE}; color: white;
                border-radius: 8px; padding: 0 16px;
            }}
            QPushButton:hover {{ background: #2563eb; }}
        """)
        refresh_btn.clicked.connect(self._populate_cards)

        topbar.addWidget(sort_btn); topbar.addSpacing(10); topbar.addWidget(refresh_btn)
        return topbar

    def _build_subheader(self) -> QLabel:
        lbl = QLabel("Current Queues · Near You")
        lbl.setFont(_font(12))
        lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        return lbl

    def _build_card_list(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 6px; border-radius: 3px; }}
            QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 3px; min-height: 30px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        self._card_container = QWidget()
        self._card_container.setStyleSheet("background: transparent;")
        self._card_layout = QVBoxLayout(self._card_container)
        self._card_layout.setContentsMargins(0, 0, 0, 0)
        self._card_layout.setSpacing(10)
        self._populate_cards()
        scroll.setWidget(self._card_container)
        return scroll

    def _populate_cards(self):
        while self._card_layout.count():
            item = self._card_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for name, dist in get_sorted_restaurants(self.user_lat, self.user_lon):
            self._card_layout.addWidget(_RestaurantCard(name, dist, get_waiting_count(name)))
        self._card_layout.addStretch()

    def update_location(self, lat: float, lon: float):
        self.user_lat = lat; self.user_lon = lon
        self._populate_cards()


# Dev preview
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setFont(QFont(FONT_FAMILY, 12))
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG_DARK))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
    app.setPalette(palette)
    win = QMainWindow()
    win.setWindowTitle("All Queues — Dev Preview")
    win.resize(1100, 720)
    win.setCentralWidget(AllQueuesPage())
    win.show()
    sys.exit(app.exec())
