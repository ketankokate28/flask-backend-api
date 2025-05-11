import os
TEMP_FRAME_DIR = "D:/Face_Detect/flask-backend-api/temp_frames"
DB_PATH = 'D:/Face_Detect/flask-backend-api/database/face_match.db'
CHECK_INTERVAL = 1  # seconds
YOLO_MODEL_PATH = "yolov8n.pt"
os.makedirs(TEMP_FRAME_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
