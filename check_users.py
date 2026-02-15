
import sqlite3
import os

db_path = "c:/Users/pruth/OneDrive/Desktop/AI-Powered Image Stylization and Cartoonization Platform/backend/data/users.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT id, username, auto_delete_days FROM users")
rows = cursor.fetchall()
for row in rows:
    print(dict(row))
conn.close()
