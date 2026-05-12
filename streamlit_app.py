import streamlit as st
import numpy as np  # Membantu AI dalam mempelajari tren statistik (Mean & Standar Deviasi)

# ==============================================================================
# PROYEK: INTEGRATED SMART INDUSTRIAL SYSTEM (ISIS) WITH ADAPTIVE AI
# Berdasarkan Modul Logika & Pemrograman Komputer 2026 - Politeknik AKA Bogor
# Pemenuhan Cakupan Materi: Bab I sampai Bab VI
# ==============================================================================

# --- CONFIGURASI HALAMAN STREAMLIT ---
st.set_page_config(
    page_title="ISIS - AI Smart System 2026",
    page_icon="🧠",
    layout="wide"
)

# ==============================================================================
# 📑 STRUKTUR MEMORI & DATABASE UTAMA (BAB V: LOGIKA LIST & DICTIONARY SESSION STATE)
# ==============================================================================
# 1. Database Inventaris Gudang Sesuai Modul
if "gudang_db" not in st.session_state:
    st.session_state["gudang_db"] = [
        {"id": 101, "nama": "Beaker Glass 250 mL", "stok": 45, "kategori": "Alat Gelas"},
        {"id": 102, "nama": "Labu Ukur 100 mL", "stok": 12, "kategori": "Alat Gelas"},
        {"id": 103, "nama": "Larutan Indikator PP", "stok": 8, "kategori": "Bahan Kimia"},
        {"id": 104, "nama": "Kertas Saring Whatman 41", "stok": 85, "kategori": "Consumables"},
        {"id": 105, "nama": "Buret 50 mL", "stok": 0, "kategori": "Alat Gelas"}
    ]

# 2. Database Log Hasil Analisis Laboratorium (Kalkulator)
if "lab_db" not in st.session_state:
    st.session_state["lab_db"] = []

# 3. Dynamic Knowledge Base AI (Tempat AI Menyimpan Memori Hasil Belajar Mandiri)
if "ai_brain_memory" not in st.session_state:
    st.session_state["ai_brain_memory"] = {
        "gravimetri": "Metode analisis kuantitatif berdasarkan pemisahan dan penimbangan berat konstan zat.",
        "iod-hubl": "Penetapan bilangan iod untuk mengukur derajat ketidakjenuhan asam lemak/minyak.",
        "glp": "Good Laboratory Practice - Standar organisasi laboratorium untuk menjamin mutu dan integritas data."
    }


# ==============================================================================
# 🛠️ BAB VI: DEFINISI FUNGSI MODULAR & RETURN VALUE (LINGKUP GLOBAL & LOKAL)
# ==============================================================================

def desimal_ke_biner(desimal):
    """
    --- BAB I: KONVERSI SISTEM BINER ---
    Mengonversi ID Desimal menjadi sistem biner untuk Barcode Scanner Industri.
    """
    if desimal == 0:
        return "0"
    biner = ""
    temp = desimal  # Variabel Lokal (Bab VI)
    while temp > 0:  # Perulangan While (Bab IV)
        sisa = temp % 2
        biner = str(sisa) + biner
        temp = temp // 2
    return biner

def hitung_kadar_air(w0, w1, w2):
    """Kalkulator Gravimetri Oven (Casting & Rumus Bab II)"""
    try:
        return round(((w1 - w2) / (w1 - w0)) * 100, 4)
    except ZeroDivisionError:
        return None

def hitung_kadar_abu(w0, w1, w2):
    """Kalkulator Gravimetri Tanur (Casting & Rumus Bab II)"""
    try:
        return round(((w2 - w0) / (w1 - w0)) * 100, 4)
    except ZeroDivisionError:
        return None

def hitung_iod_hubl(vol, norm, berat):
    """Kalkulator Titrasi Bilangan Iod (Casting & Rumus Bab II)"""
    try:
        return round((vol * norm * 12.69) / berat, 4)
    except ZeroDivisionError:
        return None

