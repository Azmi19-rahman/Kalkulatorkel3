import streamlit as st

st.title("Kalkulator Gravimetri")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

# ==============================================================================
# PROYEK: INDUSTRIAL CHEMISTRY LAB SUITE (ICLS) - VERSI 1.0
# Deskripsi: Aplikasi otomatisasi perhitungan laboratorium & kepatuhan mutu industri
# Standar: Good Laboratory Practice (GLP) & SNI ISO/IEC 17025
# ==============================================================================

# --- BAB VI: PEMBUATAN FUNGSI (Modularisasi Rumus Kimia Analitik) ---

def hitung_kadar_air(w0, w1, w2):
    """
    Menghitung kadar air (Moisture Content) dengan metode Gravimetri.
    w0 = Berat cawan kosong konstan (g)
    w1 = Berat cawan + sampel basah awal (g)
    w2 = Berat cawan + sampel kering setelah oven (g)
    """
    try:
        # Rumus: ((w1 - w2) / (w1 - w0)) * 100%
        kadar_air = ((w1 - w2) / (w1 - w0)) * 100
        return round(kadar_air, 4)
    except ZeroDivisionError:
        return None

def hitung_kadar_abu(w0, w1, w2):
    """
    Menghitung kadar abu (Ash Content) dengan metode Gravimetri Tanur.
    w0 = Berat cawan kosong konstan (g)
    w1 = Berat cawan + sampel awal (g)
    w2 = Berat cawan + abu sisa pemijaran (g)
    """
    try:
        # Rumus: ((w2 - w0) / (w1 - w0)) * 100%
        kadar_abu = ((w2 - w0) / (w1 - w0)) * 100
        return round(kadar_abu, 4)
    except ZeroDivisionError:
        return None

def hitung_kadar_iod_hubl(volume_titrasi, normalitas_thiosulfat, berat_sampel):
    """
    Menghitung Bilangan Iod (Iodine Value) dengan metode Iod-Hubl 
    untuk penentuan ketidakjenuhan minyak/lemak standar industri.
    """
    try:
        # Rumus Industri Sederhana: (V * N * 12.69) / Berat Sampel
        bilangan_iod = (volume_titrasi * normalitas_thiosulfat * 12.69) / berat_sampel
        return round(bilangan_iod, 4)
    except ZeroDivisionError:
        return None

def desimal_ke_biner(desimal):
    """
    --- BAB I: KONVERSI SISTEM BINER ---
    Konversi nilai desimal ID Pengujian ke sistem biner untuk pengkodean barcode sampel.
    """
    if desimal == 0:
        return "0"
    biner = ""
    temp = desimal
    while temp > 0:
        sisa = temp % 2
        biner = str(sisa) + biner
        temp = temp // 2
    return biner


# --- MAIN PROGRAM (Menu Utama Interaktif) ---

