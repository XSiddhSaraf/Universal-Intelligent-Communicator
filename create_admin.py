#!/usr/bin/env python3
"""
Script to create an admin user for UnIC
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.database import db_manager

def create_admin_user():
    """Create an admin user"""
    print("Creating admin user for UnIC...")
    
    try:
        username = input("Enter admin username: ").strip()
        if not username:
            print("Username cannot be empty")
            return False
        
        email = input("Enter admin email: ").strip()
        if not email or '@' not in email:
            print("Valid email is required")
            return False
        
        password = input("Enter admin password: ").strip()
        if len(password) < 6:
            print("Password must be at least 6 characters long")
            return False
        
        # Create admin user
        user_id = db_manager.create_user(username, email, password, is_admin=True)
        print(f"Admin user created successfully!")
        print(f"User ID: {user_id}")
        print(f"Username: {username}")
        print(f"Email: {email}")
        return True
        
    except ValueError as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"Failed to create admin user: {e}")
        return False

if __name__ == '__main__':
    create_admin_user()