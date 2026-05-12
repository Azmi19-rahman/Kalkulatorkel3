import streamlit as st
import numpy as np
import sqlite3
import json

# ==============================================================================
# PROYEK: ISIS (INTEGRATED SMART INDUSTRIAL SYSTEM) WITH PERMANENT AI MEMORY
# Mencakup Materi Modul Bab I - VI + Database Fisik SQLite (Anti-Reset)
# ==============================================================================

# --- CONFIGURASI HALAMAN ---
st.set_page_config(page_title="Permanent AI Lab", page_icon="🧠", layout="wide")

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
            id INTEGER PRIMARY KEY, nama TEXT, stok INTEGER, kategori TEXT
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
        cursor.executemany("INSERT INTO gudang VALUES (?, ?, ?, ?)", data_awal)
        
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

# --- FUNGSI AMBIL & MODIFIKASI DATA SQLITE ---
def get_gudang_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama, stok, kategori FROM gudang")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "nama": r[1], "stok": r[2], "kategori": r[3]} for r in rows]

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
# 🛠️ LOGIKA MODUL DASAR (BAB I & VI)
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
# 🧠 LOGIKA AI CONTINUOUS LEARNING (MEMBACA DARI DATABASE FISIK)
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
            report_ai += "\n⚠️ **[AI ANOMALY DETECTION]:** AI mendeteksi anomali! Nilai sampel ini menyimpang dari pola historis tahunan yang tersimpan di database."
    else:
        report_ai += "ℹ️ **[AI MEMORY]:** Kurang data historis permanen. AI butuh minimal 3 sampel tersimpan untuk mengaktifkan deep learning."
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
st.title("🧠 ISIS v2: Integrated Smart Industrial System + Permanent AI Memory")
st.caption("Sistem Aplikasi Industri dengan Database Fisik SQLite - Data Tidak Akan Hilang Walau Website Ditutup")
st.markdown("---")

# Sidebar Batas Mutu
st.sidebar.header("⚙️ Batas Standar Mutu QC")
air_max = st.sidebar.number_input("Maks Kadar Air (%)", value=0.1500, step=0.0100, format="%.4f")
abu_max = st.sidebar.number_input("Maks Kadar Abu (%)", value=0.0500, step=0.0100, format="%.4f")
iod_min = st.sidebar.number_input("Min Bilangan Iod", value=50.0000, step=1.0000, format="%.4f")

tab_gudang, tab_kalkulator, tab_ai = st.tabs(["📦 1. Gudang (Stok Permanen)", "🧮 2. Lab & Analisis QC", "🧠 3. Otak AI & Knowledge"])

# --- TAB 1: GUDANG ---
with tab_gudang:
    st.header("📦 Kontrol Riil Inventaris Gudang")
    gudang_aktif = get_gudang_data()
    
    col_g1, col_g2 = st.columns([1.5, 1.2])
    with col_g1:
        gudang_tampil = []
        for b in gudang_aktif:
            status = "🔴 HABIS" if b["stok"] == 0 else ("🟡 KRITIS" if b["stok"] <= 15 else "🟢 AMAN")
            gudang_tampil.append({
                "Code (Biner)": desimal_ke_biner(b["id"]), "Nama Barang": b["nama"], "Kategori": b["kategori"], "Stok": b["stok"], "Status": status
            })
        st.table(gudang_tampil)
        
    with col_g2:
        st.subheader("🔄 Pengeluaran Barang")
        list_nama = [b["nama"] for b in gudang_aktif]
        pilih_b = st.selectbox("Pilih Barang:", list_nama)
        jml_ambil = st.number_input("Jumlah Ambil:", min_value=1, step=1)
        
        if st.button("Ambil Barang", type="primary"):
            for b in gudang_aktif:
                if b["nama"] == pilih_b:
                    if b["stok"] >= jml_ambil:
                        update_stok_gudang(pilih_b, b["stok"] - jml_ambil)
                        st.success("Berhasil! Stok di database langsung berkurang."); st.rerun()
                    else: st.error("Stok di database tidak mencukupi!")

