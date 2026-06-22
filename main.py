#!/usr/bin/env python3
"""
FerryBook - Sistem Manajemen Jadwal dan Reservasi Tiket Kapal Ferry
Final Project Pemrograman Visual
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from database import init_db
from utils.theme_manager import ThemeManager
from views import LoginWindow
from main_window import MainWindow


class FerryBookApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("FerryBook")
        self.app.setApplicationVersion("1.0.0")

        font = QFont("Segoe UI", 10)
        self.app.setFont(font)

        init_db()

        self.theme_manager = ThemeManager.instance()
        self.theme_manager.apply_theme(self.app)

        self.login_window = None
        self.main_window = None

    def _show_login(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self._on_login)
        self.login_window.show()

    def _on_login(self, user: dict):
        self.login_window.close()
        self.main_window = MainWindow(user)
        self.main_window.logout_requested.connect(self._show_login)
        self.main_window.show()

    def run(self):
        self._show_login()
        return self.app.exec()


if __name__ == "__main__":
    app = FerryBookApp()
    sys.exit(app.run())
