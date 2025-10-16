#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def reset_sample_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    
    print("Clearing existing properties...")
    result = await db.properties.delete_many({})
    print(f"Deleted {result.deleted_count} properties")
    
    print("Clearing existing services...")
    result = await db.services.delete_many({})
    print(f"Deleted {result.deleted_count} services")
    
    client.close()
    print("Database cleared. Sample data will be reinitialized on next API call.")

if __name__ == "__main__":
    asyncio.run(reset_sample_data())