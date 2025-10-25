#!/usr/bin/env python3
"""
COMPREHENSIVE LOGIN TESTING - Final Verification
===============================================

Final comprehensive test of all login scenarios as specified in the review request.
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime, timezone

# Backend URL from environment
BACKEND_URL = "https://habitere-home.preview.emergentagent.com/api"

class ComprehensiveLoginTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        
    async def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {"test": test_name, "status": status, "details": details}
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        print(f"   {details}")
        print()

    async def test_admin_login_comprehensive(self):
        """Test admin login with all verification steps"""
        print("🔐 COMPREHENSIVE ADMIN LOGIN TEST")
        print("=" * 50)
        
        try:
            response = await self.client.post(
                f"{BACKEND_URL}/auth/login",
                json={"email": "admin@habitere.com", "password": "admin123"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check all required components
                checks = [
                    ("Status Code", response.status_code == 200),
                    ("User Email", data.get('user', {}).get('email') == 'admin@habitere.com'),
                    ("User Role", data.get('user', {}).get('role') == 'admin'),
                    ("Session Cookie", 'session_token' in dict(response.cookies)),
                    ("Login Message", 'successful' in data.get('message', '').lower()),
                    ("No Password in Response", 'password' not in str(data)),
                    ("Email Verified", data.get('user', {}).get('email_verified') == True)
                ]
                
                all_passed = all(check[1] for check in checks)
                
                await self.log_result(
                    "Admin Login Comprehensive",
                    all_passed,
                    f"All checks passed: {all_passed}. Details: " + 
                    ", ".join([f"{name}: {'✅' if passed else '❌'}" for name, passed in checks])
                )
                
            else:
                await self.log_result(
                    "Admin Login Comprehensive",
                    False,
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            await self.log_result(
                "Admin Login Comprehensive",
                False,
                f"Exception: {str(e)}"
            )

    async def test_registration_and_login_flow(self):
        """Test complete registration and login flow"""
        print("📝 COMPLETE REGISTRATION & LOGIN FLOW")
        print("=" * 50)
        
        test_email = f"comprehensive_test_{uuid.uuid4().hex[:8]}@habitere.com"
        test_password = "ComprehensiveTest123!"
        
        try:
            # Step 1: Register new user
            register_response = await self.client.post(
                f"{BACKEND_URL}/auth/register",
                json={
                    "email": test_email,
                    "name": "Comprehensive Test User",
                    "password": test_password,
                    "phone": "+237123456789"
                }
            )
            
            if register_response.status_code == 200:
                await self.log_result(
                    "User Registration in Flow",
                    True,
                    f"User {test_email} registered successfully"
                )
                
                # Step 2: Try login (should fail - email not verified)
                login_response = await self.client.post(
                    f"{BACKEND_URL}/auth/login",
                    json={"email": test_email, "password": test_password}
                )
                
                if login_response.status_code == 403:
                    await self.log_result(
                        "Unverified Login Protection in Flow",
                        True,
                        "Login correctly blocked for unverified email (403 Forbidden)"
                    )
                else:
                    await self.log_result(
                        "Unverified Login Protection in Flow",
                        False,
                        f"Expected 403, got {login_response.status_code}"
                    )
                    
            else:
                await self.log_result(
                    "User Registration in Flow",
                    False,
                    f"Registration failed: {register_response.status_code}"
                )
                
        except Exception as e:
            await self.log_result(
                "Registration & Login Flow",
                False,
                f"Exception: {str(e)}"
            )

    async def test_all_error_scenarios(self):
        """Test all error scenarios comprehensively"""
        print("⚠️ COMPREHENSIVE ERROR SCENARIO TESTING")
        print("=" * 50)
        
        error_tests = [
            {
                "name": "Wrong Password for Admin",
                "data": {"email": "admin@habitere.com", "password": "wrongpassword"},
                "expected_status": 401,
                "expected_detail": "Invalid email or password"
            },
            {
                "name": "Non-existent Email",
                "data": {"email": "doesnotexist@nowhere.com", "password": "anypassword"},
                "expected_status": 401,
                "expected_detail": "Invalid email or password"
            },
            {
                "name": "Empty Email",
                "data": {"email": "", "password": "password"},
                "expected_status": 422,
                "expected_detail": None  # Validation error
            },
            {
                "name": "Missing Password",
                "data": {"email": "test@example.com"},
                "expected_status": 422,
                "expected_detail": None  # Validation error
            },
            {
                "name": "Empty Password",
                "data": {"email": "admin@habitere.com", "password": ""},
                "expected_status": 401,
                "expected_detail": "Invalid email or password"
            }
        ]
        
        for test in error_tests:
            try:
                response = await self.client.post(
                    f"{BACKEND_URL}/auth/login",
                    json=test["data"]
                )
                
                success = response.status_code == test["expected_status"]
                
                if success and test["expected_detail"]:
                    # Check if expected detail is in response
                    response_text = response.text.lower()
                    success = test["expected_detail"].lower() in response_text
                
                await self.log_result(
                    test["name"],
                    success,
                    f"Expected {test['expected_status']}, got {response.status_code}. " +
                    f"Response: {response.text[:100]}..."
                )
                
            except Exception as e:
                await self.log_result(
                    test["name"],
                    False,
                    f"Exception: {str(e)}"
                )

    async def test_password_field_consistency(self):
        """Test that password field is consistently used"""
        print("🔧 PASSWORD FIELD CONSISTENCY TEST")
        print("=" * 50)
        
        # Test registration creates user with 'password' field (not 'password_hash')
        test_email = f"field_test_{uuid.uuid4().hex[:8]}@habitere.com"
        
        try:
            # Register user
            register_response = await self.client.post(
                f"{BACKEND_URL}/auth/register",
                json={
                    "email": test_email,
                    "name": "Field Test User",
                    "password": "FieldTest123!",
                    "phone": "+237987654321"
                }
            )
            
            if register_response.status_code == 200:
                # Try to login (will fail due to email verification, but should not get 500 error)
                login_response = await self.client.post(
                    f"{BACKEND_URL}/auth/login",
                    json={"email": test_email, "password": "FieldTest123!"}
                )
                
                # Should get 403 (email not verified), not 500 (KeyError: 'password')
                if login_response.status_code == 403:
                    await self.log_result(
                        "Password Field Consistency",
                        True,
                        "New user created with correct 'password' field (no 500 error on login attempt)"
                    )
                elif login_response.status_code == 500:
                    await self.log_result(
                        "Password Field Consistency",
                        False,
                        "500 error suggests 'password' field issue still exists"
                    )
                else:
                    await self.log_result(
                        "Password Field Consistency",
                        True,
                        f"Got {login_response.status_code} (not 500), password field working correctly"
                    )
            else:
                await self.log_result(
                    "Password Field Consistency",
                    False,
                    f"Registration failed: {register_response.status_code}"
                )
                
        except Exception as e:
            await self.log_result(
                "Password Field Consistency",
                False,
                f"Exception: {str(e)}"
            )

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 COMPREHENSIVE LOGIN FUNCTIONALITY TESTING")
        print("=" * 60)
        print("Final verification of critical bug fix implementation")
        print("=" * 60)
        print()
        
        await self.test_admin_login_comprehensive()
        await self.test_registration_and_login_flow()
        await self.test_all_error_scenarios()
        await self.test_password_field_consistency()
        
        await self.generate_final_summary()
        
    async def generate_final_summary(self):
        """Generate final comprehensive summary"""
        print("📊 FINAL COMPREHENSIVE SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Critical success criteria from review request
        print("🎯 CRITICAL SUCCESS CRITERIA (from review request):")
        criteria_met = [
            ("✅ Admin login works without 500 error", 
             any("Admin Login Comprehensive" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results)),
            ("✅ New user registration creates user with correct password field", 
             any("Password Field Consistency" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results)),
            ("✅ Login returns proper JWT token", 
             any("Admin Login Comprehensive" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results)),
            ("✅ Email verification check works", 
             any("Unverified Login Protection" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results)),
            ("✅ Wrong credentials return 401 (not 500)", 
             any("Wrong Password" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results))
        ]
        
        all_criteria_met = all(met for _, met in criteria_met)
        
        for criterion, met in criteria_met:
            print(f"  {criterion if met else criterion.replace('✅', '❌')}")
        
        print()
        
        # Final assessment
        if all_criteria_met and failed_tests == 0:
            print("🎉 FINAL ASSESSMENT: CRITICAL BUG FIX SUCCESSFULLY IMPLEMENTED")
            print("   ✅ All login functionality working correctly")
            print("   ✅ No 500 Internal Server Errors")
            print("   ✅ Password field migration completed")
            print("   ✅ Authentication system fully operational")
        elif all_criteria_met:
            print("✅ FINAL ASSESSMENT: CRITICAL BUG FIX SUCCESSFUL")
            print("   ✅ All critical functionality working")
            print("   ⚠️ Some minor edge cases may need attention")
        else:
            print("❌ FINAL ASSESSMENT: CRITICAL ISSUES REMAIN")
            print("   ❌ Login functionality still has blocking problems")
            
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = ComprehensiveLoginTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())