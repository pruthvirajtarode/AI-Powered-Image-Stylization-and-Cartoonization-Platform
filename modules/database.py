"""
Database operations for user management
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import config.settings as settings

# Attempt PostgreSQL Import for Production
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False


class Database:
    """Handle all database operations"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        self.db_path = db_path or settings.DATABASE_PATH
        self.db_url = os.getenv("DATABASE_URL")
        self.is_postgres = self.db_url is not None and HAS_POSTGRES
        self.placeholder = "%s" if self.is_postgres else "?"
        self.bool_true = "TRUE" if self.is_postgres else "1"
        self.bool_false = "FALSE" if self.is_postgres else "0"
        self.init_database()
    
    def get_connection(self):
        """Get database connection (PostgreSQL or SQLite)"""
        if self.is_postgres:
            conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            return conn
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Determine ID syntax
        id_serial = "SERIAL PRIMARY KEY" if self.is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
        
        # FRESH START: Drop table if schema is broken (Only works if no critical data yet)
        if self.is_postgres:
            try:
                print("♻️ ATTEMPTING TO DROP TABLE 'users'...")
                # Check if we need to fix the boolean column issue by forcing a recreation
                cursor.execute("DROP TABLE IF EXISTS users CASCADE")
                conn.commit() # Commit DROP immediately!
                print("✅ TABLE 'users' DROPPED.")
            except Exception as e:
                print(f"❌ DROP TABLE FAILED: {e}")
                conn.rollback()

        # Users table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id {id_serial},
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT {self.bool_true},
                is_verified BOOLEAN DEFAULT {self.bool_false},
                last_logout TIMESTAMP,
                last_active TIMESTAMP
            )
        """)

        # Migration Helper
        def add_column(table, column, type_def):
            try:
                cursor.execute(f"SELECT {column} FROM {table} LIMIT 1")
            except:
                print(f"🚀 Migrating {table}: Adding '{column}'...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")
                conn.commit()

        add_column("users", "role", "TEXT DEFAULT 'user'")
        add_column("users", "last_logout", "TIMESTAMP")
        add_column("users", "last_active", "TIMESTAMP")
        add_column("users", "is_verified", f"BOOLEAN DEFAULT {self.bool_false}")

        # Create or Update Default Admin User
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            import bcrypt
            print("👤 Initializing System: Creating default administrator...")
            password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(f"""
                INSERT INTO users (username, email, password_hash, full_name, role, is_verified)
                VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})
            """, ("admin", "admin@toonify.ai", password_hash, "System Admin", "admin", self.bool_true if self.is_postgres else 1))
            conn.commit()
        
        # Other Tables
        cursor.execute(f"CREATE TABLE IF NOT EXISTS verification_codes (id {id_serial}, email TEXT NOT NULL, code TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, expires_at TIMESTAMP NOT NULL)")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS transactions (id {id_serial}, user_id INTEGER NOT NULL, transaction_id TEXT UNIQUE NOT NULL, amount REAL NOT NULL, currency TEXT DEFAULT 'usd', status TEXT DEFAULT 'pending', payment_method TEXT, image_filename TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS processing_history (id {id_serial}, user_id INTEGER NOT NULL, original_filename TEXT NOT NULL, processed_filename TEXT NOT NULL, style TEXT NOT NULL, processing_time REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS user_logs (id {id_serial}, user_id INTEGER NOT NULL, action TEXT NOT NULL, details TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

        conn.commit()
        conn.close()
    
    # User Operations
    def create_user(self, username: str, email: str, password_hash: str, 
                   full_name: str = None) -> Optional[int]:
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})
            """, (username, email, password_hash, full_name))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE username = {self.placeholder}", (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE email = {self.placeholder}", (email,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE id = {self.placeholder}", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def update_last_login(self, user_id: int):
        """Update user's last login timestamp and log it"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE users SET last_login = CURRENT_TIMESTAMP
            WHERE id = {self.placeholder}
        """, (user_id,))
        conn.commit()
        conn.close()
        self.log_user_activity(user_id, "login", "User signed into the platform")

    def update_last_logout(self, user_id: int):
        """Update user's last logout timestamp and log it"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE users SET last_logout = CURRENT_TIMESTAMP
            WHERE id = {self.placeholder}
        """, (user_id,))
        conn.commit()
        conn.close()
        self.log_user_activity(user_id, "logout", "User signed out (Time-out)")

    def update_last_active(self, user_id: int):
        """Silently update user's last activity heartbeat"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE users SET last_active = CURRENT_TIMESTAMP
            WHERE id = {self.placeholder}
        """, (user_id,))
        conn.commit()
        conn.close()

    def log_user_activity(self, user_id: int, action: str, details: str = None):
        """Log user activity for admin monitoring"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO user_logs (user_id, action, details)
            VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder})
        """, (user_id, action, details))
        conn.commit()
        conn.close()
    
    def update_user_profile(self, user_id: int, **kwargs):
        """Update user profile information"""
        allowed_fields = ['full_name', 'email']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET {set_clause} WHERE id = {self.placeholder}", values)
        conn.commit()
        conn.close()
        return True
    
    # Transaction Operations
    def create_transaction(self, user_id: int, transaction_id: str, 
                          amount: float, image_filename: str = None, 
                          payment_method: str = None) -> int:
        """Create a new transaction record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO transactions 
            (user_id, transaction_id, amount, image_filename, payment_method)
            VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})
        """, (user_id, transaction_id, amount, image_filename, payment_method))
        conn.commit()
        trans_id = cursor.lastrowid
        conn.close()
        return trans_id
    
    def update_transaction_status(self, transaction_id: str, status: str):
        """Update transaction status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE transactions SET status = {self.placeholder}
            WHERE transaction_id = {self.placeholder}
        """, (status, transaction_id))
        conn.commit()
        conn.close()
    
    def get_user_transactions(self, user_id: int) -> List[Dict]:
        """Get all transactions for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM transactions 
            WHERE user_id = {self.placeholder} 
            ORDER BY created_at DESC
        """, (user_id,))
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transactions
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Dict]:
        """Get transaction by transaction ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM transactions WHERE transaction_id = {self.placeholder}
        """, (transaction_id,))
        transaction = cursor.fetchone()
        conn.close()
        return dict(transaction) if transaction else None
    
    # Processing History Operations
    def add_processing_history(self, user_id: int, original_filename: str,
                               processed_filename: str, style: str,
                               processing_time: float = None) -> int:
        """Add image processing history record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO processing_history 
            (user_id, original_filename, processed_filename, style, processing_time)
            VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})
        """, (user_id, original_filename, processed_filename, style, processing_time))
        conn.commit()
        history_id = cursor.lastrowid
        conn.close()
        return history_id
    
    def get_user_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's processing history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM processing_history 
            WHERE user_id = {self.placeholder} 
            ORDER BY created_at DESC 
            LIMIT {self.placeholder}
        """, (user_id, limit))
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return history
    
    # Statistics
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total images processed
        cursor.execute(f"""
            SELECT COUNT(*) as total_processed FROM processing_history
            WHERE user_id = {self.placeholder}
        """, (user_id,))
        total_processed = cursor.fetchone()['total_processed']
        
        # Total transactions
        cursor.execute(f"""
            SELECT COUNT(*) as total_transactions, 
                   COALESCE(SUM(amount), 0) as total_spent
            FROM transactions
            WHERE user_id = {self.placeholder} AND status = 'completed'
        """, (user_id,))
        trans_data = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_processed': total_processed,
            'total_transactions': trans_data['total_transactions'],
            'total_spent': trans_data['total_spent']
        }

    # Verification Operations
    def store_verification_code(self, email: str, code: str, expires_at: datetime):
        """Store a verification code for an email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Delete any existing codes for this email
        cursor.execute(f"DELETE FROM verification_codes WHERE email = {self.placeholder}", (email,))
        cursor.execute(f"""
            INSERT INTO verification_codes (email, code, expires_at)
            VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder})
        """, (email, code, expires_at))
        conn.commit()
        conn.close()

    def get_verification_code(self, email: str) -> Optional[Dict]:
        """Get the latest verification code for an email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM verification_codes 
            WHERE email = {self.placeholder} 
            ORDER BY created_at DESC LIMIT 1
        """, (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def verify_user_email(self, email: str):
        """Mark a user as verified"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET is_verified = {self.bool_true} WHERE email = {self.placeholder}", (email,))
        # Also delete the used code
        cursor.execute(f"DELETE FROM verification_codes WHERE email = {self.placeholder}", (email,))
        conn.commit()
        conn.close()

    # --- ADMIN DASHBOARD OPERATIONS ---
    def get_admin_dashboard_stats(self) -> Dict:
        """Get global stats for admin dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM processing_history")
        total_creations = cursor.fetchone()['total']
        
        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE status = 'completed'")
        total_revenue = cursor.fetchone()['total']
        
        interval_sql = "NOW() - INTERVAL '24 HOURS'" if self.is_postgres else "datetime('now', '-24 hours')"
        cursor.execute(f"SELECT COUNT(*) as total FROM users WHERE last_login >= {interval_sql}")
        active_today = cursor.fetchone()['total']
        
        conn.close()
        return {
            "total_users": total_users,
            "total_creations": total_creations,
            "total_revenue": total_revenue,
            "active_today": active_today
        }

    def get_recent_activity_logs(self, limit: int = 50) -> List[Dict]:
        """Get latest user logs for admin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT l.*, u.username, u.email 
            FROM user_logs l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.created_at DESC
            LIMIT {self.placeholder}
        """, (limit,))
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

    def get_all_transactions_admin(self) -> List[Dict]:
        """Get all transactions with user details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.*, u.username, u.email 
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            ORDER BY t.created_at DESC
        """)
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transactions

    def get_all_users_admin(self) -> List[Dict]:
        """Get all users with their summary stats"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, 
                   (SELECT COUNT(*) FROM processing_history WHERE user_id = u.id) as total_creations,
                   (SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = u.id AND status = 'completed') as total_spent
            FROM users u
            ORDER BY u.created_at DESC
        """)
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users


# Global database instance
db = Database()
