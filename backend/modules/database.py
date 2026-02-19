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
        """Get database connection (PostgreSQL or SQLite) with production safety"""
        if self.is_postgres:
            # Render/Postgres URL fix: Ensure postgresql:// prefix
            url = self.db_url
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            
            try:
                # Attempt standard connection with SSL for production
                if "?" in url:
                    ssl_url = f"{url}&sslmode=require" if "sslmode" not in url else url
                else:
                    ssl_url = f"{url}?sslmode=require"
                
                conn = psycopg2.connect(ssl_url, cursor_factory=RealDictCursor)
                return conn
            except Exception as e:
                print(f"⚠️ Initial Postgres connection failed: {e}")
                # Fallback to original URL if SSL tweak fails
                conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
                return conn
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Determine ID syntax
        id_serial = "SERIAL PRIMARY KEY" if self.is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
        
        # Tables will be created if they don't exist below.
        # Removed DROP TABLE logic to prevent production data loss.

        # Users table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id {id_serial},
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name VARCHAR(100),
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT {self.bool_true},
                is_verified BOOLEAN DEFAULT {self.bool_false},
                last_logout TIMESTAMP WITH TIME ZONE,
                last_active TIMESTAMP WITH TIME ZONE
            )
        """)

        # Migration Helper
        def add_column(table, column, type_def):
            try:
                cursor.execute(f"SELECT {column} FROM {table} LIMIT 1")
            except Exception:
                # Need a rollback if the select failed in Postgres
                if self.is_postgres:
                    conn.rollback()
                print(f"🚀 Migrating {table}: Adding '{column}'...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")
                conn.commit()

        add_column("users", "role", "VARCHAR(20) DEFAULT 'user'")
        add_column("users", "last_logout", "TIMESTAMP WITH TIME ZONE")
        add_column("users", "last_active", "TIMESTAMP WITH TIME ZONE")
        add_column("users", "is_verified", f"BOOLEAN DEFAULT {self.bool_false}")
        add_column("users", "auto_delete_days", "INTEGER DEFAULT 0") # 0 = Never
        add_column("users", "failed_attempts", "INTEGER DEFAULT 0")
        add_column("users", "lockout_until", "TIMESTAMP WITH TIME ZONE")

        # Create Default Admin User
        try:
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            admin_user = cursor.fetchone()
            
            if not admin_user:
                import bcrypt
                print("👤 Initializing System: Creating default administrator...")
                pw = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute(f"""
                    INSERT INTO users (username, email, password_hash, full_name, role, is_verified)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ("admin", "admin@toonify.ai", pw, "System Admin", "admin", True if self.is_postgres else 1))
                conn.commit()
        except Exception as e:
            print(f"⚠️ Admin creation skipped or failed: {e}")
            if self.is_postgres: conn.rollback()
        
        # Other Tables with correct Postgres types
        cursor.execute(f"CREATE TABLE IF NOT EXISTS verification_codes (id {id_serial}, email VARCHAR(100) NOT NULL, code VARCHAR(10) NOT NULL, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, expires_at TIMESTAMP WITH TIME ZONE NOT NULL)")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS transactions (id {id_serial}, user_id INTEGER NOT NULL, transaction_id VARCHAR(100) UNIQUE NOT NULL, amount DOUBLE PRECISION NOT NULL, currency VARCHAR(10) DEFAULT 'usd', status VARCHAR(30) DEFAULT 'pending', payment_method VARCHAR(50), image_filename TEXT, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS processing_history (id {id_serial}, user_id INTEGER NOT NULL, original_filename TEXT NOT NULL, processed_filename TEXT NOT NULL, style VARCHAR(50) NOT NULL, processing_time DOUBLE PRECISION, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS user_logs (id {id_serial}, user_id INTEGER NOT NULL, action VARCHAR(50) NOT NULL, details TEXT, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)")

        conn.commit()

        # Create Indexes for performance (Milestone 3 optimization)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_user_id ON processing_history(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_filename ON processing_history(processed_filename)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_filename ON transactions(image_filename)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_user_style ON processing_history(user_id, style)")

        conn.commit()
        conn.close()
    
    # User Operations
    def create_user(self, username: str, email: str, password_hash: str, 
                   full_name: str = None) -> Optional[int]:
        """Create a new user"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.is_postgres:
                # PostgreSQL requires RETURNING id
                cursor.execute(f"""
                    INSERT INTO users (username, email, password_hash, full_name)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (username, email, password_hash, full_name))
                user_id = cursor.fetchone()['id']
            else:
                # SQLite uses lastrowid
                cursor.execute(f"""
                    INSERT INTO users (username, email, password_hash, full_name)
                    VALUES (?, ?, ?, ?)
                """, (username, email, password_hash, full_name))
                user_id = cursor.lastrowid
                
            conn.commit()
            return user_id
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"DATABASE ERROR during create_user: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()
    
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

    def update_user_lockout(self, user_id: int, attempts: int, lockout_until: datetime = None):
        """Update failed login attempts and lockout timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE users SET failed_attempts = {self.placeholder}, lockout_until = {self.placeholder}
            WHERE id = {self.placeholder}
        """, (attempts, lockout_until, user_id))
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
    
    def update_user_settings(self, user_id: int, auto_delete_days: int):
        """Update user privacy settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET auto_delete_days = {self.placeholder} WHERE id = {self.placeholder}", 
                      (auto_delete_days, user_id))
        conn.commit()
        conn.close()
        return True

    def change_password(self, user_id: int, new_password_hash: str):
        """Update user password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET password_hash = {self.placeholder} WHERE id = {self.placeholder}", 
                      (new_password_hash, user_id))
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

    def get_transaction_by_filename(self, user_id: int, filename: str) -> Optional[Dict]:
        """Verify if a user has paid for a specific image"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM transactions WHERE user_id = {self.placeholder} AND image_filename = {self.placeholder}", (user_id, filename))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
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
    
    def get_advanced_history(self, user_id: int, style: str = None, sort_by: str = 'created_at', 
                             order: str = 'DESC', limit: int = 20, offset: int = 0) -> Dict:
        """Get paginated and filtered history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Base query with JOIN to check payment status
        query = f"""
            SELECT ph.*, 
                   CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END as is_paid
            FROM processing_history ph
            LEFT JOIN transactions t ON ph.processed_filename = t.image_filename
            WHERE ph.user_id = {self.placeholder}
        """
        params = [user_id]
        
        if style and style != 'all':
            query += f" AND ph.style = {self.placeholder}"
            params.append(style)
            
        # Count total for pagination (Simplified count)
        count_query = f"SELECT COUNT(*) as total FROM processing_history WHERE user_id = {self.placeholder}"
        count_params = [user_id]
        if style and style != 'all':
            count_query += f" AND style = {self.placeholder}"
            count_params.append(style)
            
        cursor.execute(count_query, tuple(count_params))
        row = cursor.fetchone()
        total_count = row['total'] if self.is_postgres else row[0]
        
        # Sort and Page
        valid_sorts = ['created_at', 'style', 'processing_time']
        if sort_by not in valid_sorts: sort_by = 'created_at'
        if order not in ['ASC', 'DESC']: order = 'DESC'
        
        query += f" ORDER BY ph.{sort_by} {order} LIMIT {self.placeholder} OFFSET {self.placeholder}"
        params.extend([limit, offset])
        
        cursor.execute(query, tuple(params))
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "items": history,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }

    def delete_user_history(self, user_id: int, history_id: int = None):
        """Delete specific image or all history for a user. Returns list of filenames to delete physically."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get filenames first
        if history_id:
            cursor.execute(f"SELECT processed_filename FROM processing_history WHERE id = {self.placeholder} AND user_id = {self.placeholder}", (history_id, user_id))
        else:
            cursor.execute(f"SELECT processed_filename FROM processing_history WHERE user_id = {self.placeholder}", (user_id,))
            
        files = [row['processed_filename'] for row in cursor.fetchall()]
        
        # Delete from DB
        if history_id:
            cursor.execute(f"DELETE FROM processing_history WHERE id = {self.placeholder} AND user_id = {self.placeholder}", (history_id, user_id))
        else:
            cursor.execute(f"DELETE FROM processing_history WHERE user_id = {self.placeholder}", (user_id,))
            
        conn.commit()
        conn.close()
        return files
    
    # Statistics
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics (High performance optimized)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Combined stats query using subqueries for maximum efficiency
        cursor.execute(f"""
            SELECT 
                (SELECT COUNT(*) FROM processing_history WHERE user_id = {self.placeholder}) as total_processed,
                (SELECT COUNT(*) FROM transactions WHERE user_id = {self.placeholder} AND status = 'completed') as total_transactions,
                (SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = {self.placeholder} AND status = 'completed') as total_spent,
                (SELECT style FROM processing_history WHERE user_id = {self.placeholder} GROUP BY style ORDER BY COUNT(*) DESC LIMIT 1) as favorite_style
        """, (user_id, user_id, user_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {'total_processed': 0, 'total_transactions': 0, 'total_spent': 0, 'favorite_style': "None"}

        return {
            'total_processed': row['total_processed'] if self.is_postgres else row[0],
            'total_transactions': row['total_transactions'] if self.is_postgres else row[1],
            'total_spent': row['total_spent'] if self.is_postgres else row[2],
            'favorite_style': (row['favorite_style'] if self.is_postgres else row[3]) or "None"
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

    def cleanup_old_history(self, user_id: int):
        """Delete history older than the user's auto_delete_days setting"""
        user = self.get_user_by_id(user_id)
        if not user or not user.get('auto_delete_days'):
            return []
            
        days = user['auto_delete_days']
        conn = self.get_connection()
        cursor = conn.cursor()
        
        interval_sql = f"CURRENT_TIMESTAMP - INTERVAL '{days} days'" if self.is_postgres else f"datetime('now', '-{days} days')"
        
        # Get filenames
        cursor.execute(f"""
            SELECT processed_filename FROM processing_history 
            WHERE user_id = {self.placeholder} AND created_at < {interval_sql}
        """, (user_id,))
        files = [row['processed_filename'] for row in cursor.fetchall()]
        
        if files:
            cursor.execute(f"DELETE FROM processing_history WHERE user_id = {self.placeholder} AND created_at < {interval_sql}", (user_id,))
            conn.commit()
            
        conn.close()
        return files

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
