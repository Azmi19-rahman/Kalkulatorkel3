import streamlit as st
import numpy as np  # Membantu perhitungan statistik untuk proses belajar AI

# ==============================================================================
# APLIKASI WEB: ADAPTIVE AI CHEMISTRY LAB & WAREHOUSE SUITE
# Mencakup Materi Modul Bab I - VI dengan Fitur Self-Learning & Dynamic Memory
# ==============================================================================

# --- CONFIGURASI HALAMAN ---
st.set_page_config(page_title="Self-Learning AI Lab", page_icon="🧠", layout="wide")

# --- MEMORI STATIS & DINAMIS AI (BAB V: SESSION STATE SEBAGAI MEMORI AI) ---
if "database_QC" not in st.session_state:
    st.session_state["database_QC"] = []

# Memori Pengetahuan Baru (AI akan belajar instruksi baru dari sini)
if "ai_knowledge_base" not in st.session_state:
    st.session_state["ai_knowledge_base"] = {
        "gravimetri": "Metode analisis berdasarkan penimbangan berat konstan setelah pemanasan.",
        "iod-hubl": "Metode penentuan bilangan iod menggunakan reaksi adisi pada ikatan rangkap asam lemak."
    }

# --- FUNGSIONALITAS DASAR MODUL (BAB I & VI) ---
def desimal_ke_biner(desimal):
    """Bab I: Sistem Biner untuk Barcode otomatis."""
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


# --- 🧠 LOGIKA SELF-LEARNING AI (KECERDASAN BUATAN ADAPTIF) ---

def ai_analyze_and_learn(new_data, database):
    """
    AI Belajar Sendiri: Fungsi ini menganalisis tren data masa lalu di database
    untuk merumuskan saran dan prediksi korektif secara dinamis.
    """
    # Memasukkan data baru ke memori log
    database.append(new_data)
    
    # AI mengambil semua nilai kadar air yang sukses (PASSED) untuk dipelajari
    kadar_air_sukses = [d["nilai"] for d in database if d["parameter"] == "Kadar Air" and d["status"] == "PASSED"]
    
    insight = ""
    if len(kadar_air_sukses) >= 3:
        # AI menghitung rata-rata performa optimal berdasarkan data masa lalu
        mean_optimal = np.mean(kadar_air_sukses)
        insight = (f"🧠 **[AI SELF-LEARNING REPORT]:** Saya telah mempelajari {len(kadar_air_sukses)} sampel sukses terakhir. "
                   f"Rata-rata kadar air terbaik produksi Anda sebenarnya adalah **{mean_optimal:.4f}%**. ")
        
        # AI membuat keputusan sendiri di luar aturan dasar jika mendeteksi anomali
        if new_data["nilai"] > (mean_optimal * 1.5) and new_data["status"] == "PASSED":
            insight += "\n⚠️ **[AI DETEKSI ANOMALI]:** Meskipun sampel ini 'Lolos' batas maksimum, nilainya jauh di atas rata-rata biasanya. AI menyarankan cek kondisi kelembaban ruang oven!"
    else:
        insight = "🧠 **[AI MEMORY]:** Saya sedang mengumpulkan dan mempelajari pola data sampel Anda. Butuh minimal 3 data sukses untuk mengaktifkan analisis prediktif."
        
    return insight

def ai_chatbot_thinking(pesan_user, database, knowledge_base):
    """AI Chatbot yang bisa membaca database dan memori pengetahuan yang baru dipelajarinya."""
    pesan_user = pesan_user.lower()
    
    # 1. Belajar dari interaksi basis pengetahuan dinamis
    for kunci in knowledge_base:
        if kunci in pesan_user:
            return f"🤖 **[AI KNOWLEDGE]:** Mengenai *{kunci}*, ingatan saya mencatat: {knowledge_base[kunci]}"
            
    # 2. Menganalisis kondisi database saat ini secara mandiri
    if "rekap" in pesan_user or "kondisi" in pesan_user:
        if not database: return "Database kosong. Saya belum punya data untuk dianalisis."
        total = len(database)
        reject = sum(1 for d in database if d["status"] == "REJECTED")
        return f"🤖 **[AI DATA ANALYSIS]:** Dari total {total} sampel yang saya awasi, tingkat kegagalan produk saat ini adalah {((reject/total)*100):.1f}%. Perlu perhatian khusus pada sampel yang ditolak."
        
    return "🤖 Saya belum memahami konteks tersebut. Tapi Anda bisa mengajarkan saya pengetahuan baru pada form di bawah!"


