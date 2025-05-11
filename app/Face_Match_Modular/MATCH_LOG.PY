import sqlite3
from config import db_path

conn = sqlite3.connect(db_path)
try:
    # Add the column with a default date if it doesn't already exist
    conn.execute("""
        drop table MatchFacelogs
    """)
    conn.commit()
    print("Added created_date column.")
except sqlite3.OperationalError as e:
    # “duplicate column name” means it’s already been added
    if "duplicate column name" in str(e).lower():
        print("created_date column already exists.")
    else:
        raise
finally:
    conn.close()