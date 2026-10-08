from functools import wraps
from flask import session, redirect, url_for, request, flash, current_app


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("mailer.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def check_password(password: str) -> bool:
    return password == current_app.config["LOGIN_PASSWORD"]