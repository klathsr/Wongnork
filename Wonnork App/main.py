"""
WONGNORK - Smart Queue Platform (PySide6)
Main entry point.

File structure:
    main.py                 ← run this
    shared.py               ← data, DB helpers, constants
    login_register_page.py  ← Login & Register
    all_queues_page.py      ← All Queues
    reservations_page.py    ← Reservations & booking
    my_location_page.py     ← Interactive map

Install:
    pip install PySide6 folium
    pip install PySide6-WebEngine   # optional, for live map
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette

from shared import (
    BG_DARK, BG_SIDEBAR, BG_CARD, BG_CARD_HOV, BG_ACTIVE,
    ACCENT_ORANGE, ACCENT_GREEN, ACCENT_RED,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, FONT_FAMILY
)
from login_register_page import LoginPage, RegisterPage
from all_queue      import AllQueuesPage
from reservations_page    import ReservationsPage
from my_location_page     import MyLocationPage

def _font(size: int, weight=QFont.Weight.Normal) -> QFont:
    return QFont(FONT_FAMILY, size, weight)


# ═══════════════════════════════════════════════════════════════════════════════
# Toast notification
# ═══════════════════════════════════════════════════════════════════════════════
class Toast(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFont(_font(12, QFont.Weight.Medium))
        self.setFixedHeight(44)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_message(self, msg: str, kind: str = "success"):
        bg = ACCENT_GREEN if kind == "success" else ACCENT_RED
        self.setStyleSheet(f"""
            background: {bg}; color: white;
            border-radius: 8px; padding: 0 20px;
        """)
        self.setText(("✓  " if kind == "success" else "✕  ") + msg)
        self.adjustSize()
        self.setFixedWidth(max(self.sizeHint().width() + 40, 280))
        # Position top-right of parent
        p = self.parent()
        self.move(p.width() - self.width() - 20, 16)
        self.show()
        self.raise_()
        self._timer.start(3200)

    def reposition(self, parent_width: int):
        self.move(parent_width - self.width() - 20, 16)


# ═══════════════════════════════════════════════════════════════════════════════
# Sidebar nav button
# ═══════════════════════════════════════════════════════════════════════════════
class NavButton(QPushButton):
    def __init__(self, icon: str, label: str, badge: int = 0):
        super().__init__()
        self.setFixedHeight(52)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 0, 14, 0)
        row.setSpacing(10)

        ic = QLabel(icon); ic.setFont(_font(16)); ic.setFixedWidth(24)
        ic.setStyleSheet("background: transparent;")
        row.addWidget(ic)

        lbl = QLabel(label); lbl.setFont(_font(14, QFont.Weight.Medium))
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        row.addWidget(lbl)
        row.addStretch()

        if badge:
            bdg = QLabel(str(badge))
            bdg.setFont(_font(11, QFont.Weight.Bold))
            bdg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bdg.setFixedSize(24, 24)
            bdg.setStyleSheet(f"background: {ACCENT_ORANGE}; color: white; border-radius: 12px;")
            row.addWidget(bdg)

        self._update_style()

    def setChecked(self, v: bool):
        super().setChecked(v); self._update_style()

    def _update_style(self):
        active = self.isChecked()
        bg     = BG_ACTIVE if active else "transparent"
        border = f"border-left: 3px solid {ACCENT_ORANGE};" if active else \
                 "border-left: 3px solid transparent;"
        self.setStyleSheet(f"""
            QPushButton {{ background: {bg}; {border} border-radius: 0px; text-align: left; }}
            QPushButton:hover {{ background: {BG_CARD}; }}
        """)


# ═══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════════════════
class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(230)
        self.setStyleSheet(f"background: {BG_SIDEBAR};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
        logo_wrap = QWidget(); logo_wrap.setFixedHeight(84)
        logo_wrap.setStyleSheet(f"background: {BG_SIDEBAR};")
        ll = QVBoxLayout(logo_wrap); ll.setContentsMargins(20, 20, 20, 10)

        brand = QLabel("WONGNORK")
        brand.setFont(_font(18, QFont.Weight.ExtraBold))
        brand.setStyleSheet(f"color: {ACCENT_ORANGE}; letter-spacing: 2px; background: transparent;")

        tagline = QLabel("SMART QUEUE PLATFORM")
        tagline.setFont(_font(8, QFont.Weight.Medium))
        tagline.setStyleSheet(f"color: {TEXT_MUTED}; letter-spacing: 2px; background: transparent;")

        ll.addWidget(brand); ll.addWidget(tagline)
        layout.addWidget(logo_wrap)
        layout.addWidget(self._divider())

        # User pill (updated after login)
        self._user_pill = QLabel("")
        self._user_pill.setFont(_font(11))
        self._user_pill.setFixedHeight(40)
        self._user_pill.setStyleSheet(f"color: {TEXT_SECONDARY}; padding-left: 20px; background: transparent;")
        layout.addWidget(self._user_pill)
        layout.addWidget(self._divider())
        layout.addSpacing(8)

        # Nav buttons
        self.btn_queues       = NavButton("📊", "All Queues",   badge=0)
        self.btn_reservations = NavButton("🍽️", "Reservations")
        self.btn_location     = NavButton("📍", "My Location")

        self.nav_buttons = [self.btn_queues, self.btn_reservations, self.btn_location]
        for btn in self.nav_buttons:
            layout.addWidget(btn)

        layout.addStretch()
        layout.addWidget(self._divider())

        self._logout_btn = QPushButton("🚪  Log Out")
        self._logout_btn.setFont(_font(13))
        self._logout_btn.setFixedHeight(48)
        self._logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_SECONDARY};
                text-align: left; padding-left: 20px; border-radius: 0px;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; background: {BG_CARD}; }}
        """)
        layout.addWidget(self._logout_btn)

    def set_active(self, index: int):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def set_user(self, user: dict):
        self._user_pill.setText(f"👤  {user.get('first','')} {user.get('last','')}")

    @staticmethod
    def _divider() -> QFrame:
        d = QFrame(); d.setFrameShape(QFrame.Shape.HLine)
        d.setStyleSheet(f"color: {BORDER};"); return d


