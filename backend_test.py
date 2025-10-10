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