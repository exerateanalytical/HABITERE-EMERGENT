#!/usr/bin/env python3

import requests
import json
from datetime import datetime

class SimpleHabitereAPITester:
    def __init__(self):
        self.base_url = "https://fastapi-modules-1.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Habitere-Test-Client/1.0'
        })
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

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

    def test_endpoint_accessibility(self, method: str, endpoint: str, expected_status: int, test_name: str, data=None):
        """Test if endpoint is accessible and returns expected status"""
        try:
            url = f"{self.api_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                self.log_test(test_name, False, f"Unsupported method: {method}")
                return False
            
            success = response.status_code == expected_status
            details = f"Status: {response.status_code} (expected {expected_status})"
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'message' in data:
                        details += f", Message: {data['message']}"
                    elif isinstance(data, list):
                        details += f", Items: {len(data)}"
                except:
                    pass
            
            self.log_test(test_name, success, details)
            return success
            
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False

    def run_endpoint_tests(self):
        """Test all endpoints for accessibility"""
        print("🚀 Testing Habitere API Endpoint Accessibility...")
        print(f"Testing API at: {self.api_url}")
        print("=" * 80)
        
        # Core endpoints
        print("\n🔧 Core API Endpoints...")
        print("-" * 40)
        self.test_endpoint_accessibility('GET', '/', 200, 'API Root')
        self.test_endpoint_accessibility('GET', '/health', 200, 'Health Check')
        self.test_endpoint_accessibility('POST', '/init-sample-data', 200, 'Initialize Sample Data')
        
        # Public endpoints
        print("\n🏠 Public Property & Service Endpoints...")
        print("-" * 40)
        self.test_endpoint_accessibility('GET', '/properties', 200, 'Properties List')
        self.test_endpoint_accessibility('GET', '/services', 200, 'Services List')
        self.test_endpoint_accessibility('GET', '/reviews', 200, 'Reviews List')
        
        # Admin endpoints (should return 401 without auth)
        print("\n👑 Admin Endpoints (should require auth)...")
        print("-" * 40)
        self.test_endpoint_accessibility('GET', '/admin/stats', 401, 'Admin Stats')
        self.test_endpoint_accessibility('GET', '/admin/users', 401, 'Admin Users List')
        self.test_endpoint_accessibility('GET', '/admin/properties', 401, 'Admin Properties')
        self.test_endpoint_accessibility('GET', '/admin/services', 401, 'Admin Services')
        self.test_endpoint_accessibility('GET', '/admin/analytics/users', 401, 'Admin User Analytics')
        self.test_endpoint_accessibility('GET', '/admin/analytics/properties', 401, 'Admin Property Analytics')
        
        # Review endpoints
        print("\n⭐ Review Endpoints...")
        print("-" * 40)
        self.test_endpoint_accessibility('POST', '/reviews', 401, 'Create Review (No Auth)', 
                                       {"property_id": "test", "rating": 5, "comment": "test"})
        self.test_endpoint_accessibility('GET', '/reviews/property/test-id', 200, 'Get Property Reviews')
        self.test_endpoint_accessibility('GET', '/reviews/service/test-id', 200, 'Get Service Reviews')
        self.test_endpoint_accessibility('GET', '/reviews/user/test-id', 200, 'Get User Reviews')
        
        # Message endpoints (should require auth)
        print("\n💬 Message Endpoints (should require auth)...")
        print("-" * 40)
        self.test_endpoint_accessibility('POST', '/messages', 401, 'Send Message (No Auth)',
                                       {"receiver_id": "test", "content": "test"})
        self.test_endpoint_accessibility('GET', '/messages/conversations', 401, 'Get Conversations')
        self.test_endpoint_accessibility('GET', '/messages/thread/test-id', 401, 'Get Message Thread')
        self.test_endpoint_accessibility('GET', '/messages/unread-count', 401, 'Get Unread Count')
        
        # Booking endpoints (should require auth)
        print("\n📅 Booking Endpoints (should require auth)...")
        print("-" * 40)
        self.test_endpoint_accessibility('POST', '/bookings', 401, 'Create Booking (No Auth)',
                                       {"property_id": "test", "scheduled_date": "2024-12-25T10:00:00Z"})
        self.test_endpoint_accessibility('GET', '/bookings', 401, 'Get User Bookings')
        self.test_endpoint_accessibility('GET', '/bookings/received', 401, 'Get Received Bookings')
        self.test_endpoint_accessibility('GET', '/bookings/property/test-id/slots', 200, 'Get Available Slots')
        
        # Authentication endpoints
        print("\n🔐 Authentication Endpoints...")
        print("-" * 40)
        self.test_endpoint_accessibility('GET', '/auth/me', 401, 'Get Current User (No Auth)')
        self.test_endpoint_accessibility('GET', '/auth/google/login', 200, 'Google OAuth URL')
        
        # Image upload endpoints
        print("\n🖼️ Image Upload Endpoints...")
        print("-" * 40)
        self.test_endpoint_accessibility('GET', '/images/property/test-id', 200, 'Get Entity Images')
        
        # Payment endpoints
        print("\n💳 Payment Endpoints...")
        print("-" * 40)
        self.test_endpoint_accessibility('POST', '/payments/mtn-momo', 401, 'MTN MoMo Payment (No Auth)',
                                       {"amount": "100", "phone": "237123456789"})
        self.test_endpoint_accessibility('POST', '/payments/mtn-momo/callback', 200, 'MTN MoMo Callback',
                                       {"referenceId": "test", "status": "SUCCESSFUL"})
        
        # Print summary
        print("\n" + "=" * 80)
        print(f"📊 ENDPOINT ACCESSIBILITY SUMMARY")
        print("=" * 80)
        print(f"   Total endpoints tested: {self.tests_run}")
        print(f"   Accessible as expected: {self.tests_passed}")
        print(f"   Issues found: {self.tests_run - self.tests_passed}")
        print(f"   Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # List issues
        issues = [r for r in self.results if not r['success']]
        if issues:
            print(f"\n❌ Issues Found ({len(issues)}):")
            for issue in issues:
                print(f"   - {issue['test_name']}: {issue['details']}")
        else:
            print(f"\n✅ All endpoints are accessible as expected!")
        
        # Save results
        with open('/app/endpoint_accessibility_results.json', 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": self.tests_run,
                    "passed_tests": self.tests_passed,
                    "failed_tests": self.tests_run - self.tests_passed,
                    "success_rate": (self.tests_passed/self.tests_run)*100,
                    "timestamp": datetime.now().isoformat()
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\n📄 Results saved to: /app/endpoint_accessibility_results.json")
        
        return self.tests_passed == self.tests_run

def main():
    tester = SimpleHabitereAPITester()
    success = tester.run_endpoint_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())