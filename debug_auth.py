#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

async def check_admin_user():
    """Check if admin user exists and has correct fields"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🔍 Checking admin user in database...")
    
    # Find admin user
    admin_user = await db.users.find_one({"email": "admin@habitere.com"})
    
    if admin_user:
        print("✅ Admin user found!")
        print(f"   Email: {admin_user.get('email')}")
        print(f"   Name: {admin_user.get('name')}")
        print(f"   Has password field: {'password' in admin_user}")
        print(f"   Has password_hash field: {'password_hash' in admin_user}")
        print(f"   Email verified: {admin_user.get('email_verified', False)}")
        print(f"   Role: {admin_user.get('role', 'None')}")
        print(f"   Auth provider: {admin_user.get('auth_provider', 'None')}")
        
        # Show all fields
        print(f"\n📋 All fields in admin user:")
        for key, value in admin_user.items():
            if key == '_id':
                continue
            if 'password' in key.lower():
                print(f"   {key}: {'***' if value else 'None'}")
            else:
                print(f"   {key}: {value}")
    else:
        print("❌ Admin user not found!")
        
        # Check if any users exist
        user_count = await db.users.count_documents({})
        print(f"   Total users in database: {user_count}")
        
        if user_count > 0:
            print("\n📋 Sample user fields:")
            sample_user = await db.users.find_one({})
            for key in sample_user.keys():
                if key != '_id':
                    print(f"   {key}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(check_admin_user())