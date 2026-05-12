import streamlit as st
import random

# ==============================================================================
# APLIKASI WEB: INDUSTRIAL CHEMISTRY LAB SUITE (ICLS) WITH INTEGRATED AI
# Berdasarkan Modul Logika & Pemrograman Komputer 2026 (Politeknik AKA Bogor)
# Standar Penerapan: Good Laboratory Practice (GLP) & Smart Quality Control (QC)
# ==============================================================================

# --- BAB VI: PEMBUATAN FUNGSI (Perhitungan Kimia Analitik) ---

def hitung_kadar_air(w0, w1, w2):
    """Menghitung kadar air (%) metode Gravimetri Oven."""
    try:
        kadar_air = ((w1 - w2) / (w1 - w0)) * 100
        return round(kadar_air, 4)
    except ZeroDivisionError:
        return None

def hitung_kadar_abu(w0, w1, w2):
    """Menghitung kadar abu (%) metode Gravimetri Tanur."""
    try:
        kadar_abu = ((w2 - w0) / (w1 - w0)) * 100
        return round(kadar_abu, 4)
    except ZeroDivisionError:
        return None

def hitung_iod_hubl(vol, norm, berat):
    """Menghitung Bilangan Iod (Iodine Value) metode Iod-Hubl."""
    try:
        bilangan_iod = (vol * norm * 12.69) / berat
        return round(bilangan_iod, 4)
    except ZeroDivisionError:
        return None

def desimal_ke_biner(desimal):
    """--- BAB I: KONVERSI SISTEM BINER (Untuk Barcode ID Uji) ---"""
    if desimal == 0:
        return "0"
    biner = ""
    temp = desimal
    while temp > 0:
        sisa = temp % 2
        biner = str(sisa) + biner
        temp = temp // 2
    return biner


# --- 🧠 LOGIKA AI INTEGRATED ---

def ai_quality_assurance(parameter, nilai, status):
    """AI Expert yang menganalisis hasil uji lab dan memberikan tindakan korektif."""
    if status == "PASSED":
        return f"✨ **[AI QA LOG]** Hasil uji untuk {parameter} berada dalam batas aman. Produk memenuhi spesifikasi dan siap rilis ke tahap berikutnya."
    
    # Jika REJECTED, AI memberikan saran penyelesaian masalah laboratorium (Troubleshooting)
    if parameter == "Kadar Air":
        return ("⚠️ **[AI EVALUASI]** Kadar air terlalu tinggi! \n"
                "**Analisis Penyebab AI:** Kemungkinan waktu pengeringan di oven kurang lama atau cawan belum mencapai berat konstan saat desikasi.\n"
                "**Tindakan Korektif:** Lakukan pemanasan ulang pada suhu 105°C selama 1 jam sampai selisih berat < 0,0005 g.")
    elif parameter == "Kadar Abu":
        return ("⚠️ **[AI EVALUASI]** Kadar abu melebihi ambang batas industri!\n"
                "**Analisis Penyebab AI:** Proses pemijaran di tanur kurang sempurna (masih ada sisa karbon hitam) atau sampel terkontaminasi debu luar.\n"
                "**Tindakan Korektif:** Naikkan suhu tanur secara bertahap hingga 550°C sampai diperoleh abu berwarna putih abu-abu sempurna.")
    elif parameter == "Iod-Hubl":
        return ("⚠️ **[AI EVALUASI]** Bilangan Iod terlalu rendah!\n"
                "**Analisis Penyebab AI:** Tingkat ketidakjenuhan minyak menurun akibat hidrogenasi atau minyak sudah mengalami ketengikan (oksidasi).\n"
                "**Tindakan Korektif:** Periksa kondisi penyimpanan tangki produk dan pastikan tidak terpapar cahaya/udara luar secara langsung.")
    return None

def ai_lab_chatbot(pesan_user, database):
    """🤖 Chatbot Asisten Lab yang mengevaluasi kondisi mutu keseluruhan harian."""
    pesan_user = pesan_user.lower()
    
    if "halo" in pesan_user or "hai" in pesan_user:
        return "Halo! Saya AI Assistant Lab ICLS. Ada yang bisa saya bantu analisis hari ini?"
        
    elif "status" in pesan_user or "ringkasan" in pesan_user or "hasil" in pesan_user:
        if not database:
            return "Belum ada data pengujian yang saya catat di database hari ini. Silakan lakukan kalkulasi terlebih dahulu!"
        
        total_uji = len(database)
        total_reject = sum(1 for item in database if item["status"] == "REJECTED")
        
        if total_reject > 0:
            return f"Hari ini telah dilakukan {total_uji} pengujian. Deteksi AI menemukan {total_reject} sampel GAGAL (REJECTED). Anda bisa mengecek rekomendasi perbaikan pada panel analitis."
        else:
            return f"Laporan Bagus! Dari {total_uji} sampel yang diuji hari ini, semuanya berstatus PASSED. Pertahankan performa proses produksinya!"
            
    elif "gravimetri" in pesan_user:
        return "Analisis Gravimetri mencakup Kadar Air (oven) dan Kadar Abu (tanur). Pastikan penimbangan menggunakan neraca analitik dengan ketelitian 4 desimal untuk menjaga akurasi data industri."
        
    else:
        respons_acak = [
            "Maaf, saya belum memahami pertanyaan itu. Anda bisa bertanya seperti: 'bagaimana ringkasan hasil lab hari ini?'",
            "Kata kunci tidak dikenali. Saya dilatih khusus untuk menganalisis data kadar air, kadar abu, dan bilangan Iod-Hubl.",
            "Mohon perjelas pertanyaan Anda terkait teknis operasional lab atau status mutu sampel."
        ]
        return random.choice(respons_acak)


