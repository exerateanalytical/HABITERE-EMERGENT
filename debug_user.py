#!/usr/bin/env python3
"""
Debug User Database Fields
==========================
Check what fields exist for the admin user in the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

async def check_admin_user():
    """Check admin user fields in database"""
    
    # Connect to database
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🔍 Checking admin user in database...")
    
    # Find admin user
    admin_user = await db.users.find_one({"email": "admin@habitere.com"})
    
    if admin_user:
        print("✅ Admin user found!")
        print("📋 User fields:")
        for key, value in admin_user.items():
            if key in ['password', 'password_hash']:
                print(f"  {key}: [HIDDEN - {len(str(value))} chars]")
            else:
                print(f"  {key}: {value}")
    else:
        print("❌ Admin user not found!")
        
        # Check if any users exist
        user_count = await db.users.count_documents({})
        print(f"Total users in database: {user_count}")
        
        if user_count > 0:
            print("\n📋 Sample user fields:")
            sample_user = await db.users.find_one({})
            for key, value in sample_user.items():
                if key in ['password', 'password_hash']:
                    print(f"  {key}: [HIDDEN - {len(str(value))} chars]")
                else:
                    print(f"  {key}: {value}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_admin_user())