def ambil_barang_gudang(nama_barang, jumlah_ambil, database):
    """Logika Pengurangan Stok Otomatis (Bab III, IV, V)"""
    for barang in database:  # Perulangan For (Bab IV)
        if barang["nama"].lower() == nama_barang.lower():
            # --- BAB III: PERNYATAAN KONDISIONAL ---
            if barang["stok"] == 0:
                return False, f"Gagal! Stok '{barang['nama']}' sudah kosong."
            elif jumlah_ambil > barang["stok"]:
                return False, f"Gagal! Stok tidak cukup. Sisa stok hanya {barang['stok']} unit."
            else:
                barang["stok"] -= jumlah_ambil  # Mengubah nilai stok secara dinamis
                return True, f"Berhasil mengeluarkan {jumlah_ambil} unit '{barang['nama']}'."
    return False, "Barang tidak ditemukan."


# ==============================================================================
# 🧠 REKAYASA LOGIKA AI: SELF-LEARNING & TEXT MATCHING
# ==============================================================================

def ai_statistical_learning(data_baru, database_lab):
    """🧠 AI BELAJAR SENDIRI (Mendeteksi tren historis tanpa rumus kaku)"""
    database_lab.append(data_baru)
    
    # Ambil semua data dengan parameter yang sama yang berstatus PASSED
    data_sejenis = [d["nilai"] for d in database_lab if d["parameter"] == data_baru["parameter"] and d["status"] == "PASSED"]
    
    report_ai = f"🧠 **[AI ANALYTICS]:** Menambahkan sampel baru dengan Barcode Biner: `{data_baru['id_biner']}`.\n\n"
    
    if len(data_sejenis) >= 3:
        rata_rata = np.mean(data_sejenis)
        std_dev = np.std(data_sejenis)
        report_ai += f"📈 **Hasil Pembelajaran Data Historis:** AI mendeteksi rata-rata performa optimal untuk parameter *{data_baru['parameter']}* adalah **{rata_rata:.4f}**. "
        
        # AI Berpikir Sendiri mendeteksi Anomali Penyimpangan Mutu (Bab III)
        if data_baru["status"] == "PASSED" and data_baru["nilai"] > (rata_rata + 1.5 * std_dev):
            report_ai += f"\n\n⚠️ **[AI ANOMALY ALERT]:** Meskipun sampel dinyatakan 'Lolos' uji manual, AI mendeteksi nilai ini menyimpang jauh di atas rata-rata historis produksi aman. Harap periksa kalibrasi instrumen!"
    else:
        report_ai += "ℹ️ **[AI MEMORY]:** AI sedang mengumpulkan basis data pengujian. Diperlukan minimal 3 sampel sukses agar AI bisa menyimpulkan tren produksi secara mandiri."
        
    return report_ai

def ai_chatbot_brain(pertanyaan, database_lab, memori_pengetahuan):
    """🤖 CHATBOT YANG BISA BELAJAR HAL BARU DAN MEMBACA DATA LOG"""
    pertanyaan = pertanyaan.lower()
    
    # AI Belajar dari Instruksi Baru yang Disuntikkan (Bab V: Dictionary Search)
    for kunci in memori_pengetahuan:
        if kunci in pertanyaan:
            return f"🤖 **[AI INTEGRATED KNOWLEDGE]:** Terkait *{kunci}*, memori dinamis saya mencatat: {memori_pengetahuan[kunci]}"
    
    # AI Membaca status database laboratorium secara mandiri
    if "rekap" in pertanyaan or "total" in pertanyaan or "laporan" in pertanyaan:
        if not database_lab:
            return "🤖 **[AI RESPONSE]:** Data log laboratorium hari ini masih kosong. Silakan hitung beberapa pengujian terlebih dahulu."
        total_uji = len(database_lab)
        total_reject = sum(1 for d in database_lab if d["status"] == "REJECTED")
        return f"🤖 **[AI MONITORING LOG]:** Hari ini saya mengawasi {total_uji} analisis. Terdeteksi {total_reject} produk GAGAL (REJECTED) memenuhi spesifikasi standar mutu."

    return "🤖 Maaf, konteks belum saya pelajari. Silakan ajarkan saya pengetahuan/SOP baru pada form di bawah!"


# ==============================================================================
# 💻 ANTARMUKA UTAMA APLIKASI WEB STREAMLIT (FRONTEND)
# ==============================================================================
st.title("🧪 ISIS: Integrated Smart Industrial System + Adaptive AI")
st.caption("Aplikasi Terintegrasi Pengendalian Mutu & Inventaris Gudang Berbasis Self-Learning Machine - Politeknik AKA Bogor")
st.markdown("---")

