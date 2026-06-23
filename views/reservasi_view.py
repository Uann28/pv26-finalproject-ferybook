from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QFrame, QDialog, QFormLayout, QLineEdit,
                               QSpinBox, QMessageBox, QHeaderView,
                               QAbstractItemView, QComboBox, QDateEdit,
                               QGroupBox, QScrollArea, QSizePolicy, QFileDialog)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
import models
from utils import format_rupiah, cetak_tiket_pdf
from utils.theme_manager import style_calendar


class TiketDetailDialog(QDialog):
    def __init__(self, parent, nomor_tiket):
        super().__init__(parent)
        self.setWindowTitle("Detail Tiket")
        self.setMinimumWidth(420)
        self.nomor_tiket = nomor_tiket
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        t = self.nomor_tiket and models.get_tiket_by_nomor(self.nomor_tiket)
        if not t:
            layout.addWidget(QLabel("Tiket tidak ditemukan.")); return

        title = QLabel(f"Tiket {t['nomor_tiket']}")
        title.setObjectName("section_header")
        layout.addWidget(title)

        rows = [
            ("Rute", f"{t['asal']} → {t['tujuan']}"),
            ("Kapal", t['nama_kapal']),
            ("Tanggal", t['tanggal']),
            ("Jam Berangkat", t['jam_berangkat']),
            ("Nama Penumpang", t['nama_penumpang']),
            ("No. Identitas", t['no_identitas']),
            ("No. HP", t.get('no_hp','') or '-'),
            ("Tipe Tiket", t['tipe_tiket'].capitalize()),
        ]
        if t['tipe_tiket'] == 'kendaraan':
            rows += [("Jenis Kendaraan", t.get('jenis_kendaraan','')),
                     ("No. Polisi", t.get('no_polisi',''))]
        else:
            rows.append(("Jumlah Penumpang", str(t.get('jumlah_penumpang',1))))
        rows += [
            ("Total Harga", format_rupiah(t['total_harga'])),
            ("Petugas", t['nama_petugas']),
            ("Waktu Transaksi", t['tanggal_transaksi']),
        ]
        for label, value in rows:
            row_frame = QFrame()
            row_frame.setStyleSheet("background:#162535; border-radius:5px; padding: 0;")
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(10, 6, 10, 6)
            lbl = QLabel(label); lbl.setStyleSheet("color:#7A9BB5; background:transparent; min-width:130px;")
            val = QLabel(value); val.setStyleSheet("color:#E8EDF2; background:transparent; font-weight:bold;")
            val.setWordWrap(True)
            row_layout.addWidget(lbl); row_layout.addWidget(val, 1)
            layout.addWidget(row_frame)

        btns = QHBoxLayout()
        btns.addStretch()
        pdf_btn = QPushButton("Cetak PDF"); pdf_btn.setObjectName("btn_primary")
        pdf_btn.clicked.connect(lambda: self._cetak_pdf(t))
        close_btn = QPushButton("Tutup"); close_btn.clicked.connect(self.accept)
        btns.addWidget(pdf_btn); btns.addWidget(close_btn)
        layout.addLayout(btns)

    def _cetak_pdf(self, t):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan Tiket PDF", f"Tiket_{t['nomor_tiket']}.pdf", "PDF (*.pdf)")
        if path:
            ok = cetak_tiket_pdf(t, path)
            if ok:
                QMessageBox.information(self, "Sukses", f"Tiket disimpan ke:\n{path}")
            else:
                QMessageBox.critical(self, "Error", "Gagal membuat PDF. Pastikan reportlab terinstal.")


