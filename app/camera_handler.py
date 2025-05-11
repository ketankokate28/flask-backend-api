import cv2
import multiprocessing
from db_utils import mark_stream_offline, log_frame_capture
from yolo_utils import process_frame_with_yolo
from file_utils import save_frame
from datetime import datetime

def run_camera_stream(cctv_id, name, stream_url, model, temp_frame_dir):
    print(f"[START] Camera {cctv_id} ({name}) — raw URL: {stream_url!r}")

    # If your stream_url is a digit (e.g. "0"), use it as an int for webcam
    if isinstance(stream_url, str) and stream_url.isdigit():
        idx = int(stream_url)
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        print(f"[INFO] Opening local webcam #{idx} with CAP_DSHOW")
    else:
        cap = cv2.VideoCapture(stream_url)
        print(f"[INFO] Opening network stream: {stream_url}")

    if not cap.isOpened():
        raise RuntimeError(f"❌ Cannot open stream for {name} (ID={cctv_id})")

    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"[ERROR] Lost stream from {name} ({cctv_id}), marking offline")
                mark_stream_offline(cctv_id)
                break

            frame_count += 1
            # only process every 5th frame, change as needed
            if frame_count % 5 == 0:
                try:
                    results = process_frame_with_yolo(frame, model)
                    for detected in results:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
                        filename = f"CAM{cctv_id}_frame_{timestamp}.jpg"
                        filepath = save_frame(temp_frame_dir, filename, frame)
                        log_frame_capture(cctv_id, filename)
                        print(f"[SAVED] {filepath}")
                except Exception as e:
                    print(f"[YOLO ERROR] {e}")

    finally:
        cap.release()
        print(f"[STOP] Camera {cctv_id} ({name}) — released capture")

def start_stream_process(cctv_id, name, stream_url, model, temp_frame_dir, active_processes):
    p = multiprocessing.Process(
        target=run_camera_stream,
        args=(cctv_id, name, stream_url, model, temp_frame_dir),
        daemon=True
    )
    p.start()
    active_processes[cctv_id] = p
    print(f"[PROCESS STARTED] CCTV {cctv_id}, PID={p.pid}")
