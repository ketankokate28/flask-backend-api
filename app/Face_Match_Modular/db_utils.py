# db_utils.py
import sqlite3
import logging
from config import db_path
from datetime import datetime

logger = logging.getLogger(__name__)

def init_db():
    logger.debug(f"Initializing DB: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS Matchfacelogs (
            capture_time TEXT NOT NULL,
            frame        TEXT NOT NULL,
            cctv_id      INTEGER NOT NULL,
            suspect_id   INTEGER,
            suspect      TEXT,
            distance     REAL NOT NULL,
            created_date TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    logger.info("Database initialized with WAL mode")


def log_to_db(capture_ts, frame, cctv_id, suspect_id, suspect, distance):
    """
    Logs a face match event to the Matchfacelogs table with CCTV and suspect IDs.
    """
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        created_date = datetime.now().isoformat()
        c.execute(
            """
            INSERT INTO Matchfacelogs (
                capture_time,
                frame,
                cctv_id,
                suspect_id,
                suspect,
                distance,
                created_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                capture_ts.isoformat(),
                frame,
                cctv_id,
                suspect_id,
                suspect,
                distance,
                created_date
            )
        )
        conn.commit()
        conn.close()
        logger.debug(f"Logged to DB: CCTV {cctv_id}, Suspect {suspect_id}, {frame}, {distance:.3f}")
    except Exception:
        logger.exception("Failed to log to DB")
