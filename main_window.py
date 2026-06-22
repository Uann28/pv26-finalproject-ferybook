from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QStackedWidget,
                               QMessageBox, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QAction
from views import (DashboardView, KelolaDKapalView, KelolaJadwalView,
                   ReservasiView, LaporanManifesView, ManajemenUserView)
from utils.theme_manager import ThemeManager

NAV_ITEMS_ADMIN = [
    ("Dashboard",        "dashboard"),
    ("Data Kapal",       "kapal"),
    ("Jadwal Kapal",     "jadwal"),
    ("Reservasi Tiket",  "reservasi"),
    ("Laporan Manifes",  "laporan"),
    ("Manajemen User",   "users"),
]

NAV_ITEMS_PETUGAS = [
    ("Dashboard",        "dashboard"),
    ("Reservasi Tiket",  "reservasi"),
    ("Laporan Manifes",  "laporan"),
]


def _initials(full_name: str) -> str:
    parts = full_name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return full_name[:2].upper() if full_name else "?"


def _hline() -> QFrame:
    """Thin horizontal divider."""
    f = QFrame()
    f.setObjectName("divider")
    f.setFrameShape(QFrame.HLine)
    f.setFrameShadow(QFrame.Plain)
    return f


class NavButton(QPushButton):
    def __init__(self, label: str, page_key: str, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self.setObjectName("nav_button")
        self.setFixedHeight(42)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        inner = QHBoxLayout(self)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)
        inner.setAlignment(Qt.AlignCenter)

        self._text_lbl = QLabel(label)
        self._text_lbl.setObjectName("nav_text")
        self._text_lbl.setFont(QFont("Segoe UI", 10))
        self._text_lbl.setAlignment(Qt.AlignCenter)
        inner.addWidget(self._text_lbl)

    def set_active(self, active: bool):
        self.setObjectName("nav_button_active" if active else "nav_button")
        self._text_lbl.setObjectName("nav_text_active" if active else "nav_text")
        for w in (self, self._text_lbl):
            w.style().unpolish(w)
            w.style().polish(w)


class AvatarLabel(QLabel):
    def __init__(self, initials: str, parent=None):
        super().__init__(initials, parent)
        self.setObjectName("avatar_label")
        self.setFixedSize(38, 38)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Segoe UI", 12, QFont.Bold))


class Sidebar(QFrame):
    page_changed     = Signal(str)
    logout_requested = Signal()

    def __init__(self, user: dict):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFrameShape(QFrame.NoFrame)
        self.user = user
        self._nav_buttons: list[NavButton] = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addSpacing(18)

        name_lbl = QLabel("FerryBook")
        name_lbl.setObjectName("logo_label")
        name_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        name_lbl.setContentsMargins(18, 0, 18, 0)
        root.addWidget(name_lbl)

        sub_lbl = QLabel("Ferry Management System")
        sub_lbl.setObjectName("subtitle_label")
        sub_lbl.setFont(QFont("Segoe UI", 9))
        sub_lbl.setContentsMargins(18, 2, 18, 8)
        root.addWidget(sub_lbl)

        is_admin = self.user['role'] == 'admin'

        user_row = QHBoxLayout()
        user_row.setContentsMargins(18, 0, 18, 12)
        user_row.setSpacing(8)
        uname = QLabel(self.user['full_name'])
        uname.setObjectName("user_name_label")
        uname.setFont(QFont("Segoe UI", 9))
        user_row.addWidget(uname)
        user_row.addStretch()
        badge = QLabel("Admin" if is_admin else "Petugas")
        badge.setObjectName("role_badge_admin" if is_admin else "role_badge_petugas")
        badge.setFont(QFont("Segoe UI", 8))
        user_row.addWidget(badge)
        root.addLayout(user_row)

        root.addWidget(_hline())

        items = NAV_ITEMS_ADMIN if is_admin else NAV_ITEMS_PETUGAS
        for label, key in items:
            btn = NavButton(label, key)
            btn.clicked.connect(lambda _, k=key: self._on_nav(k))
            self._nav_buttons.append(btn)
            root.addWidget(btn)
            root.addWidget(_hline())

        root.addStretch()

        root.addWidget(_hline())

        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("theme_toggle_btn")
        self.theme_btn.setFixedHeight(36)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self._update_theme_btn()
        self.theme_btn.clicked.connect(self._toggle_theme)

        theme_row = QHBoxLayout()
        theme_row.setContentsMargins(10, 8, 10, 8)
        theme_row.addWidget(self.theme_btn)
        root.addLayout(theme_row)

        root.addWidget(_hline())

        logout_btn = QPushButton("Keluar")
        logout_btn.setObjectName("logout_button")
        logout_btn.setFixedHeight(44)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        logout_btn.clicked.connect(self.logout_requested.emit)
        root.addWidget(logout_btn)

        self._set_active("dashboard")
        ThemeManager.instance().theme_changed.connect(lambda _: self._update_theme_btn())

    def _update_theme_btn(self):
        theme = ThemeManager.instance().get_current_theme()
        try:
            if theme == "dark":
                self.theme_btn.setText("Tampilan Terang")
            else:
                self.theme_btn.setText("Tampilan Gelap")
        except RuntimeError:
            pass

    def _toggle_theme(self):
        ThemeManager.instance().toggle_theme()

    def _on_nav(self, key: str):
        self._set_active(key)
        self.page_changed.emit(key)

    def _set_active(self, key: str):
        for btn in self._nav_buttons:
            btn.set_active(btn.page_key == key)


