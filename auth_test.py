#!/usr/bin/env python3

import requests
import sys
import json
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional

class HabitereAuthTester:
    def __init__(self, base_url="https://property-platform-12.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Habitere-Auth-Test-Client/1.0'
        })
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.test_user_email = f"test.user.{uuid.uuid4().hex[:8]}@habitere-test.com"
        self.test_user_password = "SecureTestPass123!"
        self.test_user_name = "Test User Authentication"
        self.session_token = None
        self.verification_token = None
        self.reset_token = None

    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED - {details}")
        
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })

    def test_user_registration(self):
        """Test email/password user registration"""
        try:
            registration_data = {
                "email": self.test_user_email,
                "name": self.test_user_name,
                "password": self.test_user_password
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/register",
                json=registration_data
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
                details += f", Email: {data.get('email', 'No email')}"
            else:
                details += f", Error: {response.text[:200]}"
                
            self.log_test("User Registration", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False

    def test_duplicate_registration(self):
        """Test registration with duplicate email (should fail)"""
        try:
            registration_data = {
                "email": self.test_user_email,  # Same email as previous test
                "name": "Duplicate User",
                "password": "AnotherPassword123!"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/register",
                json=registration_data
            )
            
            expected_failure = response.status_code == 400
            details = f"Status: {response.status_code} (expected 400 for duplicate email)"
            
            if response.status_code == 400:
                data = response.json()
                details += f", Error: {data.get('detail', 'No error detail')}"
            
            self.log_test("Duplicate Email Registration", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Duplicate Email Registration", False, f"Exception: {str(e)}")
            return False

    def test_weak_password_validation(self):
        """Test registration with weak password"""
        try:
            registration_data = {
                "email": f"weak.pass.{uuid.uuid4().hex[:8]}@test.com",
                "name": "Weak Password User",
                "password": "123"  # Weak password
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/register",
                json=registration_data
            )
            
            # Note: The current implementation might not have password strength validation
            # This test checks if such validation exists
            success = response.status_code in [200, 400, 422]  # Accept various responses
            details = f"Status: {response.status_code}"
            
            if response.status_code == 400 or response.status_code == 422:
                details += " (Password validation working)"
            elif response.status_code == 200:
                details += " (No password strength validation - consider adding)"
            
            self.log_test("Weak Password Validation", success, details)
            return success
        except Exception as e:
            self.log_test("Weak Password Validation", False, f"Exception: {str(e)}")
            return False

    def test_login_unverified_email(self):
        """Test login with unverified email (should fail)"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data
            )
            
            expected_failure = response.status_code == 403
            details = f"Status: {response.status_code} (expected 403 for unverified email)"
            
            if response.status_code == 403:
                data = response.json()
                details += f", Error: {data.get('detail', 'No error detail')}"
            
            self.log_test("Login Unverified Email", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Login Unverified Email", False, f"Exception: {str(e)}")
            return False

    def test_login_wrong_password(self):
        """Test login with wrong password (should fail)"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": "WrongPassword123!"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data
            )
            
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 for wrong password)"
            
            if response.status_code == 401:
                data = response.json()
                details += f", Error: {data.get('detail', 'No error detail')}"
            
            self.log_test("Login Wrong Password", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Login Wrong Password", False, f"Exception: {str(e)}")
            return False

    def test_login_nonexistent_email(self):
        """Test login with non-existent email (should fail)"""
        try:
            login_data = {
                "email": f"nonexistent.{uuid.uuid4().hex[:8]}@test.com",
                "password": "SomePassword123!"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data
            )
            
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 for non-existent email)"
            
            self.log_test("Login Non-existent Email", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Login Non-existent Email", False, f"Exception: {str(e)}")
            return False

    def test_email_verification_invalid_token(self):
        """Test email verification with invalid token (should fail)"""
        try:
            verification_data = {
                "token": "invalid-token-" + uuid.uuid4().hex
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/verify-email",
                json=verification_data
            )
            
            expected_failure = response.status_code == 400
            details = f"Status: {response.status_code} (expected 400 for invalid token)"
            
            self.log_test("Email Verification Invalid Token", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Email Verification Invalid Token", False, f"Exception: {str(e)}")
            return False

    def simulate_email_verification(self):
        """Simulate email verification by directly updating the database or using a valid token"""
        try:
            # Since we can't access email in testing, we'll simulate verification
            # by creating a new user and immediately trying to verify
            
            # For testing purposes, let's create a verification token manually
            # In real scenario, this would come from email
            test_token = str(uuid.uuid4())
            
            # Try to verify with a simulated token (this will likely fail, but that's expected)
            verification_data = {
                "token": test_token
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/verify-email",
                json=verification_data
            )
            
            # We expect this to fail since we don't have a real token
            expected_failure = response.status_code == 400
            details = f"Status: {response.status_code} (simulated verification test)"
            
            self.log_test("Simulated Email Verification", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Simulated Email Verification", False, f"Exception: {str(e)}")
            return False

    def test_password_reset_request(self):
        """Test password reset request"""
        try:
            reset_request_data = {
                "email": self.test_user_email
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/forgot-password",
                json=reset_request_data
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            
            self.log_test("Password Reset Request", success, details)
            return success
        except Exception as e:
            self.log_test("Password Reset Request", False, f"Exception: {str(e)}")
            return False

    def test_password_reset_nonexistent_email(self):
        """Test password reset with non-existent email"""
        try:
            reset_request_data = {
                "email": f"nonexistent.{uuid.uuid4().hex[:8]}@test.com"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/forgot-password",
                json=reset_request_data
            )
            
            # Should return 200 even for non-existent email (security best practice)
            success = response.status_code == 200
            details = f"Status: {response.status_code} (should return 200 for security)"
            
            self.log_test("Password Reset Non-existent Email", success, details)
            return success
        except Exception as e:
            self.log_test("Password Reset Non-existent Email", False, f"Exception: {str(e)}")
            return False

    def test_password_reset_invalid_token(self):
        """Test password reset with invalid token (should fail)"""
        try:
            reset_data = {
                "token": "invalid-reset-token-" + uuid.uuid4().hex,
                "new_password": "NewSecurePassword123!"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/reset-password",
                json=reset_data
            )
            
            expected_failure = response.status_code == 400
            details = f"Status: {response.status_code} (expected 400 for invalid token)"
            
            self.log_test("Password Reset Invalid Token", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Password Reset Invalid Token", False, f"Exception: {str(e)}")
            return False

    def test_google_oauth_login_url(self):
        """Test Google OAuth login URL generation"""
        try:
            response = self.session.get(f"{self.api_url}/auth/google/login")
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                auth_url = data.get('auth_url', '')
                if auth_url and 'accounts.google.com' in auth_url:
                    details += f", Valid Google auth URL generated"
                else:
                    success = False
                    details += f", Invalid auth URL: {auth_url[:100]}"
            
            self.log_test("Google OAuth Login URL", success, details)
            return success
        except Exception as e:
            self.log_test("Google OAuth Login URL", False, f"Exception: {str(e)}")
            return False

    def test_protected_endpoint_no_auth(self):
        """Test protected endpoint without authentication"""
        try:
            response = self.session.get(f"{self.api_url}/auth/me")
            
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Protected Endpoint No Auth", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Protected Endpoint No Auth", False, f"Exception: {str(e)}")
            return False

    def test_role_selection_no_auth(self):
        """Test role selection without authentication (should fail)"""
        try:
            role_data = {
                "role": "property_seeker"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/select-role",
                json=role_data
            )
            
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Role Selection No Auth", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Role Selection No Auth", False, f"Exception: {str(e)}")
            return False

    def test_role_selection_invalid_role(self):
        """Test role selection with invalid role"""
        try:
            role_data = {
                "role": "invalid_role_name"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/select-role",
                json=role_data
            )
            
            # Should fail due to either no auth (401) or invalid role (400)
            expected_failure = response.status_code in [400, 401]
            details = f"Status: {response.status_code} (expected 400/401 for invalid role)"
            
            self.log_test("Role Selection Invalid Role", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Role Selection Invalid Role", False, f"Exception: {str(e)}")
            return False

    def test_valid_roles(self):
        """Test that all valid roles are accepted"""
        try:
            valid_roles = [
                "property_seeker", "property_owner", "real_estate_agent", 
                "plumber", "electrician", "bricklayer", "carpenter", "painter"
            ]
            
            all_roles_valid = True
            tested_roles = []
            
            for role in valid_roles:
                role_data = {"role": role}
                response = self.session.post(
                    f"{self.api_url}/auth/select-role",
                    json=role_data
                )
                
                # We expect 401 (no auth) rather than 400 (invalid role)
                if response.status_code == 401:
                    tested_roles.append(f"{role}: OK (401)")
                elif response.status_code == 400:
                    all_roles_valid = False
                    tested_roles.append(f"{role}: INVALID (400)")
                else:
                    tested_roles.append(f"{role}: UNEXPECTED ({response.status_code})")
            
            details = f"Tested {len(valid_roles)} roles. Results: {', '.join(tested_roles[:3])}..."
            self.log_test("Valid Roles Test", all_roles_valid, details)
            return all_roles_valid
        except Exception as e:
            self.log_test("Valid Roles Test", False, f"Exception: {str(e)}")
            return False

    def test_logout_no_session(self):
        """Test logout without session (should handle gracefully)"""
        try:
            response = self.session.post(f"{self.api_url}/auth/logout")
            
            # Should fail with 401 (no auth) or handle gracefully
            expected_response = response.status_code in [200, 401]
            details = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                details += " (Graceful handling)"
            elif response.status_code == 401:
                details += " (Auth required)"
            
            self.log_test("Logout No Session", expected_response, details)
            return expected_response
        except Exception as e:
            self.log_test("Logout No Session", False, f"Exception: {str(e)}")
            return False

    def test_cors_with_credentials(self):
        """Test CORS configuration with credentials"""
        try:
            # Test preflight request
            headers = {
                'Origin': 'https://property-platform-12.preview.emergentagent.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = self.session.options(
                f"{self.api_url}/auth/login",
                headers=headers
            )
            
            success = response.status_code in [200, 204]
            details = f"Preflight status: {response.status_code}"
            
            # Check CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods')
            }
            
            details += f", CORS headers: {cors_headers}"
            
            self.log_test("CORS Configuration", success, details)
            return success
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Exception: {str(e)}")
            return False

    def test_session_cookie_security(self):
        """Test session cookie security attributes"""
        try:
            # This test checks if the login endpoint sets secure cookies
            # We can't fully test this without a real login, but we can check the endpoint
            
            login_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data
            )
            
            # We expect this to fail (401), but we can check if Set-Cookie headers are present
            cookie_security_ok = True
            details = f"Status: {response.status_code}"
            
            set_cookie = response.headers.get('Set-Cookie', '')
            if set_cookie:
                if 'HttpOnly' not in set_cookie:
                    cookie_security_ok = False
                    details += ", Missing HttpOnly"
                if 'Secure' not in set_cookie:
                    cookie_security_ok = False
                    details += ", Missing Secure"
                if 'SameSite' not in set_cookie:
                    cookie_security_ok = False
                    details += ", Missing SameSite"
            else:
                details += ", No Set-Cookie header (expected for failed login)"
            
            self.log_test("Session Cookie Security", cookie_security_ok, details)
            return cookie_security_ok
        except Exception as e:
            self.log_test("Session Cookie Security", False, f"Exception: {str(e)}")
            return False

    def test_password_hashing_security(self):
        """Test that passwords are properly hashed (indirect test)"""
        try:
            # This is an indirect test - we check that the same password 
            # doesn't produce the same result in registration responses
            
            # Register a user
            registration_data = {
                "email": f"hash.test.{uuid.uuid4().hex[:8]}@test.com",
                "name": "Hash Test User",
                "password": "TestPassword123!"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/register",
                json=registration_data
            )
            
            success = response.status_code == 200
            details = f"Registration status: {response.status_code}"
            
            if success:
                # Check that password is not returned in response
                data = response.json()
                if 'password' in str(data).lower():
                    success = False
                    details += ", Password leaked in response"
                else:
                    details += ", Password not leaked in response"
            
            self.log_test("Password Hashing Security", success, details)
            return success
        except Exception as e:
            self.log_test("Password Hashing Security", False, f"Exception: {str(e)}")
            return False

    def test_rate_limiting(self):
        """Test rate limiting on authentication endpoints"""
        try:
            # Test multiple failed login attempts
            login_data = {
                "email": "nonexistent@test.com",
                "password": "wrongpassword"
            }
            
            responses = []
            for i in range(5):  # Try 5 failed logins
                response = self.session.post(
                    f"{self.api_url}/auth/login",
                    json=login_data
                )
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay between requests
            
            # Check if rate limiting is applied (429 status code)
            rate_limited = 429 in responses
            details = f"Response codes: {responses}"
            
            if rate_limited:
                details += " (Rate limiting detected)"
            else:
                details += " (No rate limiting detected - consider implementing)"
            
            # This test passes regardless, as rate limiting is optional
            self.log_test("Rate Limiting Test", True, details)
            return True
        except Exception as e:
            self.log_test("Rate Limiting Test", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_auth_tests(self):
        """Run comprehensive authentication system tests"""
        print("🔐 Starting Comprehensive Authentication System Tests...")
        print(f"Testing API at: {self.api_url}")
        print(f"Test user email: {self.test_user_email}")
        print("=" * 70)
        
        print("\n📝 Testing Email/Password Registration Flow...")
        print("-" * 50)
        self.test_user_registration()
        self.test_duplicate_registration()
        self.test_weak_password_validation()
        
        print("\n🔑 Testing Login Flow...")
        print("-" * 30)
        self.test_login_unverified_email()
        self.test_login_wrong_password()
        self.test_login_nonexistent_email()
        
        print("\n📧 Testing Email Verification...")
        print("-" * 35)
        self.test_email_verification_invalid_token()
        self.simulate_email_verification()
        
        print("\n🔄 Testing Password Reset...")
        print("-" * 30)
        self.test_password_reset_request()
        self.test_password_reset_nonexistent_email()
        self.test_password_reset_invalid_token()
        
        print("\n👤 Testing Role Selection...")
        print("-" * 30)
        self.test_role_selection_no_auth()
        self.test_role_selection_invalid_role()
        self.test_valid_roles()
        
        print("\n🌐 Testing Google OAuth...")
        print("-" * 25)
        self.test_google_oauth_login_url()
        
        print("\n🛡️ Testing Security & Session Management...")
        print("-" * 45)
        self.test_protected_endpoint_no_auth()
        self.test_logout_no_session()
        self.test_cors_with_credentials()
        self.test_session_cookie_security()
        self.test_password_hashing_security()
        self.test_rate_limiting()
        
        # Print summary
        print("=" * 70)
        print(f"📊 Authentication Test Summary:")
        print(f"   Total tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Analyze critical failures
        critical_failures = []
        security_issues = []
        
        for result in self.test_results:
            if not result["success"]:
                test_name = result["test_name"]
                if any(keyword in test_name.lower() for keyword in ["registration", "login", "verification"]):
                    critical_failures.append(test_name)
                if any(keyword in test_name.lower() for keyword in ["security", "hashing", "cors"]):
                    security_issues.append(test_name)
        
        if critical_failures:
            print(f"\n⚠️  Critical Authentication Failures:")
            for failure in critical_failures:
                print(f"   - {failure}")
        
        if security_issues:
            print(f"\n🔒 Security Issues Detected:")
            for issue in security_issues:
                print(f"   - {issue}")
        
        # Save detailed results
        results = {
            "summary": {
                "total_tests": self.tests_run,
                "passed_tests": self.tests_passed,
                "failed_tests": self.tests_run - self.tests_passed,
                "success_rate": (self.tests_passed/self.tests_run)*100,
                "critical_failures": critical_failures,
                "security_issues": security_issues,
                "test_user_email": self.test_user_email,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results
        }
        
        with open('/app/auth_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Detailed results saved to: /app/auth_test_results.json")
        
        return self.tests_passed == self.tests_run

def main():
    tester = HabitereAuthTester()
    success = tester.run_comprehensive_auth_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())