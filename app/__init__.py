from datetime import datetime
from flask import Flask
from app.config import Config


def _datetime_diff(value: str) -> int:
    """Calculate days difference from date string to now"""
    try:
        dt = datetime.strptime(value.split()[0], "%Y-%m-%d")
        return (datetime.now() - dt).days
    except Exception:
        return 0


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["CONFIG_ERRORS"] = Config.validate()

    app.jinja_env.filters["datetime_diff"] = _datetime_diff

    from app.mailer.routes import bp as mailer_bp
    app.register_blueprint(mailer_bp)

    return app