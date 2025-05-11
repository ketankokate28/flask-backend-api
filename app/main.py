import time
from db_utils import fetch_online_cameras
from camera_handler import start_stream_process
from file_utils import create_directories
from yolo_utils import initialize_yolo

TEMP_FRAME_DIR = "D:/Face_Detect/flask-backend-api/temp_frames"
DB_PATH = 'D:/Face_Detect/flask-backend-api/database/face_match.db'
YOLO_MODEL_PATH = "yolov8n.pt"
CHECK_INTERVAL = 1  # seconds

if __name__ == "__main__":
    create_directories(TEMP_FRAME_DIR, DB_PATH)
    model = initialize_yolo(YOLO_MODEL_PATH)
    active_processes = {}

    print(f"📡 Watching DB: {DB_PATH}")
    while True:
        online_cameras = fetch_online_cameras()
        for cam in online_cameras:
            cctv_id, name, url = cam
            if cctv_id not in active_processes or not active_processes[cctv_id].is_alive():
                start_stream_process(cctv_id, name, url, model, TEMP_FRAME_DIR, active_processes)
        time.sleep(CHECK_INTERVAL)
        