class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle("FerryBook — Sistem Manajemen Kapal Feri")
        self.setMinimumSize(1200, 750)
        self._pages: dict = {}
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        lay = QHBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.sidebar = Sidebar(self.user)
        self.sidebar.page_changed.connect(self._switch_page)
        self.sidebar.logout_requested.connect(self._do_logout)
        lay.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")
        lay.addWidget(self.stack, 1)

        self._build_menu()
        self._build_statusbar()
        self._switch_page("dashboard")

    def _build_menu(self):
        menubar = self.menuBar()

        menu_file = menubar.addMenu("&File")

        act_logout = QAction("Logout", self)
        act_logout.triggered.connect(self._do_logout)
        menu_file.addAction(act_logout)

        menu_file.addSeparator()

        act_exit = QAction("Keluar", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)
        menu_file.addAction(act_exit)

        menu_help = menubar.addMenu("&Help")

        act_about = QAction("Tentang Aplikasi", self)
        act_about.triggered.connect(self._show_about)
        menu_help.addAction(act_about)

    def _show_about(self):
        QMessageBox.information(
            self, "Tentang FerryBook",
            "FerryBook — Sistem Manajemen Jadwal & Reservasi Tiket Kapal Feri\n"
            "Mata Kuliah: Pemrograman Visual\n\n"
            "Kelompok:\n"
            "- Juan Jordan Anugrah (F1D02310061)\n"
            "- Fairuza Luthfiana (F1D02310111)\n"
            "- Muhammad Fathan Abdullah (F1D02410124)"
        )

    def _build_statusbar(self):
        sb = self.statusBar()
        anggota = QLabel(
            "Juan Jordan Anugrah (F1D02310061)   |   "
            "Fairuza Luthfiana (F1D02310111)   |   "
            "Muhammad Fathan Abdullah (F1D02410124)"
        )
        sb.addPermanentWidget(anggota)
        sb.showMessage(f"Login sebagai: {self.user['full_name']}  |  FerryBook v1.0")

    def _get_or_create_page(self, key: str):
        if key not in self._pages:
            match key:
                case "dashboard":  page = DashboardView(self.user)
                case "kapal":      page = KelolaDKapalView(self.user)
                case "jadwal":     page = KelolaJadwalView(self.user)
                case "reservasi":  page = ReservasiView(self.user)
                case "laporan":    page = LaporanManifesView(self.user)
                case "users":      page = ManajemenUserView(self.user)
                case _: return None

            scroll = QScrollArea()
            scroll.setWidget(page)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            self.stack.addWidget(scroll)
            self._pages[key] = scroll
        return self._pages[key]

    # pindah halaman sidebar
    def _switch_page(self, key: str):
        page = self._get_or_create_page(key)
        if page:
            self.stack.setCurrentWidget(page)
            self.sidebar._set_active(key)

    def _do_logout(self):
        reply = QMessageBox.question(
            self, "Konfirmasi", "Yakin ingin keluar?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()
