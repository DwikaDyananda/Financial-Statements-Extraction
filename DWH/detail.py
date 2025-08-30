import PyPDF2
import re
import pandas as pd
import os
import mysql.connector
from mysql.connector import Error

def extract_ordered_sections_from_folder(folder_path, keyword, start_page):
    all_sections = []

    # Loop melalui semua file dalam folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            sections = extract_ordered_sections(pdf_path, keyword, start_page)
            # Tambahkan nama dokumen ke setiap section
            for section in sections:
                all_sections.append((filename, *section))

    return all_sections

def extract_ordered_sections(pdf_path, keyword, start_page):
    sections = []
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Ekstrak bagian yang terdaftar
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            
            if text:
                # Mencari pola yang cocok dengan format "angka. deskripsi"
                matches = re.findall(r'(\d+)\.\s+([^\n]+)', text)
                for match in matches:
                    number, description = match
                    # Memastikan hanya memasukkan bagian yang memiliki format yang benar
                    if number.isdigit() and len(description.strip()) > 0:
                        # Hanya masukkan jika angka 1-99
                        if 1 <= int(number) <= 99:
                            sections.append((number, description.strip()))

    # Mengurutkan berdasarkan nomor
    sections.sort(key=lambda x: int(x[0]))

    # Menghilangkan duplikat dan format yang tidak diinginkan
    unique_sections = []
    seen_numbers = set()
    for num, desc in sections:
        if num not in seen_numbers:
            unique_sections.append((num, desc))
            seen_numbers.add(num)

    return unique_sections

# Path ke folder yang berisi file PDF
folder_path = 'file_pdf'  # Ganti dengan path folder Anda
keyword = 'Catatan atas Laporan Keuangan'
start_page = 4

# Ekstrak bagian yang terdaftar dari semua file PDF dalam folder
ordered_sections = extract_ordered_sections_from_folder(folder_path, keyword, start_page)

# Buat DataFrame dari hasil
df = pd.DataFrame(ordered_sections, columns=['Nama Dokumen', 'Notes', 'Keterangan'])

# Reset index untuk tabel yang bersih
df.reset_index(drop=True, inplace=True)

# Tampilkan hasil dalam bentuk tabel
print(df)

def insert_into_database(df, host, database, user, password):
    try:
        # Membuat koneksi ke database
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Membuat tabel jika belum ada
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS tb_detail_notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nama_dokumen VARCHAR(255),
                notes VARCHAR(10),
                keterangan TEXT
            )
            '''
            cursor.execute(create_table_query)

            # Menyusun query untuk menyisipkan data
            insert_query = '''
            INSERT INTO ordered_sections (nama_dokumen, notes, keterangan)
            VALUES (%s, %s, %s)
            '''

            # Menyisipkan setiap baris dari DataFrame ke database
            for index, row in df.iterrows():
                cursor.execute(insert_query, (row['Nama Dokumen'], row['Notes'], row['Keterangan']))
            
            # Commit perubahan
            connection.commit()
            print(f"{cursor.rowcount} record(s) inserted successfully.")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

# Konfigurasi database
db_host = 'localhost'  # Ganti dengan host database Anda
db_name = 'db_calk'  # Ganti dengan nama database Anda
db_user = 'root'  # Ganti dengan username Anda
db_password = 'Dika007!#'  # Ganti dengan password Anda

# Panggil fungsi untuk menyisipkan data ke database
insert_into_database(df, db_host, db_name, db_user, db_password)