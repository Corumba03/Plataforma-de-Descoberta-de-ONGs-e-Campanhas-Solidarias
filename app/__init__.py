from flask import Flask
from app.main.models import db
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    from app.main.controllers import main_bp
    db.init_app(app)
    app.register_blueprint(main_bp)

    return app
