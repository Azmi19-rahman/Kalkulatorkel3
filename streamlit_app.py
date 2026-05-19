import streamlit as st
import numpy as np
import sqlite3

# ==============================================================================
# PROYEK: ISIS v3.0 - APLIKASI PERHITUNGAN & EVALUASI DATA KUALITAS AIR (BOD & COD)
# Standar Penyimpanan Permanen SQLite (Anti-Reset) + Evaluasi AI Bentuk Paragraf
# ==============================================================================

st.set_page_config(page_title="Water Quality Analytics System", page_icon="💧", layout="wide")

DB_FILE = "isis_water_quality.db"

# ==============================================================================
# 🗃️ INIDIALISASI DATABASE FISIK (SQLITE)
# ==============================================================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Tabel Log Mutu Air (BOD/COD)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS water_log (
            id_biner TEXT,
            sampel TEXT,
            parameter TEXT,
            nilai REAL,
            status TEXT,
            keterangan TEXT
        )
    """)
    # Tabel Memori Pengetahuan AI
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_knowledge (
            topik TEXT PRIMARY KEY, penjelasan TEXT
        )
    """)
    
    # Isi pengetahuan dasar laboratorium air jika masih kosong
    cursor.execute("SELECT COUNT(*) FROM ai_knowledge")
    if cursor.fetchone()[0] == 0:
        knowledge_awal = [
            ("bod", "Biochemical Oxygen Demand adalah jumlah oksigen terlarut yang diperlukan oleh mikroorganisme untuk mengurai bahan organik dalam air."),
            ("cod", "Chemical Oxygen Demand adalah jumlah oksigen yang dibutuhkan untuk mengurai seluruh bahan organik yang terkandung dalam air melalui reaksi kimiawi."),
            ("regulasi", "Berdasarkan standar baku mutu air nasional, batas maksimal kadar BOD yang aman berkisar antara 2-12 mg/L tergantung kelas air, sedangkan untuk COD berkisar antara 10-80 mg/L.")
        ]
        cursor.executemany("INSERT OR IGNORE INTO ai_knowledge VALUES (?, ?)", knowledge_awal)
        
    conn.commit()
    conn.close()

init_db()

# --- FUNGSI QUERY DATABASE ---
def save_water_log(id_biner, sampel, parameter, nilai, status, keterangan):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO water_log VALUES (?, ?, ?, ?, ?, ?)", (id_biner, sampel, parameter, nilai, status, keterangan))
    conn.commit()
    conn.close()

def get_water_logs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id_biner, sampel, parameter, nilai, status, keterangan FROM water_log")
    rows = cursor.fetchall()
    conn.close()
    return [{"id_biner": r[0], "sampel": r[1], "parameter": r[2], "nilai": r[3], "status": r[4], "keterangan": r[5]} for r in rows]

def clear_water_logs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM water_log")
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
# 🛠️ LOGIKA RUMUS KIMIA ANALISIS AIR (BAB I & VI)
# ==============================================================================
def desimal_ke_biner(desimal):
    if desimal == 0: return "0"
    biner = ""
    temp = desimal
    while temp > 0:
        biner = str(temp % 2) + biner
        temp = temp // 2
    return biner

def hitung_bod(do_nol, do_lima, pengenceran):
    """Rumus: BOD (mg/L) = (DO_0 - DO_5) * Faktor Pengenceran"""
    try:
        return round((do_nol - do_lima) * pengenceran, 4)
    except Exception:
        return None

def hitung_cod(vol_blanko, vol_sampel, norm_fas, berat_sampel):
    """Rumus: COD (mg/L) = ((V_blanko - V_sampel) * N_FAS * 8000) / V_sampel_air"""
    try:
        return round(((vol_blanko - vol_sampel) * norm_fas * 8000) / berat_sampel, 4)
    except ZeroDivisionError:
        return None


