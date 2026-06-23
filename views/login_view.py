from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import models


class LoginWindow(QWidget):
    login_success = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FerryBook — Login")
        self.setMinimumSize(560, 560)
        self.resize(680, 600)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(60, 40, 60, 40)
        root.addStretch()

        card = QFrame()
        card.setObjectName("login_card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(48, 36, 48, 36)
        cl.setSpacing(12)

        title = QLabel("FerryBook")
        title.setObjectName("login_title")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))

        subtitle = QLabel("Sistem Manajemen Kapal Feri")
        subtitle.setObjectName("login_subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.HLine)

        lbl_user = QLabel("Username")
        lbl_user.setObjectName("form_label")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Masukkan username...")
        self.username_input.setFixedHeight(42)

        lbl_pass = QLabel("Password")
        lbl_pass.setObjectName("form_label")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Masukkan password...")
        self.password_input.setFixedHeight(42)
        self.password_input.returnPressed.connect(self._do_login)

        self.error_label = QLabel("")
        self.error_label.setObjectName("login_error")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)

        login_btn = QPushButton("MASUK")
        login_btn.setObjectName("btn_primary")
        login_btn.setFixedHeight(44)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self._do_login)

        hint = QLabel("Demo: admin / admin123   •   petugas1 / petugas123")
        hint.setObjectName("login_hint")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)

        cl.addWidget(title)
        cl.addWidget(subtitle)
        cl.addWidget(divider)
        cl.addSpacing(6)
        cl.addWidget(lbl_user)
        cl.addWidget(self.username_input)
        cl.addWidget(lbl_pass)
        cl.addWidget(self.password_input)
        cl.addWidget(self.error_label)
        cl.addWidget(login_btn)
        cl.addWidget(hint)

        root.addWidget(card)
        root.addStretch()
        self.username_input.setFocus()

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.error_label.setText("Username dan password wajib diisi.")
            return
        user = models.login(username, password)
        if user:
            self.error_label.setText("")
            self.login_success.emit(user)
        else:
            self.error_label.setText("Username atau password salah.")
            self.password_input.clear()
            self.password_input.setFocus()
