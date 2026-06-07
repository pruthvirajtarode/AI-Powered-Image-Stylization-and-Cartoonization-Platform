import sys
sys.path.append('.')
from modules.database import Database
db = Database()
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM transactions WHERE transaction_id LIKE 'pay_%'")
conn.commit()
print('Deleted duplicate pay_ transactions:', cursor.rowcount)
conn.close()
