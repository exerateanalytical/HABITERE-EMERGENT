#!/usr/bin/env python3
"""
Authentication Debug Test
========================
Focused test to understand authentication middleware behavior.
"""

import asyncio
import aiohttp
import json

async def test_auth_behavior():
    """Test authentication behavior in detail."""
    base_url = "https://plan-builder-8.preview.emergentagent.com/api"
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing Authentication Behavior")
        
        # Test 1: Completely no headers
        print("\n1. Testing with NO headers at all:")
        try:
            async with session.post(f"{base_url}/properties", json={"title": "test"}) as response:
                text = await response.text()
                print(f"   Status: {response.status}")
                print(f"   Response: {text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Empty Authorization header
        print("\n2. Testing with empty Authorization header:")
        try:
            headers = {"Authorization": ""}
            async with session.post(f"{base_url}/properties", json={"title": "test"}, headers=headers) as response:
                text = await response.text()
                print(f"   Status: {response.status}")
                print(f"   Response: {text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Invalid Bearer token
        print("\n3. Testing with invalid Bearer token:")
        try:
            headers = {"Authorization": "Bearer invalid-token"}
            async with session.post(f"{base_url}/properties", json={"title": "test"}, headers=headers) as response:
                text = await response.text()
                print(f"   Status: {response.status}")
                print(f"   Response: {text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: No Cookie header
        print("\n4. Testing with no Cookie header:")
        try:
            async with session.post(f"{base_url}/properties", json={"title": "test"}) as response:
                text = await response.text()
                print(f"   Status: {response.status}")
                print(f"   Response: {text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 5: Check if endpoint requires specific content-type
        print("\n5. Testing different content types:")
        try:
            headers = {"Content-Type": "text/plain"}
            async with session.post(f"{base_url}/properties", data="test", headers=headers) as response:
                text = await response.text()
                print(f"   Status: {response.status}")
                print(f"   Response: {text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth_behavior())