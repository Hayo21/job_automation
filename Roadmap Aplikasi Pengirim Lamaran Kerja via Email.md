# Roadmap Aplikasi Pengirim Lamaran Kerja via Email

Disusun untuk Muniff Agustiansah · Stack: Flask + SQLite + Gmail (SMTP) · Perkiraan waktu: 7 hari (1-2 jam per hari)

Roadmap ini mengasumsikan Flask. Kalau memilih Laravel, urutan fase tetap sama.

## Fase 0: Persiapan (selesai)

- [x] Tujuan jelas: lamaran dikirim lewat email, bukan bot di platform
- [x] CV final dalam bentuk PDF
- [x] Target posisi: teknisi jaringan dan IT support
- [x] Aturan main: 20-30 email per hari, tiap email dipersonalisasi

## Fase 1: Setup dan tes kirim (hari 1) ✅

- [x] Task 1: Buat project, virtual environment, dan repo GitHub
- [x] Task 2: Aktifkan verifikasi 2 langkah di Gmail, lalu buat App Password
- [x] Task 3: Simpan kredensial di file `.env` (jangan masuk GitHub)
- [x] Task 4: Tes kirim satu email dengan CV terlampir ke email sendiri

Selesai kalau: email tes sampai di inbox dengan lampiran CV yang bisa dibuka. ✅ **TERKIRIM SEMPURNA**

## Fase 2: MVP, inti aplikasi (hari 2-3) ✅

- [x] Task 5: Form input: email HRD, nama perusahaan, posisi, kategori
- [x] Task 6: Buat 3 templat (Teknisi Jaringan, IT Support, Teknisi IT Pabrik) dengan kolom otomatis `{perusahaan}` dan `{posisi}`
- [x] Task 7: Halaman pratinjau sebelum kirim
- [x] Task 8: Tombol kirim, lalu CV PDF terlampir otomatis
- [x] Task 9: Validasi format email dan pesan sukses/gagal

Selesai kalau: bisa mengisi form, melihat pratinjau, lalu mengirim lamaran sungguhan dari website. ✅ **SELESAI**

## Fase 3: Riwayat dan pengaman (hari 4-5) ✅

- [x] Task 10: Tabel `lamaran` di SQLite (perusahaan, posisi, email, kategori, tanggal, status)
- [x] Task 11: Cek duplikat: peringatan kalau email atau perusahaan itu sudah pernah dikirimi
- [x] Task 12: Batas harian (misalnya maksimal 25) dan jeda antar kirim
- [x] Task 13: Halaman riwayat dengan filter kategori dan status
- [x] Task 14: Ubah status: Menunggu, Dipanggil, Ditolak

Selesai kalau: tidak bisa mengirim dua kali ke tujuan yang sama, dan semua lamaran tercatat. ✅ **SELESAI**

## Fase 4: Kenyamanan (hari 6) ✅

- [x] Task 15: Login sederhana, supaya hanya pemilik yang bisa memakai
- [x] Task 16: Penanganan email gagal kirim dan opsi kirim ulang
- [x] Task 17: Penanda lamaran yang lebih dari 7 hari belum dibalas (pengingat tindak lanjut)
- [x] Task 18: Ekspor riwayat ke CSV

Selesai kalau: ada login, retry gagal, reminder 7 hari, export CSV. ✅ **SELESAI**

## Fase 5: Penutup (hari 7) ✅

- [x] Task 19: Rapikan tampilan dan tulis README
- [x] Task 20: Unggah ke GitHub (tanpa `.env`)

Proyek ini nanti bisa masuk bagian proyek di CV, dengan satu baris seperti "Aplikasi pengelola lamaran kerja berbasis Flask". ✅ **SELESAI**

## Fitur ditunda (hanya kalau sempat)

- Beberapa versi CV per kategori
- Kirim terjadwal (misalnya otomatis jam 8 pagi)
- Deploy online supaya bisa diakses dari HP. Untuk awal, jalankan lokal saja, karena password email lebih aman tidak ditaruh di server publik.

## Aturan supaya cepat selesai

1. Selesaikan satu fase penuh sebelum lanjut ke fase berikutnya.
2. Setelah Fase 2, aplikasinya sudah bisa dipakai melamar. Fase 3 dan seterusnya bisa dikerjakan sambil jalan.
3. Jangan tambah fitur di luar daftar sebelum Fase 3 selesai.
