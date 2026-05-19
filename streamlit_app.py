import streamlit as st
import numpy as np
import sqlite3
import base64
import os

# ==============================================================================
# PROYEK: WATER QUALITY ANALYTICS SYSTEM (CUSTOM IMAGE ANIMATED EDITION)
# ==============================================================================

st.set_page_config(page_title="Water Quality Analytics System", page_icon="💧", layout="wide")

DB_FILE = "isis_water_quality.db"

# ==============================================================================
# 🖼️ FUNGSI ENKROPSI GAMBAR BACKGROUND KE BASE64
# ==============================================================================
def get_base64_image(image_path):
    # Memastikan file gambar ada di folder project
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# Taruh gambar lab kamu di folder yang sama dengan app.py, beri nama 'bg_lab.png'
# Jika formatnya .jpg atau .jpeg, silakan ganti nama file di bawah ini.
img_base64 = get_base64_image("bg_lab.png")

# ==============================================================================
# 🗃️ INISIALISASI DATABASE FISIK (SQLITE)
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
            ("bod", "BOD (Biochemical Oxygen Demand) merupakan takaran jumlah oksigen terlarut yang diperlukan oleh mikroorganisme untuk mendekomposisi bahan organik dalam air selama 5 hari."),
            ("cod", "COD (Chemical Oxygen Demand) adalah jumlah total oksigen yang dibutuhkan untuk mengurai seluruh bahan organik melalui reaksi kimia menggunakan oksidator kuat."),
            ("tss", "TSS (Total Suspended Solids) adalah material padatan tersuspensi (diameter > 1 mikrometer) yang tertahan pada media penyaring seperti kertas saring Whatman 41 setelah dikeringkan pada suhu 103-105°C."),
            ("do", "DO (Dissolved Oxygen) atau oksigen terlarut menunjukkan volume gas oksigen yang terkandung di dalam air. Kadar DO yang tinggi menandakan kualitas air yang baik untuk kehidupan akuatik."),
            ("regulasi", "Baku mutu air nasional diatur dalam PP No. 22 Tahun 2021. Batas parameter sangat bergantung pada kelas peruntukan air sungai atau badan air.")
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

def hitung_cod(vol_blanko, vol_sampel, norm_fas, vol_air):
    try: return round(((vol_blanko - vol_sampel) * norm_fas * 8000) / vol_air, 4)
    except ZeroDivisionError: return None

def hitung_tss(berat_akhir, berat_awal, vol_sampel_ml):
    try: return round(((berat_akhir - berat_awal) * 1000000) / vol_sampel_ml, 4)
    except ZeroDivisionError: return None

def hitung_do(vol_thiosulfat, norm_thiosulfat, vol_botol_do):
    try: return round((vol_thiosulfat * norm_thiosulfat * 8000) / (vol_botol_do - 4), 4)
    except ZeroDivisionError: return None


