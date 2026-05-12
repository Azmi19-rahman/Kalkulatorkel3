import streamlit as st

import streamlit as st
import random  # Digunakan untuk simulasi respons pintar AI

# ==============================================================================
# APLIKASI WEB: SMART WAREHOUSE INVENTORY MANAGEMENT WITH INTEGRATED AI
# Sesuai Kurikulum Modul Logika & Pemrograman Komputer 2026 (Politeknik AKA Bogor)
# Standar Penerapan: Industry 4.0 & AI Smart Lab Assistant
# ==============================================================================

# --- BAB VI: PEMBUATAN FUNGSI & LOGIKA AI ---

def desimal_ke_biner(desimal):
    """--- BAB I: KONVERSI SISTEM BINER ---"""
    if desimal == 0:
        return "0"
    biner = ""
    temp = desimal
    while temp > 0:
        sisa = temp % 2
        biner = str(sisa) + biner
        temp = temp // 2
    return biner

def ambil_barang_gudang(nama_barang, jumlah_diambil, database):
    """Fungsi pengurangan stok otomatis (Validasi Bab III)."""
    for barang in database:
        if barang["nama"].lower() == nama_barang.lower():
            if barang["stok"] == 0:
                return False, f"Gagal! Stok '{barang['nama']}' sudah kosong (0)."
            elif jumlah_diambil > barang["stok"]:
                return False, f"Gagal! Sisa stok '{barang['nama']}' hanya {barang['stok']} unit."
            else:
                barang["stok"] -= jumlah_diambil
                return True, f"Berhasil mengambil {jumlah_diambil} unit '{barang['nama']}'!"
    return False, "Barang tidak ditemukan di gudang!"

def ai_predictive_analysis(database):
    """🧠 LOGIKA AI 1: Analisis Prediktif Stok Berdasarkan Pola Penggunaan Industri"""
    rekomendasi_ai = []
    for barang in database:
        # AI mendeteksi jika stok di bawah ambang batas kritis
        if barang["stok"] == 0:
            rekomendasi_ai.append(f"🚨 **[AI URGENT]** Stok *{barang['nama']}* HABIS. AI memprediksi kelangkaan alat jika tidak di-order dalam 24 jam ke depan!")
        elif barang["stok"] <= 15:
            rekomendasi_ai.append(f"⚠️ **[AI WARNING]** Tren penggunaan *{barang['nama']}* meningkat. Disarankan melakukan restock sebanyak {int(barang['stok'] * 1.5)} unit.")
    return rekomendasi_ai

def ai_chatbot_response(pesan_user, database):
    """🤖 LOGIKA AI 2: Chatbot Asisten Gudang (Natural Language Rule Matching)"""
    pesan_user = pesan_user.lower()
    
    # Deteksi intent/maksud dari pertanyaan user (Bab III: Kondisional)
    if "halo" in pesan_user or "hai" in pesan_user:
        return "Halo! Saya AI Assistant Gudang AKA. Ada yang bisa saya bantu cek hari ini?"
        
    elif "stok" in pesan_user or "habis" in pesan_user:
        barang_habis = [b["nama"] for b in database if b["stok"] == 0]
        if barang_habis:
            return f"Berdasarkan analisis data saya, saat ini ada barang yang habis, yaitu: {', '.join(barang_habis)}. Segera hubungi bagian pengadaan ya!"
        else:
            return "Saya sudah memeriksa seluruh rak. Kabar baik, semua barang saat ini aman dan tersedia!"
            
    elif "rekomendasi" in pesan_user or "saran" in pesan_user:
        return "Saran saya: Prioritaskan pengadaan untuk barang berstatus 'KRITIS' atau 'HABIS' di dasbor sebelah kiri untuk menjaga kelancaran praktikum/produksi."
        
    else:
        # Respons fallback jika AI tidak memahami teks spesifik
        respons_acak = [
            "Maaf, bisa diperjelas pertanyaannya? Kamu bisa tanya saya tentang 'stok barang' atau 'rekomendasi gudang'.",
            "Saya belum mendeteksi perintah tersebut. Pastikan kata kunci berkaitan dengan inventaris gudang.",
            "Informasi spesifik tersebut tidak ditemukan dalam basis data log saya saat ini."
        ]
        return random.choice(respons_acak)


# --- KONFIGURASI HALAMAN STREAMLIT ---
st.set_page_config(
    page_title="Smart AI Warehouse",
    page_icon="🤖",
    layout="wide"
)

# --- DATABASE GUDANG (IN-MEMORY SESSION STATE) ---
if "gudang_db" not in st.session_state:
    st.session_state["gudang_db"] = [
        {"id": 101, "nama": "Beaker Glass 250 mL", "stok": 50, "kategori": "Alat Gelas"},
        {"id": 102, "nama": "Labu Ukur 100 mL", "stok": 5, "kategori": "Alat Gelas"},  # Disetting kritis untuk uji AI
        {"id": 103, "nama": "Larutan Indikator PP", "stok": 15, "kategori": "Bahan Kimia"},
        {"id": 104, "nama": "Kertas Saring Whatman 41", "stok": 0, "kategori": "Consumables"}, # Disetting habis untuk uji AI
        {"id": 105, "nama": "Buret 50 mL", "stok": 12, "kategori": "Alat Gelas"},
    ]

