import os
import cv2

def create_directories(temp_frame_dir, db_path):
    os.makedirs(temp_frame_dir, exist_ok=True)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

def save_frame(directory, filename, frame):
    filepath = os.path.join(directory, filename)
    try:
        cv2.imwrite(filepath, frame)
        return filepath
    except Exception as e:
        print(f"[FILE SAVE ERROR] {e}")
        return None