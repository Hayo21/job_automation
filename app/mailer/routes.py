from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app

from app.mailer.services import EmailService, RateLimiter, EmailResult
from app.mailer.templates import render_template as render_email_template, get_categories, TemplateData
from app.models import (
    init_db, count_today, check_duplicate, save_lamaran,
    get_all_lamaran, update_status, get_stats, Lamaran
)
from app.config import Config


bp = Blueprint("mailer", __name__)

_email_service: EmailService | None = None
_rate_limiter: RateLimiter | None = None


def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService(current_app.config)
    return _email_service


def get_rate_limiter() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(current_app.config["EMAIL_DELAY_SECONDS"])
    return _rate_limiter


@bp.before_app_request
def ensure_db_init():
    init_db()


@bp.route("/", methods=["GET", "POST"])
def index():
    categories = get_categories()
    errors = current_app.config.get("CONFIG_ERRORS", [])
    for err in errors:
        flash(err, "danger")

    if request.method == "POST":
        return handle_preview()

    return render_template("index.html", categories=categories)


def handle_preview():
    perusahaan = request.form.get("perusahaan", "").strip()
    posisi = request.form.get("posisi", "").strip()
    email_hrd = request.form.get("email_hrd", "").strip()
    kategori = request.form.get("kategori", "").strip()

    if not all([perusahaan, posisi, email_hrd, kategori]):
        flash("Semua field wajib diisi.", "danger")
        return redirect(url_for("mailer.index"))

    if kategori not in get_categories():
        flash("Kategori tidak valid.", "danger")
        return redirect(url_for("mailer.index"))

    if not _validate_email(email_hrd):
        flash("Format email tidak valid.", "danger")
        return redirect(url_for("mailer.index"))

    # Cek duplikat
    dup = check_duplicate(perusahaan, email_hrd)
    if dup:
        flash(
            f"Peringatan: Sudah pernah kirim ke {dup.email} ({dup.perusahaan}) "
            f"pada {dup.tanggal.split()[0]} - Status: {dup.status}",
            "warning"
        )

    # Cek batas harian
    max_daily = current_app.config["MAX_DAILY_EMAILS"]
    sent_today = count_today()
    if sent_today >= max_daily:
        flash(f"Batas harian tercapai ({max_daily} email). Coba besok.", "danger")
        return redirect(url_for("mailer.index"))

    data = TemplateData(perusahaan=perusahaan, posisi=posisi)
    subject, body_text = render_email_template(kategori, data)
    body_html = body_text.replace("\n", "<br>")

    cv_filename = current_app.config["CV_PATH"].name

    return render_template(
        "preview.html",
        perusahaan=perusahaan,
        posisi=posisi,
        email_hrd=email_hrd,
        kategori=kategori,
        subject=subject,
        body_html=body_html,
        body_text=body_text,
        cv_filename=cv_filename,
        sent_today=sent_today,
        max_daily=max_daily,
    )


@bp.route("/send", methods=["POST"])
def send():
    perusahaan = request.form.get("perusahaan", "").strip()
    posisi = request.form.get("posisi", "").strip()
    email_hrd = request.form.get("email_hrd", "").strip()
    kategori = request.form.get("kategori", "").strip()
    subject = request.form.get("subject", "").strip()
    body_text = request.form.get("body_text", "")

    if not all([perusahaan, posisi, email_hrd, kategori, subject, body_text]):
        flash("Data tidak lengkap.", "danger")
        return redirect(url_for("mailer.index"))

    if not _validate_email(email_hrd):
        flash("Format email tidak valid.", "danger")
        return redirect(url_for("mailer.index"))

    # Cek batas harian sekali lagi (race condition protection)
    max_daily = current_app.config["MAX_DAILY_EMAILS"]
    if count_today() >= max_daily:
        flash(f"Batas harian tercapai ({max_daily} email).", "danger")
        return redirect(url_for("mailer.index"))

    body_html = body_text.replace("\n", "<br>")

    get_rate_limiter().wait_if_needed()

    result: EmailResult = get_email_service().send(
        to_email=email_hrd,
        subject=subject,
        body_html=body_html,
        body_text=body_text,
        attachment_path=current_app.config["CV_PATH"],
    )

    if result.success:
        save_lamaran(perusahaan, posisi, email_hrd, kategori)
        flash(result.message, "success")
    else:
        flash(f"Gagal: {result.message}", "danger")

    return redirect(url_for("mailer.index"))


@bp.route("/riwayat")
def riwayat():
    kategori_filter = request.args.get("kategori", "").strip()
    status_filter = request.args.get("status", "").strip()

    if kategori_filter and kategori_filter not in get_categories():
        kategori_filter = ""
    valid_status = {"Menunggu", "Dipanggil", "Ditolak"}
    if status_filter and status_filter not in valid_status:
        status_filter = ""

    lamaran_list = get_all_lamaran(kategori_filter or None, status_filter or None)
    stats = get_stats()
    categories = get_categories()

    return render_template(
        "riwayat.html",
        lamaran_list=lamaran_list,
        stats=stats,
        categories=categories,
        current_kategori=kategori_filter,
        current_status=status_filter,
        valid_status=valid_status,
    )


@bp.route("/riwayat/<int:lamaran_id>/status", methods=["POST"])
def ubah_status(lamaran_id: int):
    new_status = request.form.get("status", "").strip()
    if update_status(lamaran_id, new_status):
        flash(f"Status diubah ke {new_status}", "success")
    else:
        flash("Gagal mengubah status", "danger")
    return redirect(url_for("mailer.riwayat"))


def _validate_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1]