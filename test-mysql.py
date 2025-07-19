#!/usr/bin/env python3
"""
Test MySQL connection for Hospital Management System
"""
import os
import sys
from pathlib import Path

# Add src to Python path
backend_path = Path(__file__).parent / "backend"
src_path = backend_path / "src"
sys.path.insert(0, str(src_path))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def test_mysql_connection():
    """Test MySQL connection and create tables"""
    print("🏥 Hospital Management System - MySQL Connection Test")
    print("=" * 60)
    
    try:
        # Show current configuration
        print(f"📊 Database URL: {settings.database_url}")
        
        # Create engine
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=True  # Show SQL queries
        )
        
        # Test basic connection
        print("\n🔗 Testing connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'MySQL connection successful!' as status"))
            status = result.fetchone()
            print(f"✅ {status[0]}")
        
        # Create tables
        print("\n🏗️ Creating tables...")
        from model.models import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        
        # Test session
        print("\n📋 Testing session...")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        try:
            result = session.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   📋 {table[0]}")
        finally:
            session.close()
        
        print("\n🎉 MySQL configuration is working perfectly!")
        print("🚀 You can now start the FastAPI server with MySQL")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MySQL Docker container is running: docker-compose ps")
        print("2. Check MySQL logs: docker-compose logs mysql")
        print("3. Verify .env file has correct MySQL credentials")
        print("4. Try: docker-compose restart mysql")
        return False

if __name__ == "__main__":
    success = test_mysql_connection()
    sys.exit(0 if success else 1)
