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
            capture_time TEXT,
            frame        TEXT,
            suspect      TEXT,
            distance     REAL,
            created_date TEXT
        )
        """
    )
    conn.commit()
    conn.close()
    logger.info("Database initialized with WAL mode")


def log_to_db(capture_ts, frame, suspect, distance):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO Matchfacelogs VALUES (?, ?, ?, ?,?)",
            (capture_ts.isoformat(), frame, suspect, distance,datetime.now())
        )
        conn.commit()
        conn.close()
        logger.debug(f"Logged to DB: {frame}, {suspect}, {distance:.3f}")
    except Exception as e:
        logger.exception("Failed to log to DB")
