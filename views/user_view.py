from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QFrame, QDialog, QFormLayout, QLineEdit,
                               QComboBox, QMessageBox, QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt
import models

class UserDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Tambah User" if not user else "Edit User")
        self.setMinimumWidth(380)
        self._build_ui()
        if user: self._populate(user)

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(20,20,20,20); layout.setSpacing(12)
        title = QLabel("Data Pengguna"); title.setObjectName("section_header")
        layout.addWidget(title)
        form = QFormLayout(); form.setSpacing(10)
        self.username_input = QLineEdit(); self.username_input.setFixedHeight(36)
        self.nama_input = QLineEdit(); self.nama_input.setFixedHeight(36)
        self.pass_input = QLineEdit(); self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Kosongkan jika tidak diubah"); self.pass_input.setFixedHeight(36)
        self.role_combo = QComboBox(); self.role_combo.setFixedHeight(36)
        self.role_combo.addItems(["admin","petugas"])
        form.addRow("Username *", self.username_input)
        form.addRow("Nama Lengkap *", self.nama_input)
        form.addRow("Password", self.pass_input)
        form.addRow("Role *", self.role_combo)
        layout.addLayout(form)
        btns = QHBoxLayout(); btns.addStretch()
        cancel_btn = QPushButton("Batal"); cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Simpan"); save_btn.setObjectName("btn_primary"); save_btn.clicked.connect(self._save)
        btns.addWidget(cancel_btn); btns.addWidget(save_btn)
        layout.addLayout(btns)

    def _populate(self, u):
        self.username_input.setText(u['username']); self.username_input.setEnabled(False)
        self.nama_input.setText(u['full_name'])
        idx = self.role_combo.findText(u['role'])
        if idx >= 0: self.role_combo.setCurrentIndex(idx)

    def _save(self):
        username = self.username_input.text().strip()
        nama = self.nama_input.text().strip()
        if not nama: QMessageBox.warning(self, "Validasi", "Nama lengkap wajib diisi."); return
        if self.user:
            ok, msg = models.update_user(self.user['id'], nama, self.role_combo.currentText(),
                                          self.pass_input.text() or None)
        else:
            pw = self.pass_input.text()
            if not username or not pw:
                QMessageBox.warning(self, "Validasi", "Username dan password wajib diisi."); return
            ok, msg = models.create_user(username, pw, nama, self.role_combo.currentText())
        if ok: self.accept()
        else: QMessageBox.critical(self, "Error", msg)


class ManajemenUserView(QWidget):
    def __init__(self, user: dict):
        super().__init__()
        self.current_user = user
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(24,24,24,24); layout.setSpacing(16)
        hdr = QHBoxLayout()
        titles = QVBoxLayout()
        t = QLabel("Manajemen Pengguna"); t.setObjectName("page_title")
        s = QLabel("Kelola akun admin dan petugas loket"); s.setObjectName("page_subtitle")
        titles.addWidget(t); titles.addWidget(s); hdr.addLayout(titles); hdr.addStretch()
        add_btn = QPushButton("+ Tambah User"); add_btn.setObjectName("btn_primary")
        add_btn.setFixedHeight(36); add_btn.clicked.connect(self._add); hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID","Username","Nama Lengkap","Role","Aksi"])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 200)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.hideColumn(0)
        layout.addWidget(self.table)

    def _refresh(self):
        rows = models.get_all_users()
        self.table.setRowCount(len(rows))
        for i, u in enumerate(rows):
            vals = [str(u['id']), u['username'], u['full_name']]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, c, item)
            role_item = QTableWidgetItem(u['role'].capitalize())
            role_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, role_item)
            btn_f = QWidget(); btn_f.setObjectName("action_cell")
            btn_l = QHBoxLayout(btn_f); btn_l.setContentsMargins(2, 2, 2, 2); btn_l.setSpacing(6)
            edit_btn = QPushButton("Edit"); edit_btn.setObjectName("btn_warning")
            edit_btn.setFixedHeight(32); edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.clicked.connect(lambda _, row=u: self._edit(row))
            del_btn = QPushButton("Hapus"); del_btn.setObjectName("btn_danger")
            del_btn.setFixedHeight(32); del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.clicked.connect(lambda _, uid=u['id']: self._delete(uid))
            if u['id'] == self.current_user['id']: del_btn.setEnabled(False)
            btn_l.addWidget(edit_btn); btn_l.addWidget(del_btn)
            self.table.setCellWidget(i, 4, btn_f)
            self.table.setRowHeight(i, 54)

    def _add(self):
        dlg = UserDialog(self)
        if dlg.exec(): self._refresh()

    def _edit(self, u):
        dlg = UserDialog(self, u)
        if dlg.exec(): self._refresh()

    def _delete(self, uid):
        reply = QMessageBox.question(self, "Konfirmasi", "Hapus user ini?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = models.delete_user(uid)
            if ok: self._refresh()
            else: QMessageBox.critical(self, "Error", msg)
