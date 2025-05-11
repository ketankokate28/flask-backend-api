import sqlite3
from datetime import datetime

DB_PATH = 'D:/Face_Detect/flask-backend-api/database/face_match.db'

def mark_stream_offline(cctv_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE CCTV SET status = 'offline', error_count = error_count + 1 WHERE id = ?", (cctv_id,))
        conn.commit()
        conn.close()
        print(f"[OFFLINE] CCTV {cctv_id} marked as offline")
    except Exception as e:
        print(f"[DB ERROR - OFFLINE] {e}")

def log_frame_capture(cctv_id, filename):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS FrameLog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cctv_id INTEGER,
                filename TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute("INSERT INTO FrameLog (cctv_id, filename, timestamp) VALUES (?, ?, ?)",
                       (cctv_id, filename, timestamp))
        cursor.execute("UPDATE CCTV SET last_active_timestamp = ? WHERE id = ?", (timestamp, cctv_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR - LOG] {e}")

def fetch_online_cameras():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, ip_address FROM CCTV")
        cameras = cursor.fetchall()
        conn.close()
        return cameras
    except Exception as e:
        print(f"[DB ERROR - FETCH] {e}")
        return []