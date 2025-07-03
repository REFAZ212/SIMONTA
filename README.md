# SIMONTA
SIMONTA adalah aplikasi berbasis web yang dibuat untuk mempermudah proses monitoring tugas akhir mahasiswa, mulai dari pengajuan hingga proses bimbingan dan sidang. Sistem ini dirancang untuk digunakan oleh tiga jenis pengguna: mahasiswa, dosen pembimbing, dan admin/prodi.
# Fitur Utama
Pengajuan judul tugas akhir oleh mahasiswa

Penunjukan dosen pembimbing

Manajemen jadwal bimbingan dan status bimbingan

Upload dokumen tugas akhir

Monitoring progres bimbingan

Proses verifikasi dan persiapan sidang

# Teknologi yang Digunakan
Backend: Django (Python)

Frontend: HTML, CSS, JavaScript, Bootstrap

Database: SQLite (bisa disesuaikan ke PostgreSQL/MySQL)

Tools tambahan: Django Admin, Django Forms, Django ORM

# Cara Menjalankan Proyek Ini
1. Persiapan Awal
Pastikan software berikut sudah terinstall:

Python ≥ 3.8

pip (Python package manager)

Git

(Opsional) Virtualenv untuk mengisolasi environment

2. Clone Repository
bash
Copy
Edit
git clone https://github.com/username/simonta.git
cd simonta
3. Buat Virtual Environment (Opsional tapi direkomendasikan)
bash
Copy
Edit
python -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows
4. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
Jika file requirements.txt belum dibuat, kamu bisa generate dengan:

bash
Copy
Edit
pip freeze > requirements.txt
5. Migrasi Database
bash
Copy
Edit
python manage.py makemigrations
python manage.py migrate
6. Jalankan Server
bash
Copy
Edit
python manage.py runserver
Buka browser dan akses:
http://127.0.0.1:8000/

# Akun Default (Opsional)
Kamu bisa menambahkan data dummy atau membuat superuser untuk mengakses Django Admin:

bash
Copy
Edit
python manage.py createsuperuser
📂 Struktur Folder Penting
csharp
Copy
Edit
simonta/
├── simonta/         # Folder project utama
├── monitoring/      # Aplikasi utama (apps) seperti mahasiswa, bimbingan, dll
├── templates/       # Template HTML
├── static/          # File CSS, JS, gambar
├── db.sqlite3       # Database default (SQLite)
├── manage.py
└── requirements.txt
💡 Catatan
Proyek ini masih dapat dikembangkan lebih lanjut, seperti integrasi notifikasi email atau integrasi QR Code untuk verifikasi.

Jika ingin deploy ke server seperti Heroku atau Render, pastikan konfigurasi tambahan dilakukan seperti setting ALLOWED_HOSTS, collectstatic, dan .env.

