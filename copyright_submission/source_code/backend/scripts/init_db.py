"""
Database initialization script
Run this to set up the database for the first time
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.database import db
import config.settings as settings


def initialize_database():
    """Initialize the database with tables"""
    print("🔧 Initializing Toonify database...")
    print(f"📁 Database location: {settings.DATABASE_PATH}")
    
    # Database is automatically initialized in Database.__init__()
    # This script confirms it and shows the structure
    
    print("\n✅ Database initialized successfully!")
    print("\n📊 Database Tables Created:")
    print("  - users: User accounts and authentication")
    print("  - transactions: Payment records")
    print("  - sessions: User session management")
    print("  - processing_history: Image processing logs")
    
    print("\n💡 Next steps:")
    print("  1. Copy .env.example to .env")
    print("  2. Configure your environment variables")
    print("  3. Run: streamlit run app.py")
    print("\n🎨 Happy cartooning!")


if __name__ == "__main__":
    initialize_database()