# ═══════════════════════════════════════════════════════════════════════════════
# Main Window
# ═══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WONGNORK — Smart Queue Platform")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 760)

        self._current_user = None
        self._user_lat     = 16.4550
        self._user_lon     = 102.8240

        # Root stacked widget: auth vs main app
        self._root_stack = QStackedWidget()
        self.setCentralWidget(self._root_stack)

        # ── Auth screens ──────────────────────────────────────────────────────
        self._login_page    = LoginPage()
        self._register_page = RegisterPage()
        self._auth_stack    = QStackedWidget()
        self._auth_stack.addWidget(self._login_page)    # 0
        self._auth_stack.addWidget(self._register_page) # 1

        self._root_stack.addWidget(self._auth_stack)    # 0 = auth

        # ── Main app shell ────────────────────────────────────────────────────
        self._app_shell = QWidget()
        self._app_shell.setStyleSheet(f"background: {BG_DARK};")
        shell_layout = QHBoxLayout(self._app_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self._sidebar = Sidebar()
        shell_layout.addWidget(self._sidebar)

        vdiv = QFrame(); vdiv.setFrameShape(QFrame.Shape.VLine)
        vdiv.setStyleSheet(f"color: {BORDER};")
        shell_layout.addWidget(vdiv)

        self._page_stack = QStackedWidget()
        self._page_stack.setStyleSheet(f"background: {BG_DARK};")
        shell_layout.addWidget(self._page_stack)

        self._root_stack.addWidget(self._app_shell)     # 1 = main app

        # Toast
        self._toast = Toast(self._app_shell)

        # ── Wire auth signals ─────────────────────────────────────────────────
        self._login_page.login_success.connect(self._on_login)
        self._login_page.go_register.connect(lambda: self._auth_stack.setCurrentIndex(1))
        self._register_page.go_login.connect(lambda: self._auth_stack.setCurrentIndex(0))
        self._register_page.register_success.connect(self._on_register_success)

        # ── Wire sidebar ──────────────────────────────────────────────────────
        for i, btn in enumerate(self._sidebar.nav_buttons):
            btn.clicked.connect(lambda checked=False, idx=i: self._go_to(idx))
        self._sidebar._logout_btn.clicked.connect(self._on_logout)

        # Start on auth
        self._root_stack.setCurrentIndex(0)

    # ── Auth callbacks ────────────────────────────────────────────────────────
    def _on_login(self, user: dict):
        self._current_user = user
        self._sidebar.set_user(user)
        self._build_pages()
        self._root_stack.setCurrentIndex(1)
        self._go_to(0)
        self._toast.show_message(f"Welcome back, {user['first']}! 🎉", "success")

    def _on_register_success(self):
        self._auth_stack.setCurrentIndex(0)
        self._toast_on_auth("Account created! Please sign in.")

    def _toast_on_auth(self, msg: str):
        # Brief inline message on auth stack (not in app shell)
        pass  # Optionally implement a small auth-side notification

    def _on_logout(self):
        # Clear pages
        while self._page_stack.count():
            w = self._page_stack.widget(0)
            self._page_stack.removeWidget(w)
            w.deleteLater()
        self._current_user = None
        self._auth_stack.setCurrentIndex(0)
        self._root_stack.setCurrentIndex(0)

    # ── Build pages after login ───────────────────────────────────────────────
    def _build_pages(self):
        # Clear any previous pages
        while self._page_stack.count():
            w = self._page_stack.widget(0)
            self._page_stack.removeWidget(w)
            w.deleteLater()

        self._queues_page = AllQueuesPage(self._user_lat, self._user_lon)
        self._res_page    = ReservationsPage(self._current_user, self._user_lat, self._user_lon)
        self._loc_page    = MyLocationPage(self._user_lat, self._user_lon)

        self._page_stack.addWidget(self._queues_page)   # 0
        self._page_stack.addWidget(self._res_page)      # 1
        self._page_stack.addWidget(self._loc_page)      # 2

        # Wire location updates to other pages
        self._loc_page.location_updated.connect(self._on_location_updated)

        # Wire reservation toast
        self._res_page.toast.connect(self._toast.show_message)

    def _on_location_updated(self, lat: float, lon: float):
        self._user_lat = lat; self._user_lon = lon
        if hasattr(self, "_queues_page"):
            self._queues_page.update_location(lat, lon)

    # ── Navigation ────────────────────────────────────────────────────────────
    def _go_to(self, index: int):
        self._page_stack.setCurrentIndex(index)
        self._sidebar.set_active(index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._toast.reposition(self._app_shell.width())


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setFont(QFont(FONT_FAMILY, 12))

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,     QColor(BG_DARK))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base,       QColor(BG_CARD))
    palette.setColor(QPalette.ColorRole.Text,       QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button,     QColor(BG_CARD))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT_PRIMARY))
    app.setPalette(palette)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