# --- CONFIGURASI HALAMAN STREAMLIT ---
st.set_page_config(
    page_title="Industrial Lab with AI",
    page_icon="🧪",
    layout="wide"
)

# --- DATABASE LOG LAB (BAB V: LIST SESSION STATE) ---
if "database_uji" not in st.session_state:
    st.session_state["database_uji"] = []


# --- TAMPILAN ANTARMUKA ---
st.title("🧪 Industrial Chemistry Lab Suite + Smart AI")
st.write("Kalkulator Analisis Mutu Laboratorium Berbasis AI - Standar Industri Modern (Industry 4.0).")
st.markdown("---")

# Pengaturan Batas Toleransi Mutu oleh Supervisor di Sidebar (Bab III)
st.sidebar.header("⚙️ Standar Kepatuhan Mutu (QC)")
air_max = st.sidebar.number_input("Batas Maks Kadar Air (%)", value=0.1500, step=0.0100, format="%.4f")
abu_max = st.sidebar.number_input("Batas Maks Kadar Abu (%)", value=0.0500, step=0.0100, format="%.4f")
iod_min = st.sidebar.number_input("Batas Min Bilangan Iod", value=50.0000, step=1.0000, format="%.4f")

# Navigasi Aplikasi
menu = st.selectbox(
    "Pilih Parameter Analisis Laboratorium:",
    [
        "1. Analisis Kadar Air (Gravimetri Oven)",
        "2. Analisis Kadar Abu (Gravimetri Tanur)",
        "3. Penetapan Bilangan Iod (Metode Iod-Hubl)",
        "4. Database Log QC & AI Global Analytics"
    ]
)

# Pembagian Kolom Kerja Utama (Kiri untuk Input Kalkulator, Kanan untuk AI Assistant)
col_input, col_ai_expert = st.columns([1.5, 1.2])

# Variabel pembantu untuk memicu penampilan AI Evaluator
tampilkan_ai_review = False
prm_aktif, nilai_aktif, status_aktif = "", 0.0, ""

