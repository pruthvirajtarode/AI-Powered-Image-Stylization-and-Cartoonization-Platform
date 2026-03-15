import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from modules.database import db
import sqlite3

conn = sqlite3.connect(db.db_path)
conn.row_factory = sqlite3.Row

cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor]
print("Tables:", tables)

for t in tables:
    cursor2 = conn.execute(f"PRAGMA table_info({t})")
    cols = [row[1] for row in cursor2]
    print(f"  {t}: {cols}")

conn.close()

# Check settings / env vars
import config.settings as settings
print("\n--- Settings ---")
print("GOOGLE_CLIENT_ID:", settings.GOOGLE_CLIENT_ID)
print("RAZORPAY_KEY_ID:", repr(settings.RAZORPAY_KEY_ID))
print("SMTP_USER:", repr(settings.SMTP_USER))
print("DATABASE_PATH:", settings.DATABASE_PATH)
print("TEMP_FOLDER exists:", settings.TEMP_FOLDER.exists())

# Check image_processor methods
from modules.image_processing import image_processor
methods = [m for m in dir(image_processor) if not m.startswith('_')]
print("\nImageProcessor methods:", methods)

# Check if get_image_statistics vs get_image_stats discrepancy
print("\nHas get_image_statistics:", hasattr(image_processor, 'get_image_statistics'))
print("Has get_image_stats:", hasattr(image_processor, 'get_image_stats'))
