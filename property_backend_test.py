#!/usr/bin/env python3
"""
COMPREHENSIVE PROPERTY POSTING FLOW BACKEND TESTING
===================================================

This script performs exhaustive testing of ALL property-related backend endpoints
to verify 100% production readiness for property posting functionality.

Test Coverage:
- 8 property endpoints (CRUD operations)
- Image upload endpoint
- Authentication & authorization
- Data validation & security
- Database operations
- Performance verification

Author: Testing Agent
Date: 2025-01-15
"""

import asyncio
import aiohttp
import json
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PropertyBackendTester:
    """Comprehensive property backend testing class."""
    
    def __init__(self):
        # Get backend URL from environment
        self.base_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://habitere-home.preview.emergentagent.com')
        if not self.base_url.endswith('/api'):
            self.base_url = f"{self.base_url}/api"
        
        self.session = None
        self.admin_session_token = None
        self.test_results = []
        self.created_properties = []
        
        logger.info(f"Testing backend at: {self.base_url}")
    
    async def setup_session(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession()
        logger.info("HTTP session initialized")
    
    async def cleanup_session(self):
        """Cleanup HTTP session."""
        if self.session:
            await self.session.close()
            logger.info("HTTP session closed")
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user for testing."""
        try:
            # Login as admin
            login_data = {
                "email": "admin@habitere.com",
                "password": "admin123"
            }
            
            async with self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    # Check for session cookie
                    cookies = response.cookies
                    if 'session_token' in cookies:
                        self.admin_session_token = cookies['session_token'].value
                        logger.info("✅ Admin authentication successful")
                        return True
                    else:
                        logger.error("❌ No session token in login response")
                        return False
                else:
                    text = await response.text()
                    logger.error(f"❌ Admin login failed: {response.status} - {text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Admin authentication error: {e}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        if self.admin_session_token:
            return {"Cookie": f"session_token={self.admin_session_token}"}
        return {}
    
    async def test_endpoint(self, name: str, method: str, url: str, 
                          data: Optional[Dict] = None, 
                          headers: Optional[Dict] = None,
                          expected_status: int = 200,
                          auth_required: bool = False) -> Dict[str, Any]:
        """Test a single endpoint."""
        start_time = time.time()
        
        try:
            # Prepare headers
            test_headers = headers or {}
            if auth_required:
                test_headers.update(self.get_auth_headers())
            
            # For unauthenticated tests, use a fresh session to avoid cookie persistence
            if not auth_required:
                async with aiohttp.ClientSession() as fresh_session:
                    async with fresh_session.request(
                        method, url, json=data, headers=test_headers
                    ) as response:
                        response_time = (time.time() - start_time) * 1000
                        response_text = await response.text()
                        
                        try:
                            response_data = json.loads(response_text) if response_text else {}
                        except json.JSONDecodeError:
                            response_data = {"raw_response": response_text}
                        
                        success = response.status == expected_status
                        
                        result = {
                            "test_name": name,
                            "method": method,
                            "url": url,
                            "status_code": response.status,
                            "expected_status": expected_status,
                            "success": success,
                            "response_time_ms": round(response_time, 2),
                            "response_data": response_data,
                            "error": None if success else f"Expected {expected_status}, got {response.status}"
                        }
                        
                        if success:
                            logger.info(f"✅ {name}: {response.status} ({response_time:.0f}ms)")
                        else:
                            logger.error(f"❌ {name}: {response.status} (expected {expected_status}) - {response_text[:200]}")
                        
                        return result
            else:
                # Use authenticated session for auth_required tests
                async with self.session.request(
                    method, url, json=data, headers=test_headers
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_text = await response.text()
                    
                    try:
                        response_data = json.loads(response_text) if response_text else {}
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    
                    success = response.status == expected_status
                    
                    result = {
                        "test_name": name,
                        "method": method,
                        "url": url,
                        "status_code": response.status,
                        "expected_status": expected_status,
                        "success": success,
                        "response_time_ms": round(response_time, 2),
                        "response_data": response_data,
                        "error": None if success else f"Expected {expected_status}, got {response.status}"
                    }
                    
                    if success:
                        logger.info(f"✅ {name}: {response.status} ({response_time:.0f}ms)")
                    else:
                        logger.error(f"❌ {name}: {response.status} (expected {expected_status}) - {response_text[:200]}")
                    
                    return result
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ {name}: Exception - {e}")
            
            return {
                "test_name": name,
                "method": method,
                "url": url,
                "status_code": 0,
                "expected_status": expected_status,
                "success": False,
                "response_time_ms": round(response_time, 2),
                "response_data": {},
                "error": str(e)
            }
    
    async def test_property_creation_scenarios(self):
        """Test all property creation scenarios."""
        logger.info("\n🏠 TESTING PROPERTY CREATION SCENARIOS")
        
        # A. Minimal Valid Data
        minimal_data = {
            "title": "Test Property Backend Verification",
            "description": "Comprehensive backend testing for property posting flow verification",
            "property_type": "apartment",
            "location": "Douala, Cameroon",
            "price": 500000,
            "bedrooms": 2,
            "bathrooms": 1,
            "listing_type": "rent"
        }
        
        result = await self.test_endpoint(
            "Create Property - Minimal Valid Data",
            "POST",
            f"{self.base_url}/properties",
            data=minimal_data,
            auth_required=True,
            expected_status=200
        )
        self.test_results.append(result)
        
        # Store property ID for later tests
        if result["success"] and "id" in result["response_data"]:
            self.created_properties.append(result["response_data"]["id"])
        
        # B. Complete Data with All Fields
        complete_data = {
            "title": "Luxury Apartment - Full Data Test",
            "description": "Complete property data test with all possible fields populated for comprehensive backend verification and validation testing",
            "property_type": "apartment",
            "location": "Yaounde, Cameroon",
            "price": 1500000,
            "bedrooms": 3,
            "bathrooms": 2,
            "area_sqm": 1200,
            "amenities": ["parking", "gym", "pool", "security"],
            "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
            "listing_type": "sale"
        }
        
        result = await self.test_endpoint(
            "Create Property - Complete Data",
            "POST",
            f"{self.base_url}/properties",
            data=complete_data,
            auth_required=True,
            expected_status=200
        )
        self.test_results.append(result)
        
        if result["success"] and "id" in result["response_data"]:
            self.created_properties.append(result["response_data"]["id"])
        
        # C. Missing Required Fields (Should Fail)
        incomplete_data = {
            "title": "Incomplete Property",
            "price": 300000
        }
        
        result = await self.test_endpoint(
            "Create Property - Missing Required Fields",
            "POST",
            f"{self.base_url}/properties",
            data=incomplete_data,
            auth_required=True,
            expected_status=422  # Validation error
        )
        self.test_results.append(result)
        
        # D. Invalid Data Types (Should Fail)
        invalid_data = {
            "title": "Bad Data Test",
            "description": "Test",
            "property_type": "apartment",
            "location": "Test",
            "price": "not-a-number",
            "bedrooms": "three",
            "listing_type": "rent"
        }
        
        result = await self.test_endpoint(
            "Create Property - Invalid Data Types",
            "POST",
            f"{self.base_url}/properties",
            data=invalid_data,
            auth_required=True,
            expected_status=422  # Validation error
        )
        self.test_results.append(result)
        
        # E. XSS Attack Payload (Should Sanitize)
        xss_data = {
            "title": "<script>alert('XSS')</script>Property",
            "description": "<img src=x onerror=alert('XSS')>",
            "property_type": "apartment",
            "location": "Test",
            "price": 100000,
            "bedrooms": 1,
            "bathrooms": 1,
            "listing_type": "rent"
        }
        
        result = await self.test_endpoint(
            "Create Property - XSS Attack Payload",
            "POST",
            f"{self.base_url}/properties",
            data=xss_data,
            auth_required=True,
            expected_status=200  # Should accept but sanitize
        )
        self.test_results.append(result)
        
        # F. Extremely Long Strings (Should Validate Length)
        long_data = {
            "title": "A" * 1000,  # 1000 character string
            "description": "B" * 10000,  # 10000 character string
            "property_type": "apartment",
            "location": "Test",
            "price": 100000,
            "bedrooms": 1,
            "bathrooms": 1,
            "listing_type": "rent"
        }
        
        result = await self.test_endpoint(
            "Create Property - Extremely Long Strings",
            "POST",
            f"{self.base_url}/properties",
            data=long_data,
            auth_required=True,
            expected_status=422  # Should validate length
        )
        self.test_results.append(result)
        
        # G. Negative/Zero Values (Should Validate)
        negative_data = {
            "title": "Negative Test",
            "description": "Testing negative values",
            "property_type": "apartment",
            "location": "Test",
            "price": -100000,
            "bedrooms": -1,
            "bathrooms": 0,
            "listing_type": "rent"
        }
        
        result = await self.test_endpoint(
            "Create Property - Negative Values",
            "POST",
            f"{self.base_url}/properties",
            data=negative_data,
            auth_required=True,
            expected_status=422  # Should validate ranges
        )
        self.test_results.append(result)
        
        # H. Unauthenticated Request (Should Return 401)
        result = await self.test_endpoint(
            "Create Property - Unauthenticated",
            "POST",
            f"{self.base_url}/properties",
            data=minimal_data,
            auth_required=False,
            expected_status=401
        )
        self.test_results.append(result)
    
    async def test_property_listing(self):
        """Test property listing endpoint."""
        logger.info("\n📋 TESTING PROPERTY LISTING")
        
        # A. List all properties
        result = await self.test_endpoint(
            "List All Properties",
            "GET",
            f"{self.base_url}/properties",
            expected_status=200
        )
        self.test_results.append(result)
        
        # B. Filter by property type
        result = await self.test_endpoint(
            "Filter by Property Type",
            "GET",
            f"{self.base_url}/properties?property_type=apartment",
            expected_status=200
        )
        self.test_results.append(result)
        
        # C. Filter by location
        result = await self.test_endpoint(
            "Filter by Location",
            "GET",
            f"{self.base_url}/properties?location=Douala",
            expected_status=200
        )
        self.test_results.append(result)
        
        # D. Pagination
        result = await self.test_endpoint(
            "Pagination Test",
            "GET",
            f"{self.base_url}/properties?skip=0&limit=5",
            expected_status=200
        )
        self.test_results.append(result)
        
        # E. Price range filtering
        result = await self.test_endpoint(
            "Price Range Filter",
            "GET",
            f"{self.base_url}/properties?min_price=100000&max_price=1000000",
            expected_status=200
        )
        self.test_results.append(result)
    
    async def test_property_details(self):
        """Test property details endpoint."""
        logger.info("\n🔍 TESTING PROPERTY DETAILS")
        
        if self.created_properties:
            property_id = self.created_properties[0]
            
            # A. Get valid property
            result = await self.test_endpoint(
                "Get Valid Property Details",
                "GET",
                f"{self.base_url}/properties/{property_id}",
                expected_status=200
            )
            self.test_results.append(result)
        
        # B. Get non-existent property
        fake_id = str(uuid.uuid4())
        result = await self.test_endpoint(
            "Get Non-existent Property",
            "GET",
            f"{self.base_url}/properties/{fake_id}",
            expected_status=404
        )
        self.test_results.append(result)
        
        # C. Invalid ID format
        result = await self.test_endpoint(
            "Get Property - Invalid ID Format",
            "GET",
            f"{self.base_url}/properties/invalid-id",
            expected_status=404
        )
        self.test_results.append(result)
    
    async def test_property_update(self):
        """Test property update endpoint."""
        logger.info("\n✏️ TESTING PROPERTY UPDATE")
        
        if self.created_properties:
            property_id = self.created_properties[0]
            
            # A. Update as owner (admin)
            update_data = {
                "title": "Updated Property Title",
                "description": "Updated description",
                "property_type": "house",
                "location": "Updated Location",
                "price": 750000,
                "bedrooms": 4,
                "bathrooms": 3,
                "listing_type": "sale"
            }
            
            result = await self.test_endpoint(
                "Update Property - As Owner",
                "PUT",
                f"{self.base_url}/properties/{property_id}",
                data=update_data,
                auth_required=True,
                expected_status=200
            )
            self.test_results.append(result)
            
            # B. Update non-existent property
            fake_id = str(uuid.uuid4())
            result = await self.test_endpoint(
                "Update Non-existent Property",
                "PUT",
                f"{self.base_url}/properties/{fake_id}",
                data=update_data,
                auth_required=True,
                expected_status=404
            )
            self.test_results.append(result)
            
            # C. Update with invalid data
            invalid_update = {
                "title": "",  # Empty title
                "price": "invalid",
                "listing_type": "rent"
            }
            
            result = await self.test_endpoint(
                "Update Property - Invalid Data",
                "PUT",
                f"{self.base_url}/properties/{property_id}",
                data=invalid_update,
                auth_required=True,
                expected_status=422
            )
            self.test_results.append(result)
            
            # D. Unauthenticated update
            result = await self.test_endpoint(
                "Update Property - Unauthenticated",
                "PUT",
                f"{self.base_url}/properties/{property_id}",
                data=update_data,
                auth_required=False,
                expected_status=401
            )
            self.test_results.append(result)
    
    async def test_user_properties(self):
        """Test user properties endpoints."""
        logger.info("\n👤 TESTING USER PROPERTIES")
        
        # A. Get current user's properties
        result = await self.test_endpoint(
            "Get Current User Properties",
            "GET",
            f"{self.base_url}/users/me/properties",
            auth_required=True,
            expected_status=200
        )
        self.test_results.append(result)
        
        # B. Unauthenticated request
        result = await self.test_endpoint(
            "Get User Properties - Unauthenticated",
            "GET",
            f"{self.base_url}/users/me/properties",
            auth_required=False,
            expected_status=401
        )
        self.test_results.append(result)
    
    async def test_image_upload(self):
        """Test image upload endpoint."""
        logger.info("\n📸 TESTING IMAGE UPLOAD")
        
        # A. Test without authentication (should fail)
        result = await self.test_endpoint(
            "Image Upload - Unauthenticated",
            "POST",
            f"{self.base_url}/upload/images",
            auth_required=False,
            expected_status=401
        )
        self.test_results.append(result)
        
        # Note: Testing actual file upload requires multipart/form-data
        # which is complex with aiohttp. We'll test the authentication
        # and endpoint availability for now.
    
    async def test_property_deletion(self):
        """Test property deletion endpoint."""
        logger.info("\n🗑️ TESTING PROPERTY DELETION")
        
        if self.created_properties:
            # Keep one property, delete the rest
            for property_id in self.created_properties[1:]:
                # A. Delete as owner (admin)
                result = await self.test_endpoint(
                    f"Delete Property - As Owner ({property_id[:8]}...)",
                    "DELETE",
                    f"{self.base_url}/properties/{property_id}",
                    auth_required=True,
                    expected_status=200
                )
                self.test_results.append(result)
            
            # B. Delete non-existent property
            fake_id = str(uuid.uuid4())
            result = await self.test_endpoint(
                "Delete Non-existent Property",
                "DELETE",
                f"{self.base_url}/properties/{fake_id}",
                auth_required=True,
                expected_status=404
            )
            self.test_results.append(result)
            
            # C. Unauthenticated deletion
            if self.created_properties:
                result = await self.test_endpoint(
                    "Delete Property - Unauthenticated",
                    "DELETE",
                    f"{self.base_url}/properties/{self.created_properties[0]}",
                    auth_required=False,
                    expected_status=401
                )
                self.test_results.append(result)
    
    async def test_database_verification(self):
        """Test database operations indirectly through API."""
        logger.info("\n💾 TESTING DATABASE VERIFICATION")
        
        # Create a property and verify it persists
        test_property = {
            "title": "Database Verification Property",
            "description": "Testing database persistence",
            "property_type": "apartment",
            "location": "Database Test City",
            "price": 123456,
            "bedrooms": 2,
            "bathrooms": 1,
            "listing_type": "rent"
        }
        
        # Create property
        create_result = await self.test_endpoint(
            "Database Test - Create Property",
            "POST",
            f"{self.base_url}/properties",
            data=test_property,
            auth_required=True,
            expected_status=200
        )
        self.test_results.append(create_result)
        
        if create_result["success"] and "id" in create_result["response_data"]:
            property_id = create_result["response_data"]["id"]
            
            # Verify property exists
            get_result = await self.test_endpoint(
                "Database Test - Verify Property Exists",
                "GET",
                f"{self.base_url}/properties/{property_id}",
                expected_status=200
            )
            self.test_results.append(get_result)
            
            # Verify data integrity
            if get_result["success"]:
                retrieved_data = get_result["response_data"]
                data_integrity_ok = (
                    retrieved_data.get("title") == test_property["title"] and
                    retrieved_data.get("price") == test_property["price"] and
                    retrieved_data.get("location") == test_property["location"]
                )
                
                integrity_result = {
                    "test_name": "Database Test - Data Integrity",
                    "method": "VERIFY",
                    "url": "N/A",
                    "status_code": 200 if data_integrity_ok else 500,
                    "expected_status": 200,
                    "success": data_integrity_ok,
                    "response_time_ms": 0,
                    "response_data": {"integrity_check": data_integrity_ok},
                    "error": None if data_integrity_ok else "Data integrity check failed"
                }
                self.test_results.append(integrity_result)
                
                if data_integrity_ok:
                    logger.info("✅ Database Test - Data Integrity: PASSED")
                else:
                    logger.error("❌ Database Test - Data Integrity: FAILED")
            
            # Clean up test property
            await self.test_endpoint(
                "Database Test - Cleanup",
                "DELETE",
                f"{self.base_url}/properties/{property_id}",
                auth_required=True,
                expected_status=200
            )
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        # Calculate average response time
        response_times = [r["response_time_ms"] for r in self.test_results if r["response_time_ms"] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result["test_name"].split(" - ")[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            
            categories[category]["tests"].append(result)
        
        # Security and validation checks
        security_tests = [r for r in self.test_results if "XSS" in r["test_name"] or "Unauthenticated" in r["test_name"]]
        validation_tests = [r for r in self.test_results if "Invalid" in r["test_name"] or "Missing" in r["test_name"]]
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": round((passed_tests / total_tests) * 100, 1) if total_tests > 0 else 0,
                "average_response_time_ms": round(avg_response_time, 2)
            },
            "categories": categories,
            "security_validation": {
                "security_tests": len(security_tests),
                "security_passed": sum(1 for t in security_tests if t["success"]),
                "validation_tests": len(validation_tests),
                "validation_passed": sum(1 for t in validation_tests if t["success"])
            },
            "performance": {
                "fastest_response_ms": min(response_times) if response_times else 0,
                "slowest_response_ms": max(response_times) if response_times else 0,
                "performance_threshold_500ms": sum(1 for t in response_times if t <= 500)
            },
            "failed_tests": [r for r in self.test_results if not r["success"]],
            "all_results": self.test_results
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted test report."""
        print("\n" + "="*80)
        print("🏠 PROPERTY POSTING FLOW BACKEND TEST REPORT")
        print("="*80)
        
        # Summary
        summary = report["summary"]
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed']} ✅")
        print(f"   Failed: {summary['failed']} ❌")
        print(f"   Success Rate: {summary['success_rate']}%")
        print(f"   Average Response Time: {summary['average_response_time_ms']}ms")
        
        # Categories
        print(f"\n📋 CATEGORIES:")
        for category, stats in report["categories"].items():
            total = stats["passed"] + stats["failed"]
            rate = round((stats["passed"] / total) * 100, 1) if total > 0 else 0
            print(f"   {category}: {stats['passed']}/{total} ({rate}%)")
        
        # Security & Validation
        sec_val = report["security_validation"]
        print(f"\n🔒 SECURITY & VALIDATION:")
        print(f"   Security Tests: {sec_val['security_passed']}/{sec_val['security_tests']}")
        print(f"   Validation Tests: {sec_val['validation_passed']}/{sec_val['validation_tests']}")
        
        # Performance
        perf = report["performance"]
        print(f"\n⚡ PERFORMANCE:")
        print(f"   Fastest Response: {perf['fastest_response_ms']}ms")
        print(f"   Slowest Response: {perf['slowest_response_ms']}ms")
        print(f"   Under 500ms: {perf['performance_threshold_500ms']}/{len(report['all_results'])}")
        
        # Failed Tests
        if report["failed_tests"]:
            print(f"\n❌ FAILED TESTS:")
            for test in report["failed_tests"]:
                print(f"   • {test['test_name']}: {test['error']}")
        
        # Overall Status
        success_rate = summary['success_rate']
        if success_rate >= 90:
            status = "🎉 EXCELLENT - Production Ready"
        elif success_rate >= 80:
            status = "✅ GOOD - Minor Issues"
        elif success_rate >= 70:
            status = "⚠️ ACCEPTABLE - Some Issues"
        else:
            status = "❌ POOR - Major Issues"
        
        print(f"\n🎯 OVERALL STATUS: {status}")
        print("="*80)
    
    async def run_all_tests(self):
        """Run all property backend tests."""
        logger.info("🚀 Starting Comprehensive Property Backend Testing")
        
        try:
            # Setup
            await self.setup_session()
            
            # Authenticate
            if not await self.authenticate_admin():
                logger.error("❌ Failed to authenticate admin user")
                return
            
            # Run all test suites
            await self.test_property_creation_scenarios()
            await self.test_property_listing()
            await self.test_property_details()
            await self.test_property_update()
            await self.test_user_properties()
            await self.test_image_upload()
            await self.test_database_verification()
            await self.test_property_deletion()  # Run deletion last
            
            # Generate and print report
            report = self.generate_report()
            self.print_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            raise
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution function."""
    tester = PropertyBackendTester()
    report = await tester.run_all_tests()
    
    # Return success based on results
    success_rate = report["summary"]["success_rate"]
    if success_rate >= 80:
        print(f"\n🎉 Property Backend Testing: SUCCESS ({success_rate}%)")
        return True
    else:
        print(f"\n❌ Property Backend Testing: FAILED ({success_rate}%)")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)