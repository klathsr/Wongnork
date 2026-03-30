"""
WONGNORK - Reservations Page (PySide6)
"""

import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QLineEdit, QComboBox, QDialog,
    QTextEdit, QApplication, QMainWindow
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPalette

from shared import (
    BG_DARK, BG_CARD, BG_CARD_HOV, INPUT_BG, ACCENT_ORANGE, ACCENT_GREEN,
    ACCENT_GREEN2, ACCENT_RED, ACCENT_GOLD, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, BORDER, FONT_FAMILY,
    RESTAURANT_DATA, RESERVATIONS, get_sorted_restaurants,
    add_reservation, get_user_reservations, cancel_reservation, submit_feedback
)

def _font(size: int, weight=QFont.Weight.Normal) -> QFont:
    return QFont(FONT_FAMILY, size, weight)

_COMBO_STYLE = f"""
    QComboBox {{
        background: {INPUT_BG}; color: {TEXT_PRIMARY};
        border: 1px solid {BORDER}; border-radius: 8px;
        padding: 8px 12px; font-size: 13px; font-family: "{FONT_FAMILY}";
    }}
    QComboBox:focus {{ border: 1px solid {ACCENT_ORANGE}; }}
    QComboBox::drop-down {{ border: none; width: 28px; }}
    QComboBox QAbstractItemView {{
        background: {BG_CARD}; color: {TEXT_PRIMARY};
        border: 1px solid {BORDER}; selection-background-color: {ACCENT_ORANGE};
    }}
"""

_INPUT_STYLE = f"""
    QLineEdit {{
        background: {INPUT_BG}; color: {TEXT_PRIMARY};
        border: 1px solid {BORDER}; border-radius: 8px;
        padding: 10px 14px; font-size: 13px; font-family: "{FONT_FAMILY}";
    }}
    QLineEdit:focus {{ border: 1px solid {ACCENT_ORANGE}; }}
"""

def _section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setFont(_font(9, QFont.Weight.Bold))
    lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; letter-spacing: 1px; background: transparent;")
    return lbl


