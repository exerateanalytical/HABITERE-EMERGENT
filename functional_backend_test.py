#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta
import uuid

class FunctionalHabitereAPITester:
    def __init__(self):
        self.base_url = "https://habitere-upgrade.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Habitere-Test-Client/1.0'
        })
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []
        
        # Test data
        self.sample_property_id = None
        self.sample_service_id = None

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED - {details}")
        
        self.results.append({
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_core_functionality(self):
        """Test core API functionality"""
        print("🔧 Testing Core API Functionality...")
        print("-" * 50)
        
        # Test API health and root
        try:
            health_response = self.session.get(f"{self.api_url}/health")
            health_success = health_response.status_code == 200
            self.log_test("API Health Check", health_success, 
                         f"Status: {health_response.status_code}")
            
            root_response = self.session.get(f"{self.api_url}/")
            root_success = root_response.status_code == 200
            self.log_test("API Root Endpoint", root_success, 
                         f"Status: {root_response.status_code}")
            
            # Initialize sample data
            init_response = self.session.post(f"{self.api_url}/init-sample-data")
            init_success = init_response.status_code == 200
            self.log_test("Sample Data Initialization", init_success, 
                         f"Status: {init_response.status_code}")
            
        except Exception as e:
            self.log_test("Core Functionality", False, f"Exception: {str(e)}")

    def test_properties_and_services(self):
        """Test properties and services endpoints"""
        print("\n🏠 Testing Properties and Services...")
        print("-" * 50)
        
        try:
            # Test properties listing
            properties_response = self.session.get(f"{self.api_url}/properties")
            properties_success = properties_response.status_code == 200
            
            if properties_success:
                properties_data = properties_response.json()
                properties_count = len(properties_data) if isinstance(properties_data, list) else 0
                if properties_count > 0:
                    self.sample_property_id = properties_data[0].get('id')
                self.log_test("Properties Listing", True, 
                             f"Found {properties_count} properties")
            else:
                self.log_test("Properties Listing", False, 
                             f"Status: {properties_response.status_code}")
            
            # Test services listing
            services_response = self.session.get(f"{self.api_url}/services")
            services_success = services_response.status_code == 200
            
            if services_success:
                services_data = services_response.json()
                services_count = len(services_data) if isinstance(services_data, list) else 0
                if services_count > 0:
                    self.sample_service_id = services_data[0].get('id')
                self.log_test("Services Listing", True, 
                             f"Found {services_count} services")
            else:
                self.log_test("Services Listing", False, 
                             f"Status: {services_response.status_code}")
            
            # Test property detail if we have an ID
            if self.sample_property_id:
                property_detail_response = self.session.get(
                    f"{self.api_url}/properties/{self.sample_property_id}"
                )
                property_detail_success = property_detail_response.status_code == 200
                self.log_test("Property Detail", property_detail_success, 
                             f"Status: {property_detail_response.status_code}")
            
            # Test service detail if we have an ID
            if self.sample_service_id:
                service_detail_response = self.session.get(
                    f"{self.api_url}/services/{self.sample_service_id}"
                )
                service_detail_success = service_detail_response.status_code == 200
                self.log_test("Service Detail", service_detail_success, 
                             f"Status: {service_detail_response.status_code}")
            
        except Exception as e:
            self.log_test("Properties and Services", False, f"Exception: {str(e)}")

    def test_admin_endpoints_security(self):
        """Test that admin endpoints properly require authentication"""
        print("\n👑 Testing Admin Endpoints Security...")
        print("-" * 50)
        
        admin_endpoints = [
            ('/admin/stats', 'Admin Stats'),
            ('/admin/users', 'Admin Users List'),
            ('/admin/properties', 'Admin Properties'),
            ('/admin/services', 'Admin Services'),
            ('/admin/analytics/users', 'Admin User Analytics'),
            ('/admin/analytics/properties', 'Admin Property Analytics')
        ]
        
        for endpoint, test_name in admin_endpoints:
            try:
                response = self.session.get(f"{self.api_url}{endpoint}")
                # Should return 401 (Unauthorized) without authentication
                expected_auth_failure = response.status_code == 401
                self.log_test(f"{test_name} (Auth Required)", expected_auth_failure, 
                             f"Status: {response.status_code} (expected 401)")
            except Exception as e:
                self.log_test(f"{test_name} (Auth Required)", False, f"Exception: {str(e)}")

    def test_reviews_functionality(self):
        """Test reviews endpoints functionality"""
        print("\n⭐ Testing Reviews Functionality...")
        print("-" * 50)
        
        try:
            # Test reviews listing
            reviews_response = self.session.get(f"{self.api_url}/reviews")
            reviews_success = reviews_response.status_code == 200
            
            if reviews_success:
                reviews_data = reviews_response.json()
                reviews_count = len(reviews_data) if isinstance(reviews_data, list) else 0
                self.log_test("Reviews Listing", True, f"Found {reviews_count} reviews")
            else:
                self.log_test("Reviews Listing", False, f"Status: {reviews_response.status_code}")
            
            # Test property reviews (should work even with non-existent property)
            if self.sample_property_id:
                property_reviews_response = self.session.get(
                    f"{self.api_url}/reviews/property/{self.sample_property_id}"
                )
                property_reviews_success = property_reviews_response.status_code == 200
                self.log_test("Property Reviews", property_reviews_success, 
                             f"Status: {property_reviews_response.status_code}")
            
            # Test service reviews
            if self.sample_service_id:
                service_reviews_response = self.session.get(
                    f"{self.api_url}/reviews/service/{self.sample_service_id}"
                )
                service_reviews_success = service_reviews_response.status_code == 200
                self.log_test("Service Reviews", service_reviews_success, 
                             f"Status: {service_reviews_response.status_code}")
            
            # Test user reviews
            test_user_id = "test-user-id"
            user_reviews_response = self.session.get(
                f"{self.api_url}/reviews/user/{test_user_id}"
            )
            user_reviews_success = user_reviews_response.status_code == 200
            self.log_test("User Reviews", user_reviews_success, 
                         f"Status: {user_reviews_response.status_code}")
            
            # Test creating review without auth (should fail)
            review_data = {
                "property_id": self.sample_property_id or "test-property",
                "rating": 5,
                "comment": "Test review"
            }
            create_review_response = self.session.post(f"{self.api_url}/reviews", json=review_data)
            create_review_auth_required = create_review_response.status_code == 401
            self.log_test("Create Review (Auth Required)", create_review_auth_required, 
                         f"Status: {create_review_response.status_code} (expected 401)")
            
        except Exception as e:
            self.log_test("Reviews Functionality", False, f"Exception: {str(e)}")

    def test_messaging_endpoints_security(self):
        """Test messaging endpoints security"""
        print("\n💬 Testing Messaging Endpoints Security...")
        print("-" * 50)
        
        messaging_endpoints = [
            ('POST', '/messages', 'Send Message', {"receiver_id": "test", "content": "test"}),
            ('GET', '/messages/conversations', 'Get Conversations', None),
            ('GET', '/messages/thread/test-user', 'Get Message Thread', None),
            ('GET', '/messages/unread-count', 'Get Unread Count', None)
        ]
        
        for method, endpoint, test_name, data in messaging_endpoints:
            try:
                if method == 'POST':
                    response = self.session.post(f"{self.api_url}{endpoint}", json=data)
                else:
                    response = self.session.get(f"{self.api_url}{endpoint}")
                
                # Should return 401 (Unauthorized) without authentication
                expected_auth_failure = response.status_code == 401
                self.log_test(f"{test_name} (Auth Required)", expected_auth_failure, 
                             f"Status: {response.status_code} (expected 401)")
            except Exception as e:
                self.log_test(f"{test_name} (Auth Required)", False, f"Exception: {str(e)}")

    def test_booking_endpoints_functionality(self):
        """Test booking endpoints functionality"""
        print("\n📅 Testing Booking Endpoints Functionality...")
        print("-" * 50)
        
        try:
            # Test booking creation without auth (should fail)
            booking_data = {
                "property_id": self.sample_property_id or "test-property",
                "scheduled_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "notes": "Test booking"
            }
            create_booking_response = self.session.post(f"{self.api_url}/bookings", json=booking_data)
            create_booking_auth_required = create_booking_response.status_code == 401
            self.log_test("Create Booking (Auth Required)", create_booking_auth_required, 
                         f"Status: {create_booking_response.status_code} (expected 401)")
            
            # Test getting user bookings without auth (should fail)
            user_bookings_response = self.session.get(f"{self.api_url}/bookings")
            user_bookings_auth_required = user_bookings_response.status_code == 401
            self.log_test("Get User Bookings (Auth Required)", user_bookings_auth_required, 
                         f"Status: {user_bookings_response.status_code} (expected 401)")
            
            # Test getting received bookings without auth (should fail)
            received_bookings_response = self.session.get(f"{self.api_url}/bookings/received")
            received_bookings_auth_required = received_bookings_response.status_code == 401
            self.log_test("Get Received Bookings (Auth Required)", received_bookings_auth_required, 
                         f"Status: {received_bookings_response.status_code} (expected 401)")
            
            # Test available slots with proper date parameter
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            if self.sample_property_id:
                slots_response = self.session.get(
                    f"{self.api_url}/bookings/property/{self.sample_property_id}/slots?date={tomorrow}"
                )
                slots_success = slots_response.status_code == 200
                self.log_test("Get Available Slots", slots_success, 
                             f"Status: {slots_response.status_code}")
            
        except Exception as e:
            self.log_test("Booking Endpoints", False, f"Exception: {str(e)}")

    def test_authentication_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        print("-" * 50)
        
        try:
            # Test getting current user without auth (should fail)
            me_response = self.session.get(f"{self.api_url}/auth/me")
            me_auth_required = me_response.status_code == 401
            self.log_test("Get Current User (Auth Required)", me_auth_required, 
                         f"Status: {me_response.status_code} (expected 401)")
            
            # Test Google OAuth URL generation (should work)
            google_response = self.session.get(f"{self.api_url}/auth/google/login")
            google_success = google_response.status_code == 200
            
            if google_success:
                google_data = google_response.json()
                has_auth_url = 'auth_url' in google_data
                self.log_test("Google OAuth URL Generation", has_auth_url, 
                             f"Status: {google_response.status_code}, Has auth_url: {has_auth_url}")
            else:
                self.log_test("Google OAuth URL Generation", False, 
                             f"Status: {google_response.status_code}")
            
        except Exception as e:
            self.log_test("Authentication Endpoints", False, f"Exception: {str(e)}")

    def test_image_and_payment_endpoints(self):
        """Test image upload and payment endpoints"""
        print("\n🖼️💳 Testing Image Upload and Payment Endpoints...")
        print("-" * 50)
        
        try:
            # Test getting entity images (should work)
            test_entity_id = self.sample_property_id or "test-property"
            images_response = self.session.get(f"{self.api_url}/images/property/{test_entity_id}")
            images_success = images_response.status_code == 200
            
            if images_success:
                images_data = images_response.json()
                images_count = len(images_data) if isinstance(images_data, list) else 0
                self.log_test("Get Entity Images", True, f"Found {images_count} images")
            else:
                self.log_test("Get Entity Images", False, f"Status: {images_response.status_code}")
            
            # Test MTN MoMo payment without auth (should fail)
            payment_data = {
                "amount": "1000",
                "currency": "EUR",
                "external_id": str(uuid.uuid4()),
                "payer_message": "Test payment",
                "payee_note": "Test transaction",
                "phone": "237123456789"
            }
            payment_response = self.session.post(f"{self.api_url}/payments/mtn-momo", json=payment_data)
            payment_auth_required = payment_response.status_code == 401
            self.log_test("MTN MoMo Payment (Auth Required)", payment_auth_required, 
                         f"Status: {payment_response.status_code} (expected 401)")
            
            # Test MTN MoMo callback (should work for webhooks)
            callback_data = {
                "referenceId": str(uuid.uuid4()),
                "status": "SUCCESSFUL",
                "financialTransactionId": str(uuid.uuid4())
            }
            callback_response = self.session.post(f"{self.api_url}/payments/mtn-momo/callback", json=callback_data)
            callback_success = callback_response.status_code in [200, 400, 404]  # Various acceptable responses
            self.log_test("MTN MoMo Callback", callback_success, 
                         f"Status: {callback_response.status_code}")
            
        except Exception as e:
            self.log_test("Image and Payment Endpoints", False, f"Exception: {str(e)}")

    def run_functional_tests(self):
        """Run all functional tests"""
        print("🚀 Starting Functional Habitere API Tests...")
        print(f"Testing API at: {self.api_url}")
        print("=" * 80)
        
        # Run all test categories
        self.test_core_functionality()
        self.test_properties_and_services()
        self.test_admin_endpoints_security()
        self.test_reviews_functionality()
        self.test_messaging_endpoints_security()
        self.test_booking_endpoints_functionality()
        self.test_authentication_endpoints()
        self.test_image_and_payment_endpoints()
        
        # Print comprehensive summary
        print("\n" + "=" * 80)
        print(f"📊 FUNCTIONAL TEST SUMMARY")
        print("=" * 80)
        print(f"   Total tests: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Categorize results
        categories = {
            'Core': [r for r in self.results if any(word in r['test_name'].lower() 
                    for word in ['health', 'root', 'sample'])],
            'Properties/Services': [r for r in self.results if any(word in r['test_name'].lower() 
                                   for word in ['properties', 'services', 'property', 'service'])],
            'Admin Security': [r for r in self.results if 'admin' in r['test_name'].lower()],
            'Reviews': [r for r in self.results if 'review' in r['test_name'].lower()],
            'Messaging': [r for r in self.results if 'messag' in r['test_name'].lower()],
            'Booking': [r for r in self.results if 'booking' in r['test_name'].lower()],
            'Authentication': [r for r in self.results if any(word in r['test_name'].lower() 
                              for word in ['auth', 'user', 'google'])],
            'Images/Payments': [r for r in self.results if any(word in r['test_name'].lower() 
                               for word in ['image', 'payment', 'momo'])]
        }
        
        print(f"\n📈 Results by Category:")
        for category, tests in categories.items():
            if tests:
                passed = sum(1 for t in tests if t['success'])
                total = len(tests)
                print(f"   {category}: {passed}/{total} passed ({(passed/total)*100:.1f}%)")
        
        # List failures
        failures = [r for r in self.results if not r['success']]
        if failures:
            print(f"\n❌ Failed Tests ({len(failures)}):")
            for failure in failures:
                print(f"   - {failure['test_name']}: {failure['details']}")
        else:
            print(f"\n✅ All tests passed!")
        
        # Key findings
        print(f"\n🔍 Key Findings:")
        auth_protected_working = sum(1 for r in self.results 
                                   if r['success'] and 'Auth Required' in r['test_name'])
        public_endpoints_working = sum(1 for r in self.results 
                                     if r['success'] and 'Auth Required' not in r['test_name'])
        
        print(f"   - Authentication protection: {auth_protected_working} endpoints properly secured")
        print(f"   - Public endpoints: {public_endpoints_working} endpoints accessible")
        print(f"   - Sample data: {'✅ Available' if self.sample_property_id else '❌ Not found'}")
        
        # Save results
        with open('/app/functional_test_results.json', 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": self.tests_run,
                    "passed_tests": self.tests_passed,
                    "failed_tests": self.tests_run - self.tests_passed,
                    "success_rate": (self.tests_passed/self.tests_run)*100,
                    "timestamp": datetime.now().isoformat(),
                    "sample_data": {
                        "property_id": self.sample_property_id,
                        "service_id": self.sample_service_id
                    }
                },
                "results": self.results,
                "categories": {cat: len(tests) for cat, tests in categories.items()}
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: /app/functional_test_results.json")
        
        return self.tests_passed == self.tests_run

def main():
    tester = FunctionalHabitereAPITester()
    success = tester.run_functional_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())