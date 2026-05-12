import streamlit as st
import numpy as np
import sqlite3

# ==============================================================================
# PROYEK: ISIS (INTEGRATED SMART INDUSTRIAL SYSTEM) WITH PERMANENT AI MEMORY
# Cakupan Penuh: Bab I - VI + Database Fisik SQLite + Fitur Tambah Barang Baru
# ==============================================================================

st.set_page_config(page_title="Permanent AI Lab & Warehouse", page_icon="🧠", layout="wide")

DB_FILE = "isis_ai_memory.db"

# ==============================================================================
# 🗃️ FUNGSI DATABASE SQLITE (UNTUK INGATAN PERMANEN)
# ==============================================================================
def init_db():
    """Membuat file database dan tabel jika belum ada di laptop."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Tabel Gudang
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gudang (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT UNIQUE, stok INTEGER, kategori TEXT
        )
    """)
    # Tabel Log Lab
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_log (
            id_biner TEXT, sampel TEXT, parameter TEXT, nilai REAL, status TEXT
        )
    """)
    # Tabel Memori AI
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_knowledge (
            topik TEXT PRIMARY KEY, penjelasan TEXT
        )
    """)
    
    # Isi data gudang awal jika tabel masih kosong
    cursor.execute("SELECT COUNT(*) FROM gudang")
    if cursor.fetchone()[0] == 0:
        data_awal = [
            (101, "Beaker Glass 250 mL", 45, "Alat Gelas"),
            (102, "Labu Ukur 100 mL", 12, "Alat Gelas"),
            (103, "Larutan Indikator PP", 8, "Bahan Kimia"),
            (104, "Kertas Saring Whatman 41", 85, "Consumables"),
            (105, "Buret 50 mL", 0, "Alat Gelas")
        ]
        cursor.executemany("INSERT INTO gudang (id, nama, stok, kategori) VALUES (?, ?, ?, ?)", data_awal)
        
    # Isi pengetahuan awal AI jika masih kosong
    cursor.execute("SELECT COUNT(*) FROM ai_knowledge")
    if cursor.fetchone()[0] == 0:
        knowledge_awal = [
            ("gravimetri", "Metode analisis kuantitatif berdasarkan pemisahan dan penimbangan berat konstan zat."),
            ("iod-hubl", "Penetapan bilangan iod untuk mengukur derajat ketidakjenuhan asam lemak/minyak."),
            ("glp", "Good Laboratory Practice - Standar organisasi laboratorium untuk menjamin mutu.")
        ]
        cursor.executemany("INSERT INTO ai_knowledge VALUES (?, ?)", knowledge_awal)
        
    conn.commit()
    conn.close()

# Jalankan inisialisasi database di awal program
init_db()

# --- FUNGSI DATABASES ---
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
        report_ai += f"📈 **Hasil Studi Database Fisik:** AI mengingat rata-rata nilai optimal masa lalu adalah **{rata_rata:.4f}**.\n"
        if data_baru["status"] == "PASSED" and data_baru["nilai"] > (rata_rata + 1.5 * std_dev):
            report_ai += "\n⚠️ **[AI ANOMALY DETECTION]:** AI mendeteksi anomali! Nilai sampel ini menyimpang dari pola historis harian."
    else:
        report_ai += "ℹ️ **[AI MEMORY]:** Kurang data historis permanen. AI butuh minimal 3 sampel tersimpan untuk membuat analisis prediktif."
    return report_ai

def ai_chatbot_brain(pertanyaan):
    pertanyaan = pertanyaan.lower()
    memori_pengetahuan = get_ai_knowledge()
    database_lab = get_lab_logs()
    
    for kunci in memori_pengetahuan:
        if kunci in pertanyaan:
            return f"🤖 **[AI PERMANENT MEMORY]:** Saya ingat dari database, tentang *{kunci}* adalah: {memori_pengetahuan[kunci]}"
            
    if "rekap" in pertanyaan or "total" in pertanyaan:
        if not database_lab: return "🤖 Database lab permanen kosong."
        total = len(database_lab)
        reject = sum(1 for d in database_lab if d["status"] == "REJECTED")
        return f"🤖 **[AI DATABASE REPORT]:** Total riwayat yang pernah tercatat di harddisk adalah {total} pengujian, dengan {reject} sampel reject."
        
    return "🤖 Pola teks belum ada di database otak saya. Ajarkan saya di form bawah agar saya ingat selamanya!"


# ==============================================================================
# 💻 TAMPILAN FRONTEND WEB STREAMLIT
# ==============================================================================
st.title("🧠 ISIS v2.1: Integrated Smart Industrial System + Permanent AI")
st.caption("Aplikasi Industri Modern - Menggunakan Database SQLite yang Aman dari Reset / Refresh")
st.markdown("---")

# Sidebar Batas Mutu Lab
st.sidebar.header("⚙️ Batas Standar Mutu QC")
air_max = st.sidebar.number_input("Maks Kadar Air (%)", value=0.1500, step=0.0100, format="%.4f")
abu_max = st.sidebar.number_input("Maks Kadar Abu (%)", value=0.0500, step=0.0100, format="%.4f")
iod_min = st.sidebar.number_input("Min Bilangan Iod", value=50.0000, step=1.0000, format="%.4f")

tab_gudang, tab_kalkulator, tab_ai = st.tabs(["📦 1. Gudang & Tambah Barang Baru", "🧮 2. Lab & Analisis QC", "🧠 3. Otak AI & Knowledge"])

# --- TAB 1: GUDANG TERINTEGRASI ---
with tab_gudang:
    st.header("📦 Kontrol Riil Inventaris Gudang")
    gudang_aktif = get_gudang_data()
    
    col_g1, col_g2 = st.columns([1.5, 1.2])
    with col_g1:
        st.subheader("📋 Daftar Stok di Rak")
        gudang_tampil = []
        for b in gudang_aktif:
            status = "🔴 HABIS" if b["stok"] == 0 else ("🟡 KRITIS" if b
