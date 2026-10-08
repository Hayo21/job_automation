# Aplikasi Pengirim Lamaran Kerja via Email

Flask + SQLite + Gmail SMTP untuk mengirim lamaran kerja terpersonalisasi dengan CV terlampir.

## Setup Cepat

```bash
# 1. Clone & masuk folder
cd job_automation

# 2. Buat virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Salin .env.example ke .env dan isi kredensial
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# 5. Letakkan CV Anda sebagai cv.pdf di folder root

# 6. Test kirim email (Phase 1)
python test_email.py

# 7. Jalankan aplikasi
python run.py
```

Buka http://127.0.0.1:5000

## Konfigurasi .env

| Variabel | Deskripsi |
|----------|-----------|
| `MAIL_USERNAME` | Email Gmail Anda |
| `MAIL_PASSWORD` | **App Password** 16 karakter (bukan password login) |
| `MAIL_DEFAULT_SENDER` | Sama dengan MAIL_USERNAME |
| `CV_PATH` | Path ke file CV PDF (default: cv.pdf) |
| `MAX_DAILY_EMAILS` | Batas harian (default: 25) |
| `EMAIL_DELAY_SECONDS` | Jeda antar kirim (default: 30) |

### Cara Dapatkan App Password Gmail:
1. Aktifkan 2-Step Verification di Google Account
2. Security > 2-Step Verification > App passwords
3. Buat app password baru > pilih "Mail" > "Other" > nama "Job Automation"
4. Copy 16 karakter password (tanpa spasi) ke MAIL_PASSWORD

## Struktur Project

```
job_automation/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Konfigurasi & validasi
│   ├── mailer/
│   │   ├── routes.py        # Blueprint routes
│   │   ├── services.py      # EmailService, RateLimiter
│   │   └── templates.py     # Template email per kategori
│   └── templates/
│       └── index.html       # Form UI
├── instance/                # SQLite DB (nanti Phase 3)
├── run.py                   # Entry point
├── test_email.py            # Test script Phase 1
├── requirements.txt
├── .env.example
├── .gitignore
└── cv.pdf                   # CV Anda (jangan commit)
```

## Fitur Phase 1 (MVP)
- Form input: perusahaan, posisi, email HRD, kategori
- 3 template: Teknisi Jaringan, IT Support, Teknisi IT Pabrik
- Pratinjau otomatis via `{perusahaan}` & `{posisi}`
- CV PDF terlampir otomatis
- Validasi email & error handling SMTP
- Rate limiting (jeda 30 detik default)

## Keamanan
- Kredensial di `.env` (tidak masuk Git)
- App Password Gmail (bukan password utama)
- Validasi input & sanitasi
- Rate limiting防刷
- Hanya bind ke 127.0.0.1 (lokal only)

## Roadmap
Lihat `Roadmap Aplikasi Pengirim Lamaran Kerja via Email.md`

## Lisensi
MIT - Bebas digunakan untuk keperluan pribadi.