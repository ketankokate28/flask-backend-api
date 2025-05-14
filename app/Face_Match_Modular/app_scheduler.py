# app_scheduler.py

from flask import Flask
from db_models import db
from flask_migrate import Migrate
import config

migrate = Migrate()
def create_app():
    """
    Factory that creates and configures a Flask app,
    including SQLAlchemy initialization.
    """
    app = Flask(__name__)
    # Load config values (including SQLALCHEMY_DATABASE_URI)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # If you have blueprints, register them here, e.g.:
    # from yourmodule.suspect_api import suspect_bp
    # app.register_blueprint(suspect_bp, url_prefix='/api/suspects')

    return app