# --- SIDEBAR: KONTROL PARAMETER MUTU INDUSTRI (BAB III THRESHOLD) ---
st.sidebar.header("⚙️ Batas Standar Mutu QC (Supervisor)")
air_max = st.sidebar.number_input("Maks Kadar Air (%)", value=0.1500, step=0.0100, format="%.4f")
abu_max = st.sidebar.number_input("Maks Kadar Abu (%)", value=0.0500, step=0.0100, format="%.4f")
iod_min = st.sidebar.number_input("Min Bilangan Iod", value=50.0000, step=1.0000, format="%.4f")

# Navigasi Tab Besar
tab_gudang, tab_kalkulator, tab_ai = st.tabs(["📦 1. Manajemen Gudang Otomatis", "🧮 2. Kalkulator Analisis Lab", "🧠 3. Otak & Pembelajaran AI"])

# ==============================================================================
# TAB 1: MANAJEMEN GUDANG (OTOMATIS BERUBAH JIKA DIAMBIL)
# ==============================================================================
with tab_gudang:
    st.header("📦 Kontrol Real-Time Stok Gudang")
    st.write("Stok di bawah ini terhubung langsung secara dinamis dan otomatis berkurang saat transaksi berhasil dilakukan.")
    
    col_g1, col_g2 = st.columns([1.5, 1.2])
    
    with col_g1:
        st.subheader("📋 Status Rak Penyimpanan Saat Ini")
        
        # Membangun tabel log real-time dengan perulangan (Bab IV & V)
        gudang_tampil = []
        for barang in st.session_state["gudang_db"]:
            biner_code = desimal_ke_biner(barang["id"])  # Panggilan Bab I
            
            # Penentuan status visual dengan Bab III (Kondisional)
            if barang["stok"] == 0: status = "🔴 HABIS"
            elif barang["stok"] <= 15: status = "🟡 KRITIS (Butuh Restock)"
            else: status = "🟢 AMAN"
            
            gudang_tampil.append({
                "Barcode (Biner)": biner_code,
                "Nama Barang / Alat": barang["nama"],
                "Kategori": barang["kategori"],
                "Sisa Stok (Unit)": barang["stok"],
                "Status": status
            })
        st.table(gudang_tampil)
        
    with col_g2:
        st.subheader("🔄 Ambil Barang Gudang")
        list_nama_barang = [b["nama"] for b in st.session_state["gudang_db"]]
        pilih_barang = st.selectbox("Pilih Barang:", list_nama_barang)
        
        # Casting Input Numerik (Bab II)
        jumlah_ambil_input = st.number_input("Jumlah Unit yang Diambil:", min_value=1, step=1, value=1)
        nama_analis = st.text_input("Nama Analis Lapangan:", value="Azmi Rahmandira")
        
        if st.button("Eksekusi Pengambilan Barang", type="primary"):
            # Panggilan Fungsi Otomatis Mengubah Stok (Bab VI)
            sukses, pesan = ambil_barang_gudang(pilih_barang, jumlah_ambil_input, st.session_state["gudang_db"])
            if sukses:
                st.success(pesan)
                st.toast("Database gudang diperbarui secara otomatis!")
                st.rerun()
            else:
                st.error(pesan)
                
        # Menu pengisian ulang (Restock)
        st.markdown("---")
        st.subheader("➕ Pengisian Stok Kembali (Restock)")
        pilih_restock = st.selectbox("Pilih Barang Restock:", list_nama_barang, key="restock_key")
        jumlah_tambah_input = st.number_input("Jumlah Unit yang Ditambah:", min_value=1, step=1, value=5)
        
        if st.button("Tambah Stok Gudang"):
            for barang in st.session_state["gudang_db"]:
                if barang["nama"] == pilih_restock:
                    barang["stok"] += jumlah_tambah_input
                    st.success(f"Berhasil menambahkan {jumlah_tambah_input} unit ke '{pilih_restock}'.")
                    st.rerun()

