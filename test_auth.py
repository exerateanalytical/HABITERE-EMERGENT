#!/usr/bin/env python3
"""
Simple authentication test to debug session issues
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://plan-builder-8.preview.emergentagent.com"

async def test_auth():
    connector = aiohttp.TCPConnector(ssl=False)
    jar = aiohttp.CookieJar(unsafe=True)
    
    async with aiohttp.ClientSession(connector=connector, cookie_jar=jar) as session:
        # Login
        login_data = {
            "email": "admin@habitere.com",
            "password": "admin123"
        }
        
        print("🔐 Logging in...")
        async with session.post(f"{BACKEND_URL}/api/auth/login", json=login_data) as response:
            print(f"Login status: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"Login response: {json.dumps(data, indent=2)}")
                
                # Check cookies
                print(f"Cookies after login: {session.cookie_jar}")
                for cookie in session.cookie_jar:
                    print(f"Cookie: {cookie.key}={cookie.value}, domain={cookie['domain']}, path={cookie['path']}")
                
                # Test authenticated endpoint
                print("\n🔒 Testing authenticated endpoint...")
                async with session.get(f"{BACKEND_URL}/api/auth/me") as auth_response:
                    print(f"Auth me status: {auth_response.status}")
                    auth_data = await auth_response.text()
                    print(f"Auth me response: {auth_data}")
                    
                # Test security service creation
                print("\n🛡️ Testing security service creation...")
                service_data = {
                    "title": "Test Security Service",
                    "description": "Test service for debugging",
                    "service_type": "Security Guards",
                    "price_range": "100,000 XAF/month",
                    "location": "Douala"
                }
                
                async with session.post(f"{BACKEND_URL}/api/security/services", json=service_data) as service_response:
                    print(f"Service creation status: {service_response.status}")
                    service_result = await service_response.text()
                    print(f"Service creation response: {service_result}")
            else:
                error_data = await response.text()
                print(f"Login failed: {error_data}")

if __name__ == "__main__":
    asyncio.run(test_auth())