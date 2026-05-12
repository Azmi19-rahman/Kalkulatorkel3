import streamlit as st
import numpy as np
import sqlite3

# ==============================================================================
# PROYEK: ISIS (INTEGRATED SMART INDUSTRIAL SYSTEM) WITH PERMANENT AI MEMORY
# Versi 2.2: Sistem Auto-Fix Struktur Database + Cakupan Penuh Materi Bab I - VI
# ==============================================================================

st.set_page_config(page_title="Permanent AI Lab & Warehouse", page_icon="🧠", layout="wide")

DB_FILE = "isis_ai_memory.db"

# ==============================================================================
# 🗃️ FUNGSI DATABASE SQLITE (DENGAN FITUR AUTO-FIX KOLOM KATEGORI)
# ==============================================================================
def init_db():
    """Membuat database dan otomatis memperbaiki struktur jika ada kolom yang kurang."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Membuat tabel-tabel utama jika belum ada
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gudang (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT UNIQUE, stok INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_log (
            id_biner TEXT, sampel TEXT, parameter TEXT, nilai REAL, status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_knowledge (
            topik TEXT PRIMARY KEY, penjelasan TEXT
        )
    """)
    
    # 🔧 LOGIKA AUTO-FIX: Cek apakah kolom 'kategori' sudah ada di tabel gudang
    cursor.execute("PRAGMA table_info(gudang)")
    kolom_gudang = [info[1] for info in cursor.fetchall()]
    
    if "kategori" not in kolom_gudang:
        # Jika kolom kategori belum ada (database versi lama), suntikkan kolom baru otomatis
        cursor.execute("ALTER TABLE gudang ADD COLUMN kategori TEXT DEFAULT 'Alat Gelas'")
        conn.commit()

    # 2. Isi data gudang standar jika tabel masih kosong
    cursor.execute("SELECT COUNT(*) FROM gudang")
    if cursor.fetchone()[0] == 0:
        data_awal = [
            ("Beaker Glass 250 mL", 45, "Alat Gelas"),
            ("Labu Ukur 100 mL", 12, "Alat Gelas"),
            ("Larutan Indikator PP", 8, "Bahan Kimia"),
            ("Kertas Saring Whatman 41", 85, "Consumables"),
            ("Buret 50 mL", 0, "Alat Gelas")
        ]
        cursor.executemany("INSERT INTO gudang (nama, stok, kategori) VALUES (?, ?, ?)", data_awal)
        
    # 3. Isi pengetahuan awal AI jika masih kosong
    cursor.execute("SELECT COUNT(*) FROM ai_knowledge")
    if cursor.fetchone()[0] == 0:
        knowledge_awal = [
            ("gravimetri", "Metode analisis kuantitatif berdasarkan penimbangan berat konstan zat."),
            ("iod-hubl", "Penetapan bilangan iod untuk mengukur derajat ketidakjenuhan asam lemak/minyak."),
            ("glp", "Good Laboratory Practice - Standar organisasi laboratorium untuk menjamin mutu.")
        ]
        cursor.executemany("INSERT INTO ai_knowledge VALUES (?, ?)", knowledge_awal)
        
    conn.commit()
    conn.close()

# Jalankan inisialisasi dan perbaikan otomatis database di awal program
init_db()

# --- FUNGSI QUERY DATABASE ---
def get_gudang_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama, stok, kategori FROM gudang")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "nama": r[1], "stok": r[2], "kategori": r[3]} for r in rows]

def tambah_barang_baru_db(nama, stok, kategori):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO gudang (nama, stok, kategori) VALUES (?, ?, ?)", (nama, stok, kategori))
        conn.commit()
        conn.close()
        return True, f"Berhasil menambahkan '{nama}' sebagai barang baru di gudang!"
    except sqlite3.IntegrityError:
        return False, f"Gagal! Barang dengan nama '{nama}' sudah terdaftar di gudang."

def update_stok_gudang(nama, jumlah):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE gudang SET stok = ? WHERE nama = ?", (jumlah, nama))
    conn.commit()
    conn.close()

def save_lab_log(id_biner, sampel, parameter, nilai, status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lab_log VALUES (?, ?, ?, ?, ?)", (id_biner, sampel, parameter, nilai, status))
    conn.commit()
    conn.close()

def get_lab_logs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id_biner, sampel, parameter, nilai, status FROM lab_log")
    rows = cursor.fetchall()
    conn.close()
    return [{"id_biner": r[0], "sampel": r[1], "parameter": r[2], "nilai": r[3], "status": r[4]} for r in rows]

def clear_lab_logs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lab_log")
    conn.commit()
    conn.close()

def save_ai_knowledge(topik, penjelasan):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO ai_knowledge VALUES (?, ?)", (topik, penjelasan))
    conn.commit()
    conn.close()

def get_ai_knowledge():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT topik, penjelasan FROM ai_knowledge")
    rows = cursor.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


# ==============================================================================
# 🛠️ LOGIKA RUMUS DASAR MODUL (BAB I & VI)
# ==============================================================================
def desimal_ke_biner(desimal):
    if desimal == 0: return "0"
    biner = ""
    temp = desimal
    while temp > 0:
        biner = str(temp % 2) + biner
        temp = temp // 2
    return biner

def hitung_kadar_air(w0, w1, w2):
    try: return round(((w1 - w2) / (w1 - w0)) * 100, 4)
    except ZeroDivisionError: return None

def hitung_kadar_abu(w0, w1, w2):
    try: return round(((w2 - w0) / (w1 - w0)) * 100, 4)
    except ZeroDivisionError: return None

def hitung_iod_hubl(vol, norm, berat):
    try: return round((vol * norm * 12.69) / berat, 4)
    except ZeroDivisionError: return None


# ==============================================================================
# 🧠 LOGIKA AI CONTINUOUS LEARNING
# ==============================================================================
def ai_statistical_learning(data_baru):
    logs = get_lab_logs()
    data_sejenis = [d["nilai"] for d in logs if d["parameter"] == data_baru["parameter"] and d["status"] == "PASSED"]
    
    report_ai = f"🧠 **[AI PERMANENT ANALYTICS]:** Menstabilkan ingatan sampel `{data_baru['id_biner']}` ke harddisk.\n\n"
    if len(data_sejenis) >= 3:
        rata_rata = np.mean(data_sejenis)
        std_dev = np.std(data_sejenis)
        report_ai += f"📈 **Hasil Studi Database Fisik:**
