from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QSizePolicy, QGridLayout, QScrollArea)
from PySide6.QtCore import QTimer
import models
from utils import format_rupiah
from utils.theme_manager import ThemeManager
from datetime import datetime

_HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
_BULAN = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
          "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


def _tanggal_indonesia(d):
    return f"{_HARI[d.weekday()]}, {d.day} {_BULAN[d.month]} {d.year}"


# warna per tema
_PALETTE = {
    "dark": {
        "accent": ["#00D4FF", "#00FF99", "#FFD700", "#FF6B6B"],
        "date": "#A6ADC8", "muted": "#7A9BB5", "time": "#00D4FF",
        "status": {"aktif": "#00FF99", "penuh": "#FF6B6B",
                   "dibatalkan": "#A6ADC8", "selesai": "#7A9BB5"},
    },
    "light": {
        "accent": ["#0277BD", "#2E7D32", "#EF6C00", "#C62828"],
        "date": "#37474F", "muted": "#546E7A", "time": "#0277BD",
        "status": {"aktif": "#2E7D32", "penuh": "#C62828",
                   "dibatalkan": "#607D8B", "selesai": "#78909C"},
    },
}


class StatCard(QFrame):
    def __init__(self, label, value):
        super().__init__()
        self.setObjectName("stat_card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        self.value_lbl = QLabel(str(value))
        self.value_lbl.setObjectName("stat_card_value")
        self.label_lbl = QLabel(label)
        self.label_lbl.setObjectName("stat_card_label")
        self.label_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(self.value_lbl)
        layout.addWidget(self.label_lbl)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_value(self, v):
        self.value_lbl.setText(str(v))

    def set_accent(self, color):
        self.value_lbl.setStyleSheet(
            f"color: {color}; font-size: 26px; font-weight: bold; background: transparent;")


class DashboardView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._today_jadwals = []
        self._build_ui()
        self._refresh()
        ThemeManager.instance().theme_changed.connect(lambda _: self._refresh())
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh)
        self.timer.start(30000)

    def _palette(self):
        return _PALETTE.get(ThemeManager.instance().get_current_theme(), _PALETTE["dark"])

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        hdr = QHBoxLayout()
        titles = QVBoxLayout()
        t = QLabel("Dashboard")
        t.setObjectName("page_title")
        s = QLabel(f"Selamat datang, {self.user['full_name']}")
        s.setObjectName("page_subtitle")
        titles.addWidget(t)
        titles.addWidget(s)
        hdr.addLayout(titles)
        hdr.addStretch()
        self.date_lbl = QLabel(_tanggal_indonesia(datetime.now()))
        hdr.addWidget(self.date_lbl)
        layout.addLayout(hdr)

        grid = QGridLayout()
        grid.setSpacing(12)
        self.card_jadwal = StatCard("Jadwal Hari Ini", "0")
        self.card_penumpang = StatCard("Penumpang Hari Ini", "0")
        self.card_tiket = StatCard("Tiket Diterbitkan", "0")
        self.card_pendapatan = StatCard("Pendapatan Hari Ini", "Rp 0")
        self._cards = [self.card_jadwal, self.card_penumpang,
                       self.card_tiket, self.card_pendapatan]
        for i, c in enumerate(self._cards):
            grid.addWidget(c, 0, i)
        layout.addLayout(grid)

        sched_frame = QFrame()
        sched_frame.setObjectName("stat_card")
        sched_layout = QVBoxLayout(sched_frame)
        sched_hdr = QLabel(f"Jadwal Hari Ini — {_tanggal_indonesia(datetime.now())}")
        sched_hdr.setObjectName("section_header")
        sched_layout.addWidget(sched_hdr)

        self.jadwal_list = QWidget()
        self.jadwal_list_layout = QVBoxLayout(self.jadwal_list)
        self.jadwal_list_layout.setContentsMargins(0, 0, 0, 0)
        self.jadwal_list_layout.setSpacing(6)
        sched_scroll = QScrollArea()
        sched_scroll.setWidgetResizable(True)
        sched_scroll.setFrameShape(QFrame.NoFrame)
        sched_scroll.setWidget(self.jadwal_list)
        sched_layout.addWidget(sched_scroll)
        layout.addWidget(sched_frame, 1)

    def _refresh(self):
        pal = self._palette()
        stats = models.get_statistik_dashboard()
        self.card_jadwal.set_value(stats['total_jadwal_hari_ini'])
        self.card_penumpang.set_value(stats['total_penumpang_hari_ini'])
        self.card_tiket.set_value(stats['total_tiket_hari_ini'])
        self.card_pendapatan.set_value(format_rupiah(stats['total_pendapatan_hari_ini']))
        for c, color in zip(self._cards, pal['accent']):
            c.set_accent(color)
        self.date_lbl.setStyleSheet(f"color: {pal['date']}; font-size: 13px; font-weight: bold;")
        self.date_lbl.setText(_tanggal_indonesia(datetime.now()))

        today = datetime.now().strftime("%Y-%m-%d")
        self._today_jadwals = models.get_jadwal(tanggal=today)
        self._render_jadwal(pal)

    def _clear_layout(self, lay):
        while lay.count():
            item = lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _render_jadwal(self, pal):
        self._clear_layout(self.jadwal_list_layout)
        if not self._today_jadwals:
            lbl = QLabel("Tidak ada jadwal hari ini.")
            lbl.setStyleSheet(f"color: {pal['muted']}; padding: 8px; background: transparent;")
            self.jadwal_list_layout.addWidget(lbl)
            self.jadwal_list_layout.addStretch()
            return

        for j in self._today_jadwals:
            row = QFrame()
            row.setObjectName("info_row")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 8, 12, 8)
            time_lbl = QLabel(j['jam_berangkat'])
            time_lbl.setStyleSheet(f"color: {pal['time']}; font-weight: bold; font-size: 13px; background: transparent;")
            route_lbl = QLabel(f"{j['asal']} → {j['tujuan']}")
            route_lbl.setStyleSheet("background: transparent; font-weight: bold;")
            kapal_lbl = QLabel(j['nama_kapal'])
            kapal_lbl.setStyleSheet(f"color: {pal['muted']}; font-size: 11px; background: transparent;")
            sisa_lbl = QLabel(f"Sisa kursi: {j['sisa']}")
            sisa_lbl.setStyleSheet(f"color: {pal['muted']}; font-size: 11px; background: transparent;")
            st_color = pal['status'].get(j['status'], pal['muted'])
            st_lbl = QLabel(j['status'].upper())
            st_lbl.setStyleSheet(f"color: {st_color}; font-size: 11px; font-weight: bold; background: transparent;")
            rl.addWidget(time_lbl)
            rl.addWidget(route_lbl)
            rl.addWidget(kapal_lbl)
            rl.addStretch()
            rl.addWidget(sisa_lbl)
            rl.addWidget(st_lbl)
            self.jadwal_list_layout.addWidget(row)
        self.jadwal_list_layout.addStretch()