# ==============================================================================
# TAB 2: KALKULATOR ANALISIS KIMIA INDUSTRI + EVALUASI QC
# ==============================================================================
with tab_kalkulator:
    st.header("🧮 Laboratorium Quality Control Terotomatisasi")
    
    sub_menu_lab = st.selectbox("Pilih Metode Parameter Uji:", [
        "A. Penetapan Kadar Air (Gravimetri Oven)",
        "B. Penetapan Kadar Abu (Gravimetri Tanur)",
        "C. Penetapan Bilangan Iod (Metode Iod-Hubl)"
    ])
    
    col_l1, col_l2 = st.columns([1.4, 1.2])
    
    with col_l1:
        st.subheader("📥 Input Data Mentah Penimbangan")
        nama_sampel_uji = st.text_input("Kode/Label Sampel:", value="SMPL-QC-01")
        
        if "A." in sub_menu_lab:
            w0 = st.number_input("Berat cawan kosong konstan (g) [W0]:", value=15.1054, format="%.4f", step=0.0001)
            w1 = st.number_input("Berat cawan + sampel awal (g) [W1]:", value=20.1085, format="%.4f", step=0.0001)
            w2 = st.number_input("Berat cawan + sampel kering setelah oven (g) [W2]:", value=20.1012, format="%.4f", step=0.0001)
            
            if st.button("Hitung & Kirim ke AI Evaluator", key="btn_air"):
                if w1 <= w0 or w2 > w1: st.error("Data penimbangan tidak logis (W1 harus > W0 dan W2 harus <= W1)!")
                else:
                    hasil = hitung_kadar_air(w0, w1, w2)
                    status_uji = "PASSED" if hasil <= air_max else "REJECTED"  # Bab III
                    
                    data_log = {
                        "id_biner": desimal_ke_biner(len(st.session_state["lab_db"]) + 201),
                        "sampel": nama_sampel_uji, "parameter": "Kadar Air", "nilai": hasil, "status": status_uji
                    }
                    st.session_state["active_ai_report"] = ai_statistical_learning(data_log, st.session_state["lab_db"])
                    st.success(f"Hasil Analisis: {hasil}% | Status Kepatuhan: {status_uji}")
                    st.rerun()

        elif "B." in sub_menu_lab:
            w0 = st.number_input("Berat cawan krus kosong konstan (g) [W0]:", value=22.3411, format="%.4f", step=0.0001)
            w1 = st.number_input("Berat cawan krus + sampel awal (g) [W1]:", value=27.3452, format="%.4f", step=0.0001)
            w2 = st.number_input("Berat cawan krus + abu sisa pijar (g) [W2]:", value=22.3429, format="%.4f", step=0.0001)
            
            if st.button("Hitung & Kirim ke AI Evaluator", key="btn_abu"):
                if w1 <= w0 or w2 < w0: st.error("Data penimbangan tidak valid!")
                else:
                    hasil = hitung_kadar_abu(w0, w1, w2)
                    status_uji = "PASSED" if hasil <= abu_max else "REJECTED"
                    
                    data_log = {
                        "id_biner": desimal_ke_biner(len(st.session_state["lab_db"]) + 201),
                        "sampel": nama_sampel_uji, "parameter": "Kadar Abu", "nilai": hasil, "status": status_uji
                    }
                    st.session_state["active_ai_report"] = ai_statistical_learning(data_log, st.session_state["lab_db"])
                    st.success(f"Hasil Analisis: {hasil}% | Status Kepatuhan: {status_uji}")
                    st.rerun()

        elif "C." in sub_menu_lab:
            vol_titrasi = st.number_input("Volume titrasi Na2S2O3 (mL):", value=12.45, format="%.2f", step=0.05)
            normalitas = st.number_input("Normalitas larutan tiosulfat (N):", value=0.1002, format="%.4f", step=0.0001)
            berat_minyak = st.number_input("Berat sampel minyak/lemak (g):", value=0.5012, format="%.4f", step=0.0001)
            
            if st.button("Hitung & Kirim ke AI Evaluator", key="btn_iod"):
                if berat_minyak <= 0 or vol_titrasi <= 0: st.error("Volume titrasi dan berat sampel harus di atas 0!")
                else:
                    hasil = hitung_iod_hubl(vol_titrasi, normalitas, berat_minyak)
                    status_uji = "PASSED" if hasil >= iod_min else "REJECTED"
                    
                    data_log = {
                        "id_biner": desimal_ke_biner(len(st.session_state["lab_db"]) + 201),
                        "sampel": nama_sampel_uji, "parameter": "Iod-Hubl", "nilai": hasil, "status": status_uji
                    }
                    st.session_state["active_ai_report"] = ai_statistical_learning(data_log, st.session_state["lab_db"])
                    st.success(f"Hasil Analisis: {hasil} g-I2/100g | Status Kepatuhan: {status_uji}")
                    st.rerun()

    with col_l2:
        st.subheader("🧐 Tinjauan Prediktif AI Langsung")
        if "active_ai_report" in st.session_state:
            st.info(st.session_state["active_ai_report"])
        else:
            st.caption("Silakan lakukan perhitungan di panel kiri. Hasil kalkulasi akan dievaluasi oleh sistem penalaran statistik AI.")

    # Tampilan database rekapitulasi pengujian laboratorium harian
    st.markdown("---")
    st.subheader("📋 Arsip Laporan Pengujian QC")
    if st.session_state["lab_db"]:
        st.table(st.session_state["lab_db"])
        
        # --- BAB V: OPERASI HIMPUNAN (SET) ---
        st.subheader("⚠️ Ringkasan Analitis Berbasis Himpunan (Set)")
        set_semua_sampel = {d["sampel"] for d in st.session_state["lab_db"]}
        set_sampel_reject = {d["sampel"] for d in st.session_state["lab_db"] if d["status"] == "REJECTED"}
        
        # Operasi Selisih Himpunan (Difference) untuk menyaring produk murni aman
        set_sampel_murni_lolos = set_semua_sampel.difference(set_sampel_reject)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.error(f"🔴 Produk Mengalami Kegagalan Mutu (Set Reject): {set_sampel_reject if set_sampel_reject else 'Tidak Ada'}")
        with col_s2:
            st.success(f"🟢 Produk Lolos Sempurna (Set Murni Passed): {set_sampel_murni_lolos if set_sampel_murni_lolos else 'Tidak Ada'}")
            
        if st.button("Kosongkan Semua Log Laporan QC"):
            st.session_state["lab_db"] = []
            if "active_ai_report" in st.session_state: del st.session_state["active_ai_report"]
            st.rerun()
    else:
        st.caption("Belum ada riwayat laporan pengujian yang tersimpan hari ini.")

