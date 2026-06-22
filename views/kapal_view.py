from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QDialog, QFormLayout, QLineEdit,
                               QSpinBox, QTextEdit, QMessageBox, QCheckBox,
                               QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import models


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


def _status_cell(is_active: bool) -> QWidget:
    w = QWidget()
    w.setObjectName("status_cell")
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    badge = QLabel("Aktif" if is_active else "Non-aktif")
    badge.setObjectName("badge_success" if is_active else "badge_danger")
    badge.setAlignment(Qt.AlignCenter)
    lay.addStretch()
    lay.addWidget(badge)
    lay.addStretch()
    return w


class KapalDialog(QDialog):
    def __init__(self, parent=None, kapal=None):
        super().__init__(parent)
        self.kapal = kapal
        self.setWindowTitle("Tambah Kapal" if not kapal else "Edit Kapal")
        self.setMinimumWidth(420)
        self._build_ui()
        if kapal:
            self._populate(kapal)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Data Kapal")
        title.setObjectName("section_header")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        self.nama_input = QLineEdit(); self.nama_input.setFixedHeight(36)
        self.kode_input = QLineEdit(); self.kode_input.setFixedHeight(36)
        self.kap_input = QSpinBox(); self.kap_input.setRange(1, 9999); self.kap_input.setSuffix(" kursi"); self.kap_input.setFixedHeight(36)
        self.ket_input = QTextEdit(); self.ket_input.setMaximumHeight(70)
        self.aktif_check = QCheckBox("Kapal Aktif"); self.aktif_check.setChecked(True)

        form.addRow("Nama Kapal *", self.nama_input)
        form.addRow("Kode Kapal *", self.kode_input)
        form.addRow("Kapasitas *", self.kap_input)
        form.addRow("Keterangan", self.ket_input)
        form.addRow("", self.aktif_check)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel_btn = QPushButton("Batal")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Simpan")
        save_btn.setObjectName("btn_primary")
        save_btn.clicked.connect(self._save)
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

    def _populate(self, k):
        self.nama_input.setText(k['nama_kapal'])
        self.kode_input.setText(k['kode_kapal'])
        self.kap_input.setValue(k['kapasitas'])
        self.ket_input.setPlainText(k.get('keterangan', '') or '')
        self.aktif_check.setChecked(bool(k.get('is_active', 1)))

    def _save(self):
        nama = self.nama_input.text().strip()
        kode = self.kode_input.text().strip()
        if not nama or not kode:
            QMessageBox.warning(self, "Validasi", "Nama dan kode kapal wajib diisi.")
            return
        if self.kapal:
            ok, msg = models.update_kapal(
                self.kapal['id'], nama, kode, self.kap_input.value(),
                self.ket_input.toPlainText(),
                1 if self.aktif_check.isChecked() else 0
            )
        else:
            ok, msg = models.create_kapal(
                nama, kode, self.kap_input.value(), self.ket_input.toPlainText()
            )
        if ok:
            self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)


class KelolaDKapalView(QWidget):
    COLS = ["Nama Kapal", "Kode", "Kapasitas", "Status", "Aksi"]

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        titles = QVBoxLayout(); titles.setSpacing(2)
        t = QLabel("Data Kapal")
        t.setObjectName("page_title")
        s = QLabel("Manajemen armada kapal feri")
        s.setObjectName("page_subtitle")
        titles.addWidget(t); titles.addWidget(s)
        hdr.addLayout(titles); hdr.addStretch()
        add_btn = QPushButton("Tambah Kapal")
        add_btn.setObjectName("btn_primary")
        add_btn.setFixedHeight(36)
        add_btn.clicked.connect(self._add)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.Fixed);   self.table.setColumnWidth(1, 100)
        hh.setSectionResizeMode(2, QHeaderView.Fixed);   self.table.setColumnWidth(2, 130)
        hh.setSectionResizeMode(3, QHeaderView.Fixed);   self.table.setColumnWidth(3, 110)
        hh.setSectionResizeMode(4, QHeaderView.Fixed);   self.table.setColumnWidth(4, 180)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def _refresh(self):
        rows = models.get_all_kapal()
        self.table.clearSpans()

        if not rows:
            self.table.setRowCount(1)
            empty = QTableWidgetItem("Belum ada kapal. Klik \"Tambah Kapal\" untuk menambahkan.")
            empty.setTextAlignment(Qt.AlignCenter)
            empty.setForeground(QColor("#888888"))
            self.table.setSpan(0, 0, 1, len(self.COLS))
            self.table.setItem(0, 0, empty)
            self.table.setRowHeight(0, 60)
            return

        self.table.setRowCount(len(rows))
        for i, k in enumerate(rows):
            nama_item = QTableWidgetItem(k['nama_kapal']); nama_item.setTextAlignment(Qt.AlignCenter)
            kode_item = QTableWidgetItem(k['kode_kapal']); kode_item.setTextAlignment(Qt.AlignCenter)
            kap_item = QTableWidgetItem(f"{k['kapasitas']} kursi"); kap_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, nama_item)
            self.table.setItem(i, 1, kode_item)
            self.table.setItem(i, 2, kap_item)

            self.table.setCellWidget(i, 3, _status_cell(bool(k['is_active'])))
            self.table.setCellWidget(i, 4, _action_cell(
                lambda _, row=k: self._edit(row),
                lambda _, kid=k['id']: self._delete(kid),
            ))
            self.table.setRowHeight(i, 54)

    def _add(self):
        dlg = KapalDialog(self)
        if dlg.exec():
            self._refresh()

    def _edit(self, kapal):
        dlg = KapalDialog(self, kapal)
        if dlg.exec():
            self._refresh()

    def _delete(self, kid):
        reply = QMessageBox.question(self, "Konfirmasi", "Hapus kapal ini?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = models.delete_kapal(kid)
            if ok:
                self._refresh()
            else:
                QMessageBox.critical(self, "Error", msg)