def main():
    print("=" * 60)
    print("        WELCOME TO INDUSTRIAL CHEMISTRY LAB SUITE (ICLS)")
    print("         Sistem Kontrol Kualitas Terintegrasi (QC/QA)")
    print("=" * 60)

    # --- BAB V: STRUKTUR DATA (Penyimpanan database riwayat analisis) ---
    riwayat_analisis = []  # List untuk menyimpan dict data pengujian
    
    # Kriteria Parameter Kritis Kepatuhan Mutu (Standar Baku Mutu Industri)
    # Contoh untuk produk Minyak Kelapa Sawit (CPO) / Minyak Industri
    STANDAR_MUTU = {
        "kadar_air_maks": 0.15,   # Persen (%) maksimum
        "kadar_abu_maks": 0.05,   # Persen (%) maksimum
        "iod_hubl_min": 50.0      # Nilai minimum bilangan Iod
    }

    # --- BAB IV: PERULANGAN (Sistem Menu Terus Menerus) ---
    while True:
        print("\n=== MENU UTAMA SISTEM ===")
        print("1. Analisis Kadar Air (Gravimetri Oven)")
        print("2. Analisis Kadar Abu (Gravimetri Tanur)")
        print("3. Penetapan Bilangan Iod (Metode Iod-Hubl)")
        print("4. Lihat Riwayat Log Pengujian & Status Mutu")
        print("5. Keluar Sistem")
        
        # --- BAB II: INPUT/OUTPUT & CASTING ---
        pilihan = input("\nPilih menu operasi (1-5): ")

        if pilihan == '1':
            print("\n--- ANALISIS KADAR AIR (GRAVIMETRI) ---")
            nama_sampel = input("Masukkan Kode/Nama Sampel: ")
            
            # Memastikan input berupa float (Bab II & III)
            try:
                w0 = float(input("Berat cawan kosong konstan (g): "))
                w1 = float(input("Berat cawan + sampel basah awal (g): "))
                w2 = float(input("Berat cawan + sampel kering setelah oven (g): "))
            except ValueError:
                print("[ERROR] Input berat harus berupa angka desimal!")
                continue

            # Hitung menggunakan fungsi (Bab VI)
            hasil = hitung_kadar_air(w0, w1, w2)
            
            if hasil is not None:
                # --- BAB III: KONDISIONAL (Evaluasi Mutu Industri) ---
                if hasil <= STANDAR_MUTU["kadar_air_maks"]:
                    status = "MEMENUHI STANDAR (PASSED)"
                else:
                    status = "TIDAK MEMENUHI STANDAR (REJECTED)"
                
                print(f"Hasil Kadar Air: {hasil}%")
                print(f"Status Kepatuhan: {status}")

                # Simpan data ke List Riwayat (Bab V)
                analisis_id = len(riwayat_analisis) + 101 # ID pengujian desimal
                riwayat_analisis.append({
                    "id_biner": desimal_ke_biner(analisis_id),
                    "sampel": nama_sampel,
                    "parameter": "Kadar Air",
                    "nilai": hasil,
                    "satuan": "%",
                    "status": status
                })
            else:
                print("[ERROR] Perhitungan gagal. Periksa input berat sampel Anda.")

        elif pilihan == '2':
            print("\n--- ANALISIS KADAR ABU (GRAVIMETRI) ---")
            nama_sampel = input("Masukkan Kode/Nama Sampel: ")
            try:
                w0 = float(input("Berat cawan kosong konstan (g): "))
                w1 = float(input("Berat cawan + sampel awal (g): "))
                w2 = float(input("Berat cawan + abu sisa pemijaran (g): "))
            except ValueError:
                print("[ERROR] Input berat harus berupa angka desimal!")
                continue

            hasil = hitung_kadar_abu(w0, w1, w2)
            
            if hasil is not None:
                # Kondisional Mutu (Bab III)
                if hasil <= STANDAR_MUTU["kadar_abu_maks"]:
                    status = "MEMENUHI STANDAR (PASSED)"
                else:
                    status = "TIDAK MEMENUHI STANDAR (REJECTED)"
                
                print(f"Hasil Kadar Abu: {hasil}%")
                print(f"Status Kepatuhan: {status}")

                # Simpan ke List Riwayat (Bab V)
                analisis_id = len(riwayat_analisis) + 101
                riwayat_analisis.append({
                    "id_biner": desimal_ke_biner(analisis_id),
                    "sampel": nama_sampel,
                    "parameter": "Kadar Abu",
                    "nilai": hasil,
                    "satuan": "%",
                    "status": status
                })
            else:
                print("[ERROR] Perhitungan gagal. Periksa input berat sampel Anda.")

        elif pilihan == '3':
            print("\n--- PENETAPAN BILANGAN IOD (IOD-HUBL) ---")
            nama_sampel = input("Masukkan Kode/Nama Sampel: ")
            try:
                vol = float(input("Volume titrasi thiosulfat (mL): "))
                norm = float(input("Normalitas larutan Thiosulfat (N): "))
                berat = float(input("Berat sampel minyak/lemak (g): "))
            except ValueError:
                print("[ERROR] Input parameter titrasi harus berupa angka!")
                continue

            hasil = hitung_kadar_iod_hubl(vol, norm, berat)
            
            if hasil is not None:
                # Kondisional Mutu (Bab III)
                if hasil >= STANDAR_MUTU["iod_hubl_min"]:
                    status = "MEMENUHI STANDAR (PASSED)"
                else:
                    status = "TIDAK MEMENUHI STANDAR (REJECTED)"
                
                print(f"Nilai Iod-Hubl: {hasil} g-I2/100g")
                print(f"Status Kepatuhan: {status}")

                # Simpan ke List Riwayat (Bab V)
                analisis_id = len(riwayat_analisis) + 101
                riwayat_analisis.append({
                    "id_biner": desimal_ke_biner(analisis_id),
                    "sampel": nama_sampel,
                    "parameter": "Iod-Hubl",
                    "nilai": hasil,
                    "satuan": "g-I2/100g",
                    "status": status
                })
            else:
                print("[ERROR] Perhitungan gagal. Periksa input berat dan volume titrasi.")

        elif pilihan == '4':
            print("\n" + "="*80)
            print("                 LOG DATABASE MONITORING MUTU INDUSTRI")
            print("="*80)
            
            if not riwayat_analisis:
                print("Belum ada riwayat pengujian yang tercatat hari ini.")
            else:
                # --- BAB IV & V: PERULANGAN FOR UNTUK STRUKTUR DATA LIST ---
                for index, item in enumerate(riwayat_analisis):
                    print(f"[{index + 1}] ID Barcode (Biner): {item['id_biner']} | Sampel: {item['sampel']}")
                    print(f"    Parameter : {item['parameter']}")
                    print(f"    Nilai Uji : {item['nilai']} {item['satuan']}")
                    print(f"    Keputusan : {item['status']}")
                    print("-" * 80)
                
                # --- BAB V: OPERASI HIMPUNAN (Set) ---
                # Menggunakan set untuk melihat list unik sampel yang ditolak (REJECTED)
                sampel_reject = {item['sampel'] for item in riwayat_analisis if "REJECTED" in item['status']}
                if sampel_reject:
                    print(f"PERINGATAN SISTEM: Sampel yang gagal memenuhi standar mutu: {sampel_reject}")
                else:
                    print("SISTEM CLEAR: Semua pengujian yang dilakukan hari ini lolos standar mutu!")

        elif pilihan == '5':
            print("\nMenonaktifkan sistem... Sampai jumpa di shift laboratorium berikutnya!")
            break
            
        else:
            print("[WARNING] Pilihan menu tidak valid! Harap masukkan angka 1-5.")

if __name__ == "__main__":
    main()
