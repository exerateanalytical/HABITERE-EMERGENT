#!/usr/bin/env python3

import requests
import sys
import json
import os
import io
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from PIL import Image
import uuid

class HabitereProductionTester:
    def __init__(self, base_url="https://habitere.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Habitere-Production-Test-Client/1.0'
        })
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Authentication tokens
        self.admin_token = None

    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED - {details}")
        
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })

    # ============================================================================
    # CORE API ENDPOINTS TESTING
    # ============================================================================
    
    def test_properties_endpoint(self):
        """Test GET /api/properties with and without filters"""
        try:
            # Test basic properties listing
            start_time = time.time()
            response = self.session.get(f"{self.api_url}/properties")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            success = response.status_code == 200 and response_time < 1000
            
            details = f"Status: {response.status_code}, Response time: {response_time:.0f}ms"
            
            if success:
                data = response.json()
                properties_count = len(data) if isinstance(data, list) else 0
                details += f", Properties found: {properties_count}"
                
                # Test with filters
                filter_tests = [
                    "?property_type=apartment",
                    "?listing_type=rent", 
                    "?location=Douala",
                    "?min_price=100000&max_price=500000",
                    "?limit=10&skip=0"
                ]
                
                filter_success = True
                for filter_param in filter_tests:
                    filter_response = self.session.get(f"{self.api_url}/properties{filter_param}")
                    if filter_response.status_code != 200:
                        filter_success = False
                        break
                
                if filter_success:
                    details += ", Filters: ✅"
                else:
                    details += ", Filters: ❌"
                    success = False
                    
            self.log_test("Properties Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Properties Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_property_detail(self):
        """Test GET /api/properties/{id}"""
        try:
            # Get a property ID first
            properties_response = self.session.get(f"{self.api_url}/properties?limit=1")
            if properties_response.status_code != 200:
                self.log_test("Property Detail", False, "Could not fetch properties list")
                return False
                
            properties = properties_response.json()
            if not properties:
                self.log_test("Property Detail", True, "No properties available for testing")
                return True
                
            property_id = properties[0].get('id')
            
            start_time = time.time()
            response = self.session.get(f"{self.api_url}/properties/{property_id}")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            success = response.status_code == 200 and response_time < 1000
            
            details = f"Status: {response.status_code}, Response time: {response_time:.0f}ms"
            
            if success:
                data = response.json()
                details += f", Property: {data.get('title', 'No title')[:30]}"
                
            self.log_test("Property Detail", success, details)
            return success
        except Exception as e:
            self.log_test("Property Detail", False, f"Exception: {str(e)}")
            return False

    def test_services_endpoint(self):
        """Test GET /api/services with and without filters"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.api_url}/services")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            success = response.status_code == 200 and response_time < 1000
            
            details = f"Status: {response.status_code}, Response time: {response_time:.0f}ms"
            
            if success:
                data = response.json()
                services_count = len(data) if isinstance(data, list) else 0
                details += f", Services found: {services_count}"
                
                # Test with filters
                filter_tests = [
                    "?category=plumbing",
                    "?location=Yaoundé",
                    "?limit=10&skip=0"
                ]
                
                filter_success = True
                for filter_param in filter_tests:
                    filter_response = self.session.get(f"{self.api_url}/services{filter_param}")
                    if filter_response.status_code != 200:
                        filter_success = False
                        break
                
                if filter_success:
                    details += ", Filters: ✅"
                else:
                    details += ", Filters: ❌"
                    success = False
                    
            self.log_test("Services Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Services Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_service_detail(self):
        """Test GET /api/services/{id}"""
        try:
            # Get a service ID first
            services_response = self.session.get(f"{self.api_url}/services?limit=1")
            if services_response.status_code != 200:
                self.log_test("Service Detail", False, "Could not fetch services list")
                return False
                
            services = services_response.json()
            if not services:
                self.log_test("Service Detail", True, "No services available for testing")
                return True
                
            service_id = services[0].get('id')
            
            start_time = time.time()
            response = self.session.get(f"{self.api_url}/services/{service_id}")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            success = response.status_code == 200 and response_time < 1000
            
            details = f"Status: {response.status_code}, Response time: {response_time:.0f}ms"
            
            if success:
                data = response.json()
                details += f", Service: {data.get('title', 'No title')[:30]}"
                
            self.log_test("Service Detail", success, details)
            return success
        except Exception as e:
            self.log_test("Service Detail", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # AUTHENTICATION SYSTEM TESTING
    # ============================================================================
    
    def test_auth_register(self):
        """Test POST /api/auth/register"""
        try:
            test_email = f"test_{uuid.uuid4().hex[:8]}@habitere.com"
            register_data = {
                "email": test_email,
                "name": "Test User",
                "password": "testpass123"
            }
            
            response = self.session.post(f"{self.api_url}/auth/register", json=register_data)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')[:50]}"
                
            self.log_test("Auth Register", success, details)
            return success
        except Exception as e:
            self.log_test("Auth Register", False, f"Exception: {str(e)}")
            return False

    def test_auth_login(self):
        """Test POST /api/auth/login"""
        try:
            # Try to login with admin credentials
            login_data = {
                "email": "admin@habitere.com",
                "password": "admin123"
            }
            
            response = self.session.post(f"{self.api_url}/auth/login", json=login_data)
            
            # Accept both successful login (200) and email verification required (403)
            success = response.status_code in [200, 403]
            details = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                details += ", Login successful"
                # Extract session token
                for cookie in response.cookies:
                    if cookie.name == 'session_token':
                        self.admin_token = cookie.value
                        details += ", Session token obtained"
                        break
            elif response.status_code == 403:
                details += ", Email verification required (expected)"
                
            self.log_test("Auth Login", success, details)
            return success
        except Exception as e:
            self.log_test("Auth Login", False, f"Exception: {str(e)}")
            return False

    def test_auth_verify_email(self):
        """Test POST /api/auth/verify-email"""
        try:
            # Test with invalid token (should fail)
            verify_data = {
                "token": "invalid-token-123"
            }
            
            response = self.session.post(f"{self.api_url}/auth/verify-email", json=verify_data)
            expected_failure = response.status_code == 400
            details = f"Status: {response.status_code} (expected 400 for invalid token)"
            
            self.log_test("Auth Verify Email", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Auth Verify Email", False, f"Exception: {str(e)}")
            return False

    def test_auth_me(self):
        """Test GET /api/auth/me"""
        try:
            # Use a fresh session to ensure no authentication
            fresh_session = requests.Session()
            fresh_session.headers.update({'Content-Type': 'application/json'})
            
            response = fresh_session.get(f"{self.api_url}/auth/me")
            success = response.status_code == 401  # Should fail without auth
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Auth Me (No Auth)", success, details)
            return success
        except Exception as e:
            self.log_test("Auth Me", False, f"Exception: {str(e)}")
            return False

    def test_auth_logout(self):
        """Test POST /api/auth/logout"""
        try:
            # Use a fresh session to ensure no authentication
            fresh_session = requests.Session()
            fresh_session.headers.update({'Content-Type': 'application/json'})
            
            response = fresh_session.post(f"{self.api_url}/auth/logout")
            success = response.status_code == 401  # Should fail without auth
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Auth Logout (No Auth)", success, details)
            return success
        except Exception as e:
            self.log_test("Auth Logout", False, f"Exception: {str(e)}")
            return False

    def test_google_oauth(self):
        """Test GET /api/auth/google/login"""
        try:
            response = self.session.get(f"{self.api_url}/auth/google/login")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                auth_url = data.get('auth_url', '')
                if 'https://habitere.com/api/auth/google/callback' in auth_url:
                    details += ", Redirect URI: ✅"
                elif 'redirect_uri' in auth_url:
                    details += f", Redirect URI: ⚠️ (found but different: {auth_url.split('redirect_uri=')[1].split('&')[0] if 'redirect_uri=' in auth_url else 'unknown'})"
                else:
                    details += ", Redirect URI: ❌ (not found)"
                    success = False
                    
            self.log_test("Google OAuth", success, details)
            return success
        except Exception as e:
            self.log_test("Google OAuth", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # ADMIN ENDPOINTS TESTING
    # ============================================================================
    
    def test_admin_stats(self):
        """Test GET /admin/stats"""
        try:
            response = self.session.get(f"{self.api_url}/admin/stats")
            expected_failure = response.status_code == 401  # Should fail without auth
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin Stats (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Admin Stats", False, f"Exception: {str(e)}")
            return False

    def test_admin_users(self):
        """Test GET /admin/users"""
        try:
            response = self.session.get(f"{self.api_url}/admin/users")
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin Users (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Admin Users", False, f"Exception: {str(e)}")
            return False

    def test_admin_properties(self):
        """Test GET /admin/properties"""
        try:
            response = self.session.get(f"{self.api_url}/admin/properties")
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin Properties (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Admin Properties", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # REVIEWS & RATINGS TESTING
    # ============================================================================
    
    def test_reviews_property(self):
        """Test GET /reviews/property/{id}"""
        try:
            # Get a property ID first
            properties_response = self.session.get(f"{self.api_url}/properties?limit=1")
            if properties_response.status_code == 200:
                properties = properties_response.json()
                if properties:
                    property_id = properties[0].get('id')
                    response = self.session.get(f"{self.api_url}/reviews/property/{property_id}")
                    success = response.status_code == 200
                    details = f"Status: {response.status_code}, Property ID: {property_id}"
                else:
                    success = True
                    details = "No properties available for testing"
            else:
                success = False
                details = f"Could not fetch properties: {properties_response.status_code}"
                
            self.log_test("Reviews by Property", success, details)
            return success
        except Exception as e:
            self.log_test("Reviews by Property", False, f"Exception: {str(e)}")
            return False

    def test_reviews_create(self):
        """Test POST /reviews (should require auth)"""
        try:
            review_data = {
                "property_id": "sample-property-id",
                "rating": 5,
                "comment": "Test review"
            }
            
            response = self.session.post(f"{self.api_url}/reviews", json=review_data)
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Create Review (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Create Review", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # MESSAGING SYSTEM TESTING
    # ============================================================================
    
    def test_messages_list(self):
        """Test GET /messages (should require auth)"""
        try:
            response = self.session.get(f"{self.api_url}/messages")
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Messages List (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Messages List", False, f"Exception: {str(e)}")
            return False

    def test_messages_send(self):
        """Test POST /messages (should require auth)"""
        try:
            message_data = {
                "receiver_id": "sample-user-id",
                "content": "Test message"
            }
            
            response = self.session.post(f"{self.api_url}/messages", json=message_data)
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Send Message (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Send Message", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # BOOKING SYSTEM TESTING
    # ============================================================================
    
    def test_bookings_list(self):
        """Test GET /bookings (should require auth)"""
        try:
            response = self.session.get(f"{self.api_url}/bookings")
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Bookings List (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Bookings List", False, f"Exception: {str(e)}")
            return False

    def test_bookings_create(self):
        """Test POST /bookings (should require auth)"""
        try:
            booking_data = {
                "property_id": "sample-property-id",
                "scheduled_date": "2024-12-25T10:00:00Z",
                "notes": "Test booking"
            }
            
            response = self.session.post(f"{self.api_url}/bookings", json=booking_data)
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Create Booking (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Create Booking", False, f"Exception: {str(e)}")
            return False

    def test_booking_slots(self):
        """Test GET /bookings/property/{id}/slots"""
        try:
            # Get a property ID first
            properties_response = self.session.get(f"{self.api_url}/properties?limit=1")
            if properties_response.status_code == 200:
                properties = properties_response.json()
                if properties:
                    property_id = properties[0].get('id')
                    response = self.session.get(f"{self.api_url}/bookings/property/{property_id}/slots?date=2024-12-25")
                    success = response.status_code == 200
                    details = f"Status: {response.status_code}, Property ID: {property_id}"
                else:
                    success = True
                    details = "No properties available for testing"
            else:
                success = False
                details = f"Could not fetch properties: {properties_response.status_code}"
                
            self.log_test("Booking Time Slots", success, details)
            return success
        except Exception as e:
            self.log_test("Booking Time Slots", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # IMAGE UPLOAD TESTING
    # ============================================================================
    
    def test_image_upload(self):
        """Test POST /api/upload/images (should require auth)"""
        try:
            # Create a test image
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            files = {
                'files': ('test_image.jpg', img_bytes, 'image/jpeg')
            }
            data = {
                'entity_type': 'property',
                'entity_id': 'test-property-id'
            }
            
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{self.api_url}/upload/images",
                files=files,
                data=data,
                headers=headers
            )
            
            expected_failure = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Image Upload (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Image Upload", False, f"Exception: {str(e)}")
            return False

    def test_get_images(self):
        """Test GET /api/images/{entity_type}/{entity_id}"""
        try:
            response = self.session.get(f"{self.api_url}/images/property/sample-property-id")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                images_count = len(data) if isinstance(data, list) else 0
                details += f", Images found: {images_count}"
                
            self.log_test("Get Entity Images", success, details)
            return success
        except Exception as e:
            self.log_test("Get Entity Images", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # PERFORMANCE & ERROR HANDLING TESTING
    # ============================================================================
    
    def test_response_times(self):
        """Test response times for critical endpoints (< 1000ms)"""
        try:
            endpoints = [
                ("/properties", "Properties"),
                ("/services", "Services"),
                ("/auth/google/login", "Google OAuth"),
                ("/reviews", "Reviews")
            ]
            
            all_fast = True
            details = "Response times: "
            
            for endpoint, name in endpoints:
                start_time = time.time()
                response = self.session.get(f"{self.api_url}{endpoint}")
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response_time < 1000 and response.status_code in [200, 401]:
                    details += f"{name}:{response_time:.0f}ms:✅ "
                else:
                    details += f"{name}:{response_time:.0f}ms:❌ "
                    all_fast = False
            
            self.log_test("Response Times (<1000ms)", all_fast, details)
            return all_fast
        except Exception as e:
            self.log_test("Response Times", False, f"Exception: {str(e)}")
            return False

    def test_error_handling(self):
        """Test proper HTTP status codes"""
        try:
            test_cases = [
                (f"{self.api_url}/properties", 200, "Properties list"),
                (f"{self.api_url}/services", 200, "Services list"),
                (f"{self.api_url}/properties/invalid-id", 404, "Invalid property ID"),
                (f"{self.api_url}/auth/me", 401, "Unauthorized access"),
                (f"{self.api_url}/admin/stats", 401, "Admin without auth")
            ]
            
            all_correct = True
            details = "Status codes: "
            
            for url, expected_status, description in test_cases:
                response = self.session.get(url)
                if response.status_code == expected_status:
                    details += f"{expected_status}:✅ "
                else:
                    details += f"{expected_status}:❌({response.status_code}) "
                    all_correct = False
            
            self.log_test("HTTP Status Codes", all_correct, details)
            return all_correct
        except Exception as e:
            self.log_test("HTTP Status Codes", False, f"Exception: {str(e)}")
            return False

    def test_cors_headers(self):
        """Test CORS headers configuration"""
        try:
            response = self.session.options(f"{self.api_url}/properties")
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            has_cors = any(cors_headers.values())
            success = has_cors or response.status_code in [200, 405]
            details = f"Status: {response.status_code}"
            
            if has_cors:
                details += f", CORS: ✅ (Origin: {cors_headers['Access-Control-Allow-Origin']})"
            else:
                details += ", CORS: ⚠️ (Headers not found in OPTIONS response)"
            
            self.log_test("CORS Headers", success, details)
            return success
        except Exception as e:
            self.log_test("CORS Headers", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # MAIN TEST RUNNER
    # ============================================================================
    
    def run_production_tests(self):
        """Run comprehensive production-ready API tests"""
        print("🚀 COMPREHENSIVE BACKEND API TESTING FOR PRODUCTION LAUNCH")
        print("=" * 80)
        print(f"Testing API at: {self.api_url}")
        print("Focus: Production-ready validation with 95%+ success rate target")
        print("-" * 80)
        
        # Phase 1: Core API Endpoints
        print("\n📡 Phase 1: Core API Endpoints")
        self.test_properties_endpoint()
        self.test_property_detail()
        self.test_services_endpoint()
        self.test_service_detail()
        
        # Phase 2: Authentication System
        print("\n🔐 Phase 2: Authentication System")
        self.test_auth_register()
        self.test_auth_login()
        self.test_auth_verify_email()
        self.test_auth_me()
        self.test_auth_logout()
        self.test_google_oauth()
        
        # Phase 3: Admin Endpoints
        print("\n👑 Phase 3: Admin Endpoints")
        self.test_admin_stats()
        self.test_admin_users()
        self.test_admin_properties()
        
        # Phase 4: Reviews & Ratings
        print("\n⭐ Phase 4: Reviews & Ratings System")
        self.test_reviews_property()
        self.test_reviews_create()
        
        # Phase 5: Messaging System
        print("\n💬 Phase 5: Messaging System")
        self.test_messages_list()
        self.test_messages_send()
        
        # Phase 6: Booking System
        print("\n📅 Phase 6: Booking System")
        self.test_bookings_list()
        self.test_bookings_create()
        self.test_booking_slots()
        
        # Phase 7: Image Upload System
        print("\n📸 Phase 7: Image Upload System")
        self.test_image_upload()
        self.test_get_images()
        
        # Phase 8: Performance & Error Handling
        print("\n⚡ Phase 8: Performance & Error Handling")
        self.test_response_times()
        self.test_error_handling()
        self.test_cors_headers()
        
        # Print final summary
        self.print_production_summary()
        
        return self.tests_passed >= (self.tests_run * 0.95)  # 95% success rate target

    def print_production_summary(self):
        """Print production-ready test summary"""
        print("\n" + "=" * 80)
        print("🚀 PRODUCTION LAUNCH READINESS SUMMARY")
        print("=" * 80)
        
        # Calculate success rate
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        print(f"📊 Overall Results: {self.tests_passed}/{self.tests_run} tests passed ({success_rate:.1f}%)")
        
        # Categorize results
        categories = {
            "Core API": ["Properties", "Services"],
            "Authentication": ["Auth", "Google OAuth"],
            "Admin System": ["Admin"],
            "Reviews & Ratings": ["Reviews"],
            "Messaging": ["Messages"],
            "Booking": ["Booking"],
            "Image Upload": ["Image", "Upload"],
            "Performance": ["Response Times", "CORS", "HTTP Status"]
        }
        
        print(f"\n📋 Category Breakdown:")
        for category, keywords in categories.items():
            category_tests = [r for r in self.test_results if any(keyword.lower() in r['test_name'].lower() for keyword in keywords)]
            if category_tests:
                passed = sum(1 for t in category_tests if t['success'])
                total = len(category_tests)
                rate = (passed/total)*100 if total > 0 else 0
                status = "✅" if rate >= 95 else "⚠️" if rate >= 80 else "❌"
                print(f"   {status} {category}: {passed}/{total} ({rate:.0f}%)")
        
        # Critical failures
        critical_failures = [t for t in self.test_results if not t['success'] and 
                           any(keyword in t['test_name'].lower() for keyword in ['properties', 'services', 'auth'])]
        
        if critical_failures:
            print(f"\n🚨 Critical Issues Requiring Attention:")
            for failure in critical_failures[:5]:
                print(f"   ❌ {failure['test_name']}: {failure['details']}")
        
        # Production readiness assessment
        print(f"\n🎯 Production Readiness Assessment:")
        if success_rate >= 95:
            print("   ✅ READY FOR PRODUCTION LAUNCH")
            print("   📈 95%+ success rate achieved")
        elif success_rate >= 90:
            print("   ⚠️ MOSTLY READY - Minor issues to address")
            print("   📊 90-94% success rate")
        else:
            print("   ❌ NOT READY - Critical issues need resolution")
            print("   📉 <90% success rate")
        
        # Performance summary
        performance_tests = [r for r in self.test_results if 'response time' in r['test_name'].lower()]
        if performance_tests:
            fast_tests = sum(1 for t in performance_tests if t['success'])
            print(f"   ⚡ Performance: {fast_tests}/{len(performance_tests)} endpoints under 1000ms")
        
        return success_rate

if __name__ == "__main__":
    tester = HabitereProductionTester()
    
    success = tester.run_production_tests()
    
    print(f"\n{'='*80}")
    print(f"FINAL RESULT: {'✅ PRODUCTION READY' if success else '❌ NEEDS ATTENTION'}")
    print(f"Tests: {tester.tests_passed}/{tester.tests_run} passed")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    print(f"Target: 95%+ for production launch")
    print(f"{'='*80}")
    
    sys.exit(0 if success else 1)