class ReservasiView(QWidget):
    KATEGORI = ["Pejalan Kaki", "Motor", "Mobil", "Bus", "Truk"]
    HARGA_KEYS = {
        "Motor": "harga_kendaraan_motor",
        "Mobil": "harga_kendaraan_mobil",
        "Bus":   "harga_kendaraan_bus",
        "Truk":  "harga_kendaraan_truk",
    }

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.selected_jadwal = None
        self.jadwals = []
        self._harga_satuan = 0
        self._total_harga = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        titles = QVBoxLayout()
        t = QLabel("Reservasi Tiket"); t.setObjectName("page_title")
        s = QLabel("Pemesanan tiket bertahap — pilih rute, tanggal, kapal, lalu isi data")
        s.setObjectName("page_subtitle")
        titles.addWidget(t); titles.addWidget(s)
        hdr.addLayout(titles); hdr.addStretch()
        layout.addLayout(hdr)

        main_split = QHBoxLayout()
        main_split.setSpacing(16)

        left = QFrame(); left.setObjectName("stat_card")
        left_layout = QVBoxLayout(left); left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(10)

        left_layout.addWidget(self._step_label("1. Pilih Rute"))
        self.rute_combo = QComboBox(); self.rute_combo.setFixedHeight(34)
        self.rute_combo.addItem("— Pilih Rute —", None)
        for r in models.get_all_rute():
            self.rute_combo.addItem(f"{r['asal']} → {r['tujuan']}", r['id'])
        self.rute_combo.currentIndexChanged.connect(self._on_route_changed)
        left_layout.addWidget(self.rute_combo)

        self.lbl_step2 = self._step_label("2. Pilih Tanggal Keberangkatan")
        left_layout.addWidget(self.lbl_step2)
        date_row = QHBoxLayout()
        self.filter_date = QDateEdit(); self.filter_date.setCalendarPopup(True)
        self.filter_date.setDate(QDate.currentDate())
        self.filter_date.setMinimumDate(QDate.currentDate())
        self.filter_date.setFixedHeight(34)
        self.filter_date.setDisplayFormat("dd MMMM yyyy")
        style_calendar(self.filter_date)
        self.filter_date.dateChanged.connect(lambda _: self._load_jadwal())
        date_row.addWidget(self.filter_date, 1)
        left_layout.addLayout(date_row)

        self.lbl_step3 = self._step_label("3. Pilih Kapal & Jam Tersedia")
        left_layout.addWidget(self.lbl_step3)

        self.jadwal_table = QTableWidget()
        self.jadwal_table.setColumnCount(3)
        self.jadwal_table.setHorizontalHeaderLabels(["Kapal", "Jam", "Sisa Kursi"])
        hh = self.jadwal_table.horizontalHeader()
        for c in range(3):
            hh.setSectionResizeMode(c, QHeaderView.Stretch)
        self.jadwal_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.jadwal_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.jadwal_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.jadwal_table.verticalHeader().setVisible(False)
        self.jadwal_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.jadwal_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.jadwal_table.itemSelectionChanged.connect(self._on_jadwal_selected)
        left_layout.addWidget(self.jadwal_table, 1)

        self.jadwal_info = QLabel("Pilih rute & tanggal untuk melihat jadwal tersedia.")
        self.jadwal_info.setObjectName("info_row")
        self.jadwal_info.setWordWrap(True)
        self.jadwal_info.setContentsMargins(10, 8, 10, 8)
        left_layout.addWidget(self.jadwal_info)
        main_split.addWidget(left, 1)

        self.right = QFrame(); self.right.setObjectName("stat_card")
        right_layout = QVBoxLayout(self.right); right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.addWidget(self._step_label("4. Isi Data Tiket"))

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        self.form_widget = QWidget()
        form_layout = QVBoxLayout(self.form_widget); form_layout.setSpacing(10)

        g1 = QGroupBox("Data Penumpang / Pemesan")
        g1_layout = QFormLayout(g1); g1_layout.setSpacing(8)
        self.nama_input = QLineEdit(); self.nama_input.setPlaceholderText("Nama lengkap..."); self.nama_input.setFixedHeight(34)
        self.id_input = QLineEdit(); self.id_input.setPlaceholderText("NIK / Paspor..."); self.id_input.setFixedHeight(34)
        self.hp_input = QLineEdit(); self.hp_input.setPlaceholderText("08xxxxxxxxxx"); self.hp_input.setFixedHeight(34)
        g1_layout.addRow("Nama *", self.nama_input)
        g1_layout.addRow("No. Identitas *", self.id_input)
        g1_layout.addRow("No. HP", self.hp_input)
        form_layout.addWidget(g1)

        g2 = QGroupBox("Kategori Tiket")
        g2_layout = QFormLayout(g2); g2_layout.setSpacing(8)
        self.kategori_combo = QComboBox(); self.kategori_combo.setFixedHeight(34)
        self.kategori_combo.addItems(self.KATEGORI)
        self.kategori_combo.currentTextChanged.connect(self._on_kategori_changed)
        g2_layout.addRow("Kategori *", self.kategori_combo)

        self.nopol_row_label = QLabel("No. Polisi *")
        self.nopol_input = QLineEdit(); self.nopol_input.setPlaceholderText("misal: EA 1234 AB"); self.nopol_input.setFixedHeight(34)
        g2_layout.addRow(self.nopol_row_label, self.nopol_input)
        form_layout.addWidget(g2)

        self.g_jumlah = QGroupBox("Jumlah Penumpang")
        gj_layout = QFormLayout(self.g_jumlah); gj_layout.setSpacing(8)
        self.jml_input = QSpinBox(); self.jml_input.setRange(1, 50); self.jml_input.setValue(1); self.jml_input.setFixedHeight(34)
        self.jml_input.valueChanged.connect(self._update_total)
        gj_layout.addRow("Jumlah *", self.jml_input)
        form_layout.addWidget(self.g_jumlah)

        scroll.setWidget(self.form_widget)
        right_layout.addWidget(scroll, 1)

        total_frame = QFrame(); total_frame.setObjectName("info_row")
        total_layout = QVBoxLayout(total_frame); total_layout.setContentsMargins(14, 12, 14, 12)
        total_row = QHBoxLayout()
        total_row.addWidget(QLabel("TOTAL BAYAR:"))
        total_row.addStretch()
        self.total_lbl = QLabel("Rp 0"); self.total_lbl.setStyleSheet("color:#00D4FF; font-size:20px; font-weight:bold; background:transparent;")
        total_row.addWidget(self.total_lbl)
        total_layout.addLayout(total_row)
        right_layout.addWidget(total_frame)

        self.submit_btn = QPushButton("TERBITKAN TIKET"); self.submit_btn.setObjectName("btn_success")
        self.submit_btn.setFixedHeight(44); self.submit_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.submit_btn.clicked.connect(self._submit)
        right_layout.addWidget(self.submit_btn)
        main_split.addWidget(self.right, 1)
        layout.addLayout(main_split)
        layout.addStretch()

        self._set_step_enabled(2, False)
        self._set_step_enabled(3, False)
        self.right.setEnabled(False)
        self._on_kategori_changed(self.kategori_combo.currentText())

    def _step_label(self, text):
        lbl = QLabel(text); lbl.setObjectName("section_header")
        return lbl

    def _set_step_enabled(self, step, enabled):
        if step == 2:
            self.lbl_step2.setEnabled(enabled)
            self.filter_date.setEnabled(enabled)
        elif step == 3:
            self.lbl_step3.setEnabled(enabled)
            self.jadwal_table.setEnabled(enabled)

    # pilih rute, buka langkah berikutnya
    def _on_route_changed(self):
        valid = self.rute_combo.currentData() is not None
        self._set_step_enabled(2, valid)
        self._set_step_enabled(3, valid)
        self.selected_jadwal = None
        self.right.setEnabled(False)
        self.total_lbl.setText("Rp 0")
        if valid:
            self._load_jadwal()
        else:
            self.jadwal_table.setRowCount(0)
            self.jadwal_info.setText("Pilih rute & tanggal untuk melihat jadwal tersedia.")

    def _load_jadwal(self):
        rute_id = self.rute_combo.currentData()
        if rute_id is None:
            return
        self.selected_jadwal = None
        self.right.setEnabled(False)
        self.total_lbl.setText("Rp 0")

        tanggal = self.filter_date.date().toString("yyyy-MM-dd")
        self.jadwals = models.get_jadwal(tanggal=tanggal, rute_id=rute_id, status='aktif')

        self.jadwal_table.setRowCount(len(self.jadwals))
        for i, j in enumerate(self.jadwals):
            vals = [j['nama_kapal'], j['jam_berangkat'], str(j['sisa'])]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                if c == 0:
                    item.setData(Qt.UserRole, j['id'])
                self.jadwal_table.setItem(i, c, item)
            self.jadwal_table.setRowHeight(i, 40)

        if not self.jadwals:
            self.jadwal_info.setText("Tidak ada kapal tersedia untuk rute & tanggal ini.")
        else:
            self.jadwal_info.setText(
                f"{len(self.jadwals)} kapal tersedia. Pilih salah satu untuk mengisi data tiket."
            )

    def _on_jadwal_selected(self):
        rows = self.jadwal_table.selectionModel().selectedRows()
        if not rows:
            return
        idx = rows[0].row()
        if idx < len(self.jadwals):
            self.selected_jadwal = self.jadwals[idx]
            j = self.selected_jadwal
            self.jadwal_info.setText(
                f"Dipilih: {j['nama_kapal']}  |  Berangkat {j['jam_berangkat']}  |  "
                f"Sisa kursi: {j['sisa']}"
            )
            self.right.setEnabled(True)
            self._update_total()

    def _on_kategori_changed(self, kategori):
        is_pejalan = (kategori == "Pejalan Kaki")
        self.g_jumlah.setVisible(not is_pejalan)
        self.nopol_row_label.setVisible(not is_pejalan)
        self.nopol_input.setVisible(not is_pejalan)
        if is_pejalan:
            self.jml_input.setValue(1)
        self._update_total()

    def _update_total(self):
        if not self.selected_jadwal:
            self.total_lbl.setText("Rp 0")
            self._harga_satuan = 0; self._total_harga = 0
            return
        j = self.selected_jadwal
        kategori = self.kategori_combo.currentText()
        if kategori == "Pejalan Kaki":
            harga = j.get('harga_dewasa', 0)
            total = harga
        else:
            harga = j.get(self.HARGA_KEYS.get(kategori, 'harga_kendaraan_motor'), 0)
            total = harga
        self.total_lbl.setText(format_rupiah(total))
        self._harga_satuan = harga
        self._total_harga = total

    def _submit(self):
        if not self.selected_jadwal:
            QMessageBox.warning(self, "Pilih Jadwal", "Pilih kapal & jam keberangkatan terlebih dahulu."); return
        nama = self.nama_input.text().strip()
        no_id = self.id_input.text().strip()
        if not nama or not no_id:
            QMessageBox.warning(self, "Validasi", "Nama dan No. Identitas wajib diisi."); return

        kategori = self.kategori_combo.currentText()
        if kategori == "Pejalan Kaki":
            tipe = 'penumpang'; jenis_kend = None; no_pol = None; jml = 1
        else:
            tipe = 'kendaraan'; jenis_kend = kategori
            no_pol = self.nopol_input.text().strip()
            if not no_pol:
                QMessageBox.warning(self, "Validasi", "No. Polisi kendaraan wajib diisi."); return
            jml = self.jml_input.value()

        ok, msg, nomor = models.create_tiket(
            jadwal_id=self.selected_jadwal['id'],
            petugas_id=self.user['id'],
            nama_penumpang=nama,
            no_identitas=no_id,
            no_hp=self.hp_input.text().strip(),
            tipe_tiket=tipe,
            jenis_kendaraan=jenis_kend,
            no_polisi=no_pol,
            jumlah_penumpang=jml,
            harga_satuan=self._harga_satuan,
            total_harga=self._total_harga
        )
        if ok:
            reply = QMessageBox.question(
                self, "Tiket Berhasil Diterbitkan",
                f"Nomor Tiket: {nomor}\nTotal: {format_rupiah(self._total_harga)}\n\nCetak PDF tiket?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                dlg = TiketDetailDialog(self, nomor)
                dlg.exec()
            self._reset_form()
            self._load_jadwal()
        else:
            QMessageBox.critical(self, "Gagal", msg)

    def _reset_form(self):
        self.nama_input.clear(); self.id_input.clear(); self.hp_input.clear()
        self.jml_input.setValue(1); self.nopol_input.clear()
        self.kategori_combo.setCurrentIndex(0)
        self.selected_jadwal = None
        self.right.setEnabled(False)
        self.total_lbl.setText("Rp 0")
        self.jadwal_table.clearSelection()
