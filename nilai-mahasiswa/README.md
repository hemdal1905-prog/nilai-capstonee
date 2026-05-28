# SiNilai — Sistem Manajemen Nilai Mahasiswa
> Implementasi Docker Container untuk Aplikasi Manajemen Nilai Mahasiswa Berbasis Cloud

---

## 📋 Fitur Utama

### 👨‍🏫 Role Dosen
- Login ke dashboard khusus dosen
- **Tambah nilai** mahasiswa (pilih matkul, semester, tahun ajaran)
- **Edit & hapus nilai** yang sudah diinput
- **Cari & filter** nilai berdasarkan nama/NIM/matkul/semester
- Lihat statistik: total mahasiswa, matkul, dan nilai yang diinput

### 👨‍🎓 Role Mahasiswa
- Login ke dashboard mahasiswa
- Lihat **IPK (Indeks Prestasi Kumulatif)** secara real-time
- Lihat ringkasan nilai terbaru
- **Transkrip lengkap** dengan fitur search & filter
- Info total SKS yang ditempuh

---

## 🛠️ Tech Stack

| Layer      | Teknologi             |
|------------|-----------------------|
| Backend    | Python Flask 3.0      |
| Database   | PostgreSQL 15         |
| ORM        | Flask-SQLAlchemy      |
| Auth       | Werkzeug (hash pw)    |
| Container  | Docker + Compose      |
| Frontend   | Jinja2 + CSS (no fw)  |

---

## 🚀 Cara Menjalankan

### Metode 1: Docker (Direkomendasikan)

**Prasyarat:** Docker Desktop terinstall

```bash
# 1. Clone / download project
cd nilai-mahasiswa

# 2. Jalankan semua service
docker compose up --build

# 3. Buka browser
# http://localhost:5000
```

Untuk stop:
```bash
docker compose down
```

Untuk hapus database (reset total):
```bash
docker compose down -v
```

---

### Metode 2: Tanpa Docker (Local)

**Prasyarat:** Python 3.10+, PostgreSQL terinstall

```bash
# 1. Buat virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Siapkan database PostgreSQL
# Buat database 'nilaidb' di PostgreSQL Anda
# lalu sesuaikan .env

cp .env.example .env
# Edit .env: ubah DATABASE_URL ke koneksi lokal Anda
# Contoh: postgresql://postgres:password@localhost:5432/nilaidb

# 4. Jalankan
python app.py

# Buka: http://localhost:5000
```

---

## 🔑 Akun Demo

| Role      | Username | Password  |
|-----------|----------|-----------|
| Dosen     | dosen1   | dosen123  |
| Dosen     | dosen2   | dosen123  |
| Mahasiswa | budi     | mhs123    |
| Mahasiswa | ani      | mhs123    |
| Mahasiswa | reza     | mhs123    |
| Mahasiswa | dewi     | mhs123    |
| Mahasiswa | fajar    | mhs123    |

---

## 📁 Struktur Project

```
nilai-mahasiswa/
├── app.py                  # Main Flask app + routes + models
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── static/
│   ├── css/style.css       # Semua styling
│   └── js/main.js
└── templates/
    ├── base.html           # Layout + sidebar
    ├── login.html
    ├── dosen_dashboard.html
    ├── dosen_nilai.html
    ├── dosen_mahasiswa.html
    ├── tambah_nilai.html
    ├── edit_nilai.html
    ├── mahasiswa_dashboard.html
    └── mahasiswa_transkrip.html
```

---

## 🐳 Arsitektur Docker

```
┌─────────────────────────────┐
│      Docker Network         │
│                             │
│  ┌──────────┐  ┌─────────┐  │
│  │  sinilai │  │sinilai  │  │
│  │   _web   │──│  _db    │  │
│  │ :5000    │  │ :5432   │  │
│  └──────────┘  └─────────┘  │
│         Flask    PostgreSQL  │
└─────────────────────────────┘
         ↓
   localhost:5000
```

---

## 📊 Konversi Nilai

| Nilai Angka | Huruf | Bobot |
|-------------|-------|-------|
| ≥ 85        | A     | 4.00  |
| ≥ 80        | A-    | 3.70  |
| ≥ 75        | B+    | 3.30  |
| ≥ 70        | B     | 3.00  |
| ≥ 65        | B-    | 2.70  |
| ≥ 60        | C+    | 2.30  |
| ≥ 55        | C     | 2.00  |
| ≥ 50        | C-    | 1.70  |
| ≥ 45        | D     | 1.00  |
| < 45        | E     | 0.00  |

---

## 🔒 Keamanan

- Password di-hash dengan **Werkzeug PBKDF2-SHA256**
- Session-based authentication dengan secret key
- Role-based access control (dosen vs mahasiswa)
- CSRF protection via form POST + session check

---

*Dikembangkan sebagai Capstone Project — Cloud-based Student Grade Management System*
