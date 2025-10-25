#!/usr/bin/env python3
"""
Subscription Feature Access Testing
==================================

Test the specific GET /api/subscriptions/check-access/{feature} endpoint
mentioned in the review request.
"""

import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://realestate-cam.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@habitere.com"
ADMIN_PASSWORD = "admin123"

async def test_feature_access():
    """Test feature-specific access control."""
    
    # Setup session
    connector = aiohttp.TCPConnector(ssl=False)
    timeout = aiohttp.ClientTimeout(total=30)
    session = aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )
    
    try:
        # Authenticate
        login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        async with session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                auth_token = response.cookies.get("session_token")
                if auth_token:
                    session.headers.update({"Cookie": f"session_token={auth_token.value}"})
                    logger.info("✅ Authentication successful")
                else:
                    logger.error("❌ No session token received")
                    return
            else:
                logger.error(f"❌ Authentication failed: {response.status}")
                return
        
        # Test feature access endpoints
        features_to_test = [
            "property_posting",
            "service_creation", 
            "premium_listings",
            "analytics_dashboard",
            "priority_support"
        ]
        
        for feature in features_to_test:
            try:
                async with session.get(f"{BASE_URL}/subscriptions/check-access/{feature}") as response:
                    logger.info(f"Feature '{feature}': Status {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"  Response: {data}")
                    elif response.status == 404:
                        logger.info(f"  Endpoint not found - may not be implemented with feature parameter")
                    else:
                        error_text = await response.text()
                        logger.info(f"  Error: {error_text}")
            except Exception as e:
                logger.error(f"  Exception testing feature '{feature}': {e}")
        
        # Test the base check-access endpoint (without feature parameter)
        try:
            async with session.get(f"{BASE_URL}/subscriptions/check-access") as response:
                logger.info(f"Base check-access: Status {response.status}")
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"  Response: {data}")
                else:
                    error_text = await response.text()
                    logger.info(f"  Error: {error_text}")
        except Exception as e:
            logger.error(f"Exception testing base check-access: {e}")
            
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_feature_access())