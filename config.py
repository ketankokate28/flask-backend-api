import os
from datetime import timedelta

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    DB_PATH ="C:/Users/ketan_kokate/Downloads/FaceONNX-main/FaceONNX-main/netstandard/Examples/Face-Matcher-UI/bin/Debug/net8.0-windows/Database/face_match.db"
    
    ##DB_PATH =os.path.join(BASE_DIR, 'database', 'face_match.db')  # Replace with actual filename
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    ##SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/Ketan/R&D/flask-backend-api/database/face_match.db?check_same_thread=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ['http://localhost:4200',"http://localhost:8080"]
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Adjust if config.py is deeper in project

    matched_dir = os.path.join(BASE_DIR, 'matched_faces')
    suspect_dir = os.path.join(BASE_DIR, 'suspects')