# --- ANTARMUKA APLIKASI WEB ---
st.title("🧠 Chemistry Lab Suite + Adaptive Self-Learning AI")
st.write("Aplikasi laboratorium mandiri yang mampu mempelajari tren data dan menerima memori baru secara dinamis.")
st.markdown("---")

# Batas Baku Mutu Awal (Default)
BATAS_MAKS_AIR = 0.1500

col_kalkulator, col_ai_brain = st.columns([1.4, 1.2])

# --- PANEL KIRI: OPERASI DAN KALKULASI ---
with col_kalkulator:
    st.header("💧 Input Pengujian Kadar Air (Gravimetri)")
    nama_sampel = st.text_input("Kode Sampel Lab:", value="SMPL-CPO-01")
    
    w0 = st.number_input("Berat cawan kosong konstan (g):", value=15.0000, step=0.0001, format="%.4f")
    w1 = st.number_input("Berat cawan + sampel awal (g):", value=20.0000, step=0.0001, format="%.4f")
    w2 = st.number_input("Berat cawan + sampel setelah oven (g):", value=19.9930, step=0.0001, format="%.4f")
    
    if st.button("Jalankan Kalkulasi & Kirim ke AI", type="primary"):
        hasil_air = hitung_kadar_air(w0, w1, w2)
        
        if hasil_air is not None:
            # Bab III: Kondisional penentuan status dasar
            status_mutu = "PASSED" if hasil_air <= BATAS_MAKS_AIR else "REJECTED"
            
            # Membuat struktur data dict (Bab V)
            id_uji = len(st.session_state["database_QC"]) + 101
            data_baru = {
                "id_biner": desimal_ke_biner(id_uji),
                "sampel": nama_sampel,
                "parameter": "Kadar Air",
                "nilai": hasil_air,
                "status": status_mutu
            }
            
            # Memicu proses Belajar Mandiri AI
            st.session_state["ai_report"] = ai_analyze_and_learn(data_baru, st.session_state["database_QC"])
            st.success(f"Kalkulasi Selesai! Hasil: {hasil_air}% | Status Utama: {status_mutu}")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Log Database yang Diarsip AI")
    if st.session_state["database_QC"]:
        st.table(st.session_state["database_QC"])
    else:
        st.caption("Belum ada data sampel masuk.")

# --- PANEL KANAN: OTAK AI & FITUR BELAJAR MANDIRI ---
with col_ai_brain:
    st.header("🧠 Pusat Pembelajaran Mandiri AI")
    
    # Menampilkan laporan hasil analisa belajar dari tren data
    if "ai_report" in st.session_state:
        st.info(st.session_state["ai_report"])
    else:
        st.caption("AI siap menganalisis. Masukkan beberapa data pengujian di sebelah kiri untuk melihat AI bekerja mempelajari pola.")
        
    st.markdown("---")
    
    # Fitur Mengajari AI Secara Langsung (Pembaruan Knowledge Base Dinamis)
    st.subheader("📖 Ajarkan Pengetahuan / SOP Baru ke AI")
    topik_baru = st.text_input("Topik/Kata Kunci Baru (Misal: 'k3l' atau 'ruang oven'):").lower()
    penjelasan_baru = st.text_area("Tulis Instruksi/SOP/Definisi yang Harus Diingat AI:")
    
    if st.button("Suntikkan Pengetahuan ke Memori AI"):
        if topik_baru and penjelasan_baru:
            # AI memasukkan data kata kunci baru ke dalam library memorinya secara otomatis
            st.session_state["ai_knowledge_base"][topik_baru] = penjelasan_baru
            st.toast(f"AI Berhasil mempelajari hal baru tentang '{topik_baru}'!")
        else:
            st.error("Formulir mengajar AI tidak boleh kosong!")

    st.markdown("---")
    
    # Chatbot Uji Coba Ingatan AI
    st.subheader("💬 Uji Kecerdasan & Memori AI")
    input_user = st.text_input("Tanya AI (Coba tanyakan topik baru yang sudah kamu ajarkan tadi):")
    
    if input_user:
        respons_ai = ai_chatbot_thinking(input_user, st.session_state["database_QC"], st.session_state["ai_knowledge_base"])
        st.chat_message("assistant").write(respons_ai)