# --- TAB 2: KALKULATOR ANALISIS QC ---
with tab_kalkulator:
    st.header("🧮 Laboratorium QC")
    sub_lab = st.selectbox("Metode Parameter:", ["Kadar Air (Oven)", "Kadar Abu (Tanur)", "Bilangan Iod (Iod-Hubl)"])
    col_l1, col_l2 = st.columns([1.4, 1.2])
    
    with col_l1:
        nama_smpl = st.text_input("Kode Sampel:", value="SMPL-01")
        if "Air" in sub_lab:
            w0 = st.number_input("W0 (g):", value=15.0000, format="%.4f")
            w1 = st.number_input("W1 (g):", value=20.0000, format="%.4f")
            w2 = st.number_input("W2 (g):", value=19.9920, format="%.4f")
            if st.button("Hitung & Tulis ke Database Harddisk"):
                hasil = hitung_kadar_air(w0, w1, w2)
                status = "PASSED" if hasil <= air_max else "REJECTED"
                biner = desimal_ke_biner(len(get_lab_logs()) + 1)
                save_lab_log(biner, nama_smpl, "Kadar Air", hasil, status)
                st.session_state["ai_persistent_rep"] = ai_statistical_learning({"id_biner": biner, "parameter": "Kadar Air", "nilai": hasil, "status": status})
                st.rerun()
                
        elif "Abu" in sub_lab:
            w0 = st.number_input("W0 (g):", value=20.0000, format="%.4f")
            w1 = st.number_input("W1 (g):", value=25.0000, format="%.4f")
            w2 = st.number_input("W2 (g):", value=20.0020, format="%.4f")
            if st.button("Hitung & Tulis ke Database Harddisk"):
                hasil = hitung_kadar_abu(w0, w1, w2)
                status = "PASSED" if hasil <= abu_max else "REJECTED"
                biner = desimal_ke_biner(len(get_lab_logs()) + 1)
                save_lab_log(biner, nama_smpl, "Kadar Abu", hasil, status)
                st.session_state["ai_persistent_rep"] = ai_statistical_learning({"id_biner": biner, "parameter": "Kadar Abu", "nilai": hasil, "status": status})
                st.rerun()

        elif "Iod" in sub_lab:
            vol = st.number_input("Volume (mL):", value=14.00, format="%.2f")
            norm = st.number_input("Normalitas (N):", value=0.1000, format="%.4f")
            berat = st.number_input("Berat Minyak (g):", value=0.5000, format="%.4f")
            if st.button("Hitung & Tulis ke Database Harddisk"):
                hasil = hitung_iod_hubl(vol, norm, berat)
                status = "PASSED" if hasil >= iod_min else "REJECTED"
                biner = desimal_ke_biner(len(get_lab_logs()) + 1)
                save_lab_log(biner, nama_smpl, "Iod-Hubl", hasil, status)
                st.session_state["ai_persistent_rep"] = ai_statistical_learning({"id_biner": biner, "parameter": "Iod-Hubl", "nilai": hasil, "status": status})
                st.rerun()

    with col_l2:
        st.subheader("🧐 Evaluasi Otak AI Permanen")
        if "ai_persistent_rep" in st.session_state: st.info(st.session_state["ai_persistent_rep"])
        else: st.caption("Lakukan kalkulasi untuk memicu analisis database oleh AI.")

    st.markdown("---")
    st.subheader("📋 Seluruh Riwayat yang Tersimpan di Harddisk Laptop")
    logs_tersimpan = get_lab_logs()
    if logs_tersimpan:
        st.table(logs_tersimpan)
        
        # Operasi Set (Bab V)
        set_semua = {d["sampel"] for d in logs_tersimpan}
        set_reject = {d["sampel"] for d in logs_tersimpan if d["status"] == "REJECTED"}
        st.write(f"🔴 **Set Produk Gagal (Tersimpan Fisik):** {set_reject if set_reject else 'Tidak ada'}")
        st.write(f"🟢 **Set Produk Lolos Sempurna:** {set_semua.difference(set_reject) if set_semua.difference(set_reject) else 'Tidak ada'}")
        
        if st.button("Format/Hapus Seluruh Database Log Lab"):
            clear_lab_logs(); st.rerun()
    else: st.caption("Belum ada data pengujian fisik di harddisk.")

# --- TAB 3: OTAK AI & PEMBELAJARAN ---
with tab_ai:
    st.header("🧠 Long-Term Memory AI")
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.subheader("📖 Ajarkan SOP/Aturan Baru Selamanya")
        topik = st.text_input("Topik Baru:").lower().strip()
        penjelasan = st.text_area("Penjelasan/Instruksi SOP:")
        if st.button("Suntikkan ke Memori Jangka Panjang AI"):
            if topik and penjelasan:
                save_ai_knowledge(topik, penjelasan)
                st.toast("AI berhasil mencatatnya ke dalam sel memori permanen!"); st.rerun()
                
        st.subheader("📚 Isi Otak AI di Harddisk Saat Ini")
        st.json(get_ai_knowledge())

    with col_a2:
        st.subheader("💬 Tes Ingatan AI Pasca Web Ditutup")
        chat_in = st.text_input("Tanya AI:")
        if chat_in:
            st.chat_message("assistant").write(ai_chatbot_brain(chat_in))
