from flask import Flask
from app.config import Config


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["CONFIG_ERRORS"] = Config.validate()

    from app.mailer.routes import bp as mailer_bp
    app.register_blueprint(mailer_bp)

    return app