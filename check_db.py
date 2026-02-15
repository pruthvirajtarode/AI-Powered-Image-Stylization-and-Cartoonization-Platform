
import sqlite3
import os

db_path = "c:/Users/pruth/OneDrive/Desktop/AI-Powered Image Stylization and Cartoonization Platform/backend/data/users.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT processed_filename FROM processing_history ORDER BY created_at DESC LIMIT 10")
rows = cursor.fetchall()
for row in rows:
    print(row['processed_filename'])
conn.close()
