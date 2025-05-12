import cv2
from datetime import datetime
import os
from ultralytics import YOLO
from db_utils import log_frame_capture, mark_stream_offline

TEMP_FRAME_DIR =  "D:/Face_Detect/flask-backend-api/temp_frames"
YOLO_MODEL_PATH = "yolov8n.pt"
model = YOLO(YOLO_MODEL_PATH)

def run_camera_stream(cctv_id, name, stream_url):
    print(f"[START] Camera {cctv_id} ({name})")
    cap = cv2.VideoCapture(stream_url)

    if not cap.isOpened():
        raise Exception(f"Cannot open stream for {name} ({cctv_id})")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"[ERROR] Lost stream from {name} ({cctv_id})")
            mark_stream_offline(cctv_id)
            break

        frame_count += 1
        if frame_count % 5 == 0:
            try:
                results = model(frame)
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        if cls_id == 0 and conf > 0.3:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
                            filename = f"CAM{cctv_id}_frame_{timestamp}.jpg"
                            filepath = os.path.join(TEMP_FRAME_DIR, filename)
                            cv2.imwrite(filepath, frame)
                            log_frame_capture(cctv_id, filename)
                            print(f"[SAVED] {filepath}")
                            break
            except Exception as e:
                print(f"[YOLO ERROR] {e}")

    cap.release()