# ==============================================================================
# TAB 3: PUSAT PEMBELAJARAN DAN AJAR MANDIRI AI (CONTINUOUS LEARNING MEMORY)
# ==============================================================================
with tab_ai:
    st.header("🧠 Pusat Otak & Pembelajaran Adaptif AI")
    st.write("Di panel ini, kamu bisa memantau basis pengetahuan yang sudah dipelajari AI, serta mengajari AI aturan atau SOP baru tanpa mengubah kode program.")
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.subheader("📖 Ajarkan SOP / Pengetahuan Baru ke AI")
        topik_baru = st.text_input("Topik/Kata Kunci Baru (Contoh: 'k3l', 'oven', 'titrasi'):").lower().strip()
        penjelasan_baru = st.text_area("Tulis Definisi / Instruksi Langkah Kerja Industri:")
        
        if st.button("Suntikkan Pengetahuan Baru"):
            if topik_baru and penjelasan_baru:
                # Memasukkan ke memori dictionary secara dinamis (Bab V)
                st.session_state["ai_brain_memory"][topik_baru] = penjelasan_baru
                st.toast(f"Sukses! AI telah menyimpan memori baru tentang kata kunci: '{topik_baru}'")
                st.rerun()
            else:
                st.error("Formulir pengajaran AI tidak boleh kosong!")
                
        st.markdown("---")
        st.subheader("📚 Kamus Memori Aktif AI Saat Ini")
        st.json(st.session_state["ai_brain_memory"])

    with col_a2:
        st.subheader("💬 Uji Kecerdasan & Memori Interaksi AI")
        st.write("Silakan uji apakah AI mampu mengaitkan pertanyaanmu dengan data log QC harian atau dengan SOP baru yang baru saja kamu ajarkan di panel sebelah kiri.")
        
        chat_user_input = st.text_input("Ketik pertanyaan Anda ke AI (Contoh: 'minta rekap laporan lab' atau ketik topik baru Anda):")
        
        if chat_user_input:
            respons_final_chatbot = ai_chatbot_brain(
                chat_user_input, 
                st.session_state["lab_db"], 
                st.session_state["ai_brain_memory"]
            )
            st.chat_message("assistant").write(respons_final_chatbot)