# ==============================================================================
# 🧠 LOGIKA EVALUASI AI (FORMAT PARAGRAF KONTINU)
# ==============================================================================
def ai_water_evaluation(data_baru, batas_acuan, parameter_nama, tipe_ambang="maks"):
    logs = get_water_logs()
    data_sejenis = [d["nilai"] for d in logs if d["parameter"] == data_baru["parameter"] and d["status"] == "MEMENUHI SYARAT"]
    
    pembahasan = f"Berdasarkan hasil analisis data laboratorium yang tersimpan di dalam database fisik, sampel air dengan kode identifikasi biner {data_baru['id_biner']} menunjukkan kadar {parameter_nama} sebesar {data_baru['nilai']:.4f} mg/L. "
    
    if data_baru["status"] == "MEMENUHI SYARAT":
        if tipe_ambang == "maks":
            pembahasan += f"Nilai parameter ini berada di bawah batas ambang regulasi baku mutu lingkungan yang ditetapkan yaitu sebesar {batas_acuan:.4f} mg/L, sehingga sampel air ini dinyatakan bersih dan layak untuk mendukung ekosistem perairan yang sehat. "
        else:
            pembahasan += f"Kadar oksigen terlarut ini berada di atas ambang minimum batas regulasi baku mutu lingkungan yaitu sebesar {batas_acuan:.4f} mg/L, yang menandakan pasokan oksigen bagi biota akuatik berada dalam kondisi sangat optimal. "
    else:
        if tipe_ambang == "maks":
            pembahasan += f"Kadar konsentrasi padatan atau beban limbah organik tersebut telah melampaui batas ambang standar regulasi lingkungan sebesar {batas_acuan:.4f} mg/L, yang menandakan tingkat pencemaran air yang tinggi dan berbahaya bagi badan air. "
        else:
            pembahasan += f"Kadar oksigen terlarut terpantau jatuh di bawah batas minimum kelayakan lingkungan yaitu sebesar {batas_acuan:.4f} mg/L, yang mengindikasikan terjadinya defisit oksigen parah akibat dekomposisi bahan organik berlebih. "

    if len(data_sejenis) >= 3:
        rata_rata = np.mean(data_sejenis)
        pembahasan += f"Apabila dibandingkan dengan data historis pengujian masa lalu, nilai rata-rata optimal untuk sampel yang lolos adalah {rata_rata:.4f} mg/L. Melalui analisis statistik tersebut, AI mengonfirmasi bahwa tren fluktuasi sampel ini masih berada dalam rentang deviasi normal lingkungan industri."
    else:
        pembahasan += "Saat ini AI belum mengaktifkan modul analitik prediktif mendalam dikarenakan jumlah data sampel valid yang tersimpan di harddisk komputer masih kurang dari tiga rekaman historis."
        
    return pembahasan

def ai_chatbot_brain(pertanyaan):
    pertanyaan = presidential_speech = pertanyaan.lower().strip()
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
        reject = sum(1 for d in database_air if d["status"] in ["MELEBIHI AMBANG", "DI BAWAH MINIMUM"])
        
        respons = f"**[Database Report]:** Oke, mari kita cek isi harddisk! Total riwayat pengujian yang berhasil tersimpan ada **{total} sampel**. "
        if reject > 0:
            respons += f"Tapi awas nih, ada **{reject} sampel yang ambang batasnya bermasalah (merah)**. Butuh perhatian ekstra di lingkungan ujinya ya!"
        else:
            respons += "Aman jaya! Sejauh ini belum ada sampel yang melebihi atau menyalahi ambang batas regulasi lingkungan."
            
        return respons
        
    return "Mmm, pola teks atau keyword materi itu belum ketemu di sel otak database-ku nih. Coba ajarkan aku dulu di form manajemen memori supaya aku ingat selamanya!"


# ==============================================================================
# 📱 FRONTEND & SUNTIKAN INTEGRASI BACKGROUND ASLI DAN ANIMASI LEMBUT
# ==============================================================================

# 🌌 1. Injeksi Canvas HTML5 untuk Efek Animasi Gelembung Mikro Naik Lembut di Atas Background
st.markdown("""
    <canvas id="customLabCanvas" style="position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:-1; pointer-events:none; opacity:0.5;"></canvas>
    <script>
    const canvas = document.getElementById('customLabCanvas');
    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    const dots = [];
    for(let i=0; i<20; i++) {
        dots.push({
            x: Math.random() * canvas.width,
            y: canvas.height + Math.random() * 100,
            r: Math.random() * 4 + 2,
            v: Math.random() * 0.8 + 0.3,
            op: Math.random() * 0.3 + 0.1
        });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        dots.forEach(d => {
            d.y -= d.v;
            if(d.y < -10) {
                d.y = canvas.height + 10;
                d.x = Math.random() * canvas.width;
            }
            ctx.beginPath();
            ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(100, 180, 255, ${d.op})`;
            ctx.fill();
        });
        requestAnimationFrame(draw);
    }
    draw();
    </script>
""", unsafe_allow_html=True)

