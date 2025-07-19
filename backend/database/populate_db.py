#!/usr/bin/env python3
"""
Hospital Management System - Database Population Script
Populates the database with sample doctors for testing and development.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to Python path
backend_path = Path(__file__).parent.parent
src_path = backend_path / "src"
sys.path.insert(0, str(src_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from model.models import Medico

# Import hash_password function directly to avoid relative import issues
from passlib.context import CryptContext

# Password hashing context (copied from security.py to avoid import issues)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def populate_database(auto_mode=False):
    """Populate database with sample doctors"""
    print("🏥 Hospital Management System - Database Population")
    print("=" * 60)
    
    try:
        # Create engine and session
        print(f"📊 Connecting to: {settings.database_url}")
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Check if doctors already exist
        existing_count = session.query(Medico).count()
        if existing_count > 0:
            print(f"⚠️  Database already contains {existing_count} doctors.")
            if not auto_mode:
                response = input("Do you want to add more doctors anyway? (y/N): ")
                if response.lower() != 'y':
                    print("❌ Population cancelled.")
                    return False
            else:
                print("🚀 Auto mode: Skipping population as doctors already exist.")
                return True
        
        # Sample doctors data
        doctors_data = [
            {
                "nome": "Dr. Carlos Eduardo Silva",
                "crm": "123456-SP",
                "especialidade": "Cardiologia",
                "email": "carlos.silva@hospital.com",
                "senha": "senha123",
                "hospital_id": 1
            },
            {
                "nome": "Dra. Ana Paula Santos",
                "crm": "789012-RJ", 
                "especialidade": "Pediatria",
                "email": "ana.santos@hospital.com",
                "senha": "senha456",
                "hospital_id": 1
            }
        ]
        
        print(f"\n🔧 Adding {len(doctors_data)} sample doctors...")
        
        created_doctors = []
        for i, doctor_data in enumerate(doctors_data, 1):
            # Check if doctor already exists (by CRM or email)
            existing_doctor = session.query(Medico).filter(
                (Medico.crm == doctor_data["crm"]) | 
                (Medico.email == doctor_data["email"])
            ).first()
            
            if existing_doctor:
                print(f"⚠️  Doctor {i}: {doctor_data['nome']} already exists (CRM: {doctor_data['crm']})")
                continue
            
            # Hash the password
            hashed_password = hash_password(doctor_data["senha"])
            
            # Create doctor instance
            doctor = Medico(
                nome=doctor_data["nome"],
                crm=doctor_data["crm"],
                especialidade=doctor_data["especialidade"],
                email=doctor_data["email"],
                senha=hashed_password,
                hospital_id=doctor_data["hospital_id"]
            )
            
            # Add to session
            session.add(doctor)
            created_doctors.append(doctor_data)
            print(f"✅ Doctor {i}: {doctor_data['nome']} ({doctor_data['especialidade']})")
        
        # Commit changes
        if created_doctors:
            session.commit()
            print(f"\n🎉 Successfully added {len(created_doctors)} doctors to the database!")
        else:
            print("\n📝 No new doctors were added.")
        
        # Show final count
        total_count = session.query(Medico).count()
        print(f"📊 Total doctors in database: {total_count}")
        
        # Show all doctors
        print("\n👥 All doctors in database:")
        all_doctors = session.query(Medico).all()
        for doctor in all_doctors:
            print(f"   • {doctor.nome} - {doctor.crm} - {doctor.especialidade}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

def clear_database(auto_mode=False):
    """Clear all doctors from database (for testing)"""
    print("🗑️  Clearing all doctors from database...")
    
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        count = session.query(Medico).count()
        if count == 0:
            print("📭 Database is already empty.")
            return True
        
        if not auto_mode:
            response = input(f"⚠️  This will delete {count} doctors. Are you sure? (y/N): ")
            if response.lower() != 'y':
                print("❌ Clear operation cancelled.")
                return False
        else:
            print(f"🚀 Auto mode: Clearing {count} doctors...")
        
        # Delete all doctors
        session.query(Medico).delete()
        session.commit()
        
        print(f"✅ Successfully deleted {count} doctors.")
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

def main():
    """Main function with menu"""
    print("Choose an option:")
    print("1. Populate database with sample doctors")
    print("2. Clear all doctors from database")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        populate_database(auto_mode=False)
    elif choice == "2":
        clear_database(auto_mode=False)
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Hospital Management System - Database Population')
    parser.add_argument('--auto', action='store_true', help='Run in automatic mode (no user prompts)')
    parser.add_argument('--clear', action='store_true', help='Clear all doctors from database')
    args = parser.parse_args()
    
    # Check if we have the right environment
    if not os.getenv("MYSQL_DATABASE") and "sqlite" not in settings.database_url.lower():
        print("⚠️  Database not configured. Make sure to set MYSQL_DATABASE or use SQLite.")
        print("💡 Example: MYSQL_DATABASE=hospital_db MYSQL_USER=hospital_user MYSQL_PASSWORD=hospital_pass123 MYSQL_HOST=localhost MYSQL_PORT=13307 python populate_db.py")
        sys.exit(1)
    
    # Auto mode for Docker
    if args.auto:
        print("🚀 Running in automatic mode...")
        if args.clear:
            success = clear_database(auto_mode=True)
        else:
            success = populate_database(auto_mode=True)
        
        if success:
            print("✅ Database initialization completed successfully!")
            sys.exit(0)
        else:
            print("❌ Database initialization failed!")
            sys.exit(1)
    
    # Interactive mode
    main()
