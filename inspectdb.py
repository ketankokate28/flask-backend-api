import sqlite3

# Path to your SQLite database file
db_path = 'C:/Ketan/R&D/flask-backend-api/database/face_match.db'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# # Drop the 'notifications' table if it exists
# cursor.execute("DROP TABLE IF EXISTS notifications")

# # Commit the changes and close the connection
# conn.commit()
# #conn.close()

# print("Notifications table dropped successfully.")

# Show all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:", tables)

# Check the structure of the 'notifications' table
cursor.execute("PRAGMA table_info(notifications);")
columns = cursor.fetchall()
print("Columns in 'notifications' table:", columns)

# Close the connection
conn.close()
