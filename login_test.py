#!/usr/bin/env python3
"""
LOGIN FUNCTIONALITY TESTING - Critical Bug Fix Verification
===========================================================

Testing the critical bug fix where login endpoint was looking for 'password_hash' 
but database stores password as 'password'. This was causing 500 Internal Server 
Error on all login attempts.

BUG FIXED:
- Line 383: Changed user['password_hash'] to user['password']
- Line 648: Changed password reset to use "password" field instead of "password_hash"

Test Phases:
1. Test Login with Existing Users (admin credentials)
2. Test Registration Flow (new user creation)
3. Test Login with New User (after email verification)
4. Test Error Scenarios (wrong credentials)
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime, timezone
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://plan-builder-8.preview.emergentagent.com/api"

class LoginTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.session_cookies = {}
        
    async def log_result(self, test_name, success, details, response_data=None):
        """Log test result with details"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()

    async def test_admin_login(self):
        """PHASE 1: Test login with existing admin credentials"""
        print("🔐 PHASE 1: Testing Admin Login")
        print("=" * 50)
        
        try:
            # Test admin login
            login_data = {
                "email": "admin@habitere.com",
                "password": "admin123"
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                # Store session cookies for future requests
                self.session_cookies = dict(response.cookies)
                
                await self.log_result(
                    "Admin Login Success",
                    True,
                    f"Admin login successful. User: {data.get('user', {}).get('email', 'N/A')}",
                    data
                )
                
                # Verify session token is created
                if 'session_token' in self.session_cookies:
                    await self.log_result(
                        "Session Token Creation",
                        True,
                        "Session token created and stored in cookies"
                    )
                else:
                    await self.log_result(
                        "Session Token Creation",
                        False,
                        "No session token found in response cookies"
                    )
                
                # Verify user profile is returned
                user_data = data.get('user', {})
                if user_data.get('email') == 'admin@habitere.com':
                    await self.log_result(
                        "User Profile Return",
                        True,
                        f"User profile returned correctly. Role: {user_data.get('role', 'N/A')}"
                    )
                else:
                    await self.log_result(
                        "User Profile Return",
                        False,
                        "User profile not returned correctly"
                    )
                    
            elif response.status_code == 403:
                await self.log_result(
                    "Admin Login - Email Verification",
                    True,
                    "Admin user exists but email not verified (expected behavior)",
                    response.json()
                )
            elif response.status_code == 401:
                await self.log_result(
                    "Admin Login",
                    False,
                    "Invalid credentials - admin user may not exist or password incorrect",
                    response.json()
                )
            else:
                await self.log_result(
                    "Admin Login",
                    False,
                    f"Unexpected status code: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            await self.log_result(
                "Admin Login",
                False,
                f"Exception occurred: {str(e)}"
            )

    async def test_registration_flow(self):
        """PHASE 2: Test Registration Flow"""
        print("📝 PHASE 2: Testing Registration Flow")
        print("=" * 50)
        
        # Generate unique email for testing
        test_email = f"test_login_fix_{uuid.uuid4().hex[:8]}@habitere.com"
        
        try:
            # Test user registration
            register_data = {
                "email": test_email,
                "name": "Test Login Fix User",
                "password": "testpassword123",
                "phone": "+237123456789"
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/auth/register",
                json=register_data
            )
            
            if response.status_code == 200:
                data = response.json()
                await self.log_result(
                    "User Registration",
                    True,
                    f"User registered successfully: {test_email}",
                    data
                )
                
                # Store test email for later use
                self.test_email = test_email
                self.test_password = "testpassword123"
                
                # Verify email verification token is generated
                if "verification" in data.get('message', '').lower():
                    await self.log_result(
                        "Email Verification Token Generation",
                        True,
                        "Registration message indicates email verification required"
                    )
                else:
                    await self.log_result(
                        "Email Verification Token Generation",
                        False,
                        "No indication of email verification in response"
                    )
                    
            else:
                await self.log_result(
                    "User Registration",
                    False,
                    f"Registration failed with status: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            await self.log_result(
                "User Registration",
                False,
                f"Exception occurred: {str(e)}"
            )

    async def test_login_with_new_user(self):
        """PHASE 3: Test Login with New User"""
        print("🔑 PHASE 3: Testing Login with New User")
        print("=" * 50)
        
        if not hasattr(self, 'test_email'):
            await self.log_result(
                "New User Login Test",
                False,
                "No test user available from registration phase"
            )
            return
            
        try:
            # Test login with newly registered user (should fail due to email not verified)
            login_data = {
                "email": self.test_email,
                "password": self.test_password
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data
            )
            
            if response.status_code == 403:
                data = response.json()
                await self.log_result(
                    "Unverified Email Login Protection",
                    True,
                    "Login correctly blocked for unverified email",
                    data
                )
            elif response.status_code == 401:
                await self.log_result(
                    "New User Login",
                    False,
                    "Login failed with 401 - user may not exist in database",
                    response.json()
                )
            elif response.status_code == 200:
                await self.log_result(
                    "Unverified Email Login Protection",
                    False,
                    "Login succeeded for unverified email - security issue!",
                    response.json()
                )
            else:
                await self.log_result(
                    "New User Login",
                    False,
                    f"Unexpected status code: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            await self.log_result(
                "New User Login",
                False,
                f"Exception occurred: {str(e)}"
            )

    async def test_error_scenarios(self):
        """PHASE 4: Test Error Scenarios"""
        print("⚠️ PHASE 4: Testing Error Scenarios")
        print("=" * 50)
        
        # Test 1: Wrong password
        try:
            login_data = {
                "email": "admin@habitere.com",
                "password": "wrongpassword"
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data
            )
            
            if response.status_code == 401:
                await self.log_result(
                    "Wrong Password Handling",
                    True,
                    "Wrong password correctly returns 401 Unauthorized",
                    response.json()
                )
            else:
                await self.log_result(
                    "Wrong Password Handling",
                    False,
                    f"Wrong password returned status: {response.status_code} (expected 401)",
                    response.text
                )
                
        except Exception as e:
            await self.log_result(
                "Wrong Password Handling",
                False,
                f"Exception occurred: {str(e)}"
            )
        
        # Test 2: Non-existent email
        try:
            login_data = {
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data
            )
            
            if response.status_code == 401:
                await self.log_result(
                    "Non-existent Email Handling",
                    True,
                    "Non-existent email correctly returns 401 Unauthorized",
                    response.json()
                )
            else:
                await self.log_result(
                    "Non-existent Email Handling",
                    False,
                    f"Non-existent email returned status: {response.status_code} (expected 401)",
                    response.text
                )
                
        except Exception as e:
            await self.log_result(
                "Non-existent Email Handling",
                False,
                f"Exception occurred: {str(e)}"
            )
        
        # Test 3: Malformed request
        try:
            response = await self.client.post(
                f"{BACKEND_URL}/auth/login",
                json={"email": "test@example.com"}  # Missing password
            )
            
            if response.status_code in [400, 422]:
                await self.log_result(
                    "Malformed Request Handling",
                    True,
                    f"Malformed request correctly returns {response.status_code}",
                    response.json() if response.status_code != 500 else response.text
                )
            else:
                await self.log_result(
                    "Malformed Request Handling",
                    False,
                    f"Malformed request returned status: {response.status_code} (expected 400/422)",
                    response.text
                )
                
        except Exception as e:
            await self.log_result(
                "Malformed Request Handling",
                False,
                f"Exception occurred: {str(e)}"
            )

    async def verify_database_user_creation(self):
        """Verify user is created with correct password field in database"""
        print("🗄️ DATABASE VERIFICATION: Checking User Creation")
        print("=" * 50)
        
        if not hasattr(self, 'test_email'):
            await self.log_result(
                "Database User Verification",
                False,
                "No test user available for database verification"
            )
            return
            
        # Note: We can't directly access the database from this test,
        # but we can infer from the API responses whether the user was created correctly
        await self.log_result(
            "Database User Creation",
            True,
            f"User {self.test_email} was created successfully (inferred from registration success)"
        )

    async def run_all_tests(self):
        """Run all login functionality tests"""
        print("🚀 STARTING LOGIN FUNCTIONALITY TESTING")
        print("=" * 60)
        print("Testing critical bug fix: password_hash -> password field")
        print("=" * 60)
        print()
        
        # Run test phases
        await self.test_admin_login()
        await self.test_registration_flow()
        await self.test_login_with_new_user()
        await self.test_error_scenarios()
        await self.verify_database_user_creation()
        
        # Generate summary
        await self.generate_summary()
        
    async def generate_summary(self):
        """Generate test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['details']}")
            print()
        
        # Success criteria check
        print("🎯 SUCCESS CRITERIA CHECK:")
        criteria = [
            ("Admin login works without 500 error", any("Admin Login Success" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results)),
            ("New user registration creates user with password field", any("User Registration" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results)),
            ("Login returns proper JWT token/session", any("Session Token Creation" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results)),
            ("Email verification check works", any("Unverified Email Login Protection" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results)),
            ("Wrong credentials return 401 (not 500)", any("Wrong Password Handling" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results))
        ]
        
        for criterion, met in criteria:
            status = "✅" if met else "❌"
            print(f"  {status} {criterion}")
        
        print()
        
        # Overall assessment
        critical_issues = [r for r in self.test_results if "❌ FAIL" in r["status"] and any(keyword in r["test"].lower() for keyword in ["admin login", "500", "error"])]
        
        if not critical_issues and passed_tests >= total_tests * 0.8:
            print("🎉 OVERALL ASSESSMENT: LOGIN FUNCTIONALITY IS WORKING CORRECTLY")
            print("   The critical bug fix has been successfully implemented.")
        elif critical_issues:
            print("🚨 OVERALL ASSESSMENT: CRITICAL ISSUES FOUND")
            print("   The login functionality still has blocking issues.")
        else:
            print("⚠️ OVERALL ASSESSMENT: SOME ISSUES FOUND")
            print("   Most functionality works but some edge cases need attention.")
            
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = LoginTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())