if "log_aktivitas" not in st.session_state:
    st.session_state["log_aktivitas"] = []


# --- TAMPILAN ANTARMUKA ---
st.title("📦 Smart AI Warehouse & Inventory System")
st.write("Sistem Monitoring Stok Gudang Terintegrasi dengan Kecerdasan Buatan (AI) Analitis.")
st.markdown("---")

db_aktif = st.session_state["gudang_db"]

# Layout Utama: 3 Kolom (Tabel Stok, Menu Transaksi, Fitur AI)
col_tabel, col_transaksi, col_ai = st.columns([1.5, 1.2, 1.3])

# --- KOLOM 1: REAL-TIME STOK (BAB IV & V) ---
with col_tabel:
    st.subheader("📋 Real-Time Stok Gudang")
    tampilan_tabel = []
    for item in db_aktif:
        kode_scan = desimal_ke_biner(item["id"])
        if item["stok"] == 0:
            status_stok = "🔴 HABIS"
        elif item["stok"] <= 15:
            status_stok = "🟡 KRITIS"
        else:
            status_stok = "🟢 AMAN"
            
        tampilan_tabel.append({
            "Scan Code (Biner)": kode_scan,
            "Nama Barang": item["nama"],
            "Stok": item["stok"],
            "Status": status_stok
        })
    st.table(tampilan_tabel)


# --- KOLOM 2: MENU TRANSAKSI (BAB II & III) ---
with col_transaksi:
    st.subheader("🔄 Menu Ambil & Tambah Barang")
    daftar_nama_barang = [item["nama"] for item in db_aktif]
    
    # Form Pengambilan
    barang_pilihan = st.selectbox("Pilih Barang yang Diambil:", daftar_nama_barang, key="ambil")
    jumlah_ambil = st.number_input("Jumlah Ambil (unit):", min_value=1, step=1, value=1)
    
    if st.button("Keluarkan Barang", type="primary"):
        sukses, pesan = ambil_barang_gudang(barang_pilihan, jumlah_ambil, db_aktif)
        if sukses:
            st.success(pesan)
            st.session_state["log_aktivitas"].append(f"🟢 [AMBIL] {jumlah_ambil} unit '{barang_pilihan}'")
            st.rerun()
        else:
            st.error(pesan)

    st.markdown("---")
    
    # Form Restock
    barang_restock = st.selectbox("Pilih Barang untuk Ditambah:", daftar_nama_barang, key="tambah")
    jumlah_tambah = st.number_input("Jumlah Tambah (unit):", min_value=1, step=1, value=5)
    if st.button("Tambah Stok", type="secondary"):
        for b in db_aktif:
            if b["nama"] == barang_restock:
                b["stok"] += jumlah_tambah
                st.success(f"Berhasil ditambah {jumlah_tambah} unit!")
                st.session_state["log_aktivitas"].append(f"🔵 [RESTOCK] Ditambah {jumlah_tambah} unit '{barang_restock}'")
                st.rerun()


# --- KOLOM 3: INTEGRASI AI (FITUR BARU) ---
with col_ai:
    st.subheader("🧠 Dasbor AI Smart Assistant")
    
    # Sub-Fitur 1: Hasil Prediksi Otomatis Machine Learning Palsu (Analitis)
    st.markdown("### 📊 AI Predictive Insights:")
    notifikasi_ai = ai_predictive_analysis(db_aktif)
    if notifikasi_ai:
        for alert in notifikasi_ai:
            st.write(alert)
    else:
        st.success("🎯 **[AI REPORT]** Kondisi suplai gudang dinilai sangat optimal untuk 7 hari ke depan.")
        
    st.markdown("---")
    
    # Sub-Fitur 2: Chatbot Interaktif Penjawab Otomatis
    st.markdown("### 💬 Chat dengan AI Gudang:")
    input_user = st.text_input("Tanyakan sesuatu ke AI (Contoh: 'cek barang habis' atau 'minta rekomendasi'):")
    
    if input_user:
        respons = ai_chatbot_response(input_user, db_aktif)
        st.chat_message("assistant").write(respons)

st.markdown("---")

# Bagian Paling Bawah: Operasi Himpunan & Log Aktivitas (Bab V)
col_bawah_1, col_bawah_2 = st.columns(2)

with col_bawah_1:
    st.subheader("⚠️ Manajemen Kontrol Set")
    set_barang_habis = {b["nama"] for b in db_aktif if b["stok"] == 0}
    set_barang_kritis = {b["nama"] for b in db_aktif if 0 < b["stok"] <= 15}
    
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        st.error("❌ Set Barang Habis:")
        st.write(set_barang_habis if set_barang_habis else "Kosong")
    with col_sub2:
        st.warning("⚠️ Set Barang Kritis:")
        st.write(set_barang_kritis if set_barang_kritis else "Kosong")

with col_bawah_2:
    st.subheader("📜 Log Aktivitas Gudang")
    if st.session_state["log_aktivitas"]:
        for log in reversed(st.session_state["log_aktivitas"]):
            st.text(log)
    else:
        st.caption("Belum ada aktivitas hari ini.")
