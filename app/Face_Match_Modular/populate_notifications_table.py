"""
populate_notifications_table.py

Script to insert sample notification logs into the Notifications table.
"""
import sqlite3
from datetime import datetime, timedelta
from config import db_path

def populate_notifications():
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    # Sample entries: (cctv_id, suspect_id, event_time, notification_type, message, channel, delivery_status, delivery_time)
    entries = [
        (
            1,
            42,
            (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
            'MATCH',
            'Suspect #42 (John Doe) matched on CAM1',
            'EMAIL',
            'SENT',
            (datetime.utcnow() - timedelta(minutes=9)).isoformat()
        ),
        (
            2,
            None,
            (datetime.utcnow() - timedelta(minutes=8)).isoformat(),
            'UNMATCH',
            'No suspect matched on CAM2',
            'SMS',
            'SENT',
            (datetime.utcnow() - timedelta(minutes=7)).isoformat()
        ),
        (
            3,
            7,
            (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            'MATCH',
            'Suspect #7 (Jane Smith) matched on CAM3',
            'VOICE',
            'FAILED',
            None
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO Notifications (
            cctv_id,
            suspect_id,
            event_time,
            notification_type,
            message,
            channel,
            delivery_status,
            delivery_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        entries
    )
    conn.commit()
    cursor.close()
    conn.close()
    print("Sample notification logs inserted successfully.")

if __name__ == "__main__":
    populate_notifications()
