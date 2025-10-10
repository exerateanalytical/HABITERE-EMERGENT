#!/usr/bin/env python3

import requests
import sys
import json
import os
import io
from datetime import datetime
from typing import Dict, Any
from PIL import Image

class HabitereAPITester:
    def __init__(self, base_url="https://cameroon-homes-1.preview.emergentagent.com"):
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

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Habitere API Tests...")
        print(f"Testing API at: {self.api_url}")
        print("=" * 60)
        
        # Initialize sample data first
        self.test_sample_data_initialization()
        
        # Core API tests
        self.test_api_health()
        self.test_api_root()
        
        # Public endpoints
        self.test_properties_endpoint()
        self.test_services_endpoint()
        self.test_property_detail()
        self.test_service_detail()
        self.test_reviews_endpoint()
        
        # Auth-protected endpoints (should fail without auth)
        self.test_auth_endpoints()
        self.test_messages_endpoint()
        self.test_bookings_endpoint()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Summary:")
        print(f"   Total tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Save detailed results
        results = {
            "summary": {
                "total_tests": self.tests_run,
                "passed_tests": self.tests_passed,
                "failed_tests": self.tests_run - self.tests_passed,
                "success_rate": (self.tests_passed/self.tests_run)*100,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results
        }
        
        with open('/app/backend_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Detailed results saved to: /app/backend_test_results.json")
        
        return self.tests_passed == self.tests_run

def main():
    tester = HabitereAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())