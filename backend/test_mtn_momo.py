#!/usr/bin/env python3
"""
Test script for MTN Mobile Money integration
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from server import MTNMoMoConfig, MTNMoMoTokenManager

async def test_mtn_config():
    """Test MTN MoMo configuration"""
    print("Testing MTN MoMo Configuration...")
    
    config = MTNMoMoConfig()
    print(f"Base URL: {config.base_url}")
    print(f"Target Environment: {config.target_environment}")
    print(f"API User ID: {'***' if config.api_user_id else 'Not set'}")
    print(f"API Key: {'***' if config.api_key else 'Not set'}")
    print(f"Subscription Key: {'***' if config.subscription_key else 'Not set'}")
    print(f"Callback URL: {config.callback_url or 'Not set'}")
    
    return config

async def test_token_manager():
    """Test token manager (will fail without real credentials)"""
    print("\nTesting Token Manager...")
    
    token_manager = MTNMoMoTokenManager()
    
    # This will fail without real credentials, but we can test the structure
    try:
        token = await token_manager.get_access_token()
        if token:
            print(f"Token obtained: {token[:10]}...")
        else:
            print("Token request failed (expected without real credentials)")
    except Exception as e:
        print(f"Token request error (expected): {e}")

async def main():
    """Main test function"""
    print("MTN Mobile Money Integration Test")
    print("=" * 40)
    
    # Test configuration
    config = await test_mtn_config()
    
    # Test token manager
    await test_token_manager()
    
    print("\n" + "=" * 40)
    print("Test completed!")
    print("\nTo use MTN MoMo integration:")
    print("1. Sign up at https://momodeveloper.mtn.com/")
    print("2. Get your API credentials")
    print("3. Update the .env file with your credentials:")
    print("   - MTN_MOMO_API_USER_ID")
    print("   - MTN_MOMO_API_KEY") 
    print("   - MTN_MOMO_SUBSCRIPTION_KEY")
    print("4. Set MTN_MOMO_TARGET_ENVIRONMENT to 'mtncameroon' for production")

if __name__ == "__main__":
    asyncio.run(main())