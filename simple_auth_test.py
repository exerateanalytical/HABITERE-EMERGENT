#!/usr/bin/env python3
"""
Simple Authentication Test
=========================

Simple test to isolate authentication issues.
"""

import asyncio
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://habitere-inventory.preview.emergentagent.com/api"

async def test_unauthenticated_access():
    """Test unauthenticated access to /auth/me"""
    connector = aiohttp.TCPConnector(ssl=False)
    
    # Create a fresh session with no cookies
    async with aiohttp.ClientSession(connector=connector) as session:
        logger.info("Testing unauthenticated access to /auth/me")
        
        async with session.get(f"{BASE_URL}/auth/me") as response:
            logger.info(f"Status: {response.status}")
            logger.info(f"Headers: {dict(response.headers)}")
            
            if response.status == 200:
                data = await response.json()
                logger.info(f"Response data: {data}")
            else:
                text = await response.text()
                logger.info(f"Response text: {text}")

async def test_invalid_session_token():
    """Test with invalid session token"""
    connector = aiohttp.TCPConnector(ssl=False)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        logger.info("Testing invalid session token")
        
        headers = {"Cookie": "session_token=invalid-token-12345"}
        async with session.get(f"{BASE_URL}/auth/me", headers=headers) as response:
            logger.info(f"Status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                logger.info(f"Response data: {data}")
            else:
                text = await response.text()
                logger.info(f"Response text: {text}")

async def main():
    await test_unauthenticated_access()
    await test_invalid_session_token()

if __name__ == "__main__":
    asyncio.run(main())