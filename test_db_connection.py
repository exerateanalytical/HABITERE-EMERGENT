#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

async def test_database():
    # Connect to database
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["test_database"]
    
    print("Testing database connection...")
    
    # Test properties collection
    properties_count = await db.properties.count_documents({})
    print(f"Properties count: {properties_count}")
    
    # Test services collection
    services_count = await db.services.count_documents({})
    print(f"Services count: {services_count}")
    
    # Try to insert a test property
    test_property = {
        "id": str(uuid.uuid4()),
        "owner_id": "test-owner",
        "title": "Test Property",
        "description": "Test description",
        "price": 100000,
        "currency": "XAF",
        "location": "Test Location",
        "property_type": "house",
        "listing_type": "sale",
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqm": 150,
        "images": [],
        "amenities": [],
        "available": True,
        "verified": False,
        "views": 0,
        "favorites": 0,
        "created_at": datetime.now(timezone.utc)
    }
    
    try:
        result = await db.properties.insert_one(test_property)
        print(f"Test property inserted with ID: {result.inserted_id}")
        
        # Check if it was inserted
        new_count = await db.properties.count_documents({})
        print(f"New properties count: {new_count}")
        
        # Clean up
        await db.properties.delete_one({"id": test_property["id"]})
        print("Test property cleaned up")
        
    except Exception as e:
        print(f"Error inserting test property: {e}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_database())