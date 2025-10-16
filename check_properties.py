#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_properties():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    
    print("Checking all properties in database...")
    
    # Get all properties without filters
    all_properties = await db.properties.find({}).to_list(100)
    print(f"Total properties in DB: {len(all_properties)}")
    
    for prop in all_properties:
        print(f"Property: {prop.get('title', 'No title')}")
        print(f"  Available: {prop.get('available', 'Not set')}")
        print(f"  Property Type: {prop.get('property_type', 'Not set')}")
        print(f"  Listing Type: {prop.get('listing_type', 'Not set')}")
        print("---")
    
    # Check with available filter
    available_properties = await db.properties.find({"available": True}).to_list(100)
    print(f"Available properties: {len(available_properties)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_properties())