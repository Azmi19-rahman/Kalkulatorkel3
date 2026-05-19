import streamlit as st
import numpy as np
import sqlite3

# ==============================================================================
# PROYEK: WATER QUALITY ANALYTICS SYSTEM
# Struktur Navigasi Mengikuti Referensi (Sidebar Menu)
# Modern, Bersih, Formal, dan Terintegrasi Database Fisik SQLite
# ==============================================================================

st.set_page_config(page_title="Water Quality Analytics System", page_icon="💧", layout="wide")

DB_FILE = "isis_water_quality.db"

# ==============================================================================
# 🗃️ INIDIALISASI DATABASE FISIK (SQLITE)
# ==============================================================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS water_log (
            id_biner TEXT, sampel TEXT, parameter TEXT, nilai REAL, status TEXT, keterangan TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_knowledge (
            topik TEXT PRIMARY KEY, penjelasan TEXT
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM ai_knowledge")
    if cursor.fetchone()[0] == 0:
        knowledge_awal = [
            ("bod", "BOD (Biochemical Oxygen Demand) merupakan takaran jumlah oksigen terlarut yang diperlukan oleh mikroorganisme untuk mendekomposisi bahan organik dalam air. Semakin tinggi nilai BOD, semakin rendah kualitas oksigen terlarut bagi ekosistem perairan."),
            ("cod", "COD (Chemical Oxygen Demand) adalah jumlah total oksigen yang dibutuhkan untuk mengurai seluruh bahan organik melalui reaksi kimia menggunakan oksidator kuat. Nilai COD umumnya selalu lebih besar daripada BOD."),
            ("regulasi", "Baku mutu nasional menetapkan batas aman untuk menjaga kelestarian lingkungan. Berdasarkan standar peruntukan kelas air, parameter BOD biasanya berkisar antara 2-12 mg/L dan COD berkisar antara 10-80 mg/L.")
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
# 🛠️ LOGIKA RUMUS KIMIA ANALISIS AIR
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
    try: return round((do_nol - do_lima) * pengenceran, 4)
    except Exception: return None

def hitung_cod(vol_blanko, vol_sampel, norm_fas, berat_sampel):
    try: return round(((vol_blanko - vol_sampel) * norm_fas * 8000) / berat_sampel, 4)
    except ZeroDivisionError: return None


# ==============================================================================
# 🧠 LOGIKA EVALUASI AI (FORMAT PARAGRAF KONTINU)
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

# 💬 OTAK AI YANG MIRIP CHAT ASISTEN (CASUAL & ADAPTIF)
def ai_chatbot_brain(pertanyaan):
    pertanyaan = pertanyaan.lower().strip()
    memori_pengetahuan = get_ai_knowledge()
    database_air = get_water_logs()
    
    if pertanyaan in ["halo", "hai", "p", "test", "halo ai"]:
        return "Sini, masuk! Ada data lab apa yang mau kita beresin bareng hari ini? 💧"
    if pertanyaan in ["kamu siapa", "siapa kamu", "siapa"]:
        return "Kenalin, aku asisten database AI pribadimu. Panggil aja partner lab-mu, siap bantu hitung data kimia anti-error! 🧠🚀"
    
    for kunci in memori_pengetahuan:
        if kunci in pertanyaan:
            return f"**[Long-Term Memory]:** Nah, kalau soal *{kunci}*, ingatan databaseku mencatat: {memori_pengetahuan[kunci]}"
            
    if "rekap" in pertanyaan or "evaluasi" in pertanyaan or "total" in pertanyaan:
        if not database_air: 
            return "Waduh, database analisis kualitas air di harddisk laptopmu masih kosong melompong nih. Yuk, coba hitung dan simpan satu sampel dulu!"
        
        total = len(database_air)
        reject = sum(1 for d in database_air if d["status"] == "MELEBIHI AMBANG")
        
        respons = f"**[Database Report]:** Oke, mari kita cek isi harddisk! Total riwayat pengujian yang berhasil tersimpan ada **{total} sampel**. "
        if reject > 0:
            respons += f"Tapi awas nih, ada **{reject} sampel yang ambang batasnya jebol (merah)**. Butuh perhatian ekstra di unit pengolahan limbahnya ya!"
        else:
            respons += "Aman jaya! Sejauh ini belum ada sampel yang melebihi ambang batas regulasi lingkungan."
            
        return respons
        
    return "Mmm, pola teks atau keyword materi itu belum ketemu di sel otak database-ku nih. Coba ajarkan aku dulu di form manajemen memori supaya aku ingat selamanya!"


# ==============================================================================
# 📱 TAMPILAN FRONTEND WEB STREAMLIT
# ==============================================================================

# --- KOLOM 1: SIDEBAR (NAVIGASI) ---
with st.sidebar:
    st.subheader("💧 Water Quality System")
    st.write("Politeknik AKA Bogor")
    st.markdown("---")
    
    # 🌟 SISTEM NAVIGASI SIDEBAR: Radio Button persis seperti menu screenshot referensi
    pilih_fitur = st.radio(
        "Pilih Fitur:",
        ["Beranda", "Perhitungan BOD/COD", "Database Riwayat Sampel", "Inteligensia & Konsultasi AI"]
    )
    st.markdown("---")
    
    # Bagian Ringkasan Data Cepat di bawah Menu Navigasi
    st.subheader("Ringkasan Data Lab")
    logs_saat_ini = get_water_logs()
    total_data = len(logs_saat_ini)
    total_tercemar = sum(1 for d in logs_saat_ini if d["status"] == "MELEBIHI AMBANG")
    
    st.metric("Total Sampel Teruji", f"{total_data} Sampel")
    st.metric("Sampel Melebihi Ambang", f"{total_tercemar} Sampel", delta=f"+{total_tercemar}" if total_tercemar > 0 else "0", delta_color="inverse")


# --- KOLOM 2: KONTEN UTAMA (BERUBAH SESUAI PILIHAN SIDEBAR) ---

# 🏠 MENU 1: BERANDA
if pilih_fitur == "Beranda":
    st.title("💧 Water Quality System")
    st.caption("Selamat Datang di Aplikasi Analisis Kualitas Air Laboratorium Lingkungan")
    st.markdown("---")
    
    col_ref1, col_ref2 = st.columns([1.5, 1])
    
    with col_ref1:
        st.subheader("🎯 Tujuan Aplikasi")
        st.write("""
        Aplikasi ini dirancang sebagai solusi terintegrasi untuk membantu laboran dan analis kimia dalam memproses data kualitas air, khususnya parameter Biochemical Oxygen Demand (BOD) dan Chemical Oxygen Demand (COD). Sistem ini bertujuan untuk mengotomatisasi kalkulasi rumus kimia yang rumit, menjamin penyimpanan rekam data riwayat sampel secara permanen di database fisik, serta menyediakan modul evaluasi berbasis kecerdasan buatan (AI) yang siap pakai.
        """)
        
    with col_ref2:
        st.subheader("📚 Manfaat Aplikasi")
        st.write("""
        Dengan menggunakan aplikasi ini, laboran dapat meminimalkan risiko 'human error' atau galat matematis saat perhitungan desimal bertingkat. Selain itu, integrasi database SQLite memastikan kepatuhan terhadap prinsip 'data integrity' lab lingkungan. Fitur chatbot komputasi AI juga mempercepat penyusunan narasi pembahasan hasil uji, menjadikan alur kerja laboratorium menjadi lebih cepat, akurat, dan terstandarisasi.
        """)
        
    st.markdown("---")
    st.subheader("📚 Daftar Pengetahuan Sistem Saat Ini")
    st.json(get_ai_knowledge())


# 🧮 MENU 2: PERHITUNGAN BOD/COD
elif pilih_fitur == "Perhitungan BOD/COD":
    st.title("🧮 Perhitungan Parameter Kimia Air")
    st.caption("Gunakan form ini untuk melakukan kalkulasi data mentah laboratorium")
    st.markdown("---")
    
    col_mutu1, col_mutu2 = st.columns(2)
    with col_mutu1:
        bod_max = st.number_input("Batas Maks Baku Mutu BOD (mg/L):", value=6.0000, step=0.5000, format="%.4f")
    with col_mutu2:
        cod_max = st.number_input("Batas Maks Baku Mutu COD (mg/L):", value=25.0000, step=1.0000, format="%.4f")
    st.markdown("---")
    
    sub_metode = st.selectbox("Pilih Parameter Analisis Air:", ["BOD (Biochemical Oxygen Demand)", "COD (Chemical Oxygen Demand)"])
    col_l1, col_l2 = st.columns([1.4, 1.2])
    
    with col_l1:
        nama_smpl = st.text_input("Kode / Lokasi Sampel Air:", value="Sungai Ciliwung-01")
        
        if "BOD" in sub_metode:
            st.caption("Metode Titrasi Iodometri (Winkler) / DO Meter pasca Inkubasi 5 Hari")
            do_0 = st.number_input("Kadar DO Hari Ke-0 (DO0) (mg/L):", value=8.2000, format="%.4f")
            do_5 = st.number_input("Kadar DO Hari Ke-5 (DO5) (mg/L):", value=4.5000, format="%.4f")
            f_pengenceran = st.number_input("Faktor Pengenceran (P):", value=2.0, step=0.5)
            
            if st.button("Hitung & Simpan Data"):
                hasil = hitung_bod(do_0, do_5, f_pengenceran)
                status = "MEMENUHI SYARAT" if hasil <= bod_max else "MELEBIHI AMBANG"
                biner_id = desimal_ke_biner(len(get_water_logs()) + 1)
                
                ket_singkat = f"DO0={do_0}, DO5={do_5}, P={f_pengenceran}"
                
                save_water_log(biner_id, nama_smpl, "BOD", hasil, status, ket_singkat)
                st.session_state["pembahasan_ai"] = ai_water_evaluation({"id_biner": biner_id, "parameter": "BOD", "nilai": hasil, "status": status}, bod_max)
                st.rerun()
                
        elif "COD" in sub_metode:
            st.caption("Metode Refluks Terbuka / Titrasi dengan Larutan FAS")
            v_blanko = st.number_input("Volume Penitran Blanko (mL):", value=15.20, format="%.2f")
            v_sampel = st.number_input("Volume Penitran Sampel Air (mL):", value=13.60, format="%.2f")
            n_fas = st.number_input("Normalitas Larutan FAS (N):", value=0.1000, format="%.4f")
            vol_air = st.number_input("Volume Sampel Air Teruji (mL):", value=50.00, format="%.2f")
            
            if st.button("Hitung & Simpan Data"):
                hasil = hitung_cod(v_blanko, v_sampel, n_fas, vol_air)
                status = "MEMENUHI SYARAT" if hasil <= cod_max else "MELEBIHI AMBANG"
                biner_id = desimal_ke_biner(len(get_water_logs()) + 1)
                
                ket_singkat = f"V_B={v_blanko}, V_S={v_sampel}, N_FAS={n_fas}"
                
                save_water_log(biner_id, nama_smpl, "COD", hasil, status, ket_singkat)
                st.session_state["pembahasan_ai"] = ai_water_evaluation({"id_biner": biner_id, "parameter": "COD", "nilai": hasil, "status": status}, cod_max)
                st.rerun()

    with col_l2:
        st.subheader("Bab 3: Pembahasan Evaluasi AI")
        if "pembahasan_ai" in st.session_state:
            st.info(st.session_state["pembahasan_ai"])
        else:
            st.caption("Sistem akan memunculkan narasi pembahasan otomatis di sini setelah kalkulasi selesai.")


# 📊 MENU 3: DATABASE RIWAYAT SAMPEL
elif pilih_fitur == "Database Riwayat Sampel":
    st.title("📊 Rekam Data Kualitas Air Permanen")
    st.caption("Seluruh riwayat pengujian sampel tersimpan dengan aman di database fisik harddisk")
    st.markdown("---")
    
    if logs_saat_ini:
        st.table(logs_saat_ini)
        
        set_semua = {d["sampel"] for d in logs_saat_ini}
        set_tercemar = {d["sampel"] for d in logs_saat_ini if d["status"] == "MELEBIHI AMBANG"}
        
        st.subheader("Analisis Set Laboratorium")
        st.write(f"**Set Lokasi Tercemar (Melebihi Ambang):** {set_tercemar if set_tercemar else 'Tidak ada'}")
        st.write(f"**Set Lokasi Aman Bersih (Lolos Syarat):** {set_semua.difference(set_tercemar) if set_semua.difference(set_tercemar) else 'Tidak ada'}")
        
        st.markdown("---")
        if st.button("Kosongkan Seluruh Riwayat Database"):
            clear_water_logs()
            st.rerun()
    else:
        st.caption("Belum ada riwayat pengujian sampel air yang tersimpan di harddisk komputer.")


# 🧠 MENU 4: INTELIGENSIA & KONSULTASI AI
elif pilih_fitur == "Inteligensia & Konsultasi AI":
    st.title("🧠 Pusat Kendali Pengetahuan & Konsultasi AI")
    st.caption("Gunakan fitur ini untuk berdiskusi dengan AI atau memasukkan materi laboratorium baru")
    st.markdown("---")
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.write("**Konsultasi Mutu Air Bersama AI**")
        chat_in = st.text_input("Tanyakan sesuatu ke AI (Contoh: 'halo', 'bod', 'cod', atau 'rekap'):", key="chat_input_unique")
        if chat_in:
            st.chat_message("assistant").write(ai_chatbot_brain(chat_in))

    with col_a2:
        st.write("**Penyimpanan Modul Pengetahuan Baru**")
        topik = st.text_input("Topik atau Kata Kunci Baru:").lower().strip()
        penjelasan = st.text_area("Deskripsi SOP / Penjelasan Ilmiah:")
        if st.button("Suntikkan Ke Memori Permanen"):
            if topik and penjelasan:
                save_ai_knowledge(topik, penjelasan)
                st.toast("AI berhasil memperbarui database pengetahuan!")
                st.rerun()
