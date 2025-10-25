#!/usr/bin/env python3
"""
Edge Case Validation Testing Script
==================================

Tests edge cases and boundary conditions for property validation.
"""

import requests
import json

# Backend URL from environment
BACKEND_URL = "https://realestate-cam.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "admin@habitere.com"
ADMIN_PASSWORD = "admin123"

class EdgeCaseTester:
    def __init__(self):
        self.session = requests.Session()
        
    def authenticate(self) -> bool:
        """Authenticate with admin credentials"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            return response.status_code == 200
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_edge_case(self, test_name: str, property_data: dict, expected_status: int) -> bool:
        """Test property creation with edge case data"""
        try:
            response = self.session.post(f"{BACKEND_URL}/properties", json=property_data)
            
            print(f"\n--- {test_name} ---")
            print(f"Status Code: {response.status_code} (Expected: {expected_status})")
            
            if response.status_code == expected_status:
                if expected_status == 422:
                    error_data = response.json()
                    if "detail" in error_data:
                        print("✅ Validation errors (as expected):")
                        for error in error_data["detail"]:
                            field = error.get("loc", ["unknown"])[-1]
                            message = error.get("msg", "Unknown error")
                            print(f"   - {field}: {message}")
                elif expected_status == 200:
                    result = response.json()
                    print(f"✅ Property created successfully: {result.get('id', 'Unknown ID')}")
                return True
            else:
                print(f"❌ Unexpected status code. Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False
    
    def run_edge_case_tests(self):
        """Run edge case validation tests"""
        print("🔍 EDGE CASE VALIDATION TESTING")
        print("=" * 50)
        
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return False
        
        test_results = []
        
        # Edge Case 1: Exact boundary values - minimum valid
        test_results.append(self.test_edge_case(
            "Edge Case 1 - Minimum Valid Values",
            {
                "title": "12345",  # Exactly 5 characters
                "description": "A" * 50,  # Exactly 50 characters
                "price": 0.01,  # Minimum positive price
                "location": "ABC",  # Exactly 3 characters
                "listing_type": "sale",
                "bedrooms": 0,  # Minimum bedrooms
                "bathrooms": 0,  # Minimum bathrooms
                "area_sqm": 0.01  # Minimum positive area
            },
            200
        ))
        
        # Edge Case 2: Exact boundary values - maximum valid
        test_results.append(self.test_edge_case(
            "Edge Case 2 - Maximum Valid Values",
            {
                "title": "A" * 200,  # Exactly 200 characters
                "description": "B" * 2000,  # Exactly 2000 characters
                "price": 999999999.99,  # Large price
                "location": "C" * 200,  # Exactly 200 characters
                "listing_type": "sale",
                "bedrooms": 50,  # Maximum bedrooms
                "bathrooms": 50,  # Maximum bathrooms
                "area_sqm": 999999.99  # Large area
            },
            200
        ))
        
        # Edge Case 3: Just over the limit - should fail
        test_results.append(self.test_edge_case(
            "Edge Case 3 - Just Over Title Limit",
            {
                "title": "A" * 201,  # 201 characters - just over limit
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale"
            },
            422
        ))
        
        # Edge Case 4: Just under the limit - should fail
        test_results.append(self.test_edge_case(
            "Edge Case 4 - Just Under Title Limit",
            {
                "title": "ABCD",  # 4 characters - just under limit
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale"
            },
            422
        ))
        
        # Edge Case 5: Decimal values for integers
        test_results.append(self.test_edge_case(
            "Edge Case 5 - Decimal Bedrooms",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale",
                "bedrooms": 3.5  # Decimal value for integer field
            },
            422
        ))
        
        # Edge Case 6: Very small positive values
        test_results.append(self.test_edge_case(
            "Edge Case 6 - Very Small Positive Values",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 0.000001,  # Very small positive price
                "location": "Douala",
                "listing_type": "sale",
                "area_sqm": 0.000001  # Very small positive area
            },
            200
        ))
        
        # Edge Case 7: Missing required fields
        test_results.append(self.test_edge_case(
            "Edge Case 7 - Missing Required Fields",
            {
                "title": "Valid Property Title",
                # Missing description
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale"
            },
            422
        ))
        
        # Edge Case 8: Empty strings
        test_results.append(self.test_edge_case(
            "Edge Case 8 - Empty Title",
            {
                "title": "",  # Empty string
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale"
            },
            422
        ))
        
        # Edge Case 9: Unicode characters
        test_results.append(self.test_edge_case(
            "Edge Case 9 - Unicode Characters",
            {
                "title": "Propriété Moderne à Yaoundé 🏠",  # Unicode characters
                "description": "Une belle propriété avec des caractères spéciaux et des émojis 🏡. Cette description contient plus de cinquante caractères pour respecter les exigences de validation.",
                "price": 100000,
                "location": "Yaoundé, Cameroun 🇨🇲",
                "listing_type": "sale"
            },
            200
        ))
        
        # Edge Case 10: Null values for optional fields
        test_results.append(self.test_edge_case(
            "Edge Case 10 - Null Optional Fields",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale",
                "bedrooms": None,  # Null optional field
                "bathrooms": None,  # Null optional field
                "area_sqm": None   # Null optional field
            },
            200
        ))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 EDGE CASE TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(test_results)
        total = len(test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL EDGE CASE TESTS PASSED!")
            print("✅ Validation is robust and handles edge cases correctly")
        else:
            print(f"\n⚠️  {total - passed} EDGE CASE TESTS FAILED")
            print("❌ Some edge cases may not be handled correctly")
        
        return passed == total

def main():
    """Main test execution"""
    tester = EdgeCaseTester()
    success = tester.run_edge_case_tests()
    
    if success:
        print("\n🚀 EDGE CASE VALIDATION: SUCCESSFUL")
    else:
        print("\n💥 EDGE CASE VALIDATION: SOME ISSUES FOUND")

if __name__ == "__main__":
    main()