#!/usr/bin/env python3
"""
Property Validation Testing Script
=================================

Tests the newly added validation constraints for property posting to ensure they're working correctly.

Test Scenarios:
1. Title Validation (5-200 characters)
2. Description Validation (50-2000 characters) 
3. Price Validation (must be positive)
4. Bedrooms/Bathrooms Validation (0-50)
5. Area Validation (must be positive)
6. Location Validation (3-200 characters)

Expected Results:
- Invalid data should return 422 status code with validation errors
- Valid data should return 201 status code with created property
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URL from environment
BACKEND_URL = "https://proptech-assets.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "admin@habitere.com"
ADMIN_PASSWORD = "admin123"

class ValidationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def authenticate(self) -> bool:
        """Authenticate with admin credentials"""
        try:
            # Login
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            print(f"Login response: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_property_creation(self, test_name: str, property_data: Dict[str, Any], expected_status: int) -> bool:
        """Test property creation with given data"""
        try:
            response = self.session.post(f"{BACKEND_URL}/properties", json=property_data)
            
            print(f"\n--- {test_name} ---")
            print(f"Status Code: {response.status_code} (Expected: {expected_status})")
            
            if response.status_code == expected_status:
                if expected_status == 422:
                    # Parse validation errors
                    error_data = response.json()
                    if "detail" in error_data:
                        print("✅ Validation errors (as expected):")
                        for error in error_data["detail"]:
                            field = error.get("loc", ["unknown"])[-1]
                            message = error.get("msg", "Unknown error")
                            print(f"   - {field}: {message}")
                    else:
                        print("✅ Validation failed (as expected)")
                elif expected_status in [200, 201]:
                    result = response.json()
                    print(f"✅ Property created successfully: {result.get('id', 'Unknown ID')}")
                return True
            else:
                print(f"❌ Unexpected status code. Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False
    
    def run_validation_tests(self):
        """Run all validation test scenarios"""
        print("🔍 PROPERTY VALIDATION TESTING")
        print("=" * 50)
        
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return False
        
        test_results = []
        
        # Test 1A: Title too short (< 5 chars)
        test_results.append(self.test_property_creation(
            "Test 1A - Title Too Short",
            {
                "title": "Test",  # Only 4 characters
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale"
            },
            422
        ))
        
        # Test 1B: Title too long (> 200 chars)
        long_title = "A" * 201  # 201 characters
        test_results.append(self.test_property_creation(
            "Test 1B - Title Too Long",
            {
                "title": long_title,
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale"
            },
            422
        ))
        
        # Test 1C: Valid title length
        test_results.append(self.test_property_creation(
            "Test 1C - Valid Title Length",
            {
                "title": "Beautiful Modern Apartment",  # Valid length
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale"
            },
            200
        ))
        
        # Test 2A: Description too short (< 50 chars)
        test_results.append(self.test_property_creation(
            "Test 2A - Description Too Short",
            {
                "title": "Valid Property Title",
                "description": "Too short description",  # Only ~20 characters
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale"
            },
            422
        ))
        
        # Test 2B: Description too long (> 2000 chars)
        long_description = "A" * 2001  # 2001 characters
        test_results.append(self.test_property_creation(
            "Test 2B - Description Too Long",
            {
                "title": "Valid Property Title",
                "description": long_description,
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale"
            },
            422
        ))
        
        # Test 2C: Valid description length
        test_results.append(self.test_property_creation(
            "Test 2C - Valid Description Length",
            {
                "title": "Valid Property Title",
                "description": "This is a perfectly valid description that meets all the requirements for length validation. It contains more than fifty characters but less than two thousand characters, making it acceptable for property creation in our system.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale"
            },
            201
        ))
        
        # Test 3A: Negative price
        test_results.append(self.test_property_creation(
            "Test 3A - Negative Price",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": -100000,  # Negative price
                "location": "Douala",
                "listing_type": "sale"
            },
            422
        ))
        
        # Test 3B: Zero price
        test_results.append(self.test_property_creation(
            "Test 3B - Zero Price",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 0,  # Zero price
                "location": "Douala",
                "listing_type": "sale"
            },
            422
        ))
        
        # Test 3C: Valid positive price
        test_results.append(self.test_property_creation(
            "Test 3C - Valid Positive Price",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 150000,  # Valid positive price
                "location": "Douala",
                "listing_type": "sale"
            },
            201
        ))
        
        # Test 4A: Negative bedrooms
        test_results.append(self.test_property_creation(
            "Test 4A - Negative Bedrooms",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale",
                "bedrooms": -1  # Negative bedrooms
            },
            422
        ))
        
        # Test 4B: Bedrooms > 50
        test_results.append(self.test_property_creation(
            "Test 4B - Bedrooms Too High",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale",
                "bedrooms": 51  # More than 50 bedrooms
            },
            422
        ))
        
        # Test 4C: Valid bedrooms (0-50)
        test_results.append(self.test_property_creation(
            "Test 4C - Valid Bedrooms",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale",
                "bedrooms": 3  # Valid bedrooms
            },
            201
        ))
        
        # Test 4D: Negative bathrooms
        test_results.append(self.test_property_creation(
            "Test 4D - Negative Bathrooms",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale",
                "bathrooms": -1  # Negative bathrooms
            },
            422
        ))
        
        # Test 4E: Bathrooms > 50
        test_results.append(self.test_property_creation(
            "Test 4E - Bathrooms Too High",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale",
                "bathrooms": 51  # More than 50 bathrooms
            },
            422
        ))
        
        # Test 5A: Negative area
        test_results.append(self.test_property_creation(
            "Test 5A - Negative Area",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale",
                "area_sqm": -50  # Negative area
            },
            422
        ))
        
        # Test 5B: Zero area
        test_results.append(self.test_property_creation(
            "Test 5B - Zero Area",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale",
                "area_sqm": 0  # Zero area
            },
            422
        ))
        
        # Test 5C: Valid positive area
        test_results.append(self.test_property_creation(
            "Test 5C - Valid Positive Area",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "Douala",
                "listing_type": "sale",
                "area_sqm": 120  # Valid positive area
            },
            201
        ))
        
        # Test 6A: Location too short (< 3 chars)
        test_results.append(self.test_property_creation(
            "Test 6A - Location Too Short",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": "AB",  # Only 2 characters
                "listing_type": "sale"
            },
            422
        ))
        
        # Test 6B: Location too long (> 200 chars)
        long_location = "A" * 201  # 201 characters
        test_results.append(self.test_property_creation(
            "Test 6B - Location Too Long",
            {
                "title": "Valid Property Title",
                "description": "This is a valid description with more than fifty characters to meet the minimum requirement for testing validation constraints properly.",
                "price": 100000,
                "location": long_location,
                "listing_type": "sale"
            },
            422
        ))
        
        # Test ALL VALID - Complete valid property
        test_results.append(self.test_property_creation(
            "Test ALL VALID - Complete Valid Property",
            {
                "title": "Beautiful Apartment in Douala",
                "description": "Spacious 3-bedroom apartment with modern amenities, located in the heart of Douala. Perfect for families looking for comfort and convenience.",
                "price": 500000,
                "location": "Douala, Cameroon",
                "listing_type": "sale",
                "bedrooms": 3,
                "bathrooms": 2,
                "area_sqm": 120
            },
            201
        ))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(test_results)
        total = len(test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL VALIDATION TESTS PASSED!")
            print("✅ All validation constraints are working correctly")
        else:
            print(f"\n⚠️  {total - passed} TESTS FAILED")
            print("❌ Some validation constraints may not be working as expected")
        
        return passed == total

def main():
    """Main test execution"""
    tester = ValidationTester()
    success = tester.run_validation_tests()
    
    if success:
        print("\n🚀 VALIDATION FIX VERIFICATION: SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n💥 VALIDATION FIX VERIFICATION: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()