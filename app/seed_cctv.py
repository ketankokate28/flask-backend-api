# seed_cctv.py
"""
Populates the CCTV table with dummy data for testing purposes.
"""
import sqlite3
from config import DB_PATH
from datetime import datetime

print(DB_PATH)

def seed():
    # Ensure DB schema is up-to-date
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Dummy data for three CCTV entries
    today_date = datetime.now().strftime('%Y-%m-%d')
    now_ts     = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cameras = [
        (
            'Front Gate',                # name
            'Main Entrance',             # location
            'Oversees the main gate',    # description
            '192.168.1.10',              # ip_address
            28.6139,                     # latitude
            77.2090,                     # longitude
            10.5,                        # altitude
            'Fixed',                     # camera_type
            120.0,                       # camera_angle
            '1080p',                     # resolution
            'Active',                    # recording_status
            30,                          # storage_duration_days
            today_date,                  # installation_date
            today_date,                  # last_maintenance_date
            'Online',                    # status
            now_ts,                      # last_active_timestamp
            0,                           # error_count
            1,                           # auto_restart
            0,                           # is_critical
            0,                           # face_crop_enabled
            5,                           # frame_match_interval
            1,                           # alert_group_id
            101,                         # site_id
            'Gate Zone',                 # zone
            'Guard John',                # assigned_guard
            'AXIS P3225-LV',             # camera_model
            '/var/videos/front_gate'     # video_download_location
        ),
        (
            'Lobby Cam',                 # name
            'Ground Floor Lobby',        # location
            'Monitors lobby area',       # description
            '192.168.1.11',              # ip_address
            28.6140,                     # latitude
            77.2089,                     # longitude
            3.0,                         # altitude
            'PTZ',                       # camera_type
            360.0,                       # camera_angle
            '720p',                      # resolution
            'Active',                    # recording_status
            15,                          # storage_duration_days
            today_date,                  # installation_date
            today_date,                  # last_maintenance_date
            'Online',                    # status
            now_ts,                      # last_active_timestamp
            0,                           # error_count
            1,                           # auto_restart
            0,                           # is_critical
            1,                           # face_crop_enabled
            10,                          # frame_match_interval
            2,                           # alert_group_id
            101,                         # site_id
            'Lobby Zone',                # zone
            'Guard Alice',               # assigned_guard
            'Sony SNC-EB602R',           # camera_model
            '/var/videos/lobby'          # video_download_location
        ),
        (
            'Parking Lot',               # name
            'North Parking Area',        # location
            'Covers parking spots',      # description
            '192.168.1.12',              # ip_address
            28.6141,                     # latitude
            77.2091,                     # longitude
            5.2,                         # altitude
            'Fixed',                     # camera_type
            90.0,                        # camera_angle
            '4K',                        # resolution
            'Inactive',                  # recording_status
            60,                          # storage_duration_days
            today_date,                  # installation_date
            today_date,                  # last_maintenance_date
            'Offline',                   # status
            now_ts,                      # last_active_timestamp
            1,                           # error_count
            0,                           # auto_restart
            1,                           # is_critical
            0,                           # face_crop_enabled
            5,                           # frame_match_interval
            3,                           # alert_group_id
            102,                         # site_id
            'Parking Zone',              # zone
            'Guard Bob',                 # assigned_guard
            'Hikvision DS-2CD2142FWD-I',# camera_model
            '/var/videos/parking'        # video_download_location
        )
    ]

    # Bulk insert into CCTV
    c.executemany(
        '''INSERT INTO CCTV (
            name, location, description, ip_address,
            latitude, longitude, altitude, camera_type,
            camera_angle, resolution, recording_status,
            storage_duration_days, installation_date,
            last_maintenance_date, status,
            last_active_timestamp, error_count,
            auto_restart, is_critical, face_crop_enabled,
            frame_match_interval, alert_group_id,
            site_id, zone, assigned_guard,
            camera_model, video_download_location
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )''',
        cameras
    )
    conn.commit()
    conn.close()
    print('Seeded CCTV table with dummy data')

if __name__ == '__main__':
    seed()
