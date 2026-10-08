"""
Test script untuk Phase 1 - Task 4: Tes kirim email dengan CV terlampir.
Jalankan: python test_email.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import Config
from app.mailer.services import EmailService
from app.mailer.templates import render_template, TemplateData


def main():
    print("=" * 50)
    print("TEST KIRIM EMAIL - PHASE 1 TASK 4")
    print("=" * 50)

    errors = Config.validate()
    if errors:
        print("\nKONFIGURASI ERROR:")
        for err in errors:
            print(f"  - {err}")
        print("\nSilakan isi file .env terlebih dahulu (lihat .env.example)")
        return 1

    print(f"\nCV Path: {Config.CV_PATH}")
    print(f"Dari: {Config.MAIL_DEFAULT_SENDER}")
    print(f"Server: {Config.MAIL_SERVER}:{Config.MAIL_PORT}")

    test_email = input("\nMasukkan email tujuan test (email sendiri): ").strip()
    if not test_email:
        print("Email tidak boleh kosong.")
        return 1

    data = TemplateData(perusahaan="Test Perusahaan", posisi="Teknisi Jaringan")
    subject, body_text = render_template("teknisi_jaringan", data)
    body_html = body_text.replace("\n", "<br>")

    print(f"\nSubject: {subject}")
    print(f"Body preview: {body_text[:100]}...")

    confirm = input("\nKirim email test? (y/N): ").strip().lower()
    if confirm != "y":
        print("Dibatalkan.")
        return 0

    service = EmailService(Config)
    print("\nMengirim email...")
    result = service.send(
        to_email=test_email,
        subject=subject,
        body_html=body_html,
        body_text=body_text,
        attachment_path=Config.CV_PATH,
    )

    print(f"\n{'='*50}")
    if result.success:
        print("BERHASIL: Email terkirim!")
        print(f"Detail: {result.message}")
        print("\nCek inbox (dan folder spam) email tujuan.")
        return 0
    else:
        print("GAGAL: Email tidak terkirim.")
        print(f"Error: {result.message}")
        print(f"Kode: {result.error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())