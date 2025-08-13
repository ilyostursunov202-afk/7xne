#!/usr/bin/env python3
"""
Fix admin user in database with proper password hash
"""
import os
from pymongo import MongoClient
from passlib.context import CryptContext
import uuid
from datetime import datetime

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client["ecommerce"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fix_admin_user():
    """Fix admin user with proper fields"""
    print("🔧 Fixing admin user...")
    
    # Delete existing admin
    db.users.delete_many({"email": "admin@7x.com"})
    
    # Create new admin with all required fields
    admin_data = {
        "id": str(uuid.uuid4()),
        "email": "admin@7x.com",
        "name": "7x Administrator",
        "hashed_password": pwd_context.hash("password123"),
        "role": "admin",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "phone": "+998901234567",
        "phone_verified": True,
        "email_verified": True,
        "language": "en"
    }
    
    result = db.users.insert_one(admin_data)
    print(f"✅ Admin user created with ID: {result.inserted_id}")
    
    # Verify admin exists
    admin = db.users.find_one({"email": "admin@7x.com"})
    if admin:
        print(f"✅ Admin verified: {admin['name']} ({admin['role']}) - {admin['email']}")
        print(f"✅ Password hash: {admin['hashed_password'][:50]}...")
    else:
        print("❌ Admin user not found after creation")

if __name__ == "__main__":
    fix_admin_user()