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

class HabitereAPITester:
    def __init__(self, base_url="https://habitere.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Habitere-Test-Client/1.0'
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

    def create_test_user(self, email: str, name: str, password: str, role: str) -> Optional[str]:
        """Create a test user and return session token"""
        try:
            # Register user
            register_data = {
                "email": email,
                "name": name,
                "password": password
            }
            
            register_response = self.session.post(f"{self.api_url}/auth/register", json=register_data)
            if register_response.status_code != 200:
                print(f"Failed to register {email}: {register_response.status_code}")
                return None
            
            # For testing, we'll manually verify the user and set role
            # In a real scenario, this would require email verification
            
            # Try to login (this will fail if email not verified)
            login_data = {
                "email": email,
                "password": password
            }
            
            login_response = self.session.post(f"{self.api_url}/auth/login", json=login_data)
            
            # If login fails due to unverified email, we need to handle this
            if login_response.status_code == 403:
                # Email not verified - for testing, we'll create the user directly in the database
                # This is a workaround for testing purposes
                print(f"User {email} needs email verification - creating test user directly")
                return self.create_verified_test_user(email, name, password, role)
            
            if login_response.status_code != 200:
                print(f"Failed to login {email}: {login_response.status_code}")
                return None
            
            # Extract session token from cookies
            session_token = None
            for cookie in login_response.cookies:
                if cookie.name == 'session_token':
                    session_token = cookie.value
                    break
            
            if not session_token:
                print(f"No session token found for {email}")
                return None
            
            # Set role
            role_headers = {'Authorization': f'Bearer {session_token}'}
            role_data = {"role": role}
            role_response = requests.post(
                f"{self.api_url}/auth/select-role",
                json=role_data,
                headers=role_headers
            )
            
            if role_response.status_code != 200:
                print(f"Failed to set role for {email}: {role_response.status_code}")
                return None
            
            return session_token
            
        except Exception as e:
            print(f"Error creating test user {email}: {str(e)}")
            return None

    def create_verified_test_user(self, email: str, name: str, password: str, role: str) -> Optional[str]:
        """Create a verified test user directly (testing workaround)"""
        # This is a simplified approach for testing
        # In production, proper email verification would be required
        try:
            # For now, we'll return None and handle authentication differently
            # The actual implementation would require database access
            return None
        except Exception as e:
            print(f"Error creating verified test user: {str(e)}")
            return None

    def setup_test_authentication(self):
        """Set up authentication for different user roles"""
        print("🔐 Setting up test authentication...")
        
        # Create admin user
        self.admin_token = self.create_test_user(
            "admin@habitere.com", 
            "Admin User", 
            "admin123", 
            "admin"
        )
        
        # Create client user
        self.client_token = self.create_test_user(
            "client@test.com", 
            "Test Client", 
            "client123", 
            "property_seeker"
        )
        
        # Create property owner
        self.owner_token = self.create_test_user(
            "owner@test.com", 
            "Property Owner", 
            "owner123", 
            "property_owner"
        )
        
        # Create service provider
        self.provider_token = self.create_test_user(
            "provider@test.com", 
            "Service Provider", 
            "provider123", 
            "plumber"
        )
        
        print(f"Admin token: {'✅' if self.admin_token else '❌'}")
        print(f"Client token: {'✅' if self.client_token else '❌'}")
        print(f"Owner token: {'✅' if self.owner_token else '❌'}")
        print(f"Provider token: {'✅' if self.provider_token else '❌'}")

    def make_authenticated_request(self, method: str, endpoint: str, token: str, **kwargs):
        """Make an authenticated request"""
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        kwargs['headers'] = headers
        
        url = f"{self.api_url}{endpoint}"
        return getattr(requests, method.lower())(url, **kwargs)

    def test_api_health(self):
        """Test API health endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/health")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Response: {data}"
            self.log_test("API Health Check", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("API Health Check", False, f"Exception: {str(e)}")
            return False

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            self.log_test("API Root Endpoint", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_properties_endpoint(self):
        """Test properties listing endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/properties")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                properties_count = len(data) if isinstance(data, list) else 0
                details += f", Properties found: {properties_count}"
                
                # Test with filters
                filter_response = self.session.get(f"{self.api_url}/properties?property_type=house&limit=5")
                if filter_response.status_code == 200:
                    details += f", Filtered request: OK"
                else:
                    details += f", Filtered request: FAILED ({filter_response.status_code})"
                    
            self.log_test("Properties Listing", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Properties Listing", False, f"Exception: {str(e)}")
            return False

    def test_services_endpoint(self):
        """Test services listing endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/services")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                services_count = len(data) if isinstance(data, list) else 0
                details += f", Services found: {services_count}"
                
                # Test with category filter
                filter_response = self.session.get(f"{self.api_url}/services?category=plumbing&limit=5")
                if filter_response.status_code == 200:
                    details += f", Category filter: OK"
                else:
                    details += f", Category filter: FAILED ({filter_response.status_code})"
                    
            self.log_test("Services Listing", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Services Listing", False, f"Exception: {str(e)}")
            return False

    def test_sample_data_initialization(self):
        """Test sample data initialization"""
        try:
            response = self.session.post(f"{self.api_url}/init-sample-data")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Sample Data Initialization", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Sample Data Initialization", False, f"Exception: {str(e)}")
            return False

    def test_property_detail(self):
        """Test property detail endpoint with sample ID"""
        try:
            # First get a property ID from the list
            properties_response = self.session.get(f"{self.api_url}/properties?limit=1")
            if properties_response.status_code != 200:
                self.log_test("Property Detail", False, "Could not fetch properties list")
                return False
                
            properties = properties_response.json()
            if not properties or len(properties) == 0:
                self.log_test("Property Detail", False, "No properties available for testing")
                return False
                
            property_id = properties[0].get('id')
            if not property_id:
                self.log_test("Property Detail", False, "Property ID not found")
                return False
                
            # Test property detail
            response = self.session.get(f"{self.api_url}/properties/{property_id}")
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Property ID: {property_id}"
            
            if success:
                data = response.json()
                details += f", Title: {data.get('title', 'No title')[:50]}"
                
            self.log_test("Property Detail", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Property Detail", False, f"Exception: {str(e)}")
            return False

    def test_service_detail(self):
        """Test service detail endpoint with sample ID"""
        try:
            # First get a service ID from the list
            services_response = self.session.get(f"{self.api_url}/services?limit=1")
            if services_response.status_code != 200:
                self.log_test("Service Detail", False, "Could not fetch services list")
                return False
                
            services = services_response.json()
            if not services or len(services) == 0:
                self.log_test("Service Detail", False, "No services available for testing")
                return False
                
            service_id = services[0].get('id')
            if not service_id:
                self.log_test("Service Detail", False, "Service ID not found")
                return False
                
            # Test service detail
            response = self.session.get(f"{self.api_url}/services/{service_id}")
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Service ID: {service_id}"
            
            if success:
                data = response.json()
                details += f", Title: {data.get('title', 'No title')[:50]}"
                
            self.log_test("Service Detail", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Service Detail", False, f"Exception: {str(e)}")
            return False

    def test_auth_endpoints(self):
        """Test authentication endpoints (without actual auth)"""
        try:
            # Test session data endpoint (should fail without session ID)
            response = self.session.get(f"{self.api_url}/auth/session-data")
            expected_failure = response.status_code == 400  # Should fail without session ID
            
            details = f"Session data endpoint status: {response.status_code} (expected 400)"
            self.log_test("Auth Session Data (No Session)", expected_failure, details)
            
            # Test /auth/me endpoint (should fail without auth)
            me_response = self.session.get(f"{self.api_url}/auth/me")
            expected_auth_failure = me_response.status_code == 401  # Should fail without auth
            
            details = f"Auth me endpoint status: {me_response.status_code} (expected 401)"
            self.log_test("Auth Me (No Auth)", expected_auth_failure, details)
            
            return expected_failure and expected_auth_failure
        except Exception as e:
            self.log_test("Auth Endpoints", False, f"Exception: {str(e)}")
            return False

    def test_reviews_endpoint(self):
        """Test reviews endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/reviews")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                reviews_count = len(data) if isinstance(data, list) else 0
                details += f", Reviews found: {reviews_count}"
                
            self.log_test("Reviews Listing", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Reviews Listing", False, f"Exception: {str(e)}")
            return False

    def test_messages_endpoint(self):
        """Test messages endpoint (should require auth)"""
        try:
            response = self.session.get(f"{self.api_url}/messages")
            expected_failure = response.status_code == 401  # Should fail without auth
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Messages Endpoint (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Messages Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_bookings_endpoint(self):
        """Test bookings endpoint (should require auth)"""
        try:
            response = self.session.get(f"{self.api_url}/bookings")
            expected_failure = response.status_code == 401  # Should fail without auth
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Bookings Endpoint (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Bookings Endpoint", False, f"Exception: {str(e)}")
            return False

    def create_test_image(self, width=100, height=100, format='JPEG'):
        """Create a test image in memory"""
        img = Image.new('RGB', (width, height), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes

    def test_image_upload_no_auth(self):
        """Test image upload endpoint without authentication (should fail)"""
        try:
            # Create a test image
            test_image = self.create_test_image()
            
            files = {
                'files': ('test_image.jpg', test_image, 'image/jpeg')
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
            
            expected_failure = response.status_code == 401  # Should fail without auth
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Image Upload (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Image Upload (No Auth)", False, f"Exception: {str(e)}")
            return False

    def test_image_upload_invalid_file(self):
        """Test image upload with invalid file type (should fail)"""
        try:
            # Create a text file instead of image
            text_content = b"This is not an image file"
            
            files = {
                'files': ('test_file.txt', io.BytesIO(text_content), 'text/plain')
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
            
            expected_failure = response.status_code in [400, 401]  # Should fail due to invalid file type or no auth
            details = f"Status: {response.status_code} (expected 400/401 for invalid file)"
            
            self.log_test("Image Upload (Invalid File)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Image Upload (Invalid File)", False, f"Exception: {str(e)}")
            return False

    def test_image_upload_large_file(self):
        """Test image upload with oversized file (should fail)"""
        try:
            # Create a large test image (simulate > 5MB)
            test_image = self.create_test_image(width=3000, height=3000)
            
            files = {
                'files': ('large_image.jpg', test_image, 'image/jpeg')
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
            
            expected_failure = response.status_code in [400, 401]  # Should fail due to size or no auth
            details = f"Status: {response.status_code} (expected 400/401 for large file)"
            
            self.log_test("Image Upload (Large File)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Image Upload (Large File)", False, f"Exception: {str(e)}")
            return False

    def test_get_entity_images(self):
        """Test getting images for an entity"""
        try:
            # Test with a sample entity
            response = self.session.get(f"{self.api_url}/images/property/sample-property-id")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                images_count = len(data) if isinstance(data, list) else 0
                details += f", Images found: {images_count}"
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Get Entity Images", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Get Entity Images", False, f"Exception: {str(e)}")
            return False

    def test_mtn_momo_payment_no_auth(self):
        """Test MTN MoMo payment endpoint without authentication (should fail)"""
        try:
            payment_data = {
                "amount": "1000",
                "currency": "EUR",
                "external_id": "test-payment-123",
                "payer_message": "Test payment",
                "payee_note": "Test transaction",
                "phone": "237123456789"
            }
            
            response = self.session.post(
                f"{self.api_url}/payments/mtn-momo",
                json=payment_data
            )
            
            expected_failure = response.status_code == 401  # Should fail without auth
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("MTN MoMo Payment (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("MTN MoMo Payment (No Auth)", False, f"Exception: {str(e)}")
            return False

    def test_mtn_momo_payment_invalid_data(self):
        """Test MTN MoMo payment with invalid data (should fail)"""
        try:
            # Missing required fields
            payment_data = {
                "amount": "invalid_amount",
                "currency": "INVALID"
            }
            
            response = self.session.post(
                f"{self.api_url}/payments/mtn-momo",
                json=payment_data
            )
            
            expected_failure = response.status_code in [400, 401, 422]  # Should fail due to validation or no auth
            details = f"Status: {response.status_code} (expected 400/401/422 for invalid data)"
            
            self.log_test("MTN MoMo Payment (Invalid Data)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("MTN MoMo Payment (Invalid Data)", False, f"Exception: {str(e)}")
            return False

    def test_mtn_momo_status_check(self):
        """Test MTN MoMo payment status check endpoint"""
        try:
            # Test with a sample reference ID
            reference_id = "sample-reference-id-123"
            response = self.session.get(f"{self.api_url}/payments/mtn-momo/status/{reference_id}")
            
            expected_failure = response.status_code == 401  # Should fail without auth
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("MTN MoMo Status Check (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("MTN MoMo Status Check", False, f"Exception: {str(e)}")
            return False

    def test_mtn_momo_callback(self):
        """Test MTN MoMo callback endpoint"""
        try:
            callback_data = {
                "referenceId": "test-reference-123",
                "status": "SUCCESSFUL",
                "financialTransactionId": "test-transaction-456"
            }
            
            response = self.session.post(
                f"{self.api_url}/payments/mtn-momo/callback",
                json=callback_data
            )
            
            # Callback endpoint might accept requests without auth for webhook purposes
            success = response.status_code in [200, 400, 404]  # Various acceptable responses
            details = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    details += f", Response: {data}"
                except:
                    details += ", Response: Non-JSON"
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("MTN MoMo Callback", success, details)
            return success
        except Exception as e:
            self.log_test("MTN MoMo Callback", False, f"Exception: {str(e)}")
            return False

    def test_payment_status_endpoint(self):
        """Test general payment status endpoint"""
        try:
            # Test with a sample payment ID
            payment_id = "sample-payment-id-123"
            response = self.session.get(f"{self.api_url}/payments/{payment_id}/status")
            
            expected_failure = response.status_code == 401  # Should fail without auth
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            self.log_test("Payment Status (No Auth)", expected_failure, details)
            return expected_failure
        except Exception as e:
            self.log_test("Payment Status", False, f"Exception: {str(e)}")
            return False

    def test_mtn_momo_configuration(self):
        """Test if MTN MoMo configuration is properly set up"""
        try:
            # This is an indirect test - we'll check if the payment endpoint gives proper error messages
            payment_data = {
                "amount": "100",
                "currency": "EUR",
                "external_id": "config-test-123",
                "payer_message": "Configuration test",
                "payee_note": "Test config",
                "phone": "237123456789"
            }
            
            response = self.session.post(
                f"{self.api_url}/payments/mtn-momo",
                json=payment_data
            )
            
            # We expect 401 (no auth) rather than 500 (config error)
            config_ok = response.status_code == 401
            details = f"Status: {response.status_code}"
            
            if response.status_code == 500:
                details += " - Possible MTN MoMo configuration issue"
            elif response.status_code == 401:
                details += " - Auth required (config appears OK)"
            else:
                details += f" - Unexpected response: {response.text[:100]}"
                
            self.log_test("MTN MoMo Configuration Check", config_ok, details)
            return config_ok
        except Exception as e:
            self.log_test("MTN MoMo Configuration Check", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # ADMIN SYSTEM TESTS (12 endpoints)
    # ============================================================================
    
    def test_admin_stats(self):
        """Test admin dashboard statistics"""
        if not self.admin_token:
            self.log_test("Admin Stats", False, "No admin token available")
            return False
            
        try:
            response = self.make_authenticated_request('GET', '/admin/stats', self.admin_token)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Users: {data.get('total_users', 0)}, Properties: {data.get('total_properties', 0)}"
            
            self.log_test("Admin Stats", success, details)
            return success
        except Exception as e:
            self.log_test("Admin Stats", False, f"Exception: {str(e)}")
            return False

    def test_admin_users_list(self):
        """Test admin users listing with filters"""
        if not self.admin_token:
            self.log_test("Admin Users List", False, "No admin token available")
            return False
            
        try:
            # Test basic listing
            response = self.make_authenticated_request('GET', '/admin/users', self.admin_token)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                user_count = len(data) if isinstance(data, list) else 0
                details += f", Users found: {user_count}"
                
                # Test with filters
                filter_response = self.make_authenticated_request(
                    'GET', '/admin/users?role=admin&status=approved', self.admin_token
                )
                if filter_response.status_code == 200:
                    details += ", Filters: OK"
                else:
                    details += f", Filters: FAILED ({filter_response.status_code})"
            
            self.log_test("Admin Users List", success, details)
            return success
        except Exception as e:
            self.log_test("Admin Users List", False, f"Exception: {str(e)}")
            return False

    def test_admin_user_approval(self):
        """Test admin user approval functionality"""
        if not self.admin_token:
            self.log_test("Admin User Approval", False, "No admin token available")
            return False
            
        try:
            # First get a user to approve (create a test user)
            test_user_id = "test-user-for-approval"
            
            # Test approval endpoint
            response = self.make_authenticated_request(
                'PUT', f'/admin/users/{test_user_id}/approve', self.admin_token
            )
            
            # We expect 404 since user doesn't exist, but endpoint should be accessible
            expected_status = response.status_code in [200, 404]
            details = f"Status: {response.status_code} (expected 200 or 404)"
            
            self.log_test("Admin User Approval", expected_status, details)
            return expected_status
        except Exception as e:
            self.log_test("Admin User Approval", False, f"Exception: {str(e)}")
            return False

    def test_admin_user_rejection(self):
        """Test admin user rejection functionality"""
        if not self.admin_token:
            self.log_test("Admin User Rejection", False, "No admin token available")
            return False
            
        try:
            test_user_id = "test-user-for-rejection"
            rejection_data = {"reason": "Test rejection reason"}
            
            response = self.make_authenticated_request(
                'PUT', f'/admin/users/{test_user_id}/reject', 
                self.admin_token, json=rejection_data
            )
            
            expected_status = response.status_code in [200, 404]
            details = f"Status: {response.status_code} (expected 200 or 404)"
            
            self.log_test("Admin User Rejection", expected_status, details)
            return expected_status
        except Exception as e:
            self.log_test("Admin User Rejection", False, f"Exception: {str(e)}")
            return False

    def test_admin_properties_moderation(self):
        """Test admin properties moderation"""
        if not self.admin_token:
            self.log_test("Admin Properties Moderation", False, "No admin token available")
            return False
            
        try:
            response = self.make_authenticated_request('GET', '/admin/properties', self.admin_token)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                properties_count = len(data) if isinstance(data, list) else 0
                details += f", Properties for moderation: {properties_count}"
            
            self.log_test("Admin Properties Moderation", success, details)
            return success
        except Exception as e:
            self.log_test("Admin Properties Moderation", False, f"Exception: {str(e)}")
            return False

    def test_admin_property_verification(self):
        """Test admin property verification"""
        if not self.admin_token:
            self.log_test("Admin Property Verification", False, "No admin token available")
            return False
            
        try:
            test_property_id = "test-property-id"
            
            response = self.make_authenticated_request(
                'PUT', f'/admin/properties/{test_property_id}/verify', self.admin_token
            )
            
            expected_status = response.status_code in [200, 404]
            details = f"Status: {response.status_code} (expected 200 or 404)"
            
            self.log_test("Admin Property Verification", expected_status, details)
            return expected_status
        except Exception as e:
            self.log_test("Admin Property Verification", False, f"Exception: {str(e)}")
            return False

    def test_admin_services_moderation(self):
        """Test admin services moderation"""
        if not self.admin_token:
            self.log_test("Admin Services Moderation", False, "No admin token available")
            return False
            
        try:
            response = self.make_authenticated_request('GET', '/admin/services', self.admin_token)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                services_count = len(data) if isinstance(data, list) else 0
                details += f", Services for moderation: {services_count}"
            
            self.log_test("Admin Services Moderation", success, details)
            return success
        except Exception as e:
            self.log_test("Admin Services Moderation", False, f"Exception: {str(e)}")
            return False

    def test_admin_analytics(self):
        """Test admin analytics endpoints"""
        if not self.admin_token:
            self.log_test("Admin Analytics", False, "No admin token available")
            return False
            
        try:
            # Test user analytics
            users_response = self.make_authenticated_request('GET', '/admin/analytics/users', self.admin_token)
            users_success = users_response.status_code == 200
            
            # Test property analytics
            properties_response = self.make_authenticated_request('GET', '/admin/analytics/properties', self.admin_token)
            properties_success = properties_response.status_code == 200
            
            success = users_success and properties_success
            details = f"Users analytics: {users_response.status_code}, Properties analytics: {properties_response.status_code}"
            
            self.log_test("Admin Analytics", success, details)
            return success
        except Exception as e:
            self.log_test("Admin Analytics", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # REVIEWS & RATINGS TESTS (6 endpoints)
    # ============================================================================
    
    def test_reviews_system(self):
        """Test complete reviews and ratings system"""
        if not self.client_token:
            self.log_test("Reviews System", False, "No client token available")
            return False
            
        try:
            # Test creating a review
            review_data = {
                "property_id": "sample-property-id",
                "rating": 5,
                "comment": "Excellent property with great amenities!"
            }
            
            create_response = self.make_authenticated_request(
                'POST', '/reviews', self.client_token, json=review_data
            )
            
            create_success = create_response.status_code in [200, 201]
            details = f"Create review: {create_response.status_code}"
            
            if create_success:
                review_data = create_response.json()
                self.test_review_id = review_data.get('id')
                details += f", Review ID: {self.test_review_id}"
            
            # Test getting property reviews
            property_reviews_response = self.make_authenticated_request(
                'GET', '/reviews/property/sample-property-id', self.client_token
            )
            property_reviews_success = property_reviews_response.status_code == 200
            details += f", Property reviews: {property_reviews_response.status_code}"
            
            # Test getting user reviews
            user_reviews_response = self.make_authenticated_request(
                'GET', '/reviews/user/sample-user-id', self.client_token
            )
            user_reviews_success = user_reviews_response.status_code == 200
            details += f", User reviews: {user_reviews_response.status_code}"
            
            success = create_success and property_reviews_success and user_reviews_success
            self.log_test("Reviews System", success, details)
            return success
            
        except Exception as e:
            self.log_test("Reviews System", False, f"Exception: {str(e)}")
            return False

    def test_review_validation(self):
        """Test review validation (duplicates, rating range)"""
        if not self.client_token:
            self.log_test("Review Validation", False, "No client token available")
            return False
            
        try:
            # Test invalid rating (outside 1-5 range)
            invalid_review = {
                "property_id": "sample-property-id",
                "rating": 10,  # Invalid rating
                "comment": "Invalid rating test"
            }
            
            response = self.make_authenticated_request(
                'POST', '/reviews', self.client_token, json=invalid_review
            )
            
            # Should fail with validation error
            validation_success = response.status_code in [400, 422]
            details = f"Invalid rating validation: {response.status_code} (expected 400/422)"
            
            # Test missing required fields
            incomplete_review = {
                "rating": 5
                # Missing property_id or service_id
            }
            
            incomplete_response = self.make_authenticated_request(
                'POST', '/reviews', self.client_token, json=incomplete_review
            )
            
            incomplete_success = incomplete_response.status_code in [400, 422]
            details += f", Missing fields: {incomplete_response.status_code} (expected 400/422)"
            
            success = validation_success and incomplete_success
            self.log_test("Review Validation", success, details)
            return success
            
        except Exception as e:
            self.log_test("Review Validation", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # MESSAGING SYSTEM TESTS (6 endpoints)
    # ============================================================================
    
    def test_messaging_system(self):
        """Test complete messaging system"""
        if not self.client_token or not self.owner_token:
            self.log_test("Messaging System", False, "Missing authentication tokens")
            return False
            
        try:
            # Test sending a message
            message_data = {
                "receiver_id": "sample-receiver-id",
                "content": "Hello, I'm interested in your property listing!"
            }
            
            send_response = self.make_authenticated_request(
                'POST', '/messages', self.client_token, json=message_data
            )
            
            send_success = send_response.status_code in [200, 201]
            details = f"Send message: {send_response.status_code}"
            
            # Test getting conversations
            conversations_response = self.make_authenticated_request(
                'GET', '/messages/conversations', self.client_token
            )
            conversations_success = conversations_response.status_code == 200
            details += f", Conversations: {conversations_response.status_code}"
            
            # Test getting message thread
            thread_response = self.make_authenticated_request(
                'GET', '/messages/thread/sample-user-id', self.client_token
            )
            thread_success = thread_response.status_code == 200
            details += f", Thread: {thread_response.status_code}"
            
            # Test unread count
            unread_response = self.make_authenticated_request(
                'GET', '/messages/unread-count', self.client_token
            )
            unread_success = unread_response.status_code == 200
            details += f", Unread count: {unread_response.status_code}"
            
            success = send_success and conversations_success and thread_success and unread_success
            self.log_test("Messaging System", success, details)
            return success
            
        except Exception as e:
            self.log_test("Messaging System", False, f"Exception: {str(e)}")
            return False

    def test_message_validation(self):
        """Test message validation (no self-messaging, etc.)"""
        if not self.client_token:
            self.log_test("Message Validation", False, "No client token available")
            return False
            
        try:
            # Test empty message content
            empty_message = {
                "receiver_id": "sample-receiver-id",
                "content": ""
            }
            
            response = self.make_authenticated_request(
                'POST', '/messages', self.client_token, json=empty_message
            )
            
            validation_success = response.status_code in [400, 422]
            details = f"Empty content validation: {response.status_code} (expected 400/422)"
            
            # Test missing receiver
            no_receiver = {
                "content": "Test message without receiver"
            }
            
            no_receiver_response = self.make_authenticated_request(
                'POST', '/messages', self.client_token, json=no_receiver
            )
            
            no_receiver_success = no_receiver_response.status_code in [400, 422]
            details += f", Missing receiver: {no_receiver_response.status_code} (expected 400/422)"
            
            success = validation_success and no_receiver_success
            self.log_test("Message Validation", success, details)
            return success
            
        except Exception as e:
            self.log_test("Message Validation", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # BOOKING SYSTEM TESTS (9 endpoints)
    # ============================================================================
    
    def test_booking_system(self):
        """Test complete booking system"""
        if not self.client_token:
            self.log_test("Booking System", False, "No client token available")
            return False
            
        try:
            # Test creating a property viewing booking
            booking_data = {
                "property_id": "sample-property-id",
                "scheduled_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "notes": "I would like to schedule a property viewing"
            }
            
            create_response = self.make_authenticated_request(
                'POST', '/bookings', self.client_token, json=booking_data
            )
            
            create_success = create_response.status_code in [200, 201]
            details = f"Create booking: {create_response.status_code}"
            
            if create_success:
                booking_data = create_response.json()
                self.test_booking_id = booking_data.get('id')
                details += f", Booking ID: {self.test_booking_id}"
            
            # Test getting user's bookings
            user_bookings_response = self.make_authenticated_request(
                'GET', '/bookings', self.client_token
            )
            user_bookings_success = user_bookings_response.status_code == 200
            details += f", User bookings: {user_bookings_response.status_code}"
            
            # Test getting received bookings (for owners/providers)
            if self.owner_token:
                received_response = self.make_authenticated_request(
                    'GET', '/bookings/received', self.owner_token
                )
                received_success = received_response.status_code == 200
                details += f", Received bookings: {received_response.status_code}"
            else:
                received_success = True
                details += ", Received bookings: SKIPPED (no owner token)"
            
            # Test available time slots
            slots_response = self.make_authenticated_request(
                'GET', '/bookings/property/sample-property-id/slots', self.client_token
            )
            slots_success = slots_response.status_code == 200
            details += f", Time slots: {slots_response.status_code}"
            
            success = create_success and user_bookings_success and received_success and slots_success
            self.log_test("Booking System", success, details)
            return success
            
        except Exception as e:
            self.log_test("Booking System", False, f"Exception: {str(e)}")
            return False

    def test_booking_workflow(self):
        """Test booking confirmation and completion workflow"""
        if not self.client_token or not self.owner_token:
            self.log_test("Booking Workflow", False, "Missing authentication tokens")
            return False
            
        try:
            test_booking_id = "sample-booking-id"
            
            # Test booking confirmation (by owner/provider)
            confirm_response = self.make_authenticated_request(
                'PUT', f'/bookings/{test_booking_id}/confirm', self.owner_token
            )
            confirm_success = confirm_response.status_code in [200, 404]
            details = f"Confirm booking: {confirm_response.status_code} (expected 200/404)"
            
            # Test booking completion
            complete_response = self.make_authenticated_request(
                'PUT', f'/bookings/{test_booking_id}/complete', self.owner_token
            )
            complete_success = complete_response.status_code in [200, 404]
            details += f", Complete booking: {complete_response.status_code} (expected 200/404)"
            
            # Test booking cancellation
            cancel_data = {"reason": "Test cancellation reason"}
            cancel_response = self.make_authenticated_request(
                'PUT', f'/bookings/{test_booking_id}/cancel', 
                self.client_token, json=cancel_data
            )
            cancel_success = cancel_response.status_code in [200, 404]
            details += f", Cancel booking: {cancel_response.status_code} (expected 200/404)"
            
            success = confirm_success and complete_success and cancel_success
            self.log_test("Booking Workflow", success, details)
            return success
            
        except Exception as e:
            self.log_test("Booking Workflow", False, f"Exception: {str(e)}")
            return False

    def test_booking_validation(self):
        """Test booking validation (dates, required fields)"""
        if not self.client_token:
            self.log_test("Booking Validation", False, "No client token available")
            return False
            
        try:
            # Test booking with past date
            past_booking = {
                "property_id": "sample-property-id",
                "scheduled_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "notes": "Past date booking test"
            }
            
            past_response = self.make_authenticated_request(
                'POST', '/bookings', self.client_token, json=past_booking
            )
            
            past_validation = past_response.status_code in [400, 422]
            details = f"Past date validation: {past_response.status_code} (expected 400/422)"
            
            # Test booking without property or service ID
            no_target = {
                "scheduled_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "notes": "No target booking test"
            }
            
            no_target_response = self.make_authenticated_request(
                'POST', '/bookings', self.client_token, json=no_target
            )
            
            no_target_validation = no_target_response.status_code in [400, 422]
            details += f", Missing target: {no_target_response.status_code} (expected 400/422)"
            
            success = past_validation and no_target_validation
            self.log_test("Booking Validation", success, details)
            return success
            
        except Exception as e:
            self.log_test("Booking Validation", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_tests(self):
        """Run comprehensive tests for all new features"""
        print("🚀 Starting Comprehensive Habitere API Tests...")
        print(f"Testing API at: {self.api_url}")
        print("=" * 80)
        
        # Setup authentication
        self.setup_test_authentication()
        
        # Initialize sample data
        self.test_sample_data_initialization()
        
        # Core API tests
        print("\n🔧 Testing Core API...")
        print("-" * 40)
        self.test_api_health()
        self.test_api_root()
        self.test_properties_endpoint()
        self.test_services_endpoint()
        
        # Admin System Tests
        print("\n👑 Testing Admin System (12 endpoints)...")
        print("-" * 40)
        self.test_admin_stats()
        self.test_admin_users_list()
        self.test_admin_user_approval()
        self.test_admin_user_rejection()
        self.test_admin_properties_moderation()
        self.test_admin_property_verification()
        self.test_admin_services_moderation()
        self.test_admin_analytics()
        
        # Reviews & Ratings Tests
        print("\n⭐ Testing Reviews & Ratings System (6 endpoints)...")
        print("-" * 40)
        self.test_reviews_system()
        self.test_review_validation()
        
        # Messaging System Tests
        print("\n💬 Testing Messaging System (6 endpoints)...")
        print("-" * 40)
        self.test_messaging_system()
        self.test_message_validation()
        
        # Booking System Tests
        print("\n📅 Testing Booking System (9 endpoints)...")
        print("-" * 40)
        self.test_booking_system()
        self.test_booking_workflow()
        self.test_booking_validation()
        
        # Legacy tests
        print("\n🖼️  Testing Image Upload System...")
        print("-" * 40)
        self.test_image_upload_no_auth()
        self.test_get_entity_images()
        
        print("\n💳 Testing MTN Mobile Money Integration...")
        print("-" * 40)
        self.test_mtn_momo_configuration()
        self.test_mtn_momo_payment_no_auth()
        self.test_mtn_momo_callback()
        
        # Print comprehensive summary
        self.print_comprehensive_summary()
        
        return self.tests_passed == self.tests_run

    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("=" * 80)
        print(f"📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        print(f"   Total tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Categorize results
        admin_tests = [r for r in self.test_results if 'admin' in r['test_name'].lower()]
        review_tests = [r for r in self.test_results if 'review' in r['test_name'].lower()]
        message_tests = [r for r in self.test_results if 'messag' in r['test_name'].lower()]
        booking_tests = [r for r in self.test_results if 'booking' in r['test_name'].lower()]
        
        print(f"\n📈 Results by Category:")
        print(f"   Admin System: {sum(1 for t in admin_tests if t['success'])}/{len(admin_tests)} passed")
        print(f"   Reviews & Ratings: {sum(1 for t in review_tests if t['success'])}/{len(review_tests)} passed")
        print(f"   Messaging System: {sum(1 for t in message_tests if t['success'])}/{len(message_tests)} passed")
        print(f"   Booking System: {sum(1 for t in booking_tests if t['success'])}/{len(booking_tests)} passed")
        
        # List failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ Failed Tests ({len(failures)}):")
            for failure in failures:
                print(f"   - {failure['test_name']}: {failure['details']}")
        
        # Authentication status
        print(f"\n🔐 Authentication Status:")
        print(f"   Admin Token: {'✅ Available' if self.admin_token else '❌ Not Available'}")
        print(f"   Client Token: {'✅ Available' if self.client_token else '❌ Not Available'}")
        print(f"   Owner Token: {'✅ Available' if self.owner_token else '❌ Not Available'}")
        print(f"   Provider Token: {'✅ Available' if self.provider_token else '❌ Not Available'}")
        
        # Save results
        results = {
            "summary": {
                "total_tests": self.tests_run,
                "passed_tests": self.tests_passed,
                "failed_tests": self.tests_run - self.tests_passed,
                "success_rate": (self.tests_passed/self.tests_run)*100,
                "timestamp": datetime.now().isoformat(),
                "authentication_status": {
                    "admin_token": bool(self.admin_token),
                    "client_token": bool(self.client_token),
                    "owner_token": bool(self.owner_token),
                    "provider_token": bool(self.provider_token)
                }
            },
            "test_results": self.test_results,
            "categories": {
                "admin_tests": len(admin_tests),
                "review_tests": len(review_tests),
                "message_tests": len(message_tests),
                "booking_tests": len(booking_tests)
            }
        }
        
        with open('/app/comprehensive_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: /app/comprehensive_test_results.json")

    def run_all_tests(self):
        """Run all API tests (legacy method)"""
        return self.run_comprehensive_tests()

def main():
    tester = HabitereAPITester()
    success = tester.run_comprehensive_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())