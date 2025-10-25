#!/usr/bin/env python3
"""
Auto-Login Registration Flow Testing
===================================

Tests the new authentication system changes:
1. Removed Google OAuth completely (routes deleted)
2. Removed email verification requirement
3. Users now auto-login after registration with session token
4. Users redirected to dashboard immediately

Test Coverage:
- Phase 1: Test New Registration Flow
- Phase 2: Test Login Still Works
- Phase 3: Test Google Routes Removed
- Phase 4: Verify Auto-Login Session

Author: Testing Agent
Date: 2025-01-27
"""

import asyncio
import aiohttp
import json
import logging
import random
import string
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "https://habitere-home.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@habitere.com"
ADMIN_PASSWORD = "admin123"

class AuthRegistrationTester:
    """Comprehensive tester for Auto-Login Registration Flow."""
    
    def __init__(self):
        self.session = None
        self.test_user_email = None
        self.test_user_password = "TestPassword123!"
        self.test_user_name = "Test AutoLogin User"
        self.test_user_phone = "+237123456789"
        self.session_cookie = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    async def setup_session(self):
        """Initialize HTTP session."""
        connector = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=connector)
        logger.info("HTTP session initialized")
    
    async def cleanup_session(self):
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            logger.info("HTTP session closed")
    
    def generate_test_email(self) -> str:
        """Generate unique test email."""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"test_autologin_{random_suffix}@habitere.com"
    
    def record_test(self, test_name: str, passed: bool, error_msg: str = None):
        """Record test result."""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed"] += 1
            logger.info(f"✅ {test_name}")
        else:
            self.results["failed"] += 1
            error_detail = f"{test_name}: {error_msg}" if error_msg else test_name
            self.results["errors"].append(error_detail)
            logger.error(f"❌ {test_name}: {error_msg}")
    
    # ==================== PHASE 1: NEW REGISTRATION FLOW ====================
    
    async def test_new_registration_flow(self):
        """Test Phase 1: New registration with auto-login."""
        logger.info("\n🔐 PHASE 1: Testing New Registration Flow")
        
        # Generate unique test user
        self.test_user_email = self.generate_test_email()
        
        try:
            registration_data = {
                "email": self.test_user_email,
                "name": self.test_user_name,
                "password": self.test_user_password,
                "phone": self.test_user_phone
            }
            
            async with self.session.post(f"{BASE_URL}/auth/register", json=registration_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check response contains user object
                    if "user" in data:
                        user = data["user"]
                        
                        # Verify user data
                        if (user.get("email") == self.test_user_email and
                            user.get("name") == self.test_user_name and
                            user.get("phone") == self.test_user_phone and
                            user.get("email_verified") is True):
                            
                            self.record_test("Registration Returns User Data", True)
                            
                            # Check for session cookie
                            cookies = response.cookies
                            if "session_token" in cookies:
                                self.session_cookie = cookies["session_token"].value
                                self.record_test("Registration Sets Session Cookie", True)
                            else:
                                self.record_test("Registration Sets Session Cookie", False, "No session_token cookie found")
                            
                        else:
                            self.record_test("Registration Returns User Data", False, f"Invalid user data: {user}")
                    else:
                        self.record_test("Registration Returns User Data", False, f"No user object in response: {data}")
                        
                else:
                    error_text = await response.text()
                    self.record_test("Registration Returns User Data", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.record_test("Registration Returns User Data", False, str(e))
    
    async def test_user_created_in_database(self):
        """Test that user is created in database with email_verified: true."""
        try:
            # Try to login with the newly created user to verify database creation
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    user = data.get("user", {})
                    
                    if user.get("email_verified") is True:
                        self.record_test("User Created with email_verified=true", True)
                    else:
                        self.record_test("User Created with email_verified=true", False, f"email_verified is {user.get('email_verified')}")
                else:
                    error_text = await response.text()
                    self.record_test("User Created with email_verified=true", False, f"Login failed: {response.status} - {error_text}")
                    
        except Exception as e:
            self.record_test("User Created with email_verified=true", False, str(e))
    
    async def test_session_created_in_database(self):
        """Test that session is created in sessions collection."""
        if not self.session_cookie:
            self.record_test("Session Created in Database", False, "No session cookie available")
            return
            
        try:
            # Use the session cookie to access /auth/me endpoint
            headers = {"Cookie": f"session_token={self.session_cookie}"}
            
            async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("email") == self.test_user_email:
                        self.record_test("Session Created in Database", True)
                    else:
                        self.record_test("Session Created in Database", False, f"Wrong user returned: {data.get('email')}")
                else:
                    error_text = await response.text()
                    self.record_test("Session Created in Database", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.record_test("Session Created in Database", False, str(e))
    
    # ==================== PHASE 2: LOGIN STILL WORKS ====================
    
    async def test_admin_login_works(self):
        """Test Phase 2: Login with admin user still works."""
        logger.info("\n🔑 PHASE 2: Testing Login Still Works")
        
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    user = data.get("user", {})
                    
                    if user.get("email") == ADMIN_EMAIL:
                        self.record_test("Admin Login Works", True)
                    else:
                        self.record_test("Admin Login Works", False, f"Wrong user returned: {user.get('email')}")
                else:
                    error_text = await response.text()
                    self.record_test("Admin Login Works", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.record_test("Admin Login Works", False, str(e))
    
    async def test_login_no_email_verification_check(self):
        """Test that login succeeds without checking email_verified."""
        try:
            # Login with our test user
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("message") == "Login successful":
                        self.record_test("Login Without Email Verification Check", True)
                    else:
                        self.record_test("Login Without Email Verification Check", False, f"Unexpected message: {data.get('message')}")
                elif response.status == 403:
                    error_text = await response.text()
                    self.record_test("Login Without Email Verification Check", False, f"Email verification still required: {error_text}")
                else:
                    error_text = await response.text()
                    self.record_test("Login Without Email Verification Check", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.record_test("Login Without Email Verification Check", False, str(e))
    
    # ==================== PHASE 3: GOOGLE ROUTES REMOVED ====================
    
    async def test_google_login_route_removed(self):
        """Test Phase 3: Google OAuth routes return 404."""
        logger.info("\n🚫 PHASE 3: Testing Google Routes Removed")
        
        try:
            async with self.session.get(f"{BASE_URL}/auth/google/login") as response:
                if response.status == 404:
                    self.record_test("Google Login Route Returns 404", True)
                else:
                    self.record_test("Google Login Route Returns 404", False, f"Expected 404, got {response.status}")
                    
        except Exception as e:
            self.record_test("Google Login Route Returns 404", False, str(e))
    
    async def test_google_callback_route_removed(self):
        """Test that Google OAuth callback route returns 404."""
        try:
            async with self.session.get(f"{BASE_URL}/auth/google/callback") as response:
                if response.status == 404:
                    self.record_test("Google Callback Route Returns 404", True)
                else:
                    self.record_test("Google Callback Route Returns 404", False, f"Expected 404, got {response.status}")
                    
        except Exception as e:
            self.record_test("Google Callback Route Returns 404", False, str(e))
    
    # ==================== PHASE 4: AUTO-LOGIN SESSION ====================
    
    async def test_register_another_user(self):
        """Test Phase 4: Register another test user."""
        logger.info("\n🔄 PHASE 4: Testing Auto-Login Session")
        
        # Generate another unique test user
        second_test_email = self.generate_test_email()
        
        try:
            registration_data = {
                "email": second_test_email,
                "name": "Second Test User",
                "password": "SecondTestPassword123!",
                "phone": "+237987654321"
            }
            
            async with self.session.post(f"{BASE_URL}/auth/register", json=registration_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for session cookie
                    cookies = response.cookies
                    if "session_token" in cookies:
                        second_session_cookie = cookies["session_token"].value
                        
                        # Store for next test
                        self.second_user_email = second_test_email
                        self.second_session_cookie = second_session_cookie
                        
                        self.record_test("Register Second User", True)
                    else:
                        self.record_test("Register Second User", False, "No session cookie in response")
                else:
                    error_text = await response.text()
                    self.record_test("Register Second User", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.record_test("Register Second User", False, str(e))
    
    async def test_auto_login_session_valid(self):
        """Test that auto-login session is valid immediately after registration."""
        if not hasattr(self, 'second_session_cookie'):
            self.record_test("Auto-Login Session Valid", False, "No second session cookie available")
            return
            
        try:
            # Use the session cookie to access /auth/me endpoint
            headers = {"Cookie": f"session_token={self.second_session_cookie}"}
            
            async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("email") == self.second_user_email:
                        self.record_test("Auto-Login Session Valid", True)
                    else:
                        self.record_test("Auto-Login Session Valid", False, f"Wrong user returned: {data.get('email')}")
                else:
                    error_text = await response.text()
                    self.record_test("Auto-Login Session Valid", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.record_test("Auto-Login Session Valid", False, str(e))
    
    # ==================== ADDITIONAL VALIDATION TESTS ====================
    
    async def test_duplicate_email_registration(self):
        """Test that duplicate email registration is properly rejected."""
        try:
            # Try to register with the same email again
            duplicate_data = {
                "email": self.test_user_email,
                "name": "Duplicate User",
                "password": "DuplicatePassword123!",
                "phone": "+237111111111"
            }
            
            async with self.session.post(f"{BASE_URL}/auth/register", json=duplicate_data) as response:
                if response.status == 400:
                    error_data = await response.json()
                    if "already registered" in error_data.get("detail", "").lower():
                        self.record_test("Duplicate Email Registration Rejected", True)
                    else:
                        self.record_test("Duplicate Email Registration Rejected", False, f"Wrong error message: {error_data}")
                else:
                    self.record_test("Duplicate Email Registration Rejected", False, f"Expected 400, got {response.status}")
                    
        except Exception as e:
            self.record_test("Duplicate Email Registration Rejected", False, str(e))
    
    async def test_invalid_login_credentials(self):
        """Test that invalid login credentials are properly rejected."""
        try:
            # Try to login with wrong password
            invalid_login = {
                "email": self.test_user_email,
                "password": "WrongPassword123!"
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=invalid_login) as response:
                if response.status == 401:
                    self.record_test("Invalid Login Credentials Rejected", True)
                else:
                    self.record_test("Invalid Login Credentials Rejected", False, f"Expected 401, got {response.status}")
                    
        except Exception as e:
            self.record_test("Invalid Login Credentials Rejected", False, str(e))
    
    # ==================== MAIN TEST RUNNER ====================
    
    async def run_all_tests(self):
        """Run all authentication tests."""
        logger.info("🚀 Starting Auto-Login Registration Flow Testing")
        logger.info("=" * 60)
        
        try:
            # Setup
            await self.setup_session()
            
            # Phase 1: Test New Registration Flow
            await self.test_new_registration_flow()
            await self.test_user_created_in_database()
            await self.test_session_created_in_database()
            
            # Phase 2: Test Login Still Works
            await self.test_admin_login_works()
            await self.test_login_no_email_verification_check()
            
            # Phase 3: Test Google Routes Removed
            await self.test_google_login_route_removed()
            await self.test_google_callback_route_removed()
            
            # Phase 4: Verify Auto-Login Session
            await self.test_register_another_user()
            await self.test_auto_login_session_valid()
            
            # Additional Validation Tests
            await self.test_duplicate_email_registration()
            await self.test_invalid_login_credentials()
            
        except Exception as e:
            logger.error(f"❌ Critical error during testing: {str(e)}")
            self.results["errors"].append(f"Critical error: {str(e)}")
        
        finally:
            await self.cleanup_session()
        
        return self.results
    
    def print_summary(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 60)
        logger.info("🎯 AUTO-LOGIN REGISTRATION FLOW TEST RESULTS")
        logger.info("=" * 60)
        
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info(f"📊 Total Tests: {total}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results["errors"]:
            logger.info(f"\n❌ FAILED TESTS ({len(self.results['errors'])}):") 
            for i, error in enumerate(self.results["errors"], 1):
                logger.info(f"   {i}. {error}")
        
        logger.info("\n" + "=" * 60)
        
        # Determine overall status
        if success_rate >= 90:
            logger.info("🎉 AUTO-LOGIN REGISTRATION: EXCELLENT - Production Ready!")
        elif success_rate >= 75:
            logger.info("✅ AUTO-LOGIN REGISTRATION: GOOD - Minor issues to address")
        elif success_rate >= 50:
            logger.info("⚠️ AUTO-LOGIN REGISTRATION: NEEDS WORK - Several issues found")
        else:
            logger.info("❌ AUTO-LOGIN REGISTRATION: CRITICAL ISSUES - Major problems detected")


async def main():
    """Main test execution function."""
    tester = AuthRegistrationTester()
    
    try:
        results = await tester.run_all_tests()
        tester.print_summary()
        
        # Return results for external processing
        return results
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Testing interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
    
    return tester.results


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())