# 🎨 2. CSS Kustom untuk Pasang Gambar Kamu Jadi Background Utama & Efek Glassmorphism
if img_base64:
    # Jika gambar berhasil diload dari folder lokal
    bg_style = f"""
    background: linear-gradient(135deg, rgba(255,255,255,0.75) 0%, rgba(240,247,255,0.8) 100%), 
                url('data:image/png;base64,{img_base64}') no-repeat center center fixed;
    background-size: cover;
    """
else:
    # Fallback jika kamu belum menaruh gambar bg_lab.png di folder
    bg_style = """
    background: linear-gradient(135deg, #ffffff 0%, #e6f2ff 100%);
    """

st.markdown(f"""
    <style>
    /* Pasang background custom */
    .stApp {{
        {bg_style}
        color: #1e293b !important;
    }}
    
    [data-testid="stSidebar"] {{
        background: rgba(248, 250, 252, 0.55) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-right: 1px solid rgba(203, 213, 225, 0.5);
    }}
    
    .main-title {{
        font-size: 38px;
        font-weight: 800;
        background: linear-gradient(45deg, #0284c7, #1e40af);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    /* EFEK KACA (GLASSMORPHISM) BERSIH SUPAYA GAMBAR KAMU TEMBUS KE DEPAN */
    .card-box-1 {{
        background: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 22px;
        border-radius: 14px;
        border: 1px solid rgba(14, 165, 233, 0.2);
        border-left: 6px solid #0284c7;
        color: #1e293b;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }}
    
    .card-box-2 {{
        background: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 22px;
        border-radius: 14px;
        border: 1px solid rgba(22, 163, 74, 0.2);
        border-left: 6px solid #16a34a;
        color: #1e293b;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }}
    
    .section-head {{
        color: #0369a1;
        font-weight: bold;
        border-bottom: 2px solid rgba(203, 213, 225, 0.6);
        padding-bottom: 5px;
        margin-top: 15px;
    }}
    
    label, p, span, div {{
        color: #334155 !important;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: #0f172a !important;
    }}
    
    /* Ganti desain tombol input bawaan Streamlit agar serasi dengan watercolor biru */
    .stButton>button {{
        background: linear-gradient(45deg, #0284c7, #2563eb) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
    }}
    </style>
""", unsafe_allow_html=True)


# --- KOLOM 1: SIDEBAR (NAVIGASI) ---
with st.sidebar:
    st.markdown("<h2 style='color: #0284c7; margin-bottom: 0px; font-weight:800;'>💧 Water Quality</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-style: italic; color: #64748b; margin-top:0px;'>Politeknik AKA Bogor</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    pilih_fitur = st.radio(
        "📌 Pilih Fitur Utama:",
        [
            "Beranda", 
            "Perhitungan BOD", 
            "Perhitungan COD", 
            "Perhitungan TSS", 
            "Perhitungan DO", 
            "Database Riwayat Sampel", 
            "Inteligensia & Konsultasi AI"
        ]
    )
    st.markdown("---")
    
    st.markdown("<h4 style='color: #0284c7;'>📊 Ringkasan Live Lab</h4>", unsafe_allow_html=True)
    logs_saat_ini = get_water_logs()
    total_data = len(logs_saat_ini)
    total_bermasalah = sum(1 for d in logs_saat_ini if d["status"] in ["MELEBIHI AMBANG", "DI BAWAH MINIMUM"])
    
    st.metric("Total Sampel Teruji", f"{total_data} Sampel")
    st.metric("Sampel Bermasalah", f"{total_bermasalah} Sampel", delta=f"+{total_bermasalah}" if total_bermasalah > 0 else "0", delta_color="inverse")


# --- KOLOM 2: KONTEN UTAMA ---