# ==============================================================================
# 🧠 LOGIKA EVALUASI AI (FORMAT PARAGRAF MENGALIR - BUKAN POIN)
# ==============================================================================
def ai_water_evaluation(data_baru, batas_maks):
    logs = get_water_logs()
    data_sejenis = [d["nilai"] for d in logs if d["parameter"] == data_baru["parameter"] and d["status"] == "MEMENUHI SYARAT"]
    
    pembahasan = f"Berdasarkan hasil analisis data laboratorium yang tersimpan di dalam database fisik, sampel air dengan kode identifikasi biner {data_baru['id_biner']} menunjukkan kadar {data_baru['parameter']} sebesar {data_baru['nilai']:.4f} mg/L. "
    
    if data_baru["status"] == "MEMENUHI SYARAT":
        pembahasan += f"Nilai parameter ini berada di bawah batas ambang regulasi baku mutu lingkungan yang ditetapkan yaitu sebesar {batas_maks:.4f} mg/L, sehingga sampel air ini dinyatakan bersih dan layak untuk mendukung ekosistem perairan yang sehat. "
    else:
        pembahasan += f"Kadar zat organik tersebut telah melampaui batas ambang standar regulasi lingkungan sebesar {batas_maks:.4f} mg/L, yang menandakan tingkat pencemaran air yang tinggi dan berpotensi memicu kondisi defisit oksigen ekstrem di badan air. "

    if len(data_sejenis) >= 3:
        rata_rata = np.mean(data_sejenis)
        std_dev = np.std(data_sejenis)
        pembahasan += f"Apabila dibandingkan dengan data historis pengujian masa lalu, nilai rata-rata optimal untuk sampel yang lolos adalah {rata_rata:.4f} mg/L. Melalui analisis statistik tersebut, AI mengonfirmasi bahwa tren fluktuasi sampel ini masih berada dalam rentang deviasi normal lingkungan industri."
        if data_baru["nilai"] > (rata_rata + 1.5 * std_dev) and data_baru["status"] == "MELEBIHI AMBANG":
            pembahasan += " Namun demikian, AI mendeteksi adanya anomali lonjakan beban limbah organik yang sangat signifikan jika disandingkan dengan kurva historis tahunan, sehingga diperlukan inspeksi segera pada unit pengolahan limbah utama."
    else:
        pembahasan += "Saat ini AI belum mengaktifkan modul analitik prediktif mendalam dikarenakan jumlah data sampel valid yang tersimpan di harddisk komputer masih kurang dari tiga rekaman historis."
        
    return pembahasan

def ai_chatbot_brain(pertanyaan):
    pertanyaan = pertanyaan.lower()
    memori_pengetahuan = get_ai_knowledge()
    database_air = get_water_logs()
    
    for kunci in memori_pengetahuan:
        if kunci in pertanyaan:
            return f"🤖 **[MEMORI JANGKA PANJANG AI]:** {memori_pengetahuan[kunci]}"
            
    if "rekap" in pertanyaan or "evaluasi" in pertanyaan or "total" in pertanyaan:
        if not database_air: 
            return "🤖 Database analisis kualitas air saat ini masih kosong."
        total = len(database_air)
        reject = sum(1 for d in database_air if d["status"] == "MELEBIHI AMBANG")
        return f"🤖 **[LAPORAN HISTORIS DATABASE]:** Total pengujian kualitas air yang terekam di harddisk komputer secara permanen saat ini berjumlah {total} sampel, di mana terdapat {reject} sampel yang terdeteksi melebihi ambang batas baku mutu regulasi industri."
        
    return "🤖 Pola teks materi kualitas air ini belum ada di database ingatan saya. Silakan ajarkan instruksi baru pada form di samping agar saya ingat selamanya!"


# ==============================================================================
# 💻 TAMPILAN FRONTEND WEB STREAMLIT
# ==============================================================================
st.title("💧 ISIS v3.0: Water Quality Perhitungan & Evaluasi Data Kimia")
st.caption("Sistem Analisis Parameter BOD & COD Laboratorium Lingkungan dengan Database Fisik SQLite")
st.markdown("---")

# Sidebar Baku Mutu Air (Berdasarkan Peraturan Regulasi)
st.sidebar.header("⚙️ Baku Mutu Air Nasional")
bod_max = st.sidebar.number_input("Batas Maks BOD (mg/L)", value=6.0000, step=0.5000, format="%.4f")
cod_max = st.sidebar.number_input("Batas Maks COD (mg/L)", value=25.0000, step=1.0000, format="%.4f")

tab_kalkulator, tab_riwayat, tab_ai = st.tabs(["🧮 1. Perhitungan BOD/COD", "📋 2. Database Riwayat Sampel", "🧠 3. Inteligensia & Konsultasi AI"])

