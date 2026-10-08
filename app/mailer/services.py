import smtplib
import ssl
import time
from email.message import EmailMessage
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from app.config import Config


@dataclass
class EmailResult:
    success: bool
    message: str
    error: Optional[str] = None


class EmailService:
    def __init__(self, config: Config):
        self.config = config
        self._context = ssl.create_default_context()

    def send(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        attachment_path: Optional[Path] = None,
    ) -> EmailResult:
        if not self._validate_email(to_email):
            return EmailResult(False, "Format email tidak valid", "invalid_email")

        msg = EmailMessage()
        msg["From"] = self.config.MAIL_DEFAULT_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body_text)
        msg.add_alternative(body_html, subtype="html")

        if attachment_path and attachment_path.exists():
            self._attach_file(msg, attachment_path)
        elif attachment_path:
            return EmailResult(False, f"Lampiran tidak ditemukan: {attachment_path}", "missing_attachment")

        return self._send_message(msg, to_email)

    def _validate_email(self, email: str) -> bool:
        return "@" in email and "." in email.split("@")[-1]

    def _attach_file(self, msg: EmailMessage, path: Path) -> None:
        with open(path, "rb") as f:
            file_data = f.read()
        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="pdf",
            filename=path.name,
        )

    def _send_message(self, msg: EmailMessage, to_email: str) -> EmailResult:
        try:
            with smtplib.SMTP(self.config.MAIL_SERVER, self.config.MAIL_PORT) as server:
                server.ehlo()
                if self.config.MAIL_USE_TLS:
                    server.starttls(context=self._context)
                    server.ehlo()
                server.login(self.config.MAIL_USERNAME, self.config.MAIL_PASSWORD)
                server.send_message(msg)
            return EmailResult(True, f"Email terkirim ke {to_email}")
        except smtplib.SMTPAuthenticationError:
            return EmailResult(False, "Autentikasi gagal. Cek App Password.", "auth_failed")
        except smtplib.SMTPRecipientsRefused:
            return EmailResult(False, "Email penerima ditolak oleh server.", "recipient_refused")
        except smtplib.SMTPException as e:
            return EmailResult(False, f"Gagal kirim email: {str(e)}", "smtp_error")
        except Exception as e:
            return EmailResult(False, f"Error tidak terduga: {str(e)}", "unknown_error")


class RateLimiter:
    def __init__(self, delay_seconds: int):
        self.delay_seconds = delay_seconds
        self._last_sent = 0.0

    def wait_if_needed(self) -> None:
        elapsed = time.time() - self._last_sent
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self._last_sent = time.time()