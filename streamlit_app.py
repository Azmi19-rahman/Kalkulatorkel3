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
                barang["stok
