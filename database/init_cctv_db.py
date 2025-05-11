import sqlite3
import os

DB_PATH = "database/face_match_system_dev.db"

# Step 1: Create the DB file if it doesn't exist
if not os.path.exists(DB_PATH):
    print(f"📂 Creating new database: {DB_PATH}")
else:
    print(f"✅ Using existing database: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Step 2: Create the CCTV table
cursor.execute("""
CREATE TABLE IF NOT EXISTS CCTV (
  cctv_id INTEGER PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  location VARCHAR(255),
  description TEXT,
  ip_address VARCHAR(100),
  latitude REAL,
  longitude REAL,
  altitude INTEGER,
  camera_type VARCHAR(50),
  camera_angle VARCHAR(50),
  resolution VARCHAR(50),
  recording_status VARCHAR(10),
  storage_duration_days INTEGER DEFAULT 30,
  installation_date VARCHAR(20),
  last_maintenance_date VARCHAR(20),
  status VARCHAR(20) DEFAULT 'offline',
  last_active_timestamp VARCHAR(30),
  error_count INTEGER DEFAULT 0,
  auto_restart BOOLEAN DEFAULT 1,
  is_critical BOOLEAN DEFAULT 0,
  face_crop_enabled BOOLEAN DEFAULT 1,
  frame_match_interval INTEGER DEFAULT 5,
  alert_group_id INTEGER,
  site_id VARCHAR(50),
  zone VARCHAR(100),
  assigned_guard VARCHAR(100),
  camera_model VARCHAR(100),
  video_download_location VARCHAR(255)
)
""")

# Step 3: Insert 3 dummy camera records
cursor.executescript("""
DELETE FROM CCTV;

INSERT INTO CCTV (
  cctv_id, name, location, description, ip_address,
  latitude, longitude, altitude, camera_type, camera_angle,
  resolution, recording_status, storage_duration_days,
  installation_date, last_maintenance_date,
  status, error_count, auto_restart, is_critical,
  face_crop_enabled, frame_match_interval, alert_group_id,
  site_id, zone, assigned_guard, camera_model,
  video_download_location
) VALUES
(1, 'Test Webcam', 'Lab', 'USB webcam on laptop', '0',
 0.0, 0.0, 0, 'Fixed', 'Desk View',
 '1280x720', 'On', 7,
 '2024-01-01', '2024-04-01',
 'online', 0, 1, 1,
 1, 5, 1,
 'HQ', 'Zone A', 'Guard A', 'Logitech C920',
 'C:/recordings/test_webcam'),

(2, 'Gate Camera', 'Main Gate', 'Outdoor IP cam', '192.168.1.101',
 18.52, 73.85, 12, 'PTZ', 'Entrance',
 '1920x1080', 'On', 30,
 '2023-10-15', '2024-03-12',
 'offline', 2, 1, 0,
 1, 10, 2,
 'HQ', 'Zone B', 'Guard B', 'Hikvision DS-2CD1023G0',
 'C:/recordings/gate2'),

(3, 'Parking Lot', 'Lot A', 'Parking surveillance', 'rtsp://192.168.1.150/stream',
 19.07, 72.87, 10, 'Fixed', 'Parking',
 '1280x720', 'On', 14,
 '2024-02-05', '2024-04-05',
 'offline', 0, 1, 1,
 1, 5, 3,
 'HQ', 'Zone C', 'Guard C', 'CP Plus CP-VNC-TP24PL2',
 'C:/recordings/parking');
""")

conn.commit()

# Step 4: Show online cameras
print("📡 Online CCTV cameras:")
cursor.execute("SELECT cctv_id, name, ip_address FROM CCTV WHERE status = 'online'")
for row in cursor.fetchall():
    print("  →", row)

conn.close()
print("✅ CCTV database initialized.")
