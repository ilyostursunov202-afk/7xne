#!/usr/bin/env python3
"""
Create admin user for MarketPlace e-commerce platform
"""
import sys
import os
sys.path.append('/app/backend')

import uuid
from datetime import datetime, timezone
from pymongo import MongoClient
from auth import AuthManager

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client["ecommerce"]
users_collection = db["users"]

# Auth manager
auth_manager = AuthManager()

def create_admin_user():
    admin_email = "admin@marketplace.com"
    admin_password = "admin123"  # Simple password for demo
    
    # Check if admin already exists
    existing_admin = users_collection.find_one({"email": admin_email})
    if existing_admin:
        print(f"✅ Admin user already exists: {admin_email}")
        return admin_email, admin_password
    
    # Create new admin user
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": admin_email,
        "hashed_password": auth_manager.get_password_hash(admin_password),
        "name": "Admin User",
        "phone": None,
        "avatar": None,
        "role": "admin",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_active": True,
        "addresses": []
    }
    
    users_collection.insert_one(admin_user)
    print(f"✅ Admin user created successfully!")
    print(f"📧 Email: {admin_email}")
    print(f"🔑 Password: {admin_password}")
    
    return admin_email, admin_password

if __name__ == "__main__":
    try:
        email, password = create_admin_user()
        print(f"\n🎯 ADMIN LOGIN CREDENTIALS:")
        print(f"URL: https://marketcraft-9.preview.emergentagent.com/admin")
        print(f"Email: {email}")
        print(f"Password: {password}")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")