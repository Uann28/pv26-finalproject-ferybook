from database import get_connection, hash_password
from datetime import datetime
import random
import string


# user
def login(username, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT id, username, full_name, role FROM users ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(username, password, full_name, role):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password, full_name, role) VALUES (?,?,?,?)",
            (username, hash_password(password), full_name, role)
        )
        conn.commit()
        return True, "User berhasil dibuat"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def update_user(uid, full_name, role, password=None):
    conn = get_connection()
    try:
        if password:
            conn.execute("UPDATE users SET full_name=?, role=?, password=? WHERE id=?",
                         (full_name, role, hash_password(password), uid))
        else:
            conn.execute("UPDATE users SET full_name=?, role=? WHERE id=?",
                         (full_name, role, uid))
        conn.commit()
        return True, "User berhasil diperbarui"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def delete_user(uid):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
        conn.commit()
        return True, "User dihapus"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()



# kapal
def get_all_kapal():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM kapal ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_kapal_aktif():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM kapal WHERE is_active=1 ORDER BY nama_kapal").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_kapal(nama, kode, kapasitas, ket=""):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO kapal (nama_kapal, kode_kapal, kapasitas, keterangan) VALUES (?,?,?,?)",
            (nama, kode, kapasitas, ket)
        )
        conn.commit()
        return True, "Kapal berhasil ditambahkan"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def update_kapal(kid, nama, kode, kapasitas, ket, is_active):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE kapal SET nama_kapal=?, kode_kapal=?, kapasitas=?, keterangan=?, is_active=? WHERE id=?",
            (nama, kode, kapasitas, ket, is_active, kid)
        )
        conn.commit()
        return True, "Kapal berhasil diperbarui"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def delete_kapal(kid):
    conn = get_connection()
    try:
        dipakai = conn.execute("SELECT COUNT(*) FROM jadwal WHERE kapal_id=?", (kid,)).fetchone()[0]
        if dipakai > 0:
            return False, f"Kapal tidak bisa dihapus, masih dipakai {dipakai} jadwal"
        conn.execute("DELETE FROM kapal WHERE id=?", (kid,))
        conn.commit()
        return True, "Kapal dihapus"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()



# rute
def get_all_rute():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rute ORDER BY asal").fetchall()
    conn.close()
    return [dict(r) for r in rows]



# jadwal
def get_jadwal(tanggal=None, rute_id=None, status=None):
    conn = get_connection()
    query = """
        SELECT j.*, k.nama_kapal, k.kode_kapal, r.asal, r.tujuan,
               (j.kapasitas - j.terisi) AS sisa
        FROM jadwal j
        JOIN kapal k ON j.kapal_id = k.id
        JOIN rute r ON j.rute_id = r.id
        WHERE 1=1
    """
    params = []
    if tanggal:
        query += " AND j.tanggal=?"; params.append(tanggal)
    if rute_id:
        query += " AND j.rute_id=?"; params.append(rute_id)
    if status:
        query += " AND j.status=?"; params.append(status)
    query += " ORDER BY j.tanggal, j.jam_berangkat"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_jadwal(kapal_id, rute_id, tanggal, jam_berangkat, jam_tiba,
                  harga_dewasa, harga_motor, harga_mobil, harga_bus, harga_truk, kapasitas):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO jadwal (kapal_id, rute_id, tanggal, jam_berangkat, jam_tiba,
                harga_dewasa, harga_kendaraan_motor, harga_kendaraan_mobil,
                harga_kendaraan_bus, harga_kendaraan_truk, kapasitas)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (kapal_id, rute_id, tanggal, jam_berangkat, jam_tiba,
              harga_dewasa, harga_motor, harga_mobil, harga_bus, harga_truk, kapasitas))
        conn.commit()
        return True, "Jadwal berhasil dibuat"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def update_jadwal(jid, kapal_id, rute_id, tanggal, jam_berangkat, jam_tiba,
                  harga_dewasa, harga_motor, harga_mobil, harga_bus, harga_truk, kapasitas):
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE jadwal SET kapal_id=?, rute_id=?, tanggal=?, jam_berangkat=?, jam_tiba=?,
                harga_dewasa=?, harga_kendaraan_motor=?, harga_kendaraan_mobil=?,
                harga_kendaraan_bus=?, harga_kendaraan_truk=?, kapasitas=?
            WHERE id=?
        """, (kapal_id, rute_id, tanggal, jam_berangkat, jam_tiba,
              harga_dewasa, harga_motor, harga_mobil, harga_bus, harga_truk, kapasitas, jid))
        conn.commit()
        return True, "Jadwal berhasil diperbarui"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def delete_jadwal(jid):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM jadwal WHERE id=?", (jid,))
        conn.commit()
        return True, "Jadwal dihapus"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()



# tiket
def generate_nomor_tiket():
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"FRY-{ts}-{rand}"


def create_tiket(jadwal_id, petugas_id, nama_penumpang, no_identitas, no_hp,
                 tipe_tiket, jenis_kendaraan, no_polisi, jumlah_penumpang,
                 harga_satuan, total_harga):
    conn = get_connection()
    try:
        nomor = generate_nomor_tiket()
        j = conn.execute("SELECT * FROM jadwal WHERE id=?", (jadwal_id,)).fetchone()
        if not j:
            return False, "Jadwal tidak ditemukan", None
        if j['status'] != 'aktif':
            return False, f"Jadwal berstatus '{j['status']}'", None
        # cek sisa kursi
        sisa = j['kapasitas'] - j['terisi']
        if jumlah_penumpang > sisa:
            return False, f"Kapasitas tidak cukup. Sisa kursi: {sisa}", None
        conn.execute("UPDATE jadwal SET terisi = terisi + ? WHERE id=?",
                     (jumlah_penumpang, jadwal_id))
        if j['terisi'] + jumlah_penumpang >= j['kapasitas']:
            conn.execute("UPDATE jadwal SET status='penuh' WHERE id=?", (jadwal_id,))
        conn.execute("""
            INSERT INTO tiket (nomor_tiket, jadwal_id, petugas_id, nama_penumpang, no_identitas,
                no_hp, tipe_tiket, jenis_kendaraan, no_polisi, jumlah_penumpang,
                harga_satuan, total_harga)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (nomor, jadwal_id, petugas_id, nama_penumpang, no_identitas,
              no_hp, tipe_tiket, jenis_kendaraan, no_polisi, jumlah_penumpang,
              harga_satuan, total_harga))
        conn.commit()
        return True, "Tiket berhasil diterbitkan", nomor
    except Exception as e:
        conn.rollback()
        return False, str(e), None
    finally:
        conn.close()