# ═══════════════════════════════════════════════════════════════════════════════
# Feedback Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class _FeedbackDialog(QDialog):
    def __init__(self, res_id: int, rest_name: str, parent=None):
        super().__init__(parent)
        self.res_id    = res_id
        self.rest_name = rest_name
        self._rating   = 0

        self.setWindowTitle("Post-Service Evaluation")
        self.setFixedSize(440, 400)
        self.setStyleSheet(f"background: {BG_DARK};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)

        title = QLabel("How was your experience?")
        title.setFont(_font(18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")

        sub = QLabel(f"at {rest_name}")
        sub.setFont(_font(11))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")

        # Stars
        star_row = QHBoxLayout()
        star_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stars = []
        for i in range(1, 6):
            s = QLabel("☆")
            s.setFont(_font(30))
            s.setStyleSheet(f"color: {BORDER}; background: transparent;")
            s.setCursor(Qt.CursorShape.PointingHandCursor)
            s.mousePressEvent = lambda _, idx=i: self._set_rating(idx)
            star_row.addWidget(s)
            self._stars.append(s)

        # Comment
        comment_lbl = _section_label("Leave a comment (optional)")
        self._comment = QTextEdit()
        self._comment.setFixedHeight(80)
        self._comment.setStyleSheet(f"""
            QTextEdit {{
                background: {INPUT_BG}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px; padding: 8px;
                font-size: 12px; font-family: "{FONT_FAMILY}";
            }}
        """)

        self._err = QLabel("")
        self._err.setStyleSheet(f"color: {ACCENT_RED}; background: transparent;")
        self._err.setFont(_font(10))

        submit_btn = QPushButton("Submit Feedback")
        submit_btn.setFixedHeight(46)
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_ORANGE}; color: white; border-radius: 8px;
                font-size: 14px; font-weight: 600; font-family: "{FONT_FAMILY}";
            }}
            QPushButton:hover {{ background: #d4621f; }}
        """)
        submit_btn.clicked.connect(self._submit)

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(8)
        layout.addLayout(star_row)
        layout.addSpacing(8)
        layout.addWidget(comment_lbl)
        layout.addWidget(self._comment)
        layout.addWidget(self._err)
        layout.addWidget(submit_btn)

    def _set_rating(self, idx: int):
        self._rating = idx
        for i, s in enumerate(self._stars, 1):
            s.setText("★" if i <= idx else "☆")
            s.setStyleSheet(f"color: {ACCENT_GOLD if i <= idx else BORDER}; background: transparent;")

    def _submit(self):
        if self._rating == 0:
            self._err.setText("⚠  Please select a star rating."); return
        submit_feedback(self.res_id, self._rating, self._comment.toPlainText().strip())
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
# Booking Form
# ═══════════════════════════════════════════════════════════════════════════════
class _BookingForm(QFrame):
    booked = Signal()

    def __init__(self, user: dict, user_lat: float, user_lon: float):
        super().__init__()
        self._user     = user
        self._user_lat = user_lat
        self._user_lon = user_lon
        self._dropdown_map = {}

        self.setStyleSheet(f"QFrame {{ background: {BG_CARD}; border-radius: 12px; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        hdr = QLabel("  🗓️  New Booking")
        hdr.setFont(_font(14, QFont.Weight.Bold))
        hdr.setFixedHeight(54)
        hdr.setStyleSheet(f"""
            background: {ACCENT_ORANGE}; color: white;
            border-radius: 12px 12px 0 0; padding-left: 16px;
        """)
        layout.addWidget(hdr)

        body = QWidget()
        body.setStyleSheet(f"background: {BG_CARD}; border-radius: 0 0 12px 12px;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(24, 20, 24, 24)
        bl.setSpacing(10)

        # Guest name
        bl.addWidget(_section_label("Guest Name"))
        self._name_inp = QLineEdit()
        self._name_inp.setPlaceholderText(user.get("first", ""))
        self._name_inp.setFixedHeight(42)
        self._name_inp.setStyleSheet(_INPUT_STYLE)
        bl.addWidget(self._name_inp)

        # Restaurant
        bl.addSpacing(4)
        bl.addWidget(_section_label("Select Restaurant"))
        sorted_rests = get_sorted_restaurants(user_lat, user_lon)
        self._dropdown_map = {f"{r[0]} ({r[1]:.1f} km)": r[0] for r in sorted_rests}
        self._rest_combo = QComboBox()
        self._rest_combo.addItems(list(self._dropdown_map.keys()))
        self._rest_combo.setFixedHeight(42)
        self._rest_combo.setStyleSheet(_COMBO_STYLE)
        bl.addWidget(self._rest_combo)

        # Date row
        now = datetime.datetime.now()
        bl.addSpacing(4)

        date_time_row = QHBoxLayout(); date_time_row.setSpacing(12)

        date_col = QVBoxLayout()
        date_col.addWidget(_section_label("Date"))
        date_inner = QHBoxLayout(); date_inner.setSpacing(4)

        self._day   = QComboBox(); self._day.addItems([f"{i:02d}" for i in range(1, 32)])
        self._month = QComboBox(); self._month.addItems([f"{i:02d}" for i in range(1, 13)])
        self._year  = QComboBox(); self._year.addItems([str(now.year), str(now.year+1)])
        self._day.setCurrentText(now.strftime("%d"))
        self._month.setCurrentText(now.strftime("%m"))

        for w in (self._day, self._month, self._year):
            w.setFixedHeight(40); w.setStyleSheet(_COMBO_STYLE)
        date_inner.addWidget(self._day)
        date_inner.addWidget(QLabel("/"))
        date_inner.addWidget(self._month)
        date_inner.addWidget(QLabel("/"))
        date_inner.addWidget(self._year)
        date_col.addLayout(date_inner)

        time_col = QVBoxLayout()
        time_col.addWidget(_section_label("Time"))
        self._time = QComboBox()
        times = [f"{h:02d}:{m:02d}" for h in range(0, 24) for m in (0, 30)]
        self._time.addItems(times)
        self._time.setCurrentText(now.strftime("%H:00"))
        self._time.setFixedHeight(40); self._time.setStyleSheet(_COMBO_STYLE)
        time_col.addWidget(self._time)

        date_time_row.addLayout(date_col, 2)
        date_time_row.addLayout(time_col, 1)
        bl.addLayout(date_time_row)

        # Guests
        bl.addSpacing(4)
        bl.addWidget(_section_label("Guests"))
        self._guests = QComboBox()
        self._guests.addItems([str(i) for i in range(1, 11)])
        self._guests.setCurrentText("2")
        self._guests.setFixedHeight(42); self._guests.setStyleSheet(_COMBO_STYLE)
        bl.addWidget(self._guests)

        self._err = QLabel("")
        self._err.setFont(_font(10))
        self._err.setStyleSheet(f"color: {ACCENT_RED}; background: transparent;")
        bl.addWidget(self._err)

        confirm_btn = QPushButton("✓  Confirm & Join Queue")
        confirm_btn.setFixedHeight(48)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT_ORANGE}; color: white; border-radius: 8px;
                font-size: 14px; font-weight: 600; font-family: "{FONT_FAMILY}";
            }}
            QPushButton:hover {{ background: #d4621f; }}
        """)
        confirm_btn.clicked.connect(self._do_reserve)
        bl.addWidget(confirm_btn)

        layout.addWidget(body)

    def _do_reserve(self):
        self._err.setText("")
        name     = self._name_inp.text().strip() or self._user.get("first", "Guest")
        rest_key = self._rest_combo.currentText()
        rest     = self._dropdown_map.get(rest_key, rest_key.split(" (")[0])

        try:
            y, mo, d = int(self._year.currentText()), int(self._month.currentText()), int(self._day.currentText())
            hh, mm = map(int, self._time.currentText().split(":"))
            dt = datetime.datetime(y, mo, d, hh, mm)
        except ValueError:
            self._err.setText("⚠  Invalid date."); return

        if dt < datetime.datetime.now():
            self._err.setText("⚠  Cannot book a past date/time."); return

        add_reservation(self._user.get("email", ""), name, rest,
                        f"{y}-{mo:02d}-{d:02d}", self._time.currentText(),
                        self._guests.currentText(), "")
        self.booked.emit()


# ═══════════════════════════════════════════════════════════════════════════════
# Booking List
# ═══════════════════════════════════════════════════════════════════════════════
class _BookingList(QFrame):
    refresh_requested = Signal()

    def __init__(self, user: dict):
        super().__init__()
        self._user = user
        self.setStyleSheet(f"QFrame {{ background: {BG_CARD}; border-radius: 12px; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        hdr = QLabel("  📋  Live Queue & History")
        hdr.setFont(_font(14, QFont.Weight.Bold))
        hdr.setFixedHeight(54)
        hdr.setStyleSheet(f"""
            background: {ACCENT_ORANGE}; color: white;
            border-radius: 12px 12px 0 0; padding-left: 16px;
        """)
        layout.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; border-radius: 0 0 12px 12px; }}
            QScrollBar:vertical {{ background: transparent; width: 6px; border-radius: 3px; }}
            QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 3px; min-height: 30px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        self._list_widget = QWidget()
        self._list_widget.setStyleSheet(f"background: {BG_CARD};")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(16, 16, 16, 16)
        self._list_layout.setSpacing(10)

        self.refresh()

        scroll.setWidget(self._list_widget)
        layout.addWidget(scroll)

    def refresh(self):
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        bookings = get_user_reservations(self._user.get("email", ""))
        if not bookings:
            empty = QLabel("No queues yet. Book a table to get started! 🍽️")
            empty.setFont(_font(12))
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"color: {TEXT_MUTED}; padding: 40px; background: transparent;")
            self._list_layout.addWidget(empty)
            self._list_layout.addStretch()
            return

        for res in reversed(bookings):
            self._list_layout.addWidget(self._make_row(res))
        self._list_layout.addStretch()

    def _make_row(self, res: dict) -> QFrame:
        status   = res.get("status", "Waiting in Line")
        rest_name = res.get("restaurant", "Unknown")

        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{ background: {BG_CARD_HOV}; border-radius: 10px; }}
        """)

        rl = QHBoxLayout(row)
        rl.setContentsMargins(16, 12, 16, 12)
        rl.setSpacing(12)

        # Left info
        left = QVBoxLayout(); left.setSpacing(4)

        name_lbl = QLabel(f"🏢  {rest_name}")
        name_lbl.setFont(_font(13, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        left.addWidget(name_lbl)

        if status in ("Waiting in Line", "Confirmed"):
            ahead = sum(1 for r in RESERVATIONS
                        if r.get("restaurant") == rest_name
                        and r.get("status") == "Waiting in Line"
                        and r["id"] < res["id"])
            q_color = ACCENT_RED if ahead > 0 else ACCENT_GREEN
            q_info = QLabel(f"🎫 Queue: {res.get('queue_number','N/A')}   |   ⏳ {ahead} queues ahead")
            q_info.setFont(_font(11, QFont.Weight.Medium))
            q_info.setStyleSheet(f"color: {q_color}; background: transparent;")
            left.addWidget(q_info)

        meta = QLabel(f"📅 {res['date']}  •  🕐 {res['time']}  •  👥 {res['guests']} pax")
        meta.setFont(_font(10))
        meta.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        left.addWidget(meta)

        rl.addLayout(left)
        rl.addStretch()

        # Right actions
        right = QVBoxLayout(); right.setSpacing(6)
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        if status == "Completed":
            rating  = res.get("rating", 0)
            stars   = "★" * rating + "☆" * (5 - rating)
            done_lbl = QLabel("Completed")
            done_lbl.setFont(_font(11, QFont.Weight.Bold))
            done_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; background: transparent;")
            done_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            star_lbl = QLabel(stars)
            star_lbl.setFont(_font(18))
            star_lbl.setStyleSheet(f"color: {ACCENT_GOLD}; background: transparent;")
            star_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            right.addWidget(done_lbl); right.addWidget(star_lbl)

        elif status == "Cancelled":
            c_lbl = QLabel("Cancelled")
            c_lbl.setFont(_font(11, QFont.Weight.Bold))
            c_lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
            c_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            right.addWidget(c_lbl)

        else:
            wait_lbl = QLabel("Status: Waiting")
            wait_lbl.setFont(_font(10, QFont.Weight.Bold))
            wait_lbl.setStyleSheet(f"color: {ACCENT_ORANGE}; background: transparent;")
            wait_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            right.addWidget(wait_lbl)

            btn_row = QHBoxLayout(); btn_row.setSpacing(8)

            finish_btn = QPushButton("🍽️  Finish & Rate")
            finish_btn.setFixedHeight(32)
            finish_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            finish_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {ACCENT_GREEN2}; color: white; border-radius: 6px;
                    font-size: 11px; font-weight: 600; padding: 0 10px;
                    font-family: "{FONT_FAMILY}";
                }}
                QPushButton:hover {{ background: #15803d; }}
            """)
            finish_btn.clicked.connect(
                lambda checked=False, rid=res["id"], rn=rest_name: self._show_feedback(rid, rn)
            )

            cancel_btn = QPushButton("Cancel")
            cancel_btn.setFixedHeight(32)
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {ACCENT_RED}; border-radius: 6px;
                    font-size: 11px; font-weight: 600; padding: 0 10px;
                    border: 1px solid {ACCENT_RED}; font-family: "{FONT_FAMILY}";
                }}
                QPushButton:hover {{ background: rgba(239,68,68,0.1); }}
            """)
            cancel_btn.clicked.connect(
                lambda checked=False, rid=res["id"]: self._cancel(rid)
            )

            btn_row.addWidget(finish_btn); btn_row.addWidget(cancel_btn)
            right.addLayout(btn_row)

        rl.addLayout(right)
        return row

    def _show_feedback(self, res_id: int, rest_name: str):
        dlg = _FeedbackDialog(res_id, rest_name, self)
        if dlg.exec(): self.refresh()

    def _cancel(self, res_id: int):
        cancel_reservation(res_id)
        self.refresh()


# ═══════════════════════════════════════════════════════════════════════════════
# Reservations Page
# ═══════════════════════════════════════════════════════════════════════════════
class ReservationsPage(QWidget):
    toast = Signal(str, str)   # message, kind

    def __init__(self, user: dict, user_lat: float = 16.4550, user_lon: float = 102.8240, parent=None):
        super().__init__(parent)
        self._user = user
        self.setStyleSheet(f"background: {BG_DARK};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(0)

        # Header
        title = QLabel("Find & Book a Table")
        title.setFont(_font(28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)
        layout.addSpacing(24)

        # Two column layout
        cols = QHBoxLayout(); cols.setSpacing(24)

        self._form = _BookingForm(user, user_lat, user_lon)
        self._list = _BookingList(user)

        self._form.booked.connect(self._on_booked)

        cols.addWidget(self._form, 1)
        cols.addWidget(self._list, 1)
        layout.addLayout(cols)

    def _on_booked(self):
        self._list.refresh()
        self.toast.emit("Joined queue successfully! 🎉", "success")

    def refresh(self):
        self._list.refresh()


# Dev preview
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setFont(QFont(FONT_FAMILY, 12))
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG_DARK))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
    app.setPalette(palette)

    demo_user = {"first": "Demo", "last": "User", "email": "demo@wongnork.com"}
    win = QMainWindow()
    win.setWindowTitle("Reservations — Dev Preview")
    win.resize(1200, 760)
    win.setCentralWidget(ReservationsPage(demo_user))
    win.show()
    sys.exit(app.exec())
