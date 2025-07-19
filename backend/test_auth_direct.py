#!/usr/bin/env python3
"""
Direct test of authentication endpoints
"""
import requests
import json

def test_auth_endpoints():
    print("🧪 Testing Authentication Endpoints directly...")
    
    base_url = "http://localhost:8000"
    
    # Test registration
    user_data = {
        'nome': 'Test Doctor',
        'email': 'testdoc@hospital.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123',
        'role': 'doctor',
        'crm': '99999-XX',
        'especialidade': 'Teste'
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=user_data, timeout=5)
        print(f"✅ Registration: {response.status_code}")
        if response.status_code == 200:
            print(f"   User: {response.json()['nome']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return
    
    # Test login
    login_data = {
        'email': 'testdoc@hospital.com',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        print(f"✅ Login: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            token = token_data['access_token']
            print(f"   Token: {token[:50]}...")
            
            # Test protected endpoint
            headers = {'Authorization': f'Bearer {token}'}
            me_response = requests.get(f"{base_url}/api/auth/me", headers=headers, timeout=5)
            print(f"✅ Get current user: {me_response.status_code}")
            if me_response.status_code == 200:
                print(f"   User: {me_response.json()['nome']}")
            else:
                print(f"   Error: {me_response.text}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Login failed: {e}")

if __name__ == "__main__":
    test_auth_endpoints()
