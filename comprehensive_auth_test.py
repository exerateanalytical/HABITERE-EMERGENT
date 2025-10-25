#!/usr/bin/env python3
"""
Comprehensive Authentication System Testing
==========================================

Additional comprehensive tests for the auto-login registration system
to ensure all edge cases and workflows are properly handled.

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
BASE_URL = "https://realestate-cam.preview.emergentagent.com/api"

class ComprehensiveAuthTester:
    """Additional comprehensive authentication tests."""
    
    def __init__(self):
        self.session = None
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
        return f"comprehensive_test_{random_suffix}@habitere.com"
    
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
    
    async def test_registration_validation(self):
        """Test registration input validation."""
        logger.info("\n📝 Testing Registration Validation")
        
        # Test missing email
        try:
            invalid_data = {
                "name": "Test User",
                "password": "TestPassword123!"
            }
            
            async with self.session.post(f"{BASE_URL}/auth/register", json=invalid_data) as response:
                if response.status == 422:  # Validation error
                    self.record_test("Registration Validation - Missing Email", True)
                else:
                    self.record_test("Registration Validation - Missing Email", False, f"Expected 422, got {response.status}")
        except Exception as e:
            self.record_test("Registration Validation - Missing Email", False, str(e))
        
        # Test missing password
        try:
            invalid_data = {
                "email": self.generate_test_email(),
                "name": "Test User"
            }
            
            async with self.session.post(f"{BASE_URL}/auth/register", json=invalid_data) as response:
                if response.status == 422:  # Validation error
                    self.record_test("Registration Validation - Missing Password", True)
                else:
                    self.record_test("Registration Validation - Missing Password", False, f"Expected 422, got {response.status}")
        except Exception as e:
            self.record_test("Registration Validation - Missing Password", False, str(e))
        
        # Test invalid email format
        try:
            invalid_data = {
                "email": "invalid-email-format",
                "name": "Test User",
                "password": "TestPassword123!"
            }
            
            async with self.session.post(f"{BASE_URL}/auth/register", json=invalid_data) as response:
                if response.status in [400, 422]:  # Validation error
                    self.record_test("Registration Validation - Invalid Email Format", True)
                else:
                    self.record_test("Registration Validation - Invalid Email Format", False, f"Expected 400/422, got {response.status}")
        except Exception as e:
            self.record_test("Registration Validation - Invalid Email Format", False, str(e))
    
    async def test_login_validation(self):
        """Test login input validation."""
        logger.info("\n🔐 Testing Login Validation")
        
        # Test missing email
        try:
            invalid_data = {
                "password": "TestPassword123!"
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=invalid_data) as response:
                if response.status == 422:  # Validation error
                    self.record_test("Login Validation - Missing Email", True)
                else:
                    self.record_test("Login Validation - Missing Email", False, f"Expected 422, got {response.status}")
        except Exception as e:
            self.record_test("Login Validation - Missing Email", False, str(e))
        
        # Test missing password
        try:
            invalid_data = {
                "email": "test@example.com"
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=invalid_data) as response:
                if response.status == 422:  # Validation error
                    self.record_test("Login Validation - Missing Password", True)
                else:
                    self.record_test("Login Validation - Missing Password", False, f"Expected 422, got {response.status}")
        except Exception as e:
            self.record_test("Login Validation - Missing Password", False, str(e))
    
    async def test_session_management(self):
        """Test session management functionality."""
        logger.info("\n🎫 Testing Session Management")
        
        # Create a test user
        test_email = self.generate_test_email()
        test_password = "SessionTestPassword123!"
        
        try:
            # Register user
            registration_data = {
                "email": test_email,
                "name": "Session Test User",
                "password": test_password,
                "phone": "+237123456789"
            }
            
            async with self.session.post(f"{BASE_URL}/auth/register", json=registration_data) as response:
                if response.status == 200:
                    cookies = response.cookies
                    if "session_token" in cookies:
                        session_token = cookies["session_token"].value
                        
                        # Test /auth/me with session
                        headers = {"Cookie": f"session_token={session_token}"}
                        async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as me_response:
                            if me_response.status == 200:
                                user_data = await me_response.json()
                                if user_data.get("email") == test_email:
                                    self.record_test("Session Management - /auth/me Works", True)
                                else:
                                    self.record_test("Session Management - /auth/me Works", False, f"Wrong user: {user_data.get('email')}")
                            else:
                                self.record_test("Session Management - /auth/me Works", False, f"Status {me_response.status}")
                        
                        # Test logout
                        async with self.session.post(f"{BASE_URL}/auth/logout", headers=headers) as logout_response:
                            if logout_response.status == 200:
                                self.record_test("Session Management - Logout Works", True)
                                
                                # Test that session is invalidated after logout
                                async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as me_after_logout:
                                    if me_after_logout.status == 401:
                                        self.record_test("Session Management - Session Invalidated After Logout", True)
                                    else:
                                        self.record_test("Session Management - Session Invalidated After Logout", False, f"Expected 401, got {me_after_logout.status}")
                            else:
                                self.record_test("Session Management - Logout Works", False, f"Status {logout_response.status}")
                    else:
                        self.record_test("Session Management - /auth/me Works", False, "No session cookie")
                else:
                    self.record_test("Session Management - /auth/me Works", False, f"Registration failed: {response.status}")
        except Exception as e:
            self.record_test("Session Management - /auth/me Works", False, str(e))
    
    async def test_multiple_sessions(self):
        """Test multiple concurrent sessions."""
        logger.info("\n👥 Testing Multiple Sessions")
        
        # Create a test user
        test_email = self.generate_test_email()
        test_password = "MultiSessionTest123!"
        
        try:
            # Register user
            registration_data = {
                "email": test_email,
                "name": "Multi Session Test User",
                "password": test_password
            }
            
            async with self.session.post(f"{BASE_URL}/auth/register", json=registration_data) as response:
                if response.status == 200:
                    # Login multiple times to create multiple sessions
                    login_data = {
                        "email": test_email,
                        "password": test_password
                    }
                    
                    session_tokens = []
                    
                    # Create 3 sessions
                    for i in range(3):
                        async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as login_response:
                            if login_response.status == 200:
                                cookies = login_response.cookies
                                if "session_token" in cookies:
                                    session_tokens.append(cookies["session_token"].value)
                    
                    if len(session_tokens) == 3:
                        # Test that all sessions work
                        all_sessions_work = True
                        for token in session_tokens:
                            headers = {"Cookie": f"session_token={token}"}
                            async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as me_response:
                                if me_response.status != 200:
                                    all_sessions_work = False
                                    break
                        
                        if all_sessions_work:
                            self.record_test("Multiple Sessions - All Sessions Work", True)
                        else:
                            self.record_test("Multiple Sessions - All Sessions Work", False, "Some sessions failed")
                    else:
                        self.record_test("Multiple Sessions - All Sessions Work", False, f"Only created {len(session_tokens)} sessions")
                else:
                    self.record_test("Multiple Sessions - All Sessions Work", False, f"Registration failed: {response.status}")
        except Exception as e:
            self.record_test("Multiple Sessions - All Sessions Work", False, str(e))
    
    async def test_edge_cases(self):
        """Test edge cases and security scenarios."""
        logger.info("\n🔒 Testing Edge Cases and Security")
        
        # Test accessing protected endpoint without authentication
        try:
            async with self.session.get(f"{BASE_URL}/auth/me") as response:
                if response.status == 401:
                    self.record_test("Security - Unauthenticated Access Blocked", True)
                else:
                    self.record_test("Security - Unauthenticated Access Blocked", False, f"Expected 401, got {response.status}")
        except Exception as e:
            self.record_test("Security - Unauthenticated Access Blocked", False, str(e))
        
        # Test with invalid session token
        try:
            headers = {"Cookie": "session_token=invalid-token-12345"}
            async with self.session.get(f"{BASE_URL}/auth/me", headers=headers) as response:
                if response.status == 401:
                    self.record_test("Security - Invalid Session Token Rejected", True)
                else:
                    self.record_test("Security - Invalid Session Token Rejected", False, f"Expected 401, got {response.status}")
        except Exception as e:
            self.record_test("Security - Invalid Session Token Rejected", False, str(e))
        
        # Test empty request bodies
        try:
            async with self.session.post(f"{BASE_URL}/auth/register", json={}) as response:
                if response.status == 422:  # Validation error
                    self.record_test("Security - Empty Registration Request Rejected", True)
                else:
                    self.record_test("Security - Empty Registration Request Rejected", False, f"Expected 422, got {response.status}")
        except Exception as e:
            self.record_test("Security - Empty Registration Request Rejected", False, str(e))
    
    async def run_all_tests(self):
        """Run all comprehensive authentication tests."""
        logger.info("🚀 Starting Comprehensive Authentication Testing")
        logger.info("=" * 60)
        
        try:
            # Setup
            await self.setup_session()
            
            # Run test suites
            await self.test_registration_validation()
            await self.test_login_validation()
            await self.test_session_management()
            await self.test_multiple_sessions()
            await self.test_edge_cases()
            
        except Exception as e:
            logger.error(f"❌ Critical error during testing: {str(e)}")
            self.results["errors"].append(f"Critical error: {str(e)}")
        
        finally:
            await self.cleanup_session()
        
        return self.results
    
    def print_summary(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 60)
        logger.info("🎯 COMPREHENSIVE AUTHENTICATION TEST RESULTS")
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
            logger.info("🎉 COMPREHENSIVE AUTHENTICATION: EXCELLENT - Production Ready!")
        elif success_rate >= 75:
            logger.info("✅ COMPREHENSIVE AUTHENTICATION: GOOD - Minor issues to address")
        elif success_rate >= 50:
            logger.info("⚠️ COMPREHENSIVE AUTHENTICATION: NEEDS WORK - Several issues found")
        else:
            logger.info("❌ COMPREHENSIVE AUTHENTICATION: CRITICAL ISSUES - Major problems detected")


async def main():
    """Main test execution function."""
    tester = ComprehensiveAuthTester()
    
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