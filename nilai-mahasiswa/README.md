# SiNilai — Sistem Penilaian Mahasiswa 🎓

Aplikasi web berbasis Docker untuk pengelolaan nilai mahasiswa oleh dosen.

---

## 🗂️ Struktur File

```
sinilai/
├── app.py                  # Backend Flask (logic, routing, auth)
├── requirements.txt        # Dependensi Python
├── Dockerfile              # Image untuk Flask app
├── docker-compose.yml      # Orkestrasi Docker (web + db)
├── README.md               # Dokumentasi ini
└── templates/
    ├── login.html          # Halaman login (dosen & mahasiswa)
    ├── dosen.html          # Dashboard dosen (CRUD nilai)
    └── mahasiswa.html      # Dashboard mahasiswa (read-only)
```

---

## 🗄️ Skema Database

### Tabel: `mahasiswa`

| Kolom   | Tipe          | Keterangan                         |
|---------|---------------|------------------------------------|
| id      | INTEGER (PK)  | Auto-increment primary key         |
| nama    | VARCHAR(100)  | Nama lengkap mahasiswa             |
| nim     | VARCHAR(20)   | NIM (unique), digunakan untuk login|
| clo1    | FLOAT         | Nilai CLO 1 (0–100)                |
| clo2    | FLOAT         | Nilai CLO 2 (0–100)                |
| clo3    | FLOAT         | Nilai CLO 3 (0–100)                |
| clo4    | FLOAT         | Nilai CLO 4 (0–100)                |

> **Nilai Akhir** dihitung otomatis: `(CLO1 + CLO2 + CLO3 + CLO4) / 4`

### Grade Otomatis
| Range      | Grade |
|------------|-------|
| ≥ 85       | A     |
| 75 – 84.99 | B     |
| 65 – 74.99 | C     |
| 55 – 64.99 | D     |
| < 55       | E     |

---

## 🚀 Cara Menjalankan

### Prasyarat
- Docker & Docker Compose sudah terinstall

### Langkah

```bash
# 1. Clone / salin folder proyek
cd sinilai/

# 2. Jalankan semua service
docker compose up --build

# 3. Tunggu hingga muncul pesan:
#    "Running on http://0.0.0.0:5000"
#    (DB healthcheck butuh ~15 detik pertama kali)

# 4. Buka browser
open http://localhost:5000
```

> Untuk menjalankan di background: `docker compose up --build -d`
> Untuk menghentikan: `docker compose down`
> Untuk menghapus data DB juga: `docker compose down -v`

---

## 🔐 Kredensial

### Dosen (hardcoded)
| Field    | Value      |
|----------|------------|
| Username | `dosen`    |
| Password | `dosen123` |

### Mahasiswa (contoh seed data)
| Nama           | NIM      |
|----------------|----------|
| Andi Prasetyo  | 2021001  |
| Siti Rahayu    | 2021002  |
| Budi Kurniawan | 2021003  |

Mahasiswa login menggunakan **Nama + NIM** (tidak perlu registrasi).

---

## ✨ Fitur Ringkasan

| Fitur                              | Dosen | Mahasiswa |
|------------------------------------|:-----:|:---------:|
| Login dengan username/password     | ✅    |           |
| Login dengan Nama + NIM            |       | ✅        |
| Tambah mahasiswa + nilai CLO       | ✅    |           |
| Edit nilai CLO mahasiswa           | ✅    |           |
| Hapus data mahasiswa               | ✅    |           |
| Lihat semua mahasiswa + statistik  | ✅    |           |
| Lihat nilai CLO sendiri            |       | ✅        |
| Edit nilai                         |       | ❌ (read-only) |

---

## ⚙️ Environment Variables (docker-compose.yml)

| Variabel        | Default                                      |
|-----------------|----------------------------------------------|
| DATABASE_URL    | `postgresql://admin:admin123@db:5432/nilaidb` |
| SECRET_KEY      | `sinilai-secret-key-2025`                    |
| FLASK_ENV       | `production`                                 |
