from flask import Flask
from models import db  # your SQLAlchemy models file
import config

# 1. Initialize Flask app and SQLAlchemy
app = Flask(__name__)
app.config.from_mapping({
    'SQLALCHEMY_DATABASE_URI': f'sqlite:///{config.db_path}',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
})

db.init_app(app)

# 2. Import all models so they are registered on SQLAlchemy's metadata
#    This assumes models.py defines all your model classes and sets db = SQLAlchemy()
import models  # noqa: F401

# 3. Create all tables in one go
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("All tables created successfully.")
