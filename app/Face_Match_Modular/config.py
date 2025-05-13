# config.py
from datetime import timedelta
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret'
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
SQLALCHEMY_DATABASE_URI = 'sqlite:///D:/Face_Detect/flask-backend-api/database/face_match.db?check_same_thread=False'
SQLALCHEMY_TRACK_MODIFICATIONS = False
CORS_ORIGINS = ['http://localhost:4200']
# Paths
temp_frames      = "D:/Face_Detect/flask-backend-api/temp_frames"
matched_dir      = "D:/Face_Detect/flask-backend-api/matched_faces"
suspect_dir      = "D:/Face_Detect/flask-backend-api/suspects"
db_path          = 'D:/Face_Detect/flask-backend-api/database/face_match.db'
csv_log          = "D:/Face_Detect/flask-backend-api/database/match_log.csv"

# Thresholds & Timing
threshold        = 0.45
resize_width     = 500
blur_thresh      = 100.0
time_window      = timedelta(hours=100)
suspect_refresh  = timedelta(hours=500)
check_interval   = 5  # seconds
model_type       = "hog"

# Throttle window (only one alert per suspect per window)
ALERT_THROTTLE_WINDOW = timedelta(minutes=2)
# Concurrency
workers          = 4

# Email Alerts
e_mail_sender    = "bhaleraoprakash100@gmail.com"
e_mail_password  = "qwct xwtz dqel tmkk"
e_mail_receiver  = "pnmsrwnsh@gmail.com"

# Twilio Alerts
twilio_sid       = "YOUR_TWILIO_SID"
twilio_token     = "YOUR_TWILIO_TOKEN"
twilio_from      = "+19714064252"
twilio_to        = "+919890059930"

# ── Image‐prep thresholds ────────────────────────────────────────────────────
# Variance‐of‐Laplacian below this → considered blurry
blur_threshold      = float(os.getenv("BLUR_THRESHOLD",      "100.0"))
# Mean pixel < this (0–255) → consider “too dark” → boost brightness
brightness_threshold = float(os.getenv("BRIGHTNESS_THRESHOLD", "80.0"))