# 🏠 MENU 1: BERANDA
if pilih_fitur == "Beranda":
    st.markdown("<p class='main-title'>💧 Water Quality Analytics System</p>", unsafe_allow_html=True)
    st.caption("Selamat Datang di Dashboard Komputasi dan Analisis Kualitas Air Laboratorium Lingkungan")
    st.markdown("---")
    
    col_ref1, col_ref2 = st.columns(2)
    with col_ref1:
        st.markdown("""
            <div class='card-box-1'>
                <h3 style='color: #0284c7; margin-top:0px;'>🎯 Tujuan Aplikasi</h3>
                <p>Aplikasi ini dirancang sebagai solusi digital terintegrasi untuk mendampingi laboran serta analis kimia dalam memproses pengujian parameter kualitas air (BOD, COD, TSS, dan DO). Sistem mengotomatisasi kalkulasi bertingkat untuk mengeliminasi faktor galat manusia, sekaligus mengamankan penyimpanan data ke memori fisik komputer secara real-time.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_ref2:
        st.markdown("""
            <div class='card-box-2'>
                <h3 style='color: #16a34a; margin-top:0px;'>📚 Manfaat Aplikasi</h3>
                <p>Lewat integrasi basis data SQLite, kepatuhan validitas pengujian dan prinsip 'data integrity' laboratorium lingkungan tetap terjaga penuh. Didukung modul evaluasi otomatis berbasis kecerdasan buatan (AI), proses penyusunan narasi Bab 3 Pembahasan laporan praktikum atau kerja industri menjadi jauh lebih cepat, terstruktur, dan akurat.</p>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<h3 class='section-head'>📚 Basis Data Pengetahuan Sistem</h3>", unsafe_allow_html=True)
    st.json(get_ai_knowledge())


# 🧪 MENU 2: PERHITUNGAN BOD
elif pilih_fitur == "Perhitungan BOD":
    st.markdown("<h1 style='color: #0284c7;'>🧪 Input Analisis Parameter BOD</h1>", unsafe_allow_html=True)
    st.caption("Metode Titrasi Iodometri (Winkler) / DO Meter pasca Inkubasi 5 Hari")
    st.markdown("---")
    
    bod_max = st.number_input("🚨 Batas Maks Baku Mutu BOD (mg/L):", value=6.0000, step=0.5000, format="%.4f")
    st.markdown("---")
    
    col_l1, col_l2 = st.columns([1.4, 1.2])
    with col_l1:
        nama_smpl = st.text_input("📍 Kode / Lokasi Sampel Air:", value="Sungai Ciliwung-01", key="bod_sample")
        do_0 = st.number_input("Kadar DO Hari Ke-0 (DO0) (mg/L):", value=8.2000, format="%.4f")
        do_5 = st.number_input("Kadar DO Hari Ke-5 (DO5) (mg/L):", value=4.5000, format="%.4f")
        f_pengenceran = st.number_input("Faktor Pengenceran (P):", value=2.0, step=0.5)
        
        if st.button("🔥 Hitung & Simpan Data BOD", use_container_width=True):
            hasil = hitung_bod(do_0, do_5, f_pengenceran)
            status = "MEMENUHI SYARAT" if hasil <= bod_max else "MELEBIHI AMBANG"
            biner_id = desimal_ke_biner(len(get_water_logs()) + 1)
            ket_singkat = f"DO0={do_0}, DO5={do_5}, P={f_pengenceran}"
            
            save_water_log(biner_id, nama_smpl, "BOD", hasil, status, ket_singkat)
            st.session_state["pembahasan_bod"] = ai_water_evaluation({"id_biner": biner_id, "parameter": "BOD", "nilai": hasil, "status": status}, bod_max, "BOD", "maks")
            st.session_state["status_bod"] = status
            st.session_state["nilai_bod"] = hasil
            st.rerun()

    with col_l2:
        st.markdown("<h3 style='color: #0284c7;'>🧐 Hasil & Pembahasan AI</h3>", unsafe_allow_html=True)
        if "pembahasan_bod" in st.session_state:
            if st.session_state["status_bod"] == "MEMENUHI SYARAT":
                st.success(f"🎉 HASIL: {st.session_state['nilai_bod']:.4f} mg/L ({st.session_state['status_bod']})")
            else:
                st.error(f"❌ HASIL: {st.session_state['nilai_bod']:.4f} mg/L ({st.session_state['status_bod']})")
            st.info(st.session_state["pembahasan_bod"])
        else:
            st.caption("Hasil perhitungan dan narasi otomatis pembahasan akan muncul di panel ini setelah tombol hitung ditekan.")


# 🧪 MENU 3: PERHITUNGAN COD
elif pilih_fitur == "Perhitungan COD":
    st.markdown("<h1 style='color: #0284c7;'>🧪 Input Analisis Parameter COD</h1>", unsafe_allow_html=True)
    st.caption("Metode Refluks Terbuka / Titrasi dengan Larutan FAS")
    st.markdown("---")
    
    cod_max = st.number_input("🚨 Batas Maks Baku Mutu COD (mg/L):", value=25.0000, step=1.0000, format="%.4f")
    st.markdown("---")
    
    col_l1, col_l2 = st.columns([1.4, 1.2])
    with col_l1:
        nama_smpl = st.text_input("📍 Kode / Lokasi Sampel Air:", value="Sungai Ciliwung-01", key="cod_sample")
        v_blanko = st.number_input("Volume Penitran Blanko (mL):", value=15.20, format="%.2f")
        v_sampel = st.number_input("Volume Penitran Sampel Air (mL):", value=13.60, format="%.2f")
        n_fas = st.number_input("Normalitas Larutan FAS (N):", value=0.1000, format="%.4f")
        vol_air = st.number_input("Volume Sampel Air Teruji (mL):", value=50.00, format="%.2f")
        
        if st.button("🔥 Hitung & Simpan Data COD", use_container_width=True):
            hasil = hitung_cod(v_blanko, v_sampel, n_fas, vol_air)
            status = "MEMENUHI SYARAT" if hasil <= cod_max else "MELEBIHI AMBANG"
            biner_id = desimal_ke_biner(len(get_water_logs()) + 1)
            command_ket = f"V_B={v_blanko}, V_S={v_sampel}, N_FAS={n_fas}"
            
            save_water_log(biner_id, nama_smpl, "COD", hasil, status, command_ket)
            st.session_state["pembahasan_cod"] = ai_water_evaluation({"id_biner": biner_id, "parameter": "COD", "nilai": hasil, "status": status}, cod_max, "COD", "maks")
            st.session_state["status_cod"] = status
            st.session_state["nilai_cod"] = hasil
            st.rerun()

    with col_l2:
        st.markdown("<h3 style='color: #0284c7;'>🧐 Hasil & Pembahasan AI</h3>", unsafe_allow_html=True)
        if "pembahasan_cod" in st.session_state:
            if st.session_state["status_cod"] == "MEMENUHI SYARAT":
                st.success(f"🎉 HASIL: {st.session_state['nilai_cod']:.4f} mg/L ({st.session_state['status_cod']})")
            else:
                st.error(f"❌ HASIL: {st.session_state['nilai_cod']:.4f} mg/L ({st.session_state['status_cod']})")
            st.info(st.session_state["pembahasan_cod"])
        else:
            st.caption("Hasil perhitungan dan narasi otomatis pembahasan akan muncul di panel ini setelah tombol hitung ditekan.")


# ⚖️ MENU 4: PERHITUNGAN TSS
elif pilih_fitur == "Perhitungan TSS":
    st.markdown("<h1 style='color: #0284c7;'>⚖️ Input Analisis Parameter TSS</h1>", unsafe_allow_html=True)
    st.caption("Metode Gravimetri (Penyaringan dengan Kertas Saring & Oven 105°C)")
    st.markdown("---")
    
    tss_max = st.number_input("🚨 Batas Maks Baku Mutu TSS (mg/L):", value=50.0000, step=5.0000, format="%.4f")
    st.markdown("---")
    
    col_n1, col_n2 = st.columns([1.4, 1.2])
    with col_n1:
        nama_smpl_baru = st.text_input("📍 Kode / Lokasi Sampel Air:", value="Sungai Ciliwung-02", key="tss_sample")
        b_awal = st.number_input("Berat Kertas Saring Kosong (gram):", value=1.2345, format="%.4f")
        b_akhir = st.number_input("Berat Kertas Saring + Padatan Kering (gram):", value=1.2455, format="%.4f")
        v_air_tss = st.number_input("Volume Sampel Air yang Disaring (mL):", value=100.00, format="%.2f")
        
        if st.button("🔥 Hitung & Simpan Data TSS", use_container_width=True):
            hasil = hitung_tss(b_akhir, b_awal, v_air_tss)
            status = "MEMENUHI SYARAT" if hasil <= tss_max else "MELEBIHI AMBANG"
            biner_id = desimal_ke_biner(len(get_water_logs()) + 1)
            command_ket = f"B_Awal={b_awal} g, B_Akhir={b_akhir} g, V={v_air_tss} mL"
            
            save_water_log(biner_id, nama_smpl_baru, "TSS", hasil, status, command_ket)
            st.session_state["pembahasan_tss"] = ai_water_evaluation({"id_biner": biner_id, "parameter": "TSS", "nilai": hasil, "status": status}, tss_max, "TSS", "maks")
            st.session_state["status_tss"] = status
            st.session_state["nilai_tss"] = hasil
            st.rerun()

    with col_n2:
        st.markdown("<h3 style='color: #0284c7;'>🧐 Hasil & Pembahasan AI</h3>", unsafe_allow_html=True)
        if "pembahasan_tss" in st.session_state:
            if st.session_state["status_tss"] == "MEMENUHI SYARAT":
                st.success(f"🎉 HASIL: {st.session_state['nilai_tss']:.4f} mg/L ({st.session_state['status_tss']})")
            else:
                st.error(f"❌ HASIL: {st.session_state['nilai_tss']:.4f} mg/L ({st.session_state['status_tss']})")
            st.info(st.session_state["pembahasan_tss"])
        else:
            st.caption("Hasil perhitungan dan narasi otomatis pembahasan akan muncul di panel ini setelah tombol hitung ditekan.")


# ⚖️ MENU 5: PERHITUNGAN DO
elif pilih_fitur == "Perhitungan DO":
    st.markdown("<h1 style='color: #0284c7;'>🧪 Input Analisis Parameter DO</h1>", unsafe_allow_html=True)
    st.caption("Metode Standar Fiksasi Lapangan & Titrasi Natrium Thiosulfat (Na2S2O3)")
    st.markdown("---")
    
    do_min = st.number_input("🚨 Batas Minimum Baku Mutu DO (mg/L):", value=4.0000, step=0.5000, format="%.4f")
    st.markdown("---")
    
    col_n1, col_n2 = st.columns([1.4, 1.2])
    with col_n1:
        nama_smpl_baru = st.text_input("📍 Kode / Lokasi Sampel Air:", value="Sungai Ciliwung-02", key="do_sample")
        v_thio = st.number_input("Volume Penitran Thiosulfat (mL):", value=5.40, format="%.2f")
        n_thio = st.number_input("Normalitas Larutan Thiosulfat (N):", value=0.0250, format="%.4f")
        v_botol = st.number_input("Volume Botol DO yang Digunakan (mL):", value=250.00, format="%.2f")
        
        if st.button("🔥 Hitung & Simpan Data DO", use_container_width=True):
            hasil = hitung_do(v_thio, n_thio, v_botol)
            status = "MEMENUHI SYARAT" if hasil >= do_min else "DI BAWAH MINIMUM"
            biner_id = desimal_ke_biner(len(get_water_logs()) + 1)
            command_ket = f"V_Thio={v_thio} mL, N={n_thio}, V_Botol={v_botol} mL"
            
            save_water_log(biner_id, nama_smpl_baru, "DO", hasil, status, command_ket)
            st.session_state["pembahasan_do"] = ai_water_evaluation({"id_biner": biner_id, "parameter": "DO", "nilai": hasil, "status": status}, do_min, "Dissolved Oxygen (DO)", "min")
            st.session_state["status_do"] = status
            st.session_state["nilai_do"] = hasil
            st.rerun()

    with col_n2:
        st.markdown("<h3 style='color: #0284c7;'>🧐 Hasil & Pembahasan AI</h3>", unsafe_allow_html=True)
        if "pembahasan_do" in st.session_state:
            if st.session_state["status_do"] == "MEMENUHI SYARAT":
                st.success(f"🎉 HASIL: {st.session_state['nilai_do']:.4f} mg/L ({st.session_state['status_do']})")
            else:
                st.warning(f"⚠️ HASIL: {st.session_state['nilai_do']:.4f} mg/L ({st.session_state['status_do']})")
            st.info(st.session_state["pembahasan_do"])
        else:
            st.caption("Hasil perhitungan dan narasi otomatis pembahasan akan muncul di panel ini setelah tombol hitung ditekan.")


# 📊 MENU 6: DATABASE RIWAYAT SAMPEL
elif pilih_fitur == "Database Riwayat Sampel":
    st.markdown("<h1 style='color: #0284c7;'>📊 Rekam Data Kualitas Air Permanen</h1>", unsafe_allow_html=True)
    st.caption("Seluruh riwayat pengujian sampel terintegrasi langsung di database fisik harddisk SQLite")
    st.markdown("---")
    
    if logs_saat_ini:
        st.table(logs_saat_ini)
        
        set_semua = {d["sampel"] for d in logs_saat_ini}
        set_tercemar = {d["sampel"] for d in logs_saat_ini if d["status"] in ["MELEBIHI AMBANG", "DI BAWAH MINIMUM"]}
        
        st.markdown("<h3 class='section-head'>📊 Analisis Matematika Set Laboratorium</h3>", unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(f"<div style='background-color:rgba(239,68,68,0.05); padding:15px; border-radius:8px; border:1px solid rgba(239,68,68,0.2); border-left:4px solid #ef4444;'>⚠️ <b>Set Lokasi Bermasalah:</b> {set_tercemar if set_tercemar else 'Tidak ada'}</div>", unsafe_allow_html=True)
        with col_s2:
            st.markdown(f"<div style='background-color:rgba(34,197,94,0.05); padding:15px; border-radius:8px; border:1px solid rgba(34,197,94,0.2); border-left:4px solid #22c55e;'>✅ <b>Set Lokasi Lolos Syarat:</b> {set_semua.difference(set_tercemar) if set_semua.difference(set_tercemar) else 'Tidak ada'}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("🗑️ Kosongkan Seluruh Riwayat Database", use_container_width=True):
            clear_water_logs()
            st.rerun()
    else:
        st.info("Belum ada riwayat pengujian sampel air yang tersimpan di dalam database.")


# 🧠 MENU 7: INTELIGENSIA & KONSULTASI AI
elif pilih_fitur == "Inteligensia & Konsultasi AI":
    st.markdown("<h1 style='color: #0284c7;'>🧠 Pusat Kendali Pengetahuan & Konsultasi AI</h1>", unsafe_allow_html=True)
    st.caption("Diskusikan hasil analisis mutu air secara langsung atau tambahkan Standar Prosedur Operasional baru")
    st.markdown("---")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown("<h4 style='color: #0f172a;'>💬 Konsultasi Bersama AI Partner</h4>", unsafe_allow_html=True)
        chat_in = st.text_input("Ketik di sini (Contoh: 'halo', 'do', 'tss', atau 'rekap'):", key="chat_input_unique")
        if chat_in:
            with st.chat_message("assistant"):
                st.write(ai_chatbot_brain(chat_in))

    with col_a2:
        st.markdown("<h4 style='color: #0f172a;'>💾 Suntikkan Materi Pengetahuan Baru</h4>", unsafe_allow_html=True)
        topik = st.text_input("Topik Baru (Kata Kunci):").lower().strip()
        penjelasan = st.text_area("Deskripsi SOP / Penjelasan Ilmiah Kimia Analisis:")
        if st.button("🚀 Simpan Permanen ke Memori AI", use_container_width=True):
            if topik and penjelasan:
                save_ai_knowledge(topik, penjelasan)
                st.toast("AI sukses memperbarui memori pengetahuannya!")
                st.rerun()
