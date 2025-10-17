#!/usr/bin/env python3

import requests
import sys
import json
import os
import io
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from PIL import Image
import uuid

class ComprehensiveBackendTester:
    def __init__(self, base_url="https://habitere.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Habitere-Comprehensive-Test/1.0'
        })
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Authentication tokens
        self.admin_token = None
        self.client_token = None
        self.owner_token = None
        self.provider_token = None
        
        # Test data IDs
        self.test_property_id = None
        self.test_service_id = None
        self.test_booking_id = None
        self.test_review_id = None
        self.test_message_id = None
        self.test_user_id = None

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

    def make_authenticated_request(self, method: str, endpoint: str, token: str = None, **kwargs):
        """Make an authenticated request"""
        if token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {token}'
            kwargs['headers'] = headers
        
        url = f"{self.api_url}{endpoint}"
        return getattr(requests, method.lower())(url, **kwargs)

    # ============================================================================
    # CORE MODULE TESTS (3 endpoints)
    # ============================================================================
    
    def test_core_root_endpoint(self):
        """Test GET /api/ - Root endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            self.log_test("Core - Root Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Core - Root Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_core_health_endpoint(self):
        """Test GET /api/health - Health check"""
        try:
            response = self.session.get(f"{self.api_url}/health")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Status: {data.get('status', 'unknown')}"
            self.log_test("Core - Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Core - Health Check", False, f"Exception: {str(e)}")
            return False

    def test_core_sample_data_init(self):
        """Test POST /api/init-sample-data - Initialize sample data"""
        try:
            response = self.session.post(f"{self.api_url}/init-sample-data")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            self.log_test("Core - Sample Data Init", success, details)
            return success
        except Exception as e:
            self.log_test("Core - Sample Data Init", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # AUTHENTICATION MODULE TESTS (11 endpoints)
    # ============================================================================
    
    def test_auth_register(self):
        """Test POST /api/auth/register - User registration"""
        try:
            test_email = f"test_{uuid.uuid4().hex[:8]}@habitere.com"
            register_data = {
                "email": test_email,
                "name": "Test User",
                "password": "testpass123"
            }
            
            response = self.session.post(f"{self.api_url}/auth/register", json=register_data)
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Email: {test_email}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            
            self.log_test("Auth - Register", success, details)
            return success
        except Exception as e:
            self.log_test("Auth - Register", False, f"Exception: {str(e)}")
            return False

    def test_auth_login(self):
        """Test POST /api/auth/login - User login"""
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
                # Extract session token
                for cookie in response.cookies:
                    if cookie.name == 'session_token':
                        self.admin_token = cookie.value
                        details += ", Session token obtained"
                        break
            elif response.status_code == 403:
                details += ", Email verification required (expected)"
            
            self.log_test("Auth - Login", success, details)
            return success
        except Exception as e:
            self.log_test("Auth - Login", False, f"Exception: {str(e)}")
            return False

    def test_auth_verify_email(self):
        """Test POST /api/auth/verify-email - Email verification"""
        try:
            verify_data = {
                "token": "invalid-test-token"
            }
            
            response = self.session.post(f"{self.api_url}/auth/verify-email", json=verify_data)
            # Should fail with invalid token (400)
            success = response.status_code == 400
            details = f"Status: {response.status_code} (expected 400 for invalid token)"
            
            self.log_test("Auth - Verify Email", success, details)
            return success
        except Exception as e:
            self.log_test("Auth - Verify Email", False, f"Exception: {str(e)}")
            return False

    def test_auth_resend_verification(self):
        """Test POST /api/auth/resend-verification - Resend verification email"""
        try:
            resend_data = {
                "email": "admin@habitere.com"
            }
            
            response = self.session.post(f"{self.api_url}/auth/resend-verification", json=resend_data)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            self.log_test("Auth - Resend Verification", success, details)
            return success
        except Exception as e:
            self.log_test("Auth - Resend Verification", False, f"Exception: {str(e)}")
            return False

    def test_auth_forgot_password(self):
        """Test POST /api/auth/forgot-password - Forgot password"""
        try:
            forgot_data = {
                "email": "admin@habitere.com"
            }
            
            response = self.session.post(f"{self.api_url}/auth/forgot-password", json=forgot_data)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            self.log_test("Auth - Forgot Password", success, details)
            return success
        except Exception as e:
            self.log_test("Auth - Forgot Password", False, f"Exception: {str(e)}")
            return False

    def test_auth_reset_password(self):
        """Test POST /api/auth/reset-password - Reset password"""
        try:
            reset_data = {
                "token": "invalid-test-token",
                "new_password": "newpassword123"
            }
            
            response = self.session.post(f"{self.api_url}/auth/reset-password", json=reset_data)
            # Should fail with invalid token (400)
            success = response.status_code == 400
            details = f"Status: {response.status_code} (expected 400 for invalid token)"
            
            self.log_test("Auth - Reset Password", success, details)
            return success
        except Exception as e:
            self.log_test("Auth - Reset Password", False, f"Exception: {str(e)}")
            return False

    def test_auth_select_role(self):
        """Test POST /api/auth/select-role - Select user role"""
        try:
            role_data = {
                "role": "property_seeker"
            }
            
            response = self.session.post(f"{self.api_url}/auth/select-role", json=role_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Auth - Select Role", success, details)
            return success
        except Exception as e:
            self.log_test("Auth - Select Role", False, f"Exception: {str(e)}")
            return False

    def test_auth_google_login(self):
        """Test GET /api/auth/google/login - Google OAuth login"""
        try:
            response = self.session.get(f"{self.api_url}/auth/google/login")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                auth_url = data.get('auth_url', '')
                if 'https://habitere.com/api/auth/google/callback' in auth_url:
                    details += ", Redirect URI: ✅"
                else:
                    details += ", Redirect URI: ❌"
            
            self.log_test("Auth - Google Login", success, details)
            return success
        except Exception as e:
            self.log_test("Auth - Google Login", False, f"Exception: {str(e)}")
            return False

    def test_auth_google_callback(self):
        """Test GET /api/auth/google/callback - Google OAuth callback"""
        try:
            # Test without required parameters (should fail)
            response = self.session.get(f"{self.api_url}/auth/google/callback")
            # Should fail with missing parameters (422 or 400)
            success = response.status_code in [400, 422]
            details = f"Status: {response.status_code} (expected 400/422 without params)"
            
            self.log_test("Auth - Google Callback", success, details)
            return success
        except Exception as e:
            self.log_test("Auth - Google Callback", False, f"Exception: {str(e)}")
            return False

    def test_auth_me(self):
        """Test GET /api/auth/me - Get current user"""
        try:
            response = self.session.get(f"{self.api_url}/auth/me")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Auth - Me", success, details)
            return success
        except Exception as e:
            self.log_test("Auth - Me", False, f"Exception: {str(e)}")
            return False

    def test_auth_logout(self):
        """Test POST /api/auth/logout - User logout"""
        try:
            response = self.session.post(f"{self.api_url}/auth/logout")
            # Should work even without authentication
            success = response.status_code in [200, 401]
            details = f"Status: {response.status_code}"
            
            self.log_test("Auth - Logout", success, details)
            return success
        except Exception as e:
            self.log_test("Auth - Logout", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # PROPERTIES MODULE TESTS (8 endpoints)
    # ============================================================================
    
    def test_properties_list(self):
        """Test GET /api/properties - List properties"""
        try:
            response = self.session.get(f"{self.api_url}/properties")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                details += f", Properties: {count}"
                
                # Store first property ID for other tests
                if data and len(data) > 0:
                    self.test_property_id = data[0].get('id')
            
            self.log_test("Properties - List", success, details)
            return success
        except Exception as e:
            self.log_test("Properties - List", False, f"Exception: {str(e)}")
            return False

    def test_properties_get_by_id(self):
        """Test GET /api/properties/{id} - Get property by ID"""
        try:
            if not self.test_property_id:
                # Get a property ID first
                props_response = self.session.get(f"{self.api_url}/properties?limit=1")
                if props_response.status_code == 200:
                    props = props_response.json()
                    if props and len(props) > 0:
                        self.test_property_id = props[0].get('id')
            
            if not self.test_property_id:
                self.log_test("Properties - Get by ID", False, "No property ID available")
                return False
            
            response = self.session.get(f"{self.api_url}/properties/{self.test_property_id}")
            success = response.status_code == 200
            details = f"Status: {response.status_code}, ID: {self.test_property_id}"
            
            if success:
                data = response.json()
                details += f", Title: {data.get('title', 'No title')[:30]}"
            
            self.log_test("Properties - Get by ID", success, details)
            return success
        except Exception as e:
            self.log_test("Properties - Get by ID", False, f"Exception: {str(e)}")
            return False

    def test_properties_create(self):
        """Test POST /api/properties - Create property"""
        try:
            property_data = {
                "title": "Test Property",
                "description": "A test property for API validation",
                "price": 150000,
                "location": "Douala, Cameroon",
                "listing_type": "sale",
                "bedrooms": 3,
                "bathrooms": 2,
                "area_sqm": 120.5
            }
            
            response = self.session.post(f"{self.api_url}/properties", json=property_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Properties - Create", success, details)
            return success
        except Exception as e:
            self.log_test("Properties - Create", False, f"Exception: {str(e)}")
            return False

    def test_properties_update(self):
        """Test PUT /api/properties/{id} - Update property"""
        try:
            test_id = self.test_property_id or "test-property-id"
            update_data = {
                "title": "Updated Test Property",
                "price": 160000
            }
            
            response = self.session.put(f"{self.api_url}/properties/{test_id}", json=update_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Properties - Update", success, details)
            return success
        except Exception as e:
            self.log_test("Properties - Update", False, f"Exception: {str(e)}")
            return False

    def test_properties_delete(self):
        """Test DELETE /api/properties/{id} - Delete property"""
        try:
            test_id = "test-property-id"
            
            response = self.session.delete(f"{self.api_url}/properties/{test_id}")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Properties - Delete", success, details)
            return success
        except Exception as e:
            self.log_test("Properties - Delete", False, f"Exception: {str(e)}")
            return False

    def test_properties_cleanup_old(self):
        """Test DELETE /api/properties/cleanup/old - Cleanup old properties"""
        try:
            response = self.session.delete(f"{self.api_url}/properties/cleanup/old")
            # Should work without authentication (cleanup utility)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Deleted: {data.get('deleted_count', 0)}"
            
            self.log_test("Properties - Cleanup Old", success, details)
            return success
        except Exception as e:
            self.log_test("Properties - Cleanup Old", False, f"Exception: {str(e)}")
            return False

    def test_properties_user_properties(self):
        """Test GET /api/users/me/properties - Get current user's properties"""
        try:
            response = self.session.get(f"{self.api_url}/users/me/properties")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Properties - User Properties", success, details)
            return success
        except Exception as e:
            self.log_test("Properties - User Properties", False, f"Exception: {str(e)}")
            return False

    def test_properties_user_by_id(self):
        """Test GET /api/users/{user_id}/properties - Get user's properties by ID"""
        try:
            test_user_id = "test-user-id"
            
            response = self.session.get(f"{self.api_url}/users/{test_user_id}/properties")
            # Should work without authentication (public endpoint)
            success = response.status_code in [200, 404]
            details = f"Status: {response.status_code} (expected 200 or 404)"
            
            self.log_test("Properties - User Properties by ID", success, details)
            return success
        except Exception as e:
            self.log_test("Properties - User Properties by ID", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # SERVICES MODULE TESTS (7 endpoints)
    # ============================================================================
    
    def test_services_list(self):
        """Test GET /api/services - List services"""
        try:
            response = self.session.get(f"{self.api_url}/services")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                details += f", Services: {count}"
                
                # Store first service ID for other tests
                if data and len(data) > 0:
                    self.test_service_id = data[0].get('id')
            
            self.log_test("Services - List", success, details)
            return success
        except Exception as e:
            self.log_test("Services - List", False, f"Exception: {str(e)}")
            return False

    def test_services_get_by_id(self):
        """Test GET /api/services/{id} - Get service by ID"""
        try:
            if not self.test_service_id:
                # Get a service ID first
                services_response = self.session.get(f"{self.api_url}/services?limit=1")
                if services_response.status_code == 200:
                    services = services_response.json()
                    if services and len(services) > 0:
                        self.test_service_id = services[0].get('id')
            
            if not self.test_service_id:
                self.log_test("Services - Get by ID", False, "No service ID available")
                return False
            
            response = self.session.get(f"{self.api_url}/services/{self.test_service_id}")
            success = response.status_code == 200
            details = f"Status: {response.status_code}, ID: {self.test_service_id}"
            
            if success:
                data = response.json()
                details += f", Title: {data.get('title', 'No title')[:30]}"
            
            self.log_test("Services - Get by ID", success, details)
            return success
        except Exception as e:
            self.log_test("Services - Get by ID", False, f"Exception: {str(e)}")
            return False

    def test_services_create(self):
        """Test POST /api/services - Create service"""
        try:
            service_data = {
                "category": "plumbing",
                "title": "Professional Plumbing Service",
                "description": "Expert plumbing services for residential and commercial properties",
                "price_range": "25000-50000 XAF",
                "location": "Yaoundé, Cameroon"
            }
            
            response = self.session.post(f"{self.api_url}/services", json=service_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Services - Create", success, details)
            return success
        except Exception as e:
            self.log_test("Services - Create", False, f"Exception: {str(e)}")
            return False

    def test_services_update(self):
        """Test PUT /api/services/{id} - Update service"""
        try:
            test_id = self.test_service_id or "test-service-id"
            update_data = {
                "title": "Updated Plumbing Service",
                "price_range": "30000-60000 XAF"
            }
            
            response = self.session.put(f"{self.api_url}/services/{test_id}", json=update_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Services - Update", success, details)
            return success
        except Exception as e:
            self.log_test("Services - Update", False, f"Exception: {str(e)}")
            return False

    def test_services_delete(self):
        """Test DELETE /api/services/{id} - Delete service"""
        try:
            test_id = "test-service-id"
            
            response = self.session.delete(f"{self.api_url}/services/{test_id}")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Services - Delete", success, details)
            return success
        except Exception as e:
            self.log_test("Services - Delete", False, f"Exception: {str(e)}")
            return False

    def test_services_user_services(self):
        """Test GET /api/users/me/services - Get current user's services"""
        try:
            response = self.session.get(f"{self.api_url}/users/me/services")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Services - User Services", success, details)
            return success
        except Exception as e:
            self.log_test("Services - User Services", False, f"Exception: {str(e)}")
            return False

    def test_services_user_by_id(self):
        """Test GET /api/users/{user_id}/services - Get user's services by ID"""
        try:
            test_user_id = "test-user-id"
            
            response = self.session.get(f"{self.api_url}/users/{test_user_id}/services")
            # Should work without authentication (public endpoint)
            success = response.status_code in [200, 404]
            details = f"Status: {response.status_code} (expected 200 or 404)"
            
            self.log_test("Services - User Services by ID", success, details)
            return success
        except Exception as e:
            self.log_test("Services - User Services by ID", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # USERS MODULE TESTS (3 endpoints)
    # ============================================================================
    
    def test_users_profile(self):
        """Test GET /api/users/me - Get current user profile"""
        try:
            response = self.session.get(f"{self.api_url}/users/me")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Users - Profile", success, details)
            return success
        except Exception as e:
            self.log_test("Users - Profile", False, f"Exception: {str(e)}")
            return False

    def test_users_update_profile(self):
        """Test PUT /api/users/me - Update current user profile"""
        try:
            update_data = {
                "name": "Updated Test User",
                "phone": "+237123456789",
                "location": "Douala, Cameroon"
            }
            
            response = self.session.put(f"{self.api_url}/users/me", json=update_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Users - Update Profile", success, details)
            return success
        except Exception as e:
            self.log_test("Users - Update Profile", False, f"Exception: {str(e)}")
            return False

    def test_users_get_by_id(self):
        """Test GET /api/users/{user_id} - Get user by ID"""
        try:
            test_user_id = "test-user-id"
            
            response = self.session.get(f"{self.api_url}/users/{test_user_id}")
            # Should work without authentication (public endpoint) but return 404 for non-existent user
            success = response.status_code in [200, 404]
            details = f"Status: {response.status_code} (expected 200 or 404)"
            
            self.log_test("Users - Get by ID", success, details)
            return success
        except Exception as e:
            self.log_test("Users - Get by ID", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # BOOKINGS MODULE TESTS (8 endpoints)
    # ============================================================================
    
    def test_bookings_create(self):
        """Test POST /api/bookings - Create booking"""
        try:
            booking_data = {
                "property_id": self.test_property_id or "test-property-id",
                "scheduled_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "notes": "Test booking for property viewing"
            }
            
            response = self.session.post(f"{self.api_url}/bookings", json=booking_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Bookings - Create", success, details)
            return success
        except Exception as e:
            self.log_test("Bookings - Create", False, f"Exception: {str(e)}")
            return False

    def test_bookings_list(self):
        """Test GET /api/bookings - List user bookings"""
        try:
            response = self.session.get(f"{self.api_url}/bookings")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Bookings - List", success, details)
            return success
        except Exception as e:
            self.log_test("Bookings - List", False, f"Exception: {str(e)}")
            return False

    def test_bookings_received(self):
        """Test GET /api/bookings/received - List received bookings"""
        try:
            response = self.session.get(f"{self.api_url}/bookings/received")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Bookings - Received", success, details)
            return success
        except Exception as e:
            self.log_test("Bookings - Received", False, f"Exception: {str(e)}")
            return False

    def test_bookings_confirm(self):
        """Test PUT /api/bookings/{id}/confirm - Confirm booking"""
        try:
            test_booking_id = "test-booking-id"
            
            response = self.session.put(f"{self.api_url}/bookings/{test_booking_id}/confirm")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Bookings - Confirm", success, details)
            return success
        except Exception as e:
            self.log_test("Bookings - Confirm", False, f"Exception: {str(e)}")
            return False

    def test_bookings_complete(self):
        """Test PUT /api/bookings/{id}/complete - Complete booking"""
        try:
            test_booking_id = "test-booking-id"
            
            response = self.session.put(f"{self.api_url}/bookings/{test_booking_id}/complete")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Bookings - Complete", success, details)
            return success
        except Exception as e:
            self.log_test("Bookings - Complete", False, f"Exception: {str(e)}")
            return False

    def test_bookings_cancel(self):
        """Test PUT /api/bookings/{id}/cancel - Cancel booking"""
        try:
            test_booking_id = "test-booking-id"
            cancel_data = {
                "reason": "Test cancellation"
            }
            
            response = self.session.put(f"{self.api_url}/bookings/{test_booking_id}/cancel", json=cancel_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Bookings - Cancel", success, details)
            return success
        except Exception as e:
            self.log_test("Bookings - Cancel", False, f"Exception: {str(e)}")
            return False

    def test_bookings_property_slots(self):
        """Test GET /api/bookings/property/{id}/slots - Get available time slots"""
        try:
            test_property_id = self.test_property_id or "test-property-id"
            date_param = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            response = self.session.get(f"{self.api_url}/bookings/property/{test_property_id}/slots?date={date_param}")
            # Should work without authentication (public endpoint)
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Date: {date_param}"
            
            if success:
                data = response.json()
                slots_count = len(data) if isinstance(data, list) else 0
                details += f", Available slots: {slots_count}"
            
            self.log_test("Bookings - Property Slots", success, details)
            return success
        except Exception as e:
            self.log_test("Bookings - Property Slots", False, f"Exception: {str(e)}")
            return False

    def test_bookings_service_slots(self):
        """Test GET /api/bookings/service/{id}/slots - Get service time slots"""
        try:
            test_service_id = self.test_service_id or "test-service-id"
            date_param = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            response = self.session.get(f"{self.api_url}/bookings/service/{test_service_id}/slots?date={date_param}")
            # Should work without authentication (public endpoint)
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Date: {date_param}"
            
            if success:
                data = response.json()
                slots_count = len(data) if isinstance(data, list) else 0
                details += f", Available slots: {slots_count}"
            
            self.log_test("Bookings - Service Slots", success, details)
            return success
        except Exception as e:
            self.log_test("Bookings - Service Slots", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # MESSAGES MODULE TESTS (6 endpoints)
    # ============================================================================
    
    def test_messages_send(self):
        """Test POST /api/messages - Send message"""
        try:
            message_data = {
                "receiver_id": "test-receiver-id",
                "content": "Test message for API validation"
            }
            
            response = self.session.post(f"{self.api_url}/messages", json=message_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Messages - Send", success, details)
            return success
        except Exception as e:
            self.log_test("Messages - Send", False, f"Exception: {str(e)}")
            return False

    def test_messages_conversations(self):
        """Test GET /api/messages/conversations - Get conversations"""
        try:
            response = self.session.get(f"{self.api_url}/messages/conversations")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Messages - Conversations", success, details)
            return success
        except Exception as e:
            self.log_test("Messages - Conversations", False, f"Exception: {str(e)}")
            return False

    def test_messages_thread(self):
        """Test GET /api/messages/thread/{user_id} - Get message thread"""
        try:
            test_user_id = "test-user-id"
            
            response = self.session.get(f"{self.api_url}/messages/thread/{test_user_id}")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Messages - Thread", success, details)
            return success
        except Exception as e:
            self.log_test("Messages - Thread", False, f"Exception: {str(e)}")
            return False

    def test_messages_unread_count(self):
        """Test GET /api/messages/unread-count - Get unread message count"""
        try:
            response = self.session.get(f"{self.api_url}/messages/unread-count")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Messages - Unread Count", success, details)
            return success
        except Exception as e:
            self.log_test("Messages - Unread Count", False, f"Exception: {str(e)}")
            return False

    def test_messages_mark_read(self):
        """Test PUT /api/messages/{id}/read - Mark message as read"""
        try:
            test_message_id = "test-message-id"
            
            response = self.session.put(f"{self.api_url}/messages/{test_message_id}/read")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Messages - Mark Read", success, details)
            return success
        except Exception as e:
            self.log_test("Messages - Mark Read", False, f"Exception: {str(e)}")
            return False

    def test_messages_delete(self):
        """Test DELETE /api/messages/{id} - Delete message"""
        try:
            test_message_id = "test-message-id"
            
            response = self.session.delete(f"{self.api_url}/messages/{test_message_id}")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Messages - Delete", success, details)
            return success
        except Exception as e:
            self.log_test("Messages - Delete", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # REVIEWS MODULE TESTS (6 endpoints)
    # ============================================================================
    
    def test_reviews_list(self):
        """Test GET /api/reviews - List reviews"""
        try:
            response = self.session.get(f"{self.api_url}/reviews")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                details += f", Reviews: {count}"
            
            self.log_test("Reviews - List", success, details)
            return success
        except Exception as e:
            self.log_test("Reviews - List", False, f"Exception: {str(e)}")
            return False

    def test_reviews_create(self):
        """Test POST /api/reviews - Create review"""
        try:
            review_data = {
                "property_id": self.test_property_id or "test-property-id",
                "rating": 5,
                "comment": "Excellent property with great amenities!"
            }
            
            response = self.session.post(f"{self.api_url}/reviews", json=review_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Reviews - Create", success, details)
            return success
        except Exception as e:
            self.log_test("Reviews - Create", False, f"Exception: {str(e)}")
            return False

    def test_reviews_property(self):
        """Test GET /api/reviews/property/{id} - Get property reviews"""
        try:
            test_property_id = self.test_property_id or "test-property-id"
            
            response = self.session.get(f"{self.api_url}/reviews/property/{test_property_id}")
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Property ID: {test_property_id}"
            
            if success:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                details += f", Reviews: {count}"
            
            self.log_test("Reviews - Property Reviews", success, details)
            return success
        except Exception as e:
            self.log_test("Reviews - Property Reviews", False, f"Exception: {str(e)}")
            return False

    def test_reviews_service(self):
        """Test GET /api/reviews/service/{id} - Get service reviews"""
        try:
            test_service_id = self.test_service_id or "test-service-id"
            
            response = self.session.get(f"{self.api_url}/reviews/service/{test_service_id}")
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Service ID: {test_service_id}"
            
            if success:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                details += f", Reviews: {count}"
            
            self.log_test("Reviews - Service Reviews", success, details)
            return success
        except Exception as e:
            self.log_test("Reviews - Service Reviews", False, f"Exception: {str(e)}")
            return False

    def test_reviews_user(self):
        """Test GET /api/reviews/user/{id} - Get user reviews"""
        try:
            test_user_id = "test-user-id"
            
            response = self.session.get(f"{self.api_url}/reviews/user/{test_user_id}")
            success = response.status_code == 200
            details = f"Status: {response.status_code}, User ID: {test_user_id}"
            
            if success:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                details += f", Reviews: {count}"
            
            self.log_test("Reviews - User Reviews", success, details)
            return success
        except Exception as e:
            self.log_test("Reviews - User Reviews", False, f"Exception: {str(e)}")
            return False

    def test_reviews_update(self):
        """Test PUT /api/reviews/{id} - Update review"""
        try:
            test_review_id = "test-review-id"
            update_data = {
                "rating": 4,
                "comment": "Updated review comment"
            }
            
            response = self.session.put(f"{self.api_url}/reviews/{test_review_id}", json=update_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Reviews - Update", success, details)
            return success
        except Exception as e:
            self.log_test("Reviews - Update", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # IMAGES MODULE TESTS (4 endpoints)
    # ============================================================================
    
    def test_images_upload(self):
        """Test POST /api/upload/images - Upload images"""
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
            
            # Remove Content-Type header for multipart form data
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{self.api_url}/upload/images",
                files=files,
                data=data,
                headers=headers
            )
            
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Images - Upload", success, details)
            return success
        except Exception as e:
            self.log_test("Images - Upload", False, f"Exception: {str(e)}")
            return False

    def test_images_get_entity_images(self):
        """Test GET /api/images/{entity_type}/{entity_id} - Get entity images"""
        try:
            response = self.session.get(f"{self.api_url}/images/property/test-property-id")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                details += f", Images: {count}"
            
            self.log_test("Images - Get Entity Images", success, details)
            return success
        except Exception as e:
            self.log_test("Images - Get Entity Images", False, f"Exception: {str(e)}")
            return False

    def test_images_update(self):
        """Test PUT /api/images/{id} - Update image"""
        try:
            test_image_id = "test-image-id"
            update_data = {
                "alt_text": "Updated alt text",
                "is_primary": True
            }
            
            response = self.session.put(f"{self.api_url}/images/{test_image_id}", json=update_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Images - Update", success, details)
            return success
        except Exception as e:
            self.log_test("Images - Update", False, f"Exception: {str(e)}")
            return False

    def test_images_delete(self):
        """Test DELETE /api/images/{id} - Delete image"""
        try:
            test_image_id = "test-image-id"
            
            response = self.session.delete(f"{self.api_url}/images/{test_image_id}")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Images - Delete", success, details)
            return success
        except Exception as e:
            self.log_test("Images - Delete", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # PAYMENTS MODULE TESTS (4 endpoints)
    # ============================================================================
    
    def test_payments_mtn_momo(self):
        """Test POST /api/payments/mtn-momo - MTN MoMo payment"""
        try:
            payment_data = {
                "amount": "1000",
                "currency": "EUR",
                "external_id": "test-payment-123",
                "payer_message": "Test payment",
                "payee_note": "Test transaction",
                "phone": "237123456789"
            }
            
            response = self.session.post(f"{self.api_url}/payments/mtn-momo", json=payment_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Payments - MTN MoMo", success, details)
            return success
        except Exception as e:
            self.log_test("Payments - MTN MoMo", False, f"Exception: {str(e)}")
            return False

    def test_payments_mtn_momo_status(self):
        """Test GET /api/payments/mtn-momo/status/{reference_id} - MTN MoMo status"""
        try:
            reference_id = "test-reference-123"
            
            response = self.session.get(f"{self.api_url}/payments/mtn-momo/status/{reference_id}")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Payments - MTN MoMo Status", success, details)
            return success
        except Exception as e:
            self.log_test("Payments - MTN MoMo Status", False, f"Exception: {str(e)}")
            return False

    def test_payments_mtn_momo_callback(self):
        """Test POST /api/payments/mtn-momo/callback - MTN MoMo callback"""
        try:
            callback_data = {
                "referenceId": "test-reference-123",
                "status": "SUCCESSFUL",
                "financialTransactionId": "test-transaction-456"
            }
            
            response = self.session.post(f"{self.api_url}/payments/mtn-momo/callback", json=callback_data)
            # Callback endpoint might accept requests without auth for webhook purposes
            success = response.status_code in [200, 400, 404]
            details = f"Status: {response.status_code}"
            
            self.log_test("Payments - MTN MoMo Callback", success, details)
            return success
        except Exception as e:
            self.log_test("Payments - MTN MoMo Callback", False, f"Exception: {str(e)}")
            return False

    def test_payments_status(self):
        """Test GET /api/payments/{payment_id}/status - Payment status"""
        try:
            payment_id = "test-payment-id"
            
            response = self.session.get(f"{self.api_url}/payments/{payment_id}/status")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Payments - Status", success, details)
            return success
        except Exception as e:
            self.log_test("Payments - Status", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # ADMIN MODULE TESTS (12 endpoints)
    # ============================================================================
    
    def test_admin_stats(self):
        """Test GET /api/admin/stats - Admin dashboard stats"""
        try:
            response = self.session.get(f"{self.api_url}/admin/stats")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - Stats", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - Stats", False, f"Exception: {str(e)}")
            return False

    def test_admin_users(self):
        """Test GET /api/admin/users - Admin users list"""
        try:
            response = self.session.get(f"{self.api_url}/admin/users")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - Users", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - Users", False, f"Exception: {str(e)}")
            return False

    def test_admin_user_approve(self):
        """Test PUT /api/admin/users/{id}/approve - Approve user"""
        try:
            test_user_id = "test-user-id"
            
            response = self.session.put(f"{self.api_url}/admin/users/{test_user_id}/approve")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - User Approve", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - User Approve", False, f"Exception: {str(e)}")
            return False

    def test_admin_user_reject(self):
        """Test PUT /api/admin/users/{id}/reject - Reject user"""
        try:
            test_user_id = "test-user-id"
            reject_data = {"reason": "Test rejection"}
            
            response = self.session.put(f"{self.api_url}/admin/users/{test_user_id}/reject", json=reject_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - User Reject", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - User Reject", False, f"Exception: {str(e)}")
            return False

    def test_admin_properties(self):
        """Test GET /api/admin/properties - Admin properties list"""
        try:
            response = self.session.get(f"{self.api_url}/admin/properties")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - Properties", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - Properties", False, f"Exception: {str(e)}")
            return False

    def test_admin_property_verify(self):
        """Test PUT /api/admin/properties/{id}/verify - Verify property"""
        try:
            test_property_id = "test-property-id"
            
            response = self.session.put(f"{self.api_url}/admin/properties/{test_property_id}/verify")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - Property Verify", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - Property Verify", False, f"Exception: {str(e)}")
            return False

    def test_admin_property_reject(self):
        """Test PUT /api/admin/properties/{id}/reject - Reject property"""
        try:
            test_property_id = "test-property-id"
            reject_data = {"reason": "Test rejection"}
            
            response = self.session.put(f"{self.api_url}/admin/properties/{test_property_id}/reject", json=reject_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - Property Reject", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - Property Reject", False, f"Exception: {str(e)}")
            return False

    def test_admin_services(self):
        """Test GET /api/admin/services - Admin services list"""
        try:
            response = self.session.get(f"{self.api_url}/admin/services")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - Services", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - Services", False, f"Exception: {str(e)}")
            return False

    def test_admin_service_verify(self):
        """Test PUT /api/admin/services/{id}/verify - Verify service"""
        try:
            test_service_id = "test-service-id"
            
            response = self.session.put(f"{self.api_url}/admin/services/{test_service_id}/verify")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - Service Verify", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - Service Verify", False, f"Exception: {str(e)}")
            return False

    def test_admin_service_reject(self):
        """Test PUT /api/admin/services/{id}/reject - Reject service"""
        try:
            test_service_id = "test-service-id"
            reject_data = {"reason": "Test rejection"}
            
            response = self.session.put(f"{self.api_url}/admin/services/{test_service_id}/reject", json=reject_data)
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - Service Reject", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - Service Reject", False, f"Exception: {str(e)}")
            return False

    def test_admin_analytics_users(self):
        """Test GET /api/admin/analytics/users - User analytics"""
        try:
            response = self.session.get(f"{self.api_url}/admin/analytics/users")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - Analytics Users", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - Analytics Users", False, f"Exception: {str(e)}")
            return False

    def test_admin_analytics_properties(self):
        """Test GET /api/admin/analytics/properties - Property analytics"""
        try:
            response = self.session.get(f"{self.api_url}/admin/analytics/properties")
            # Should fail without authentication (401)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Admin - Analytics Properties", success, details)
            return success
        except Exception as e:
            self.log_test("Admin - Analytics Properties", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # MAIN TEST RUNNER
    # ============================================================================
    
    def run_comprehensive_tests(self):
        """Run comprehensive backend API tests for all 72 endpoints"""
        print("🚀 COMPREHENSIVE BACKEND API TESTING - POST-REFACTORING VALIDATION")
        print("=" * 80)
        print(f"Testing API at: {self.api_url}")
        print("Objective: Verify all 72 refactored API routes work correctly")
        print("-" * 80)
        
        # Core Module (3 endpoints)
        print("\n📍 CORE MODULE (3 endpoints)")
        print("-" * 40)
        self.test_core_root_endpoint()
        self.test_core_health_endpoint()
        self.test_core_sample_data_init()
        
        # Authentication Module (11 endpoints)
        print("\n🔐 AUTHENTICATION MODULE (11 endpoints)")
        print("-" * 40)
        self.test_auth_register()
        self.test_auth_login()
        self.test_auth_verify_email()
        self.test_auth_resend_verification()
        self.test_auth_forgot_password()
        self.test_auth_reset_password()
        self.test_auth_select_role()
        self.test_auth_google_login()
        self.test_auth_google_callback()
        self.test_auth_me()
        self.test_auth_logout()
        
        # Properties Module (8 endpoints)
        print("\n🏠 PROPERTIES MODULE (8 endpoints)")
        print("-" * 40)
        self.test_properties_list()
        self.test_properties_get_by_id()
        self.test_properties_create()
        self.test_properties_update()
        self.test_properties_delete()
        self.test_properties_cleanup_old()
        self.test_properties_user_properties()
        self.test_properties_user_by_id()
        
        # Services Module (7 endpoints)
        print("\n🔧 SERVICES MODULE (7 endpoints)")
        print("-" * 40)
        self.test_services_list()
        self.test_services_get_by_id()
        self.test_services_create()
        self.test_services_update()
        self.test_services_delete()
        self.test_services_user_services()
        self.test_services_user_by_id()
        
        # Users Module (3 endpoints)
        print("\n👤 USERS MODULE (3 endpoints)")
        print("-" * 40)
        self.test_users_profile()
        self.test_users_update_profile()
        self.test_users_get_by_id()
        
        # Bookings Module (8 endpoints)
        print("\n📅 BOOKINGS MODULE (8 endpoints)")
        print("-" * 40)
        self.test_bookings_create()
        self.test_bookings_list()
        self.test_bookings_received()
        self.test_bookings_confirm()
        self.test_bookings_complete()
        self.test_bookings_cancel()
        self.test_bookings_property_slots()
        self.test_bookings_service_slots()
        
        # Messages Module (6 endpoints)
        print("\n💬 MESSAGES MODULE (6 endpoints)")
        print("-" * 40)
        self.test_messages_send()
        self.test_messages_conversations()
        self.test_messages_thread()
        self.test_messages_unread_count()
        self.test_messages_mark_read()
        self.test_messages_delete()
        
        # Reviews Module (6 endpoints)
        print("\n⭐ REVIEWS MODULE (6 endpoints)")
        print("-" * 40)
        self.test_reviews_list()
        self.test_reviews_create()
        self.test_reviews_property()
        self.test_reviews_service()
        self.test_reviews_user()
        self.test_reviews_update()
        
        # Images Module (4 endpoints)
        print("\n🖼️ IMAGES MODULE (4 endpoints)")
        print("-" * 40)
        self.test_images_upload()
        self.test_images_get_entity_images()
        self.test_images_update()
        self.test_images_delete()
        
        # Payments Module (4 endpoints)
        print("\n💳 PAYMENTS MODULE (4 endpoints)")
        print("-" * 40)
        self.test_payments_mtn_momo()
        self.test_payments_mtn_momo_status()
        self.test_payments_mtn_momo_callback()
        self.test_payments_status()
        
        # Admin Module (12 endpoints)
        print("\n👑 ADMIN MODULE (12 endpoints)")
        print("-" * 40)
        self.test_admin_stats()
        self.test_admin_users()
        self.test_admin_user_approve()
        self.test_admin_user_reject()
        self.test_admin_properties()
        self.test_admin_property_verify()
        self.test_admin_property_reject()
        self.test_admin_services()
        self.test_admin_service_verify()
        self.test_admin_service_reject()
        self.test_admin_analytics_users()
        self.test_admin_analytics_properties()
        
        # Print final summary
        self.print_final_summary()
        
        return self.tests_passed == self.tests_run

    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        print(f"📊 Overall Results: {self.tests_passed}/{self.tests_run} tests passed ({success_rate:.1f}%)")
        
        # Group results by module
        modules = {
            "Core": [r for r in self.test_results if r['test_name'].startswith('Core')],
            "Authentication": [r for r in self.test_results if r['test_name'].startswith('Auth')],
            "Properties": [r for r in self.test_results if r['test_name'].startswith('Properties')],
            "Services": [r for r in self.test_results if r['test_name'].startswith('Services')],
            "Users": [r for r in self.test_results if r['test_name'].startswith('Users')],
            "Bookings": [r for r in self.test_results if r['test_name'].startswith('Bookings')],
            "Messages": [r for r in self.test_results if r['test_name'].startswith('Messages')],
            "Reviews": [r for r in self.test_results if r['test_name'].startswith('Reviews')],
            "Images": [r for r in self.test_results if r['test_name'].startswith('Images')],
            "Payments": [r for r in self.test_results if r['test_name'].startswith('Payments')],
            "Admin": [r for r in self.test_results if r['test_name'].startswith('Admin')]
        }
        
        print(f"\n📋 Module-wise Results:")
        for module_name, tests in modules.items():
            if tests:
                passed = sum(1 for t in tests if t['success'])
                total = len(tests)
                rate = (passed / total) * 100 if total > 0 else 0
                status = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"
                print(f"   {status} {module_name}: {passed}/{total} ({rate:.1f}%)")
        
        # Failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
        
        # Critical findings
        print(f"\n🔍 Critical Findings:")
        
        # Check if core endpoints work
        core_tests = [r for r in self.test_results if r['test_name'].startswith('Core')]
        core_passed = sum(1 for t in core_tests if t['success'])
        if core_passed == len(core_tests):
            print("   ✅ Core API endpoints functional")
        else:
            print("   ❌ Core API endpoints have issues")
        
        # Check authentication protection
        auth_protected_tests = [r for r in self.test_results if "expected 401 without auth" in r['details']]
        auth_protected_passed = sum(1 for t in auth_protected_tests if t['success'])
        if auth_protected_passed > 0:
            print(f"   ✅ Authentication protection working ({auth_protected_passed} endpoints properly secured)")
        
        # Check public endpoints
        public_tests = [r for r in self.test_results if r['test_name'] in [
            'Properties - List', 'Services - List', 'Reviews - List', 
            'Properties - Get by ID', 'Services - Get by ID'
        ]]
        public_passed = sum(1 for t in public_tests if t['success'])
        if public_passed > 0:
            print(f"   ✅ Public endpoints accessible ({public_passed} endpoints working)")
        
        print(f"\n🎉 REFACTORING VALIDATION: {'SUCCESS' if success_rate >= 95 else 'NEEDS ATTENTION'}")
        print(f"   All 72 API endpoints have been tested across 12 route modules")
        print(f"   Modular architecture is {'✅ WORKING' if success_rate >= 95 else '⚠️ PARTIALLY WORKING'}")
        
        return success_rate


def main():
    """Main function to run comprehensive backend tests"""
    print("Starting Comprehensive Backend API Testing...")
    
    # Use the correct backend URL
    backend_url = "https://habitere.com"
    
    tester = ComprehensiveBackendTester(backend_url)
    
    try:
        success = tester.run_comprehensive_tests()
        
        if success:
            print(f"\n🎉 All tests passed! Backend refactoring validation successful.")
            sys.exit(0)
        else:
            print(f"\n⚠️ Some tests failed. Check the summary above for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()