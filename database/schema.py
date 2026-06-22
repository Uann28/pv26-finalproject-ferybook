import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ferrybook.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # buat semua tabel
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS kapal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_kapal TEXT NOT NULL,
            kode_kapal TEXT UNIQUE NOT NULL,
            kapasitas INTEGER NOT NULL,
            keterangan TEXT,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS rute (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asal TEXT NOT NULL,
            tujuan TEXT NOT NULL,
            jarak_km REAL,
            durasi_menit INTEGER
        );

        CREATE TABLE IF NOT EXISTS jadwal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kapal_id INTEGER NOT NULL,
            rute_id INTEGER NOT NULL,
            tanggal TEXT NOT NULL,
            jam_berangkat TEXT NOT NULL,
            jam_tiba TEXT,
            harga_dewasa REAL NOT NULL,
            harga_kendaraan_motor REAL NOT NULL,
            harga_kendaraan_mobil REAL NOT NULL,
            harga_kendaraan_bus REAL NOT NULL,
            harga_kendaraan_truk REAL NOT NULL,
            kapasitas INTEGER NOT NULL,
            terisi INTEGER DEFAULT 0,
            status TEXT DEFAULT 'aktif',
            FOREIGN KEY (kapal_id) REFERENCES kapal(id),
            FOREIGN KEY (rute_id) REFERENCES rute(id)
        );

        CREATE TABLE IF NOT EXISTS tiket (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor_tiket TEXT UNIQUE NOT NULL,
            jadwal_id INTEGER NOT NULL,
            petugas_id INTEGER NOT NULL,
            nama_penumpang TEXT NOT NULL,
            no_identitas TEXT NOT NULL,
            no_hp TEXT,
            tipe_tiket TEXT NOT NULL,
            jenis_kendaraan TEXT,
            no_polisi TEXT,
            jumlah_penumpang INTEGER DEFAULT 1,
            harga_satuan REAL NOT NULL,
            total_harga REAL NOT NULL,
            tanggal_transaksi TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (jadwal_id) REFERENCES jadwal(id),
            FOREIGN KEY (petugas_id) REFERENCES users(id)
        );
    """)

    _seed(conn, cur)
    conn.commit()
    conn.close()


# isi data awal
def _seed(conn, cur):
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO users (username, password, full_name, role) VALUES (?,?,?,?)",
            [
                ("admin", hash_password("admin123"), "Super Administrator", "admin"),
                ("petugas1", hash_password("petugas123"), "Budi Santoso", "petugas"),
            ],
        )

    cur.execute("SELECT COUNT(*) FROM rute")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO rute (asal, tujuan, jarak_km, durasi_menit) VALUES (?,?,?,?)",
            [
                ("Kayangan", "Pototano", 15.0, 90),
                ("Pototano", "Kayangan", 15.0, 90),
                ("Lembar", "Padangbai", 40.0, 270),
                ("Ketapang", "Gilimanuk", 5.0, 45),
            ],
        )

    cur.execute("SELECT COUNT(*) FROM kapal")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO kapal (nama_kapal, kode_kapal, kapasitas, keterangan) VALUES (?,?,?,?)",
            [
                ("KM Nusa Tenggara I", "KM-001", 300, "Kapal Feri Utama"),
                ("KM Nusa Tenggara II", "KM-002", 250, "Kapal Feri Cadangan"),
                ("KM Bahari Express", "KM-003", 200, "Kapal Cepat"),
            ],
        )

    cur.execute("SELECT COUNT(*) FROM jadwal")
    if cur.fetchone()[0] == 0:
        from datetime import datetime, timedelta
        harga = (25000, 80000, 250000, 600000, 900000)
        jam_list = [("08:00", "09:30"), ("13:00", "14:30")]
        rute_ids = [r[0] for r in cur.execute("SELECT id FROM rute").fetchall()]
        kapal_rows = cur.execute("SELECT id, kapasitas FROM kapal").fetchall()
        for d in range(3):
            tgl = (datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d")
            for i, (kid, kap) in enumerate(kapal_rows):
                rid = rute_ids[i % len(rute_ids)]
                for brk, tiba in jam_list:
                    cur.execute(
                        "INSERT INTO jadwal (kapal_id, rute_id, tanggal, jam_berangkat, jam_tiba,"
                        " harga_dewasa, harga_kendaraan_motor, harga_kendaraan_mobil,"
                        " harga_kendaraan_bus, harga_kendaraan_truk, kapasitas)"
                        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (kid, rid, tgl, brk, tiba) + harga + (kap,),
                    )
