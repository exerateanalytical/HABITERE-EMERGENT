#!/usr/bin/env python3
"""
Fix Password Field Migration
============================
Migrate users from 'password_hash' field to 'password' field
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

async def migrate_password_fields():
    """Migrate password_hash field to password field for all users"""
    
    # Connect to database
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🔧 Starting password field migration...")
    
    # Find users with password_hash field
    users_with_old_field = await db.users.find({"password_hash": {"$exists": True}}).to_list(None)
    
    print(f"Found {len(users_with_old_field)} users with 'password_hash' field")
    
    migrated_count = 0
    
    for user in users_with_old_field:
        try:
            # Update the user to use 'password' field instead of 'password_hash'
            result = await db.users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {"password": user["password_hash"]},
                    "$unset": {"password_hash": ""}
                }
            )
            
            if result.modified_count > 0:
                migrated_count += 1
                print(f"✅ Migrated user: {user.get('email', 'Unknown')}")
            else:
                print(f"⚠️ Failed to migrate user: {user.get('email', 'Unknown')}")
                
        except Exception as e:
            print(f"❌ Error migrating user {user.get('email', 'Unknown')}: {e}")
    
    print(f"\n🎉 Migration complete! Migrated {migrated_count} users")
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    remaining_old_users = await db.users.count_documents({"password_hash": {"$exists": True}})
    new_users = await db.users.count_documents({"password": {"$exists": True}})
    
    print(f"Users with 'password_hash' field: {remaining_old_users}")
    print(f"Users with 'password' field: {new_users}")
    
    if remaining_old_users == 0:
        print("✅ All users successfully migrated!")
    else:
        print("⚠️ Some users still have old field structure")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_password_fields())