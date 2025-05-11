import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///D:/Face_Detect/flask-backend-api/database/face_match.db?check_same_thread=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ['http://localhost:4200']