# ------------------------------------------------------------------------------
# PROSES INPUT & KALKULASI (BAB II, III, & VI)
# ------------------------------------------------------------------------------
with col_input:
    if menu.startswith("1"):
        st.header("💧 Kadar Air (Gravimetri Oven)")
        nama_sampel = st.text_input("Kode Sampel:", value="SAM-WATER-001")
        w0 = st.number_input("Berat cawan kosong konstan (g) [W0]:", value=15.1200, step=0.0001, format="%.4f")
        w1 = st.number_input("Berat cawan + sampel awal (g) [W1]:", value=20.1250, step=0.0001, format="%.4f")
        w2 = st.number_input("Berat cawan + sampel kering oven (g) [W2]:", value=20.1190, step=0.0001, format="%.4f")
        
        if st.button("Hitung Kadar Air", type="primary"):
            if w1 <= w0 or w2 > w1:
                st.error("Input Invalid! Periksa kembali data penimbangan Anda.")
            else:
                hasil = hitung_kadar_air(w0, w1, w2)
                if hasil is not None:
                    st.metric(label="Hasil Analisis", value=f"{hasil} %")
                    status = "PASSED" if hasil <= air_max else "REJECTED"
                    
                    # Simpan ke DB
                    id_biner = desimal_ke_biner(len(st.session_state["database_uji"]) + 101)
                    st.session_state["database_uji"].append({
                        "id_biner": id_biner, "sampel": nama_sampel, "parameter": "Kadar Air",
                        "nilai": hasil, "satuan": "%", "status": status
                    })
                    # Set pemicu AI review
                    tampilkan_ai_review, prm_aktif, nilai_aktif, status_aktif = True, "Kadar Air", hasil, status

    elif menu.startswith("2"):
        st.header("🔥 Kadar Abu (Gravimetri Tanur)")
        nama_sampel = st.text_input("Kode Sampel:", value="SAM-ASH-001")
        w0 = st.number_input("Berat cawan kosong konstan (g) [W0]:", value=20.5500, step=0.0001, format="%.4f")
        w1 = st.number_input("Berat cawan + sampel awal (g) [W1]:", value=25.5550, step=0.0001, format="%.4f")
        w2 = st.number_input("Berat cawan + abu sisa pijar (g) [W2]:", value=20.5520, step=0.0001, format="%.4f")
        
        if st.button("Hitung Kadar Abu", type="primary"):
            if w1 <= w0 or w2 < w0:
                st.error("Input Invalid! Periksa kembali data penimbangan Anda.")
            else:
                hasil = hitung_kadar_abu(w0, w1, w2)
                if hasil is not None:
                    st.metric(label="Hasil Analisis", value=f"{hasil} %")
                    status = "PASSED" if hasil <= abu_max else "REJECTED"
                    
                    id_biner = desimal_ke_biner(len(st.session_state["database_uji"]) + 101)
                    st.session_state["database_uji"].append({
                        "id_biner": id_biner, "sampel": nama_sampel, "parameter": "Kadar Abu",
                        "nilai": hasil, "satuan": "%", "status": status
                    })
                    tampilkan_ai_review, prm_aktif, nilai_aktif, status_aktif = True, "Kadar Abu", hasil, status

    elif menu.startswith("3"):
        st.header("🧪 Bilangan Iod (Metode Iod-Hubl)")
        nama_sampel = st.text_input("Kode Sampel:", value="SAM-OIL-001")
        vol = st.number_input("Volume Titrasi Na2S2O3 (mL):", value=15.50, step=0.05, format="%.2f")
        norm = st.number_input("Normalitas Na2S2O3 (N):", value=0.1002, step=0.0001, format="%.4f")
        berat = st.number_input("Berat Sampel Minyak (g):", value=0.4950, step=0.0001, format="%.4f")
        
        if st.button("Hitung Bilangan Iod", type="primary"):
            if berat <= 0 or vol <= 0:
                st.error("Input Invalid! Volume dan berat sampel harus bernilai positif.")
            else:
                hasil = hitung_iod_hubl(vol, norm, berat)
                if hasil is not None:
                    st.metric(label="Hasil Analisis", value=f"{hasil} g-I2/100g")
                    status = "PASSED" if hasil >= iod_min else "REJECTED"
                    
                    id_biner = desimal_ke_biner(len(st.session_state["database_uji"]) + 101)
                    st.session_state["database_uji"].append({
                        "id_biner": id_biner, "sampel": nama_sampel, "parameter": "Iod-Hubl",
                        "nilai": hasil, "satuan": "g-I2/100g", "status": status
                    })
                    tampilkan_ai_review, prm_aktif, nilai_aktif, status_aktif = True, "Iod-Hubl", hasil, status

    elif menu.startswith("4"):
        st.header("📊 Database Log & Global Analytics")
        riwayat = st.session_state["database_uji"]
        if not riwayat:
            st.warning("Belum ada data pengujian laboratorium yang terekam.")
        else:
            st.table(riwayat)
            if st.button("Hapus Semua Log"):
                st.session_state["database_uji"] = []
                st.rerun()

# ------------------------------------------------------------------------------
# PANEL DESENTRALISASI INTEGRASI AI (KOLOM KANAN)
# ------------------------------------------------------------------------------
with col_ai_expert:
    st.subheader("🧠 AI Smart Lab Evaluator")
    
    # Menampilkan Analisis Otomatis pasca-kalkulasi parameter aktif
    if tampilkan_ai_review:
        st.markdown(f"**Analisis Real-Time Terakhir:** `{prm_aktif}` = {nilai_aktif}")
        if status_aktif == "PASSED":
            st.success(f"Status Kepatuhan Mutu: {status_aktif}")
        else:
            st.error(f"Status Kepatuhan Mutu: {status_aktif}")
            
        # Panggil fungsi AI QA Specialist
        analisis_qa_ai = ai_quality_assurance(prm_aktif, nilai_aktif, status_aktif)
        st.info(analisis_qa_ai)
    else:
        st.caption("Silakan lakukan perhitungan di panel kiri untuk memicu review otomatis dari AI QA Specialist.")
        
    st.markdown("---")
    
    # Fitur Chatbot Asisten AI
    st.markdown("### 💬 Chat dengan AI Asisten Lab:")
    input_chat = st.text_input("Tanyakan sesuatu ke AI (Contoh: 'cek status lab hari ini' atau 'jelaskan gravimetri'):")
    
    if input_chat:
        jawaban_chatbot = ai_lab_chatbot(input_chat, st.session_state["database_uji"])
        st.chat_message("assistant").write(jawaban_chatbot)
