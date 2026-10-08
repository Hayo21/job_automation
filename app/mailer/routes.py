from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app

from app.mailer.services import EmailService, RateLimiter, EmailResult
from app.mailer.templates import render_template as render_email_template, get_categories, TemplateData
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
        flash(result.message, "success")
    else:
        flash(f"Gagal: {result.message}", "danger")

    return redirect(url_for("mailer.index"))


def _validate_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1]