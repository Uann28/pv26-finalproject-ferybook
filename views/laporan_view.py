from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QFrame, QHeaderView, QAbstractItemView,
                               QComboBox, QDateEdit, QLineEdit, QFileDialog,
                               QMessageBox, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt, QDate
import models
from utils import format_rupiah, cetak_laporan_manifes_pdf
from utils.theme_manager import style_calendar
import csv, os

class LaporanManifesView(QWidget):
    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self._data = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        titles = QVBoxLayout()
        t = QLabel("Laporan Manifes"); t.setObjectName("page_title")
        s = QLabel("Rekap data penumpang dan pendapatan operasional"); s.setObjectName("page_subtitle")
        titles.addWidget(t); titles.addWidget(s)
        hdr.addLayout(titles); hdr.addStretch()
        layout.addLayout(hdr)

        filter_frame = QFrame(); filter_frame.setObjectName("toolbar_frame")
        f_layout = QHBoxLayout(filter_frame); f_layout.setContentsMargins(12, 8, 12, 8); f_layout.setSpacing(10)
        f_layout.addWidget(QLabel("Dari:"))
        self.tgl_awal = QDateEdit(); self.tgl_awal.setCalendarPopup(True)
        self.tgl_awal.setDate(QDate.currentDate().addDays(-7)); self.tgl_awal.setFixedHeight(32)
        style_calendar(self.tgl_awal)
        f_layout.addWidget(self.tgl_awal)
        f_layout.addWidget(QLabel("Sampai:"))
        self.tgl_akhir = QDateEdit(); self.tgl_akhir.setCalendarPopup(True)
        self.tgl_akhir.setDate(QDate.currentDate()); self.tgl_akhir.setFixedHeight(32)
        style_calendar(self.tgl_akhir)
        f_layout.addWidget(self.tgl_akhir)
        f_layout.addWidget(QLabel("Rute:"))
        self.rute_combo = QComboBox(); self.rute_combo.setFixedHeight(32)
        self.rute_combo.addItem("Semua Rute", None)
        for r in models.get_all_rute():
            self.rute_combo.addItem(f"{r['asal']} → {r['tujuan']}", r['id'])
        f_layout.addWidget(self.rute_combo)
        cari_btn = QPushButton("Tampilkan"); cari_btn.setObjectName("btn_primary"); cari_btn.setFixedHeight(32)
        cari_btn.clicked.connect(self._refresh)
        f_layout.addWidget(cari_btn)
        f_layout.addStretch()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama / no. tiket / kapal...")
        self.search_input.setFixedHeight(32)
        self.search_input.setMinimumWidth(220)
        self.search_input.textChanged.connect(self._filter_tabel)
        f_layout.addWidget(self.search_input)
        layout.addWidget(filter_frame)

        sum_row = QHBoxLayout(); sum_row.setSpacing(12)
        self.sum_cards = {}
        for key, label, color in [
            ("tiket","Total Tiket","#00D4FF"),
            ("penumpang","Total Penumpang","#00FF99"),
            ("kendaraan","Total Kendaraan","#FFD700"),
            ("pendapatan","Total Pendapatan","#FF6B6B"),
        ]:
            card = QFrame(); card.setObjectName("stat_card")
            cl = QVBoxLayout(card); cl.setContentsMargins(14,14,14,14)
            val = QLabel("0"); val.setStyleSheet(f"color:{color};font-size:22px;font-weight:bold;background:transparent;")
            lbl = QLabel(label); lbl.setObjectName("stat_card_label"); lbl.setStyleSheet("background:transparent;")
            cl.addWidget(val); cl.addWidget(lbl)
            self.sum_cards[key] = val
            sum_row.addWidget(card)
        layout.addLayout(sum_row)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["No. Tiket","Nama","No. ID","Rute","Kapal","Tanggal","Jam","Tipe","Jml","Total"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        exp_bar = QHBoxLayout(); exp_bar.addStretch()
        csv_btn = QPushButton("Ekspor CSV"); csv_btn.setObjectName("btn_warning"); csv_btn.setFixedHeight(34)
        csv_btn.clicked.connect(self._export_csv)
        pdf_btn = QPushButton("Ekspor PDF"); pdf_btn.setObjectName("btn_primary"); pdf_btn.setFixedHeight(34)
        pdf_btn.clicked.connect(self._export_pdf)
        exp_bar.addWidget(csv_btn); exp_bar.addWidget(pdf_btn)
        layout.addLayout(exp_bar)

    def _refresh(self):
        tgl_awal = self.tgl_awal.date().toString("yyyy-MM-dd")
        tgl_akhir = self.tgl_akhir.date().toString("yyyy-MM-dd")
        rute_id = self.rute_combo.currentData()
        self._data = models.get_laporan_manifes(tgl_awal, tgl_akhir, rute_id)

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self._data))
        total_pend = 0; total_p = 0; total_k = 0
        for i, t in enumerate(self._data):
            vals = [t['nomor_tiket'], t['nama_penumpang'], t['no_identitas'],
                    f"{t['asal']}→{t['tujuan']}", t['nama_kapal'], t['tanggal'],
                    t['jam_berangkat'], t['tipe_tiket'].capitalize(),
                    str(t['jumlah_penumpang']), format_rupiah(t['total_harga'])]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, c, item)
            self.table.setRowHeight(i, 34)
            total_pend += t['total_harga']
            if t['tipe_tiket'] == 'penumpang': total_p += t['jumlah_penumpang']
            else: total_k += 1

        self.table.setSortingEnabled(True)
        self._filter_tabel(self.search_input.text())

        self.sum_cards['tiket'].setText(str(len(self._data)))
        self.sum_cards['penumpang'].setText(str(total_p))
        self.sum_cards['kendaraan'].setText(str(total_k))
        self.sum_cards['pendapatan'].setText(format_rupiah(total_pend))

    # cari di tabel
    def _filter_tabel(self, teks):
        teks = (teks or "").strip().lower()
        for r in range(self.table.rowCount()):
            cocok = False
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item and teks in item.text().lower():
                    cocok = True
                    break
            self.table.setRowHidden(r, bool(teks) and not cocok)

    def _export_csv(self):
        if not self._data:
            QMessageBox.warning(self, "Data Kosong", "Tidak ada data untuk diekspor."); return
        path, _ = QFileDialog.getSaveFileName(self, "Ekspor CSV", "manifes.csv", "CSV (*.csv)")
        if not path: return
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['nomor_tiket','nama_penumpang','no_identitas',
                    'asal','tujuan','nama_kapal','tanggal','jam_berangkat','tipe_tiket',
                    'jumlah_penumpang','total_harga'])
                writer.writeheader()
                for t in self._data:
                    writer.writerow({k: t.get(k,'') for k in writer.fieldnames})
            QMessageBox.information(self, "Sukses", f"Data diekspor ke:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _export_pdf(self):
        if not self._data:
            QMessageBox.warning(self, "Data Kosong", "Tidak ada data untuk diekspor."); return
        path, _ = QFileDialog.getSaveFileName(self, "Ekspor PDF", "manifes.pdf", "PDF (*.pdf)")
        if not path: return
        tgl_a = self.tgl_awal.date().toString("dd/MM/yyyy")
        tgl_b = self.tgl_akhir.date().toString("dd/MM/yyyy")
        judul = f"Periode: {tgl_a} s/d {tgl_b}"
        ok = cetak_laporan_manifes_pdf(self._data, judul, path)
        if ok:
            QMessageBox.information(self, "Sukses", f"Laporan PDF disimpan ke:\n{path}")
        else:
            QMessageBox.critical(self, "Error", "Gagal membuat PDF.")
