from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QDialog, QFormLayout,
                               QSpinBox, QDoubleSpinBox, QMessageBox,
                               QHeaderView, QAbstractItemView, QComboBox,
                               QDateEdit, QTimeEdit, QGridLayout, QGroupBox,
                               QSizePolicy)
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtGui import QFont, QColor
import models
from utils.theme_manager import style_calendar
from datetime import datetime


def _action_cell(edit_cb, del_cb) -> QWidget:
    w = QWidget()
    w.setObjectName("action_cell")
    lay = QHBoxLayout(w)
    lay.setContentsMargins(2, 2, 2, 2)
    lay.setSpacing(6)

    edit_btn = QPushButton("Edit")
    edit_btn.setObjectName("btn_warning")
    edit_btn.setFixedHeight(32)
    edit_btn.setCursor(Qt.PointingHandCursor)
    edit_btn.clicked.connect(edit_cb)

    del_btn = QPushButton("Hapus")
    del_btn.setObjectName("btn_danger")
    del_btn.setFixedHeight(32)
    del_btn.setCursor(Qt.PointingHandCursor)
    del_btn.clicked.connect(del_cb)

    lay.addWidget(edit_btn)
    lay.addWidget(del_btn)
    return w


class JadwalDialog(QDialog):
    def __init__(self, parent=None, jadwal=None):
        super().__init__(parent)
        self.jadwal = jadwal
        self.setWindowTitle("Edit Jadwal" if jadwal else "Tambah Jadwal Baru")
        self.setMinimumWidth(580)
        self._build_ui()
        self._load_combos()
        if jadwal:
            self._populate(jadwal)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("Edit Jadwal Keberangkatan" if self.jadwal else "Buat Jadwal Keberangkatan")
        title.setObjectName("section_header")
        layout.addWidget(title)

        g1 = QGroupBox("Informasi Kapal & Rute")
        g1_layout = QFormLayout(g1); g1_layout.setSpacing(10)
        self.kapal_combo = QComboBox(); self.kapal_combo.setFixedHeight(36)
        self.rute_combo  = QComboBox(); self.rute_combo.setFixedHeight(36)
        g1_layout.addRow("Kapal *", self.kapal_combo)
        g1_layout.addRow("Rute *",  self.rute_combo)
        layout.addWidget(g1)

        g2 = QGroupBox("Jadwal Waktu")
        g2_layout = QGridLayout(g2); g2_layout.setSpacing(10)

        self.tanggal_input = QDateEdit()
        self.tanggal_input.setCalendarPopup(True)
        self.tanggal_input.setDate(QDate.currentDate())
        self.tanggal_input.setFixedHeight(36)
        self.tanggal_input.setDisplayFormat("dd MMMM yyyy")
        style_calendar(self.tanggal_input)
        if not self.jadwal:
            self.tanggal_input.setMinimumDate(QDate.currentDate())
            self.tanggal_input.setMaximumDate(QDate.currentDate().addDays(13))

        self.jam_brgkt_input = QTimeEdit()
        self.jam_brgkt_input.setTime(QTime(8, 0))
        self.jam_brgkt_input.setFixedHeight(36)
        self.jam_brgkt_input.setDisplayFormat("HH:mm")

        self.jam_tiba_preview = QLabel("-")
        self.jam_tiba_preview.setStyleSheet("font-weight: bold;")
        self.jam_brgkt_input.timeChanged.connect(lambda _: self._update_jam_tiba_preview())
        self.rute_combo.currentIndexChanged.connect(lambda _: self._update_jam_tiba_preview())

        g2_layout.addWidget(QLabel("Tanggal *"),       0, 0); g2_layout.addWidget(self.tanggal_input,   0, 1)
        g2_layout.addWidget(QLabel("Jam Berangkat *"), 1, 0); g2_layout.addWidget(self.jam_brgkt_input, 1, 1)
        g2_layout.addWidget(QLabel("Jam Tiba (Est.)"), 2, 0); g2_layout.addWidget(self.jam_tiba_preview, 2, 1)
        layout.addWidget(g2)

        g3 = QGroupBox("Kapasitas")
        g3_layout = QGridLayout(g3); g3_layout.setSpacing(10)
        self.kap_input = QSpinBox(); self.kap_input.setRange(1, 9999); self.kap_input.setValue(300); self.kap_input.setFixedHeight(36)
        g3_layout.addWidget(QLabel("Kapasitas (kursi) *"), 0, 0); g3_layout.addWidget(self.kap_input, 0, 1)
        layout.addWidget(g3)

        g4 = QGroupBox("Tarif (Rp)")
        g4_layout = QGridLayout(g4); g4_layout.setSpacing(10)
        self.h_dewasa = QDoubleSpinBox(); self.h_dewasa.setRange(0, 9999999); self.h_dewasa.setValue(25000);  self.h_dewasa.setPrefix("Rp "); self.h_dewasa.setFixedHeight(36)
        self.h_motor  = QDoubleSpinBox(); self.h_motor.setRange(0, 9999999);  self.h_motor.setValue(80000);   self.h_motor.setPrefix("Rp ");  self.h_motor.setFixedHeight(36)
        self.h_mobil  = QDoubleSpinBox(); self.h_mobil.setRange(0, 9999999);  self.h_mobil.setValue(250000);  self.h_mobil.setPrefix("Rp ");  self.h_mobil.setFixedHeight(36)
        self.h_bus    = QDoubleSpinBox(); self.h_bus.setRange(0, 9999999);    self.h_bus.setValue(600000);    self.h_bus.setPrefix("Rp ");    self.h_bus.setFixedHeight(36)
        self.h_truk   = QDoubleSpinBox(); self.h_truk.setRange(0, 9999999);   self.h_truk.setValue(900000);   self.h_truk.setPrefix("Rp ");   self.h_truk.setFixedHeight(36)
        g4_layout.addWidget(QLabel("Penumpang Dewasa"), 0, 0); g4_layout.addWidget(self.h_dewasa, 0, 1)
        g4_layout.addWidget(QLabel("Motor"),             1, 0); g4_layout.addWidget(self.h_motor,  1, 1)
        g4_layout.addWidget(QLabel("Mobil"),             2, 0); g4_layout.addWidget(self.h_mobil,  2, 1)
        g4_layout.addWidget(QLabel("Bus"),               3, 0); g4_layout.addWidget(self.h_bus,    3, 1)
        g4_layout.addWidget(QLabel("Truk"),              4, 0); g4_layout.addWidget(self.h_truk,   4, 1)
        layout.addWidget(g4)

        btns = QHBoxLayout(); btns.addStretch()
        cancel_btn = QPushButton("Batal"); cancel_btn.clicked.connect(self.reject)
        save_btn   = QPushButton("Simpan Perubahan" if self.jadwal else "Buat Jadwal")
        save_btn.setObjectName("btn_primary"); save_btn.clicked.connect(self._save)
        btns.addWidget(cancel_btn); btns.addWidget(save_btn)
        layout.addLayout(btns)

    def _load_combos(self):
        self.kapals = models.get_kapal_aktif()
        for k in self.kapals:
            self.kapal_combo.addItem(f"{k['nama_kapal']} ({k['kode_kapal']})", k['id'])
        self.rutes = models.get_all_rute()
        for r in self.rutes:
            self.rute_combo.addItem(f"{r['asal']} → {r['tujuan']}", r['id'])
        if self.kapals and not self.jadwal:
            self.kap_input.setValue(self.kapals[0]['kapasitas'])
        self.kapal_combo.currentIndexChanged.connect(self._on_kapal_changed)
        self._update_jam_tiba_preview()

    def _on_kapal_changed(self, idx):
        if not self.jadwal and idx < len(self.kapals):
            self.kap_input.setValue(self.kapals[idx]['kapasitas'])

    def _durasi_rute(self):
        rid = self.rute_combo.currentData()
        for r in getattr(self, 'rutes', []):
            if r['id'] == rid:
                return r.get('durasi_menit') or 60
        return 60

    # jam tiba otomatis
    def _hitung_jam_tiba(self):
        t = self.jam_brgkt_input.time()
        total = t.hour() * 60 + t.minute() + max(self._durasi_rute(), 30)
        return f"{(total // 60) % 24:02d}:{total % 60:02d}"

    def _update_jam_tiba_preview(self):
        self.jam_tiba_preview.setText(self._hitung_jam_tiba())

    def _populate(self, j):
        for i, k in enumerate(self.kapals):
            if k['id'] == j['kapal_id']:
                self.kapal_combo.setCurrentIndex(i); break
        for i, r in enumerate(self.rutes):
            if r['id'] == j['rute_id']:
                self.rute_combo.setCurrentIndex(i); break
        self.tanggal_input.setDate(QDate.fromString(j['tanggal'], "yyyy-MM-dd"))
        self.jam_brgkt_input.setTime(QTime.fromString(j['jam_berangkat'], "HH:mm"))
        self._update_jam_tiba_preview()
        self.kap_input.setValue(j['kapasitas'])
        self.h_dewasa.setValue(j['harga_dewasa'])
        self.h_motor.setValue(j['harga_kendaraan_motor'])
        self.h_mobil.setValue(j['harga_kendaraan_mobil'])
        self.h_bus.setValue(j['harga_kendaraan_bus'])
        self.h_truk.setValue(j['harga_kendaraan_truk'])

    def _save(self):
        kapal_id = self.kapal_combo.currentData()
        rute_id  = self.rute_combo.currentData()
        if not kapal_id or not rute_id:
            QMessageBox.warning(self, "Validasi", "Pilih kapal dan rute."); return
        tanggal = self.tanggal_input.date().toString("yyyy-MM-dd")
        if not self.jadwal:
            if tanggal < datetime.now().strftime("%Y-%m-%d"):
                QMessageBox.warning(self, "Validasi", "Tanggal tidak boleh di masa lalu."); return
        jam_brgkt = self.jam_brgkt_input.time().toString("HH:mm")
        jam_tiba  = self._hitung_jam_tiba()
        if self.jadwal:
            ok, msg = models.update_jadwal(
                self.jadwal['id'], kapal_id, rute_id, tanggal, jam_brgkt, jam_tiba,
                self.h_dewasa.value(), self.h_motor.value(),
                self.h_mobil.value(), self.h_bus.value(), self.h_truk.value(),
                self.kap_input.value()
            )
        else:
            ok, msg = models.create_jadwal(
                kapal_id, rute_id, tanggal, jam_brgkt, jam_tiba,
                self.h_dewasa.value(), self.h_motor.value(),
                self.h_mobil.value(), self.h_bus.value(), self.h_truk.value(),
                self.kap_input.value()
            )
        if ok:
            QMessageBox.information(self, "Sukses", msg); self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)


