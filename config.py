import os
from datetime import timedelta

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    DB_PATH ="C:/Users/ketan_kokate/Downloads/FaceONNX-main/FaceONNX-main/netstandard/Examples/Face-Matcher-UI/bin/Debug/net8.0-windows/Database/face_match.db"
    
    ##DB_PATH =os.path.join(BASE_DIR, 'database', 'face_match.db')  # Replace with actual filename
    ##SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"

    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://neondb_owner:npg_KNZdxz0Rku3O"
        "@ep-floral-sea-a81vd21b-pooler.eastus2.azure.neon.tech/face_match"
        "?sslmode=require&channel_binding=require"
    )

    ##SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/Ketan/R&D/flask-backend-api/database/face_match.db?check_same_thread=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ['http://localhost:4200',"http://localhost:8080"]
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Adjust if config.py is deeper in project

    matched_dir = os.path.join(BASE_DIR, 'matchedsuspect')
    suspect_dir = os.path.join(BASE_DIR, 'suspects')
    UPLOAD_FOLDER = suspect_dir
    # Default is local file system
    STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'blob')  # 'local' or 'blob'
    