#!/usr/bin/env python3
"""
Standalone script to create database tables for Docker initialization
This script doesn't rely on relative imports and can be run independently
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to Python path
backend_path = Path(__file__).parent.parent
src_path = backend_path / "src"
sys.path.insert(0, str(src_path))

# Import models after adding to path
from model.models import Base

def get_database_url():
    """Build database URL from environment variables"""
    mysql_user = os.getenv("MYSQL_USER", "hospital_user")
    mysql_password = os.getenv("MYSQL_PASSWORD", "hospital_pass")
    mysql_host = os.getenv("MYSQL_HOST", "localhost")
    mysql_port = os.getenv("MYSQL_PORT", "3306")
    mysql_database = os.getenv("MYSQL_DATABASE", "hospital_db")
    
    return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

def create_tables():
    """Create all database tables"""
    print(f"🔗 Connecting to database...")
    
    database_url = get_database_url()
    print(f"📊 Database URL: {database_url}")
    
    # Create engine
    engine = create_engine(database_url, pool_pre_ping=True)
    
    try:
        # Create all tables
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        engine.dispose()

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)