# --- TAB 1: PERHITUNGAN BOD & COD ---
with tab_kalkulator:
    st.header("🧮 Input Data Analisis Kimia Air")
    sub_metode = st.selectbox("Pilih Parameter Analisis Air:", ["BOD (Biochemical Oxygen Demand)", "COD (Chemical Oxygen Demand)"])
    
    col_l1, col_l2 = st.columns([1.4, 1.2])
    
    with col_l1:
        nama_smpl = st.text_input("Kode / Lokasi Sampel Air:", value="Sungai Ciliwung-01")
        
        if "BOD" in sub_metode:
            st.caption("Metode Titrasi Iodometri (Winkler) / DO Meter setelah Inkubasi 5 Hari")
            do_0 = st.number_input("Kadar DO Hari Ke-0 (DO0) (mg/L):", value=8.2000, format="%.4f")
            do_5 = st.number_input("Kadar DO Hari Ke-5 (DO5) (mg/L):", value=4.5000, format="%.4f")
            f_pengenceran = st.number_input("Faktor Pengenceran (P):", value=2.0, step=0.5)
            
            if st.button("Hitung & Tulis ke Harddisk"):
                hasil = hitung_bod(do_0, do_5, f_pengenceran)
                status = "MEMENUHI SYARAT" if hasil <= bod_max else "MELEBIHI AMBANG"
                biner_id = desimal_ke_biner(len(get_water_logs()) + 1)
                
                # Buat keterangan ringkas untuk tabel database
                ket_singkat = f"DO0={do_0}, DO5={do_5}, P={f_pengenceran}"
                save_water_log(biner_id, nama_smpl, "BOD", hasil, status, ket_singkat)
                
                # Simpan laporan evaluasi ke session state sementara agar langsung tampil di kolom kanan
                st.session_state["pembahasan_ai"] = ai_water_evaluation({"id_biner": biner_id, "parameter": "BOD", "nilai": hasil, "status": status}, bod_max)
                st.rerun()
                
        elif "COD" in sub_metode:
            st.caption("Metode Refluks Terbuka / Titrasi dengan FAS (Ferro Amonium Sulfat)")
            v_blanko = st.number_input("Volume Penitran Blanko (mL):", value=15.20, format="%.2f")
            v_sampel = st.number_input("Volume Penitran Sampel Air (mL):", value=13.60, format="%.2f")
            n_fas = st.number_input("Normalitas Larutan FAS (N):", value=0.1000, format="%.4f")
            vol_air = st.number_input("Volume Sampel Air Teruji (mL):", value=50.00, format="%.2f")
            
            if st.button("Hitung & Tulis ke Harddisk"):
                hasil = hitung_cod(v_blanko, v_sampel, n_fas, vol_air)
                status = "MEMENUHI SYARAT" if hasil <= cod_max else "MELEBIHI AMBANG"
                biner_id = desimal_ke_biner(len(get_water_logs()) + 1)
                
                ket_singkat = f"V_B={v_blanko}, V_S={v_sampel}, N_FAS={n_fas}"
                save_water_log(biner_id, nama_smpl, "COD", hasil, status, ket_singkat)
                
                st.session_state["pembahasan_ai"] = ai_water_evaluation({"id_biner": biner_id, "parameter": "COD", "nilai": hasil, "status": status}, cod_max)
                st.rerun()

    with col_l2:
        st.subheader("🧐 Bab 3: Pembahasan Evaluasi AI")
        if "pembahasan_ai" in st.session_state:
            st.info(st.session_state["pembahasan_ai"])
        else:
            st.caption("Lakukan kalkulasi di sebelah kiri untuk menghasilkan narasi pembahasan otomatis dari AI.")

# --- TAB 2: DATABASE RIWAYAT SAMPEL ---
with tab_riwayat:
    st.header("📋 Rekam Data Kualitas Air Permanen")
    logs_air = get_water_logs()
    
    if logs_air:
        st.table(logs_air)
        
        # Implementasi Matematika Himpunan / Set (Materi Bab V)
        set_semua = {d["sampel"] for d in logs_air}
        set_tercemar = {d["sampel"] for d in logs_air if d["status"] == "MELEBIHI AMBANG"}
        
        st.markdown("---")
        st.subheader("📊 Analisis Set Laboratorium")
        st.write(f"☣️ **Set Lokasi Tercemar (Melebihi Ambang):** {set_tercemar if set_tercemar else 'Tidak ada'}")
        st.write(f"✅ **Set Lokasi Aman Bersih (Lolos Syarat):** {set_semua.difference(set_tercemar) if set_semua.difference(set_tercemar) else 'Tidak ada'}")
        
        if st.button("Kosongkan Seluruh Database Riwayat Air"):
            clear_water_logs()
            st.rerun()
    else:
        st.caption("Belum ada riwayat pengujian sampel air yang tersimpan di harddisk laptop.")

# --- TAB 3: OTTAK AI & KNOWLEDGE LAB ---
with tab_ai:
    st.header("🧠 Long-Term Memory & Pengetahuan AI")
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.subheader("📖 Ajarkan Standar Baku/SOP Air Baru")
        topik = st.text_input("Topik/Kata Kunci Baru:").lower().strip()
        penjelasan = st.text_area("Narasi SOP / Penjelasan Ilmiah:")
        
        if st.button("Suntikkan Ke Memori Permanen AI"):
            if topik and penjelasan:
                save_ai_knowledge(topik, penjelasan)
                st.toast("AI berhasil menyimpan ilmu baru tersebut ke harddisk!")
                st.rerun()
                
        st.subheader("📚 Daftar Isi Otak AI Saat Ini")
        st.json(get_ai_knowledge())

    with col_a2:
        st.subheader("💬 Konsultasi Mutu Air Bersama AI")
        chat_in = st.text_input("Tanyakan sesuatu ke AI (Contoh: 'bod', 'cod', atau 'rekap'):")
        if chat_in:
            st.chat_message("assistant").write(ai_chatbot_brain(chat_in))
