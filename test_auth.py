#!/usr/bin/env python3
"""
Test script for authentication functionality
"""

import requests
import json
import sys
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
}

def test_registration():
    """Test user registration"""
    print("Testing user registration...")
    
    response = requests.post(f"{BASE_URL}/api/auth/register", 
                           json=TEST_USER)
    
    if response.status_code == 201:
        print("✓ Registration successful")
        return True
    else:
        print(f"✗ Registration failed: {response.status_code} - {response.text}")
        return False

def test_login():
    """Test user login"""
    print("Testing user login...")
    
    response = requests.post(f"{BASE_URL}/api/auth/login", 
                           json={
                               "username": TEST_USER["username"],
                               "password": TEST_USER["password"]
                           })
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Login successful")
        print(f"Session token: {data['session_token'][:20]}...")
        return data['session_token']
    else:
        print(f"✗ Login failed: {response.status_code} - {response.text}")
        return None

def test_protected_endpoint(session_token):
    """Test protected endpoint access"""
    print("Testing protected endpoint access...")
    
    headers = {"Authorization": f"Bearer {session_token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Protected endpoint access successful")
        print(f"User: {data['user']['username']}")
        return True
    else:
        print(f"✗ Protected endpoint access failed: {response.status_code} - {response.text}")
        return False

def test_admin_login():
    """Test admin login"""
    print("Testing admin login...")
    
    response = requests.post(f"{BASE_URL}/api/auth/login", 
                           json={
                               "username": "admin",
                               "password": "password123"
                           })
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Admin login successful")
        print(f"Admin token: {data['session_token'][:20]}...")
        return data['session_token']
    else:
        print(f"✗ Admin login failed: {response.status_code} - {response.text}")
        return None

def test_logout(session_token):
    """Test user logout"""
    print("Testing logout...")
    
    headers = {"Authorization": f"Bearer {session_token}"}
    response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    
    if response.status_code == 200:
        print("✓ Logout successful")
        return True
    else:
        print(f"✗ Logout failed: {response.status_code} - {response.text}")
        return False

def main():
    """Run all authentication tests"""
    print("UnIC Authentication Test Suite")
    print("=" * 40)
    
    try:
        # Test server health
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("Server is not running. Please start the API server first.")
            print("Run: python main.py --mode api")
            return False
        print("✓ Server is running")
        
        # Test registration
        if not test_registration():
            print("Skipping other tests due to registration failure")
            return False
        
        # Test login
        session_token = test_login()
        if not session_token:
            return False
        
        # Test protected endpoint
        if not test_protected_endpoint(session_token):
            return False
        
        # Test admin login
        admin_token = test_admin_login()
        if admin_token:
            print("✓ Admin authentication working")
        
        # Test logout
        if not test_logout(session_token):
            return False
        
        print("\n" + "=" * 40)
        print("✓ All authentication tests passed!")
        return True
        
    except requests.ConnectionError:
        print("Cannot connect to server. Please start the API server first.")
        print("Run: python main.py --mode api")
        return False
    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)