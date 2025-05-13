from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///C:/Ketan/R&D/flask-backend-api/database/face_match.db")

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
    print("✅ alembic_version table dropped.")
