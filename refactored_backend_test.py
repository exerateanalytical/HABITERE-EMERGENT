#!/usr/bin/env python3

import requests
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class RefactoredBackendTester:
    def __init__(self):
        # Use the REACT_APP_BACKEND_URL from frontend/.env as specified in the review request
        self.base_url = "https://plan-builder-8.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Habitere-Refactored-Test-Client/1.0'
        })
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data
        self.sample_property_id = None
        self.sample_service_id = None
        self.sample_user_id = None

    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED - {details}")
        
        if details:
            print(f"   └─ {details}")
        
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })

    def make_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request to API endpoint"""
        url = f"{self.api_url}{endpoint}"
        try:
            response = getattr(self.session, method.lower())(url, **kwargs)
            return response
        except Exception as e:
            print(f"Request failed: {method} {url} - {str(e)}")
            return None

    # ============================================================================
    # 1. CORE ENDPOINTS (/api/)
    # ============================================================================
    
    def test_api_root_endpoint(self):
        """Test GET / - Root endpoint"""
        try:
            response = self.make_request('GET', '/')
            if not response:
                self.log_test("API Root Endpoint", False, "Request failed")
                return False
                
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    data = response.json()
                    message = data.get('message', 'No message')
                    details += f", Message: {message}"
                except:
                    details += ", Response: Non-JSON"
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("API Root Endpoint", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_api_health_endpoint(self):
        """Test GET /health - Health check"""
        try:
            response = self.make_request('GET', '/health')
            if not response:
                self.log_test("API Health Check", False, "Request failed")
                return False
                
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    details += f", Health Status: {status}"
                except:
                    details += ", Response: Non-JSON"
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("API Health Check", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("API Health Check", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # 2. AUTHENTICATION ENDPOINTS (/api/auth/)
    # ============================================================================
    
    def test_auth_register_endpoint(self):
        """Test POST /auth/register - User registration"""
        try:
            # Generate unique email for testing
            test_email = f"test_{uuid.uuid4().hex[:8]}@habitere.com"
            
            register_data = {
                "email": test_email,
                "name": "Test User",
                "password": "testpass123"
            }
            
            response = self.make_request('POST', '/auth/register', json=register_data)
            if not response:
                self.log_test("Auth Register", False, "Request failed")
                return False
                
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    data = response.json()
                    message = data.get('message', 'No message')
                    details += f", Message: {message[:100]}"
                except:
                    details += ", Response: Non-JSON"
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Auth Register", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Auth Register", False, f"Exception: {str(e)}")
            return False

    def test_auth_login_endpoint(self):
        """Test POST /auth/login - User login"""
        try:
            # Try to login with admin credentials
            login_data = {
                "email": "admin@habitere.com",
                "password": "admin123"
            }
            
            response = self.make_request('POST', '/auth/login', json=login_data)
            if not response:
                self.log_test("Auth Login", False, "Request failed")
                return False
                
            # Accept both successful login (200) and email verification required (403)
            success = response.status_code in [200, 403]
            details = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                details += ", Login successful"
                try:
                    data = response.json()
                    user_email = data.get('user', {}).get('email', 'unknown')
                    details += f", User: {user_email}"
                except:
                    details += ", Response: Non-JSON"
            elif response.status_code == 403:
                details += ", Email verification required (expected behavior)"
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Auth Login", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Auth Login", False, f"Exception: {str(e)}")
            return False

    def test_auth_me_endpoint(self):
        """Test GET /auth/me - Get current user (should require authentication)"""
        try:
            response = self.make_request('GET', '/auth/me')
            if not response:
                self.log_test("Auth Me (No Auth)", False, "Request failed")
                return False
                
            # Should return 401 without authentication
            success = response.status_code == 401
            details = f"Status: {response.status_code} (expected 401 without auth)"
            
            if not success:
                details += f", Unexpected response: {response.text[:100]}"
                
            self.log_test("Auth Me (No Auth)", success, details)
            return success
        except Exception as e:
            self.log_test("Auth Me (No Auth)", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # 3. PROPERTIES ENDPOINTS (/api/properties)
    # ============================================================================
    
    def test_properties_list_endpoint(self):
        """Test GET /properties - List properties"""
        try:
            response = self.make_request('GET', '/properties')
            if not response:
                self.log_test("Properties List", False, "Request failed")
                return False
                
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        properties_count = len(data)
                        details += f", Properties found: {properties_count}"
                        
                        # Store first property ID for detail testing
                        if properties_count > 0 and data[0].get('id'):
                            self.sample_property_id = data[0]['id']
                            details += f", Sample ID: {self.sample_property_id[:8]}..."
                    else:
                        details += ", Response: Not a list"
                        success = False
                except:
                    details += ", Response: Non-JSON"
                    success = False
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Properties List", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Properties List", False, f"Exception: {str(e)}")
            return False

    def test_properties_filters(self):
        """Test GET /properties with filters"""
        try:
            # Test with various filters
            filter_params = {
                'property_type': 'apartment',
                'listing_type': 'rent',
                'location': 'Douala',
                'limit': 5
            }
            
            response = self.make_request('GET', '/properties', params=filter_params)
            if not response:
                self.log_test("Properties Filters", False, "Request failed")
                return False
                
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        filtered_count = len(data)
                        details += f", Filtered results: {filtered_count}"
                    else:
                        details += ", Response: Not a list"
                        success = False
                except:
                    details += ", Response: Non-JSON"
                    success = False
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Properties Filters", success, details)
            return success
        except Exception as e:
            self.log_test("Properties Filters", False, f"Exception: {str(e)}")
            return False

    def test_property_detail_endpoint(self):
        """Test GET /properties/{id} - Get property by ID"""
        try:
            if not self.sample_property_id:
                self.log_test("Property Detail", False, "No sample property ID available")
                return False
                
            response = self.make_request('GET', f'/properties/{self.sample_property_id}')
            if not response:
                self.log_test("Property Detail", False, "Request failed")
                return False
                
            success = response.status_code == 200
            details = f"Status: {response.status_code}, ID: {self.sample_property_id[:8]}..."
            
            if success:
                try:
                    data = response.json()
                    title = data.get('title', 'No title')
                    price = data.get('price', 0)
                    details += f", Title: {title[:30]}..., Price: {price}"
                except:
                    details += ", Response: Non-JSON"
                    success = False
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Property Detail", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Property Detail", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # 4. SERVICES ENDPOINTS (/api/services)
    # ============================================================================
    
    def test_services_list_endpoint(self):
        """Test GET /services - List services"""
        try:
            response = self.make_request('GET', '/services')
            if not response:
                self.log_test("Services List", False, "Request failed")
                return False
                
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        services_count = len(data)
                        details += f", Services found: {services_count}"
                        
                        # Store first service ID for detail testing
                        if services_count > 0 and data[0].get('id'):
                            self.sample_service_id = data[0]['id']
                            details += f", Sample ID: {self.sample_service_id[:8]}..."
                    else:
                        details += ", Response: Not a list"
                        success = False
                except:
                    details += ", Response: Non-JSON"
                    success = False
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Services List", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Services List", False, f"Exception: {str(e)}")
            return False

    def test_services_filters(self):
        """Test GET /services with filters"""
        try:
            # Test with category and location filters
            filter_params = {
                'category': 'plumbing',
                'location': 'Yaoundé',
                'limit': 5
            }
            
            response = self.make_request('GET', '/services', params=filter_params)
            if not response:
                self.log_test("Services Filters", False, "Request failed")
                return False
                
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        filtered_count = len(data)
                        details += f", Filtered results: {filtered_count}"
                    else:
                        details += ", Response: Not a list"
                        success = False
                except:
                    details += ", Response: Non-JSON"
                    success = False
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Services Filters", success, details)
            return success
        except Exception as e:
            self.log_test("Services Filters", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # 5. USERS ENDPOINTS (/api/users)
    # ============================================================================
    
    def test_users_get_by_id_endpoint(self):
        """Test GET /users/{id} - Get user by ID"""
        try:
            # Use a sample user ID (admin user)
            test_user_id = "admin-user-id"  # This might not exist, but we test the endpoint
            
            response = self.make_request('GET', f'/users/{test_user_id}')
            if not response:
                self.log_test("Users Get By ID", False, "Request failed")
                return False
                
            # Accept both 200 (user found) and 404 (user not found) as valid responses
            success = response.status_code in [200, 404]
            details = f"Status: {response.status_code}, ID: {test_user_id}"
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    name = data.get('name', 'No name')
                    email = data.get('email', 'No email')
                    details += f", Name: {name}, Email: {email}"
                except:
                    details += ", Response: Non-JSON"
            elif response.status_code == 404:
                details += " (user not found - expected for test ID)"
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Users Get By ID", success, details, response.json() if response.status_code == 200 else None)
            return success
        except Exception as e:
            self.log_test("Users Get By ID", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # 6. IMAGES ENDPOINTS (/api/images)
    # ============================================================================
    
    def test_images_endpoint(self):
        """Test image retrieval endpoints"""
        try:
            # Test getting images for a property
            entity_type = "property"
            entity_id = self.sample_property_id if self.sample_property_id else "sample-property-id"
            
            response = self.make_request('GET', f'/images/{entity_type}/{entity_id}')
            if not response:
                self.log_test("Images Retrieval", False, "Request failed")
                return False
                
            # Accept both 200 (images found) and 404 (no images) as valid responses
            success = response.status_code in [200, 404]
            details = f"Status: {response.status_code}, Entity: {entity_type}/{entity_id[:8]}..."
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        images_count = len(data)
                        details += f", Images found: {images_count}"
                    else:
                        details += ", Response: Not a list"
                except:
                    details += ", Response: Non-JSON"
            elif response.status_code == 404:
                details += " (no images found - acceptable)"
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Images Retrieval", success, details, response.json() if response.status_code == 200 else None)
            return success
        except Exception as e:
            self.log_test("Images Retrieval", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # 7. REVIEWS ENDPOINTS (/api/reviews)
    # ============================================================================
    
    def test_reviews_list_endpoint(self):
        """Test GET /reviews - List reviews"""
        try:
            response = self.make_request('GET', '/reviews')
            if not response:
                self.log_test("Reviews List", False, "Request failed")
                return False
                
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        reviews_count = len(data)
                        details += f", Reviews found: {reviews_count}"
                    else:
                        details += ", Response: Not a list"
                        success = False
                except:
                    details += ", Response: Non-JSON"
                    success = False
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Reviews List", success, details, response.json() if success else None)
            return success
        except Exception as e:
            self.log_test("Reviews List", False, f"Exception: {str(e)}")
            return False

    def test_reviews_filters(self):
        """Test GET /reviews with filters"""
        try:
            # Test with property filter
            filter_params = {
                'property_id': self.sample_property_id if self.sample_property_id else 'sample-property-id',
                'limit': 10
            }
            
            response = self.make_request('GET', '/reviews', params=filter_params)
            if not response:
                self.log_test("Reviews Filters", False, "Request failed")
                return False
                
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        filtered_count = len(data)
                        details += f", Filtered reviews: {filtered_count}"
                    else:
                        details += ", Response: Not a list"
                        success = False
                except:
                    details += ", Response: Non-JSON"
                    success = False
            else:
                details += f", Error: {response.text[:100]}"
                
            self.log_test("Reviews Filters", success, details)
            return success
        except Exception as e:
            self.log_test("Reviews Filters", False, f"Exception: {str(e)}")
            return False

    # ============================================================================
    # MAIN TEST RUNNER
    # ============================================================================
    
    def run_all_tests(self):
        """Run all refactored backend API tests"""
        print("🚀 REFACTORED BACKEND API TESTING")
        print("=" * 60)
        print(f"Testing API at: {self.api_url}")
        print("Focus: Testing all refactored backend API endpoints after modular architecture refactoring")
        print("-" * 60)
        
        # 1. Core Endpoints
        print("\n1️⃣ CORE ENDPOINTS (/api/)")
        print("-" * 30)
        self.test_api_root_endpoint()
        self.test_api_health_endpoint()
        
        # 2. Authentication Endpoints
        print("\n2️⃣ AUTHENTICATION ENDPOINTS (/api/auth/)")
        print("-" * 40)
        self.test_auth_register_endpoint()
        self.test_auth_login_endpoint()
        self.test_auth_me_endpoint()
        
        # 3. Properties Endpoints
        print("\n3️⃣ PROPERTIES ENDPOINTS (/api/properties)")
        print("-" * 40)
        self.test_properties_list_endpoint()
        self.test_properties_filters()
        self.test_property_detail_endpoint()
        
        # 4. Services Endpoints
        print("\n4️⃣ SERVICES ENDPOINTS (/api/services)")
        print("-" * 35)
        self.test_services_list_endpoint()
        self.test_services_filters()
        
        # 5. Users Endpoints
        print("\n5️⃣ USERS ENDPOINTS (/api/users)")
        print("-" * 30)
        self.test_users_get_by_id_endpoint()
        
        # 6. Images Endpoints
        print("\n6️⃣ IMAGES ENDPOINTS (/api/images)")
        print("-" * 32)
        self.test_images_endpoint()
        
        # 7. Reviews Endpoints
        print("\n7️⃣ REVIEWS ENDPOINTS (/api/reviews)")
        print("-" * 33)
        self.test_reviews_list_endpoint()
        self.test_reviews_filters()
        
        # Print final summary
        self.print_final_summary()
        
        return self.tests_passed == self.tests_run

    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 REFACTORED BACKEND API TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Overall Results: {self.tests_passed}/{self.tests_run} tests passed ({success_rate:.1f}%)")
        
        # Group results by endpoint category
        categories = {
            "Core": ["API Root Endpoint", "API Health Check"],
            "Authentication": ["Auth Register", "Auth Login", "Auth Me"],
            "Properties": ["Properties List", "Properties Filters", "Property Detail"],
            "Services": ["Services List", "Services Filters"],
            "Users": ["Users Get By ID"],
            "Images": ["Images Retrieval"],
            "Reviews": ["Reviews List", "Reviews Filters"]
        }
        
        print(f"\n📊 Results by Category:")
        for category, test_names in categories.items():
            category_tests = [r for r in self.test_results if r['test_name'] in test_names]
            passed = sum(1 for t in category_tests if t['success'])
            total = len(category_tests)
            if total > 0:
                rate = (passed / total * 100)
                status = "✅" if rate == 100 else "⚠️" if rate >= 50 else "❌"
                print(f"   {status} {category}: {passed}/{total} ({rate:.0f}%)")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
        
        # Show critical issues
        critical_failures = [r for r in self.test_results if not r['success'] and 
                           any(keyword in r['test_name'].lower() for keyword in ['health', 'root', 'properties list', 'services list'])]
        
        if critical_failures:
            print(f"\n🚨 Critical Issues:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test_name']}: {failure['details']}")
        
        # Configuration info
        print(f"\n⚙️ Configuration:")
        print(f"   • Backend URL: {self.base_url}")
        print(f"   • API Base: {self.api_url}")
        print(f"   • Sample Property ID: {self.sample_property_id[:8] + '...' if self.sample_property_id else 'None'}")
        print(f"   • Sample Service ID: {self.sample_service_id[:8] + '...' if self.sample_service_id else 'None'}")
        
        return success_rate

def main():
    """Main function to run the refactored backend tests"""
    print("Starting Refactored Backend API Testing...")
    
    tester = RefactoredBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 All tests passed! Backend refactoring appears successful.")
        sys.exit(0)
    else:
        print(f"\n⚠️ Some tests failed. Please review the results above.")
        sys.exit(1)

if __name__ == "__main__":
    main()