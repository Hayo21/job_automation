import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    CV_PATH = BASE_DIR / os.getenv("CV_PATH", "cv.pdf")
    MAX_DAILY_EMAILS = int(os.getenv("MAX_DAILY_EMAILS", 25))
    EMAIL_DELAY_SECONDS = int(os.getenv("EMAIL_DELAY_SECONDS", 30))
    LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "changeme")

    @classmethod
    def validate(cls) -> list[str]:
        errors = []
        if not cls.MAIL_USERNAME:
            errors.append("MAIL_USERNAME tidak diset di .env")
        if not cls.MAIL_PASSWORD:
            errors.append("MAIL_PASSWORD tidak diset di .env")
        if not cls.MAIL_DEFAULT_SENDER:
            errors.append("MAIL_DEFAULT_SENDER tidak diset di .env")
        if not cls.CV_PATH.exists():
            errors.append(f"CV tidak ditemukan: {cls.CV_PATH}")
        if cls.LOGIN_PASSWORD == "changeme":
            errors.append("LOGIN_PASSWORD masih default! Ganti di .env")
        return errors