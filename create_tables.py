# create_tables.py

from app import create_app
from models import db
from sqlalchemy import inspect

# Create the Flask app and push app context
app = create_app()
with app.app_context():
    # Create all tables defined on the models
    db.create_all()

    # (Optional) Print out which tables now exist
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("✔ Tables in database:", tables)
