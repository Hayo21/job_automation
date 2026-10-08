# Aplikasi Pengirim Lamaran Kerja via Email

Flask + SQLite + Gmail SMTP untuk mengirim lamaran kerja terpersonalisasi dengan CV terlampir otomatis.

## Fitur Utama

- **Form Input**: Perusahaan, posisi, email HRD, kategori template
- **3 Template Siap Pakai**: Teknisi Jaringan, IT Support, Teknisi IT Pabrik
- **Pratinjau Sebelum Kirim**: Lihat email lengkap dengan variabel terisi
- **CV Terlampir Otomatis**: PDF dilampirkan ke setiap email
- **Rate Limiting**: Jeda 30 detik antar kirim, batas 25 email/hari
- **Cek Duplikat**: Peringatan jika sudah pernah kirim ke email/perusahaan sama
- **Riwayat Lengkap**: Filter kategori/status, statistik, ubah status inline
- **Retry Gagal Kirim**: Simpan error, kirim ulang dengan 1 klik
- **Follow-up Reminder**: Badge ⏰ untuk lamaran >7 hari belum dibalas
- **Export CSV**: Download riwayat lengkap
- **Login Sederhana**: Password di `.env`, session-based

## Quick Start

```bash
# 1. Clone & masuk folder
cd job_automation

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Konfigurasi
copy .env.example .env         # Windows
# cp .env.example .env         # Linux/Mac
# Edit .env isi kredensial Gmail (lihat bawah)

# 5. Letakkan CV sebagai cv_Muniff.pdf di folder root

# 6. Test kirim email
python test_email.py

# 7. Jalankan aplikasi
python run.py
```

Buka http://127.0.0.1:5000 → login dengan password dari `.env`

## Konfigurasi .env

| Variabel | Deskripsi | Contoh |
|----------|-----------|--------|
| `SECRET_KEY` | Random string 32+ char | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `MAIL_SERVER` | SMTP Gmail | `smtp.gmail.com` |
| `MAIL_PORT` | Port TLS | `587` |
| `MAIL_USE_TLS` | Gunakan TLS | `True` |
| `MAIL_USERNAME` | Email Gmail Anda | `anda@gmail.com` |
| `MAIL_PASSWORD` | **App Password 16 char** | `abcdefghijklmnop` (tanpa spasi!) |
| `MAIL_DEFAULT_SENDER` | Sama dengan username | `anda@gmail.com` |
| `CV_PATH` | File CV PDF | `cv_Muniff.pdf` |
| `MAX_DAILY_EMAILS` | Batas harian | `25` |
| `EMAIL_DELAY_SECONDS` | Jeda antar kirim | `30` |
| `LOGIN_PASSWORD` | Password login app | `PasswordAman123!` |

### Cara Dapatkan App Password Gmail:
1. Aktifkan **2-Step Verification**: https://myaccount.google.com/security
2. Security → 2-Step Verification → **App passwords**
3. Select app: **Mail** → Device: **Other (Custom name)** → nama: `Job Automation`
4. **Generate** → copy 16 karakter **tanpa spasi** ke `MAIL_PASSWORD`

## Struktur Project

```
job_automation/
├── app/
│   ├── __init__.py          # Flask app factory + Jinja filter
│   ├── config.py            # Config + validasi .env
│   ├── auth.py              # Login decorator + password check
│   ├── models.py            # SQLite DB + CRUD + migration
│   ├── mailer/
│   │   ├── routes.py        # Blueprint: form, preview, send, riwayat, retry, export
│   │   ├── services.py      # EmailService (SMTP) + RateLimiter
│   │   └── templates.py     # 3 template email + render
│   └── templates/
│       ├── index.html       # Form input
│       ├── preview.html     # Pratinjau email
│       ├── riwayat.html     # Tabel riwayat + filter + aksi
│       └── login.html       # Halaman login
├── instance/                # SQLite DB (auto-create)
├── run.py                   # Entry point
├── test_email.py            # Test script Phase 1
├── requirements.txt
├── .env.example             # Template konfigurasi
├── .gitignore
└── README.md
```

## Alur Kerja

1. **Login** → `/login` (password dari `LOGIN_PASSWORD`)
2. **Form** → Isi perusahaan, posisi, email HRD, pilih template
3. **Preview** → Cek email lengkap, lihat "Terkirim hari ini: X/25"
4. **Kirim** → CV terlampir, rate limit 30 detik, simpan ke DB
5. **Riwayat** (`/riwayat`) → 
   - Stats cards: Total, Hari Ini, Menunggu, Dipanggil, Ditolak, Gagal, >7 Hari
   - Filter kategori & status
   - Ubah status inline (Menunggu/Dipanggil/Ditolak/Gagal)
   - 🔄 Retry untuk status Gagal
   - Badge ⏰ untuk follow-up >7 hari
   - **Export CSV** → download riwayat lengkap

## Keamanan

- Kredensial di `.env` (tidak masuk Git via `.gitignore`)
- App Password Gmail (bukan password utama)
- Validasi input & sanitasi email
- Rate limiting mencegah spam
- Bind ke `127.0.0.1` (lokal only, tidak expose ke internet)
- Session-based auth sederhana

## Tech Stack

- **Backend**: Flask 3.x, Python 3.10+
- **Database**: SQLite (file-based, zero-config)
- **Email**: smtplib + SSL/TLS (Gmail SMTP)
- **Frontend**: Vanilla HTML/CSS (no framework, lightweight)

## Roadmap

Lihat `Roadmap Aplikasi Pengirim Lamaran Kerja via Email.md` untuk detail 5 fase (7 hari).

## Fitur Ditunda (Optional)

- Multiple versi CV per kategori
- Kirim terjadwal (cron/job scheduler)
- Deploy online (VPS/Docker) - untuk awal jalankan lokal saja, lebih aman

## Lisensi

MIT - Bebas digunakan untuk keperluan pribadi.