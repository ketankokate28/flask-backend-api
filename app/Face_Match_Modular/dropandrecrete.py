import sqlite3
import logging
from config import db_path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles database operations including table recreation."""

    def __init__(self, db_path):
        self.db_path = db_path

    def recreate_table(self):
        """Drops and recreates the Matchfacelogs table."""
        logger.debug(f"Dropping and recreating Matchfacelogs table in {self.db_path}")
        print(f"Dropping and recreating Matchfacelogs table in {self.db_path}")

        queries = [
            "DROP TABLE IF EXISTS Matchfacelogs;",
            """
            CREATE TABLE Matchfacelogs (
                capture_time TEXT,
                frame TEXT,
                suspect TEXT,
                distance REAL,
                cctv_id INTEGER,
                suspect_id INTEGER,
                created_date TEXT
            )
            """
        ]
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for query in queries:
                    cursor.execute(query)
                conn.commit()
            logger.info("Matchfacelogs table dropped and recreated successfully")
        except Exception:
            logger.exception("Failed to recreate Matchfacelogs table")

# Instantiate the DatabaseManager and recreate the table
db_manager = DatabaseManager(db_path)
db_manager.recreate_table()