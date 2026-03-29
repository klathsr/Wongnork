"""
WONGNORK - Login & Register Page (PySide6)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QApplication, QMainWindow, QMessageBox, 
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPalette

from shared import (
    BG_DARK, BG_CARD, BG_CARD_HOV, ACCENT_ORANGE, ACCENT_GREEN, ACCENT_GREEN2,
    ACCENT_RED, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, INPUT_BG, FONT_FAMILY,
    find_user, add_user, valid_email
)

def _font(size: int, weight=QFont.Weight.Normal) -> QFont:
    return QFont(FONT_FAMILY, size, weight)

def _field_style(focus=False) -> str:
    border_color = ACCENT_ORANGE if focus else BORDER
    return f"""
        QLineEdit {{
            background: {INPUT_BG};
            color: {TEXT_PRIMARY};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 13px;
            font-family: "{FONT_FAMILY}";
        }}
        QLineEdit:focus {{
            border: 1px solid {ACCENT_ORANGE};
        }}
    """

def _btn_style(bg: str, hover: str, text_color: str = "white", border: str = "none") -> str:
    return f"""
        QPushButton {{
            background: {bg};
            color: {text_color};
            border: {border};
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
            font-weight: 600;
            font-family: "{FONT_FAMILY}";
        }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:pressed {{ background: {bg}; }}
    """


# ═══════════════════════════════════════════════════════════════════════════════
# Left branding panel
# ═══════════════════════════════════════════════════════════════════════════════
class _BrandPanel(QWidget):
    def __init__(self, title: str, subtitle: str, accent: str = ACCENT_ORANGE):
        super().__init__()
        self.setFixedWidth(300)
        self.setStyleSheet(f"background: {accent}; border-radius: 0px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 0, 36, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel("WONGNORK")
        logo.setFont(_font(22, QFont.Weight.ExtraBold))
        logo.setStyleSheet("color: white; letter-spacing: 3px; background: transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tag = QLabel("SMART QUEUE PLATFORM")
        tag.setFont(_font(8, QFont.Weight.Medium))
        tag.setStyleSheet("color: rgba(255,255,255,0.65); letter-spacing: 2px; background: transparent;")
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Avatar circle (drawn via a styled label)
        avatar = QLabel("👤")
        avatar.setFont(_font(48))
        avatar.setFixedSize(100, 100)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(
            "background: rgba(255,255,255,0.15); border-radius: 50px; color: white;"
        )

        title_lbl = QLabel(title)
        title_lbl.setFont(_font(24, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: white; background: transparent;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setWordWrap(True)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setFont(_font(11))
        sub_lbl.setStyleSheet("color: rgba(255,255,255,0.7); background: transparent;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setWordWrap(True)

        layout.addStretch()
        layout.addWidget(logo)
        layout.addWidget(tag)
        layout.addSpacing(32)
        layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(title_lbl)
        layout.addSpacing(8)
        layout.addWidget(sub_lbl)
        layout.addStretch()


# ═══════════════════════════════════════════════════════════════════════════════
# Login Page
# ═══════════════════════════════════════════════════════════════════════════════
class LoginPage(QWidget):
    # Signals
    login_success = Signal(dict)   # emits user dict
    go_register   = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG_DARK};")
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left brand panel
        root.addWidget(_BrandPanel("Welcome\nBack", "Sign in to manage your\nrestaurant queues"))

        # Right form
        right = QWidget()
        right.setStyleSheet(f"background: {BG_DARK};")
        form_layout = QVBoxLayout(right)
        form_layout.setContentsMargins(60, 0, 60, 0)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Sign In")
        title.setFont(_font(28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")

        sub = QLabel("Enter your credentials to continue")
        sub.setFont(_font(12))
        sub.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")

        # Email
        email_lbl = QLabel("EMAIL ADDRESS")
        email_lbl.setFont(_font(9, QFont.Weight.Bold))
        email_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; letter-spacing: 1px; background: transparent;")

        self._email = QLineEdit()
        self._email.setPlaceholderText("you@example.com")
        self._email.setFixedHeight(44)
        self._email.setStyleSheet(_field_style())

        # Password
        pw_lbl = QLabel("PASSWORD")
        pw_lbl.setFont(_font(9, QFont.Weight.Bold))
        pw_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; letter-spacing: 1px; background: transparent;")

        self._pw = QLineEdit()
        self._pw.setPlaceholderText("••••••••")
        self._pw.setEchoMode(QLineEdit.EchoMode.Password)
        self._pw.setFixedHeight(44)
        self._pw.setStyleSheet(_field_style())
        self._pw.returnPressed.connect(self._do_login)

        # Error label
        self._err = QLabel("")
        self._err.setFont(_font(10))
        self._err.setStyleSheet(f"color: {ACCENT_RED}; background: transparent;")

        # Buttons
        sign_in_btn = QPushButton("Sign In")
        sign_in_btn.setFixedHeight(48)
        sign_in_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sign_in_btn.setStyleSheet(_btn_style(ACCENT_ORANGE, "#d4621f"))
        sign_in_btn.clicked.connect(self._do_login)

        # Divider
        div = QHBoxLayout()
        div.setSpacing(10)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setSizePolicy(QFrame.sizePolicy.Expanding, QFrame.sizePolicy.Preferred)

        or_lbl = QLabel("or")
        or_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setSizePolicy(QFrame.sizePolicy.Expanding, QFrame.sizePolicy.Preferred)

        div.addWidget(line1)
        div.addWidget(or_lbl)
        div.addWidget(line2)

        reg_btn = QPushButton("Create an Account")
        reg_btn.setFixedHeight(48)
        reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_btn.setStyleSheet(_btn_style("transparent", BG_CARD_HOV, TEXT_PRIMARY,
                                         border=f"1px solid {BORDER}"))
        reg_btn.clicked.connect(self.go_register)

        form_layout.addStretch()
        form_layout.addWidget(title)
        form_layout.addSpacing(4)
        form_layout.addWidget(sub)
        form_layout.addSpacing(32)
        form_layout.addWidget(email_lbl)
        form_layout.addSpacing(6)
        form_layout.addWidget(self._email)
        form_layout.addSpacing(16)
        form_layout.addWidget(pw_lbl)
        form_layout.addSpacing(6)
        form_layout.addWidget(self._pw)
        form_layout.addSpacing(4)
        form_layout.addWidget(self._err)
        form_layout.addSpacing(12)
        form_layout.addWidget(sign_in_btn)
        form_layout.addSpacing(16)
        form_layout.addLayout(div)
        form_layout.addSpacing(8)
        form_layout.addWidget(reg_btn)
        form_layout.addStretch()

        root.addWidget(right)

    def _do_login(self):
        email = self._email.text().strip()
        pw    = self._pw.text()
        self._err.setText("")

        if not email or not pw:
            self._err.setText("⚠  Please fill in all fields.")
            return

        user = find_user(email)
        if user and user["password"] == pw:
            self.login_success.emit(user)
        else:
            self._err.setText("⚠  Invalid email or password.")


# ═══════════════════════════════════════════════════════════════════════════════
# Register Page
# ═══════════════════════════════════════════════════════════════════════════════
class RegisterPage(QWidget):
    register_success = Signal()
    go_login         = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG_DARK};")
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(_BrandPanel("Join Us\nToday", "Create your account and\nstart managing queues", accent=ACCENT_GREEN2))

        right = QWidget()
        right.setStyleSheet(f"background: {BG_DARK};")
        fl = QVBoxLayout(right)
        fl.setContentsMargins(60, 0, 60, 0)
        fl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Create Account")
        title.setFont(_font(28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")

        sub = QLabel("Fill in your details to get started")
        sub.setFont(_font(12))
        sub.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")

        # Name row
        name_row = QHBoxLayout()
        name_row.setSpacing(12)

        first_col = QVBoxLayout()
        first_lbl = QLabel("FIRST NAME")
        first_lbl.setFont(_font(9, QFont.Weight.Bold))
        first_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; letter-spacing: 1px; background: transparent;")
        self._first = QLineEdit(); self._first.setPlaceholderText("John")
        self._first.setFixedHeight(44); self._first.setStyleSheet(_field_style())
        first_col.addWidget(first_lbl); first_col.addWidget(self._first)

        last_col = QVBoxLayout()
        last_lbl = QLabel("LAST NAME")
        last_lbl.setFont(_font(9, QFont.Weight.Bold))
        last_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; letter-spacing: 1px; background: transparent;")
        self._last = QLineEdit(); self._last.setPlaceholderText("Doe")
        self._last.setFixedHeight(44); self._last.setStyleSheet(_field_style())
        last_col.addWidget(last_lbl); last_col.addWidget(self._last)

        name_row.addLayout(first_col)
        name_row.addLayout(last_col)

        # Email
        email_lbl = QLabel("EMAIL ADDRESS")
        email_lbl.setFont(_font(9, QFont.Weight.Bold))
        email_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; letter-spacing: 1px; background: transparent;")
        self._email = QLineEdit(); self._email.setPlaceholderText("you@example.com")
        self._email.setFixedHeight(44); self._email.setStyleSheet(_field_style())

        # Password
        pw_lbl = QLabel("PASSWORD")
        pw_lbl.setFont(_font(9, QFont.Weight.Bold))
        pw_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; letter-spacing: 1px; background: transparent;")
        self._pw = QLineEdit(); self._pw.setPlaceholderText("••••••••")
        self._pw.setEchoMode(QLineEdit.EchoMode.Password)
        self._pw.setFixedHeight(44); self._pw.setStyleSheet(_field_style())

        # Confirm Password
        cpw_lbl = QLabel("CONFIRM PASSWORD")
        cpw_lbl.setFont(_font(9, QFont.Weight.Bold))
        cpw_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; letter-spacing: 1px; background: transparent;")
        self._cpw = QLineEdit(); self._cpw.setPlaceholderText("••••••••")
        self._cpw.setEchoMode(QLineEdit.EchoMode.Password)
        self._cpw.setFixedHeight(44); self._cpw.setStyleSheet(_field_style())

        self._err = QLabel("")
        self._err.setFont(_font(10))
        self._err.setStyleSheet(f"color: {ACCENT_RED}; background: transparent;")

        reg_btn = QPushButton("Create Account")
        reg_btn.setFixedHeight(48)
        reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_btn.setStyleSheet(_btn_style(ACCENT_GREEN2, "#14532d"))
        reg_btn.clicked.connect(self._do_register)

        div = QHBoxLayout(); div.setSpacing(10)
        line1 = QFrame(); line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet(f"color: {BORDER};")
        or_lbl = QLabel("or"); or_lbl.setFont(_font(10))
        or_lbl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        line2 = QFrame(); line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f"color: {BORDER};")
        div.addWidget(line1); div.addWidget(or_lbl); div.addWidget(line2)

        back_btn = QPushButton("Back to Sign In")
        back_btn.setFixedHeight(48)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet(_btn_style("transparent", BG_CARD_HOV, TEXT_PRIMARY,
                                           border=f"1px solid {BORDER}"))
        back_btn.clicked.connect(self.go_login)

        fl.addStretch()
        fl.addWidget(title)
        fl.addSpacing(4)
        fl.addWidget(sub)
        fl.addSpacing(28)
        fl.addLayout(name_row)
        fl.addSpacing(12)
        fl.addWidget(email_lbl)
        fl.addSpacing(6)
        fl.addWidget(self._email)
        fl.addSpacing(12)
        fl.addWidget(pw_lbl)
        fl.addSpacing(6)
        fl.addWidget(self._pw)
        fl.addSpacing(12)
        fl.addWidget(cpw_lbl)
        fl.addSpacing(6)
        fl.addWidget(self._cpw)
        fl.addSpacing(4)
        fl.addWidget(self._err)
        fl.addSpacing(12)
        fl.addWidget(reg_btn)
        fl.addSpacing(12)
        fl.addLayout(div)
        fl.addSpacing(8)
        fl.addWidget(back_btn)
        fl.addStretch()

        root.addWidget(right)

    def _do_register(self):
        first = self._first.text().strip()
        last  = self._last.text().strip()
        email = self._email.text().strip()
        pw    = self._pw.text()
        cpw   = self._cpw.text()
        self._err.setText("")

        if not first or not last or not email or not pw:
            self._err.setText("⚠  Please fill in all fields."); return
        if not valid_email(email):
            self._err.setText("⚠  Invalid email address."); return
        if pw != cpw:
            self._err.setText("⚠  Passwords do not match."); return
        if find_user(email):
            self._err.setText("⚠  Email already registered."); return

        add_user(first, last, email, pw)
        self.register_success.emit()


# ═══════════════════════════════════════════════════════════════════════════════
# Dev preview
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setFont(QFont(FONT_FAMILY, 12))
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,     QColor(BG_DARK))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
    app.setPalette(palette)

    from PySide6.QtWidgets import QStackedWidget
    stack = QStackedWidget()
    stack.setWindowTitle("Login & Register — Dev Preview")
    stack.resize(960, 640)

    login_page = LoginPage()
    reg_page   = RegisterPage()

    stack.addWidget(login_page)
    stack.addWidget(reg_page)

    login_page.go_register.connect(lambda: stack.setCurrentIndex(1))
    reg_page.go_login.connect(lambda: stack.setCurrentIndex(0))
    reg_page.register_success.connect(lambda: stack.setCurrentIndex(0))
    login_page.login_success.connect(lambda u: print(f"Logged in as {u['email']}"))

    stack.show()
    sys.exit(app.exec())
