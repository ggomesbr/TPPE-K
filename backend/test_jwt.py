#!/usr/bin/env python3
"""
Quick test script for JWT functionality
"""
import sys
import os
sys.path.append('/home/bielluiz/UnB/TPPE/Trab-K-V3/backend')

from src.security import create_access_token, verify_token
from datetime import timedelta
import json

def test_jwt():
    print("🧪 Testing JWT functionality...")
    
    # Test data
    data = {'user_id': 1, 'email': 'test@hospital.com', 'role': 'doctor'}
    
    # Create token
    token = create_access_token(data)
    print(f"✅ Token created: {token[:50]}...")
    
    # Verify token
    payload = verify_token(token, 'access')
    print(f"✅ Token verified: {payload}")
    
    if payload:
        print("🎉 JWT is working correctly!")
    else:
        print("❌ JWT verification failed")
        
        # Debug by decoding without verification
        from jose import jwt
        try:
            raw_payload = jwt.decode(token, options={"verify_signature": False})
            print(f"🔍 Raw payload: {json.dumps(raw_payload, indent=2, default=str)}")
        except Exception as e:
            print(f"❌ Failed to decode token: {e}")

if __name__ == "__main__":
    test_jwt()