def get_tiket_by_nomor(nomor):
    conn = get_connection()
    row = conn.execute("""
        SELECT t.*, j.tanggal, j.jam_berangkat, k.nama_kapal, k.kode_kapal,
               r.asal, r.tujuan, u.full_name AS nama_petugas
        FROM tiket t
        JOIN jadwal j ON t.jadwal_id = j.id
        JOIN kapal k ON j.kapal_id = k.id
        JOIN rute r ON j.rute_id = r.id
        JOIN users u ON t.petugas_id = u.id
        WHERE t.nomor_tiket = ?
    """, (nomor,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_laporan_manifes(tanggal_awal, tanggal_akhir, rute_id=None):
    conn = get_connection()
    query = """
        SELECT t.*, j.tanggal, j.jam_berangkat, k.nama_kapal, r.asal, r.tujuan,
               u.full_name AS nama_petugas
        FROM tiket t
        JOIN jadwal j ON t.jadwal_id = j.id
        JOIN kapal k ON j.kapal_id = k.id
        JOIN rute r ON j.rute_id = r.id
        JOIN users u ON t.petugas_id = u.id
        WHERE j.tanggal BETWEEN ? AND ?
    """
    params = [tanggal_awal, tanggal_akhir]
    if rute_id:
        query += " AND j.rute_id=?"; params.append(rute_id)
    query += " ORDER BY j.tanggal, j.jam_berangkat"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]



# dashboard
def get_statistik_dashboard():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    stats = {}
    stats['total_jadwal_hari_ini'] = conn.execute(
        "SELECT COUNT(*) FROM jadwal WHERE tanggal=?", (today,)).fetchone()[0]
    stats['total_penumpang_hari_ini'] = conn.execute(
        "SELECT COALESCE(SUM(t.jumlah_penumpang),0) FROM tiket t "
        "JOIN jadwal j ON t.jadwal_id=j.id WHERE j.tanggal=?", (today,)).fetchone()[0]
    stats['total_tiket_hari_ini'] = conn.execute(
        "SELECT COUNT(*) FROM tiket t JOIN jadwal j ON t.jadwal_id=j.id WHERE j.tanggal=?",
        (today,)).fetchone()[0]
    stats['total_pendapatan_hari_ini'] = conn.execute(
        "SELECT COALESCE(SUM(t.total_harga),0) FROM tiket t "
        "JOIN jadwal j ON t.jadwal_id=j.id WHERE j.tanggal=?", (today,)).fetchone()[0]
    conn.close()
    return stats
