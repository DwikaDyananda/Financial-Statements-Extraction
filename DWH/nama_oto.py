import pdfplumber
import re
import os
import pandas as pd

# Daftar bulan untuk pencocokan
bulan_list_id = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

bulan_list_en = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Fungsi untuk membaca teks dari file PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        # Ambil teks dari halaman pertama
        first_page = pdf.pages[0]
        text = first_page.extract_text()
    return text

# Fungsi untuk mengekstrak nama perusahaan dan bulan/tahun dari teks PDF
def find_company_and_month_year(text):
    # Pencocokan nama perusahaan yang dimulai dengan "PT" dan mengandung "Tbk" atau variasinya
    company_pattern = re.compile(r"(PT\s[\w\s]+Tbk[\w\s]*)", re.IGNORECASE)
    company_match = company_pattern.search(text)
    
    # Pencocokan bulan dan tahun (baik bahasa Indonesia maupun Inggris)
    months_years = []
    for bulan in bulan_list_id + bulan_list_en:  # Menggabungkan bulan dalam bahasa Indonesia dan Inggris
        # Regex untuk menemukan bulan dan tahun setelahnya
        pattern = re.compile(rf"(\b{bulan}\b)\s(\d{{4}})", re.IGNORECASE)
        
        # Cari kecocokan dengan pola regex
        matches = pattern.findall(text)
        
        for match in matches:
            month, year = match
            months_years.append((month.strip(), int(year)))  # Simpan bulan dan tahun sebagai tuple

    # Menyimpan nama perusahaan dan bulan/tahun yang ditemukan
    company_name = company_match.group(1) if company_match else "Tidak ditemukan"
    
    return company_name, months_years

# Fungsi untuk mendapatkan bulan dan tahun terbaru dari list bulan/tahun
def get_latest_month_and_year(months_years):
    # Jika tidak ada bulan atau tahun yang ditemukan
    if not months_years:
        return None, None
    
    # Menemukan tahun terbesar dan bulan yang sesuai dengan tahun tersebut
    latest_year = max(months_years, key=lambda x: x[1])[1]  # Ambil tahun terbesar
    latest_month = next(month for month, year in months_years if year == latest_year)  # Ambil bulan yang sesuai dengan tahun terbesar
    
    return latest_month, latest_year

# Fungsi untuk mengonversi bulan menjadi kuartal
def convert_month_to_quarter(month):
    # Normalisasi nama bulan
    month = month.strip().capitalize()
    
    q1 = ["Januari", "February", "Maret", "March"]
    q2 = ["April", "Mei", "May", "Juni", "June"]
    q3 = ["Juli", "July", "Agustus", "August", "September"]
    q4 = ["Oktober", "October", "November", "Desember", "December"]
    
    if month in q1:
        return "Q1"
    elif month in q2:
        return "Q2"
    elif month in q3:
        return "Q3"
    elif month in q4:
        return "Q4"
    else:
        return "Unknown"

# Fungsi untuk memproses banyak file PDF dalam folder dan menghasilkan DataFrame
def extract_data_from_folder(folder_path):
    data = []
    
    # Loop untuk memproses setiap file PDF dalam folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(pdf_path)
            
            # Temukan nama perusahaan dan bulan/tahun dari teks
            company_name, months_years = find_company_and_month_year(text)
            
            # Ambil bulan dan tahun terbaru
            latest_month, latest_year = get_latest_month_and_year(months_years)
            
            # Konversi bulan menjadi kuartal
            if latest_month and latest_year:
                quarter = convert_month_to_quarter(latest_month)
                data.append([company_name, quarter, latest_year])
    
    # Membuat DataFrame dari hasil ekstraksi
    df = pd.DataFrame(data, columns=["Nama Perusahaan", "Quartal", "Tahun Terbaru"])
    return df

# Ganti dengan path folder yang berisi file PDF
folder_path = "C:/TI-Dwika/Semester 7/Pangkalan Data/file_pdf"

# Ekstrak data dari folder dan tampilkan DataFrame
df = extract_data_from_folder(folder_path)
print(df)
