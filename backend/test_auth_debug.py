"""
Test script to debug authentication session issues
"""
import os
import sys
sys.path.append('/home/bielluiz/UnB/TPPE/Trab-K-V3/backend')

from fastapi.testclient import TestClient
from src.main import app
from src.database.database import get_database, SessionLocal
from src.model.models import Usuario
from src.security import hash_password
from datetime import datetime

# Override database dependency for testing
def override_get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_database] = override_get_database

def test_auth_with_existing_user():
    """Test authentication with a user that definitely exists in the database"""
    
    # First, create a user directly in the database
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(Usuario).filter(Usuario.email == "direct.test@hospital.com").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
        
        # Create test user directly
        test_user = Usuario(
            nome="Direct Test User",
            email="direct.test@hospital.com",
            senha=hash_password("directpass123"),
            role="doctor",
            crm="DIRECT-123",
            especialidade="Testing",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Created user directly in DB: {test_user.id}")
        
    except Exception as e:
        print(f"❌ Failed to create user: {e}")
        return
    finally:
        db.close()
    
    # Now test with TestClient
    client = TestClient(app)
    
    # Test login
    login_data = {
        'email': 'direct.test@hospital.com',
        'password': 'directpass123'
    }
    
    login_response = client.post('/api/auth/login', json=login_data)
    print(f"✅ Login response: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data['access_token']
        print(f"✅ Got token: {token[:50]}...")
        print(f"✅ User in token response: {token_data['user']['nome']}")
        
        # Test the /me endpoint
        headers = {'Authorization': f'Bearer {token}'}
        me_response = client.get('/api/auth/me', headers=headers)
        print(f"✅ /me response: {me_response.status_code}")
        
        if me_response.status_code != 200:
            print(f"❌ Error: {me_response.text}")
            
            # Let's also test token verification directly
            from src.security import verify_token
            payload = verify_token(token, "access")
            print(f"✅ Direct token verification: {payload}")
        else:
            user_info = me_response.json()
            print(f"✅ Current user: {user_info['nome']}")
    else:
        print(f"❌ Login failed: {login_response.text}")

if __name__ == "__main__":
    test_auth_with_existing_user()