class KelolaJadwalView(QWidget):
    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self._jadwal_data = []
        self._build_ui()
        self._apply_filters()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        hdr = QHBoxLayout()
        titles = QVBoxLayout(); titles.setSpacing(2)
        t = QLabel("Kelola Jadwal Kapal"); t.setObjectName("page_title")
        s = QLabel("Kelola jadwal keberangkatan kapal feri")
        s.setObjectName("page_subtitle")
        titles.addWidget(t); titles.addWidget(s)
        hdr.addLayout(titles); hdr.addStretch()

        self.count_badge = QLabel()
        self.count_badge.setObjectName("badge_info")
        self.count_badge.setFixedHeight(32)
        self.count_badge.setContentsMargins(12, 0, 12, 0)
        self.count_badge.setAlignment(Qt.AlignCenter)
        hdr.addWidget(self.count_badge)

        add_btn = QPushButton("Tambah Jadwal")
        add_btn.setObjectName("btn_primary"); add_btn.setFixedHeight(36)
        add_btn.clicked.connect(self._add)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        tb = QHBoxLayout()
        tb.setContentsMargins(0, 4, 0, 4)
        tb.setSpacing(16)

        tgl_lbl = QLabel("Tanggal:")
        tgl_lbl.setFont(QFont("Segoe UI", 10))

        self.filter_date = QDateEdit()
        self.filter_date.setCalendarPopup(True)
        self.filter_date.setDate(QDate.currentDate())
        self.filter_date.setMinimumDate(QDate.currentDate())
        self.filter_date.setMaximumDate(QDate.currentDate().addDays(13))
        self.filter_date.setFixedHeight(36)
        self.filter_date.setFixedWidth(190)
        self.filter_date.setDisplayFormat("dd MMMM yyyy")
        style_calendar(self.filter_date)
        self.filter_date.dateChanged.connect(lambda _: self._apply_filters())

        rute_lbl = QLabel("Rute:")
        rute_lbl.setFont(QFont("Segoe UI", 10))

        self.rute_combo = QComboBox()
        self.rute_combo.setFixedHeight(36)
        self.rute_combo.setFixedWidth(240)
        self.rute_combo.addItem("Semua Rute", None)
        for r in models.get_all_rute():
            self.rute_combo.addItem(f"{r['asal']} → {r['tujuan']}", r['id'])
        self.rute_combo.currentIndexChanged.connect(lambda _: self._apply_filters())

        tb.addWidget(tgl_lbl)
        tb.addWidget(self.filter_date)
        tb.addSpacing(8)
        tb.addWidget(rute_lbl)
        tb.addWidget(self.rute_combo)
        tb.addStretch()

        refresh_btn = QPushButton("Tampilkan / Refresh")
        refresh_btn.setObjectName("btn_primary")
        refresh_btn.setFixedHeight(36)
        refresh_btn.clicked.connect(self._apply_filters)
        tb.addWidget(refresh_btn)
        layout.addLayout(tb)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Kapal", "Rute", "Tanggal", "Berangkat", "Tiba",
            "Terisi / Kapasitas", "Aksi"
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.Fixed); self.table.setColumnWidth(2, 110)
        hh.setSectionResizeMode(3, QHeaderView.Fixed); self.table.setColumnWidth(3, 85)
        hh.setSectionResizeMode(4, QHeaderView.Fixed); self.table.setColumnWidth(4, 85)
        hh.setSectionResizeMode(5, QHeaderView.Fixed); self.table.setColumnWidth(5, 140)
        hh.setSectionResizeMode(6, QHeaderView.Fixed); self.table.setColumnWidth(6, 180)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.table, 1)

    def _apply_filters(self):
        tgl_str = self.filter_date.date().toString("yyyy-MM-dd")
        rows    = models.get_jadwal(tanggal=tgl_str)

        rute_id = self.rute_combo.currentData()
        if rute_id is not None:
            rows = [r for r in rows if r['rute_id'] == rute_id]

        self._jadwal_data = rows

        today_count = len(models.get_jadwal(tanggal=QDate.currentDate().toString("yyyy-MM-dd")))
        self.count_badge.setText(f"{today_count} jadwal hari ini")

        self._populate_table()

    def _populate_table(self):
        rows = self._jadwal_data
        self.table.clearSpans()
        self.table.setRowCount(max(len(rows), 1))

        if not rows:
            empty = QTableWidgetItem("Tidak ada jadwal untuk tanggal / rute yang dipilih")
            empty.setTextAlignment(Qt.AlignCenter)
            empty.setForeground(QColor("#888888"))
            self.table.setSpan(0, 0, 1, 7)
            self.table.setItem(0, 0, empty)
            self.table.setRowHeight(0, 60)
            return

        for i, j in enumerate(rows):
            kapal_item = QTableWidgetItem(j['nama_kapal'])
            kapal_item.setData(Qt.UserRole, j['id'])
            kapal_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, kapal_item)

            for c, v in enumerate([
                f"{j['asal']} → {j['tujuan']}",
                j['tanggal'],
                j.get('jam_berangkat', ''),
                j.get('jam_tiba', ''),
                f"{j['terisi']} / {j['kapasitas']}",
            ], start=1):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, c, item)

            self.table.setCellWidget(i, 6, _action_cell(
                lambda _, row=j: self._edit(row),
                lambda _, jid=j['id']: self._delete(jid),
            ))
            self.table.setRowHeight(i, 54)

    def _add(self):
        dlg = JadwalDialog(self)
        if dlg.exec(): self._apply_filters()

    def _edit(self, jadwal):
        dlg = JadwalDialog(self, jadwal)
        if dlg.exec(): self._apply_filters()

    def _delete(self, jid: int):
        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Hapus jadwal ini? Tiket terkait juga akan terhapus.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ok, msg = models.delete_jadwal(jid)
            if ok:
                self._apply_filters()
            else:
                QMessageBox.critical(self, "Error", msg)
