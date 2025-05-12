#!/usr/bin/env python3
"""
create_notifications_table.py

Script to create the Notifications table and indexes in the SQLite database.
"""
import sqlite3
from config import db_path

def create_notifications_table():
    conn = sqlite3.connect(db_path)
    # Enable Write-Ahead Logging for better concurrency
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

# Drop existing Notifications table if it exists
    cursor.execute(
        "DROP TABLE IF EXISTS Notifications;"
    )

    # Create Notifications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Notifications (
      notification_id     INTEGER    PRIMARY KEY AUTOINCREMENT,
      cctv_id             INTEGER    NULL,
      suspect_id          INTEGER    NULL,
      event_time          TEXT       NOT NULL,
      notification_type   TEXT       NOT NULL,
      message             TEXT       NOT NULL,
      channel             TEXT       NOT NULL,
      delivery_status     TEXT       NOT NULL DEFAULT 'PENDING',
      delivery_time       TEXT       NULL,
      created_at          TEXT       NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (cctv_id)    REFERENCES CCTV(cctv_id),
      FOREIGN KEY (suspect_id) REFERENCES suspects(suspect_id)
    );
    """)

    # Create indexes for performance
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_notifications_event_time ON Notifications(event_time);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_notifications_cctv_id ON Notifications(cctv_id);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_notifications_suspect_id ON Notifications(suspect_id);"
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("Notifications table and indexes created successfully.")

if __name__ == "__main__":
    create_notifications_table()
