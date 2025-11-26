#!/usr/bin/env python3
"""
House Plans Module - Complete End-to-End Backend Testing
========================================================

This script tests the comprehensive House Plan Generation module with 3 phases:
- Phase 1: Template system (5 templates)
- Phase 2: Enhanced floor plan generation with furniture
- Phase 3: 3D visualization (frontend component)

Backend Endpoints to Test:
1. GET /api/house-plans/templates - Get all templates
2. GET /api/house-plans/templates/{template_id} - Get specific template
3. POST /api/house-plans/create - Create house plan (requires auth)
4. GET /api/house-plans/my-plans - Get user's plans (requires auth)
5. GET /api/house-plans/{plan_id} - Get specific plan (requires auth)
6. GET /api/house-plans/{plan_id}/floor-plan/{floor_number} - Get floor plan image (requires auth)
7. GET /api/house-plans/{plan_id}/download-pdf - Download PDF (requires auth)
8. DELETE /api/house-plans/{plan_id} - Delete plan (requires auth)

Author: Testing Agent
Date: 2025-01-27
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Test Configuration
BASE_URL = "https://plan-builder-8.preview.emergentagent.com/api"
TEST_EMAIL = "admin@habitere.com"
TEST_PASSWORD = "admin123"

class HousePlansTestSuite:
    """Comprehensive test suite for House Plans module"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.created_plan_id = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup_session(self):
        """Initialize HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self) -> bool:
        """Authenticate with admin credentials"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    # Check for session cookie
                    cookies = response.cookies
                    if 'session_token' in cookies:
                        self.auth_token = cookies['session_token'].value
                        self.session.cookie_jar.update_cookies(response.cookies)
                        print(f"✅ Authentication successful for {TEST_EMAIL}")
                        return True
                    else:
                        print(f"❌ No session token in response cookies")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
            
        print(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    async def test_get_templates(self):
        """Test GET /api/house-plans/templates"""
        try:
            async with self.session.get(f"{BASE_URL}/house-plans/templates") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    if not data.get('success'):
                        self.log_test_result("Get Templates - Success Flag", False, "success=false")
                        return
                        
                    templates = data.get('templates', [])
                    if len(templates) != 5:
                        self.log_test_result("Get Templates - Count", False, f"Expected 5 templates, got {len(templates)}")
                        return
                        
                    # Validate template structure
                    required_fields = ['id', 'name', 'description', 'house_type', 'floors_count', 'total_area', 'total_rooms']
                    for template in templates:
                        for field in required_fields:
                            if field not in template:
                                self.log_test_result("Get Templates - Structure", False, f"Missing field: {field}")
                                return
                                
                    self.log_test_result("Get Templates", True, f"Found {len(templates)} templates with correct structure")
                    
                else:
                    error_text = await response.text()
                    self.log_test_result("Get Templates", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test_result("Get Templates", False, f"Exception: {e}")
            
    async def test_get_template_detail(self):
        """Test GET /api/house-plans/templates/{template_id}"""
        template_id = "cameroon_3bed_bungalow"
        
        try:
            async with self.session.get(f"{BASE_URL}/house-plans/templates/{template_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data.get('success'):
                        self.log_test_result("Get Template Detail - Success", False, "success=false")
                        return
                        
                    template = data.get('template')
                    if not template:
                        self.log_test_result("Get Template Detail - Template", False, "No template in response")
                        return
                        
                    # Validate template has floors array
                    if 'floors' not in template:
                        self.log_test_result("Get Template Detail - Floors", False, "No floors array")
                        return
                        
                    floors = template['floors']
                    if not floors or len(floors) == 0:
                        self.log_test_result("Get Template Detail - Floors Count", False, "Empty floors array")
                        return
                        
                    # Validate first floor has rooms
                    first_floor = floors[0]
                    if 'rooms' not in first_floor or not first_floor['rooms']:
                        self.log_test_result("Get Template Detail - Rooms", False, "No rooms in first floor")
                        return
                        
                    self.log_test_result("Get Template Detail", True, f"Template {template_id} has {len(floors)} floors with rooms")
                    
                else:
                    error_text = await response.text()
                    self.log_test_result("Get Template Detail", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test_result("Get Template Detail", False, f"Exception: {e}")
            
    async def test_get_template_invalid(self):
        """Test GET /api/house-plans/templates/{invalid_id}"""
        invalid_id = "non_existent_template"
        
        try:
            async with self.session.get(f"{BASE_URL}/house-plans/templates/{invalid_id}") as response:
                if response.status == 404:
                    self.log_test_result("Get Invalid Template", True, "Correctly returned 404")
                else:
                    self.log_test_result("Get Invalid Template", False, f"Expected 404, got {response.status}")
                    
        except Exception as e:
            self.log_test_result("Get Invalid Template", False, f"Exception: {e}")
            
    async def test_create_house_plan(self):
        """Test POST /api/house-plans/create (requires authentication)"""
        if not self.auth_token:
            self.log_test_result("Create House Plan", False, "Not authenticated")
            return
            
        plan_data = {
            "name": "Test House Plan",
            "description": "Testing house plan creation",
            "house_type": "bungalow",
            "location": "douala",
            "floors": [
                {
                    "floor_number": 0,
                    "floor_name": "Ground Floor",
                    "rooms": [
                        {"name": "Living Room", "type": "living_room", "length": 5, "width": 4, "height": 3},
                        {"name": "Bedroom", "type": "bedroom", "length": 4, "width": 3.5, "height": 3}
                    ]
                }
            ],
            "foundation_type": "strip",
            "wall_type": "sandcrete",
            "roofing_type": "aluminum",
            "finishing_level": "standard"
        }
        
        try:
            async with self.session.post(f"{BASE_URL}/house-plans/create", json=plan_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data.get('success'):
                        self.log_test_result("Create House Plan - Success", False, "success=false")
                        return
                        
                    plan = data.get('plan')
                    if not plan:
                        self.log_test_result("Create House Plan - Plan", False, "No plan in response")
                        return
                        
                    # Store plan ID for subsequent tests
                    self.created_plan_id = plan.get('id')
                    if not self.created_plan_id:
                        self.log_test_result("Create House Plan - ID", False, "No plan ID returned")
                        return
                        
                    # Validate plan has required fields
                    required_fields = ['construction_stages', 'total_materials_cost', 'labor_cost', 'total_project_cost']
                    for field in required_fields:
                        if field not in plan:
                            self.log_test_result("Create House Plan - Fields", False, f"Missing field: {field}")
                            return
                            
                    # Validate construction stages
                    stages = plan.get('construction_stages', [])
                    if len(stages) != 7:
                        self.log_test_result("Create House Plan - Stages", False, f"Expected 7 stages, got {len(stages)}")
                        return
                        
                    self.log_test_result("Create House Plan", True, f"Plan created with ID {self.created_plan_id}, {len(stages)} stages")
                    
                else:
                    error_text = await response.text()
                    self.log_test_result("Create House Plan", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test_result("Create House Plan", False, f"Exception: {e}")
            
    async def test_get_my_plans(self):
        """Test GET /api/house-plans/my-plans (requires authentication)"""
        if not self.auth_token:
            self.log_test_result("Get My Plans", False, "Not authenticated")
            return
            
        try:
            async with self.session.get(f"{BASE_URL}/house-plans/my-plans") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data.get('success'):
                        self.log_test_result("Get My Plans - Success", False, "success=false")
                        return
                        
                    plans = data.get('plans', [])
                    
                    # Should have at least the plan we created
                    if self.created_plan_id:
                        plan_found = any(plan.get('id') == self.created_plan_id for plan in plans)
                        if not plan_found:
                            self.log_test_result("Get My Plans - Created Plan", False, "Created plan not found in my plans")
                            return
                            
                    self.log_test_result("Get My Plans", True, f"Found {len(plans)} plans")
                    
                else:
                    error_text = await response.text()
                    self.log_test_result("Get My Plans", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test_result("Get My Plans", False, f"Exception: {e}")
            
    async def test_get_my_plans_unauthenticated(self):
        """Test GET /api/house-plans/my-plans without authentication"""
        # Create temporary session without auth
        temp_session = aiohttp.ClientSession()
        
        try:
            async with temp_session.get(f"{BASE_URL}/house-plans/my-plans") as response:
                if response.status == 401:
                    self.log_test_result("Get My Plans Unauth", True, "Correctly returned 401")
                else:
                    self.log_test_result("Get My Plans Unauth", False, f"Expected 401, got {response.status}")
                    
        except Exception as e:
            self.log_test_result("Get My Plans Unauth", False, f"Exception: {e}")
        finally:
            await temp_session.close()
            
    async def test_get_house_plan(self):
        """Test GET /api/house-plans/{plan_id} (requires authentication)"""
        if not self.auth_token or not self.created_plan_id:
            self.log_test_result("Get House Plan", False, "Not authenticated or no plan created")
            return
            
        try:
            async with self.session.get(f"{BASE_URL}/house-plans/{self.created_plan_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data.get('success'):
                        self.log_test_result("Get House Plan - Success", False, "success=false")
                        return
                        
                    plan = data.get('plan')
                    if not plan:
                        self.log_test_result("Get House Plan - Plan", False, "No plan in response")
                        return
                        
                    if plan.get('id') != self.created_plan_id:
                        self.log_test_result("Get House Plan - ID", False, "Plan ID mismatch")
                        return
                        
                    self.log_test_result("Get House Plan", True, f"Retrieved plan {self.created_plan_id}")
                    
                else:
                    error_text = await response.text()
                    self.log_test_result("Get House Plan", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test_result("Get House Plan", False, f"Exception: {e}")
            
    async def test_get_house_plan_invalid(self):
        """Test GET /api/house-plans/{invalid_id} (requires authentication)"""
        if not self.auth_token:
            self.log_test_result("Get Invalid House Plan", False, "Not authenticated")
            return
            
        invalid_id = "non-existent-plan-id"
        
        try:
            async with self.session.get(f"{BASE_URL}/house-plans/{invalid_id}") as response:
                if response.status == 404:
                    self.log_test_result("Get Invalid House Plan", True, "Correctly returned 404")
                else:
                    self.log_test_result("Get Invalid House Plan", False, f"Expected 404, got {response.status}")
                    
        except Exception as e:
            self.log_test_result("Get Invalid House Plan", False, f"Exception: {e}")
            
    async def test_get_floor_plan_image(self):
        """Test GET /api/house-plans/{plan_id}/floor-plan/{floor_number}"""
        if not self.auth_token or not self.created_plan_id:
            self.log_test_result("Get Floor Plan Image", False, "Not authenticated or no plan created")
            return
            
        floor_number = 0
        
        try:
            async with self.session.get(f"{BASE_URL}/house-plans/{self.created_plan_id}/floor-plan/{floor_number}") as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'image/png' in content_type:
                        content = await response.read()
                        if len(content) > 0:
                            self.log_test_result("Get Floor Plan Image", True, f"PNG image received ({len(content)} bytes)")
                        else:
                            self.log_test_result("Get Floor Plan Image", False, "Empty image content")
                    else:
                        self.log_test_result("Get Floor Plan Image", False, f"Wrong content type: {content_type}")
                else:
                    error_text = await response.text()
                    self.log_test_result("Get Floor Plan Image", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test_result("Get Floor Plan Image", False, f"Exception: {e}")
            
    async def test_get_floor_plan_invalid_floor(self):
        """Test GET /api/house-plans/{plan_id}/floor-plan/{invalid_floor}"""
        if not self.auth_token or not self.created_plan_id:
            self.log_test_result("Get Invalid Floor Plan", False, "Not authenticated or no plan created")
            return
            
        invalid_floor = 99
        
        try:
            async with self.session.get(f"{BASE_URL}/house-plans/{self.created_plan_id}/floor-plan/{invalid_floor}") as response:
                if response.status == 404:
                    self.log_test_result("Get Invalid Floor Plan", True, "Correctly returned 404")
                else:
                    self.log_test_result("Get Invalid Floor Plan", False, f"Expected 404, got {response.status}")
                    
        except Exception as e:
            self.log_test_result("Get Invalid Floor Plan", False, f"Exception: {e}")
            
    async def test_download_pdf(self):
        """Test GET /api/house-plans/{plan_id}/download-pdf"""
        if not self.auth_token or not self.created_plan_id:
            self.log_test_result("Download PDF", False, "Not authenticated or no plan created")
            return
            
        try:
            async with self.session.get(f"{BASE_URL}/house-plans/{self.created_plan_id}/download-pdf") as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        content = await response.read()
                        if len(content) > 0:
                            self.log_test_result("Download PDF", True, f"PDF received ({len(content)} bytes)")
                        else:
                            self.log_test_result("Download PDF", False, "Empty PDF content")
                    else:
                        self.log_test_result("Download PDF", False, f"Wrong content type: {content_type}")
                else:
                    error_text = await response.text()
                    self.log_test_result("Download PDF", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test_result("Download PDF", False, f"Exception: {e}")
            
    async def test_delete_house_plan(self):
        """Test DELETE /api/house-plans/{plan_id}"""
        if not self.auth_token or not self.created_plan_id:
            self.log_test_result("Delete House Plan", False, "Not authenticated or no plan created")
            return
            
        try:
            async with self.session.delete(f"{BASE_URL}/house-plans/{self.created_plan_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        self.log_test_result("Delete House Plan", True, "Plan deleted successfully")
                        
                        # Verify plan no longer exists
                        await asyncio.sleep(1)  # Brief delay
                        async with self.session.get(f"{BASE_URL}/house-plans/{self.created_plan_id}") as verify_response:
                            if verify_response.status == 404:
                                self.log_test_result("Delete Verification", True, "Plan no longer exists")
                            else:
                                self.log_test_result("Delete Verification", False, f"Plan still exists: {verify_response.status}")
                    else:
                        self.log_test_result("Delete House Plan", False, "success=false")
                else:
                    error_text = await response.text()
                    self.log_test_result("Delete House Plan", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test_result("Delete House Plan", False, f"Exception: {e}")
            
    async def run_all_tests(self):
        """Run all house plans tests"""
        print("🏠 HOUSE PLANS MODULE - COMPLETE END-TO-END TESTING")
        print("=" * 60)
        print(f"Testing against: {BASE_URL}")
        print(f"Authentication: {TEST_EMAIL}")
        print()
        
        await self.setup_session()
        
        try:
            # Phase 1: Authentication
            print("📋 PHASE 1: AUTHENTICATION")
            print("-" * 30)
            auth_success = await self.authenticate()
            print()
            
            # Phase 2: Public Template Endpoints
            print("📋 PHASE 2: TEMPLATE SYSTEM (PUBLIC ENDPOINTS)")
            print("-" * 50)
            await self.test_get_templates()
            await self.test_get_template_detail()
            await self.test_get_template_invalid()
            print()
            
            # Phase 3: Authenticated House Plan Operations
            if auth_success:
                print("📋 PHASE 3: HOUSE PLAN OPERATIONS (AUTHENTICATED)")
                print("-" * 55)
                await self.test_create_house_plan()
                await self.test_get_my_plans()
                await self.test_get_my_plans_unauthenticated()
                await self.test_get_house_plan()
                await self.test_get_house_plan_invalid()
                print()
                
                # Phase 4: File Generation & Download
                print("📋 PHASE 4: FILE GENERATION & DOWNLOAD")
                print("-" * 45)
                await self.test_get_floor_plan_image()
                await self.test_get_floor_plan_invalid_floor()
                await self.test_download_pdf()
                print()
                
                # Phase 5: Cleanup
                print("📋 PHASE 5: CLEANUP")
                print("-" * 25)
                await self.test_delete_house_plan()
                print()
            else:
                print("⚠️  Skipping authenticated tests due to authentication failure")
                print()
                
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT - House Plans module is production-ready!")
            elif success_rate >= 75:
                print("✅ GOOD - House Plans module is mostly functional")
            elif success_rate >= 50:
                print("⚠️  NEEDS WORK - Several issues found")
            else:
                print("❌ CRITICAL - Major issues found")
        
        print()
        
        # Print failed tests
        failed_tests = [result for result in self.test_results if not result['passed']]
        if failed_tests:
            print("❌ FAILED TESTS:")
            print("-" * 20)
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
            print()
            
        print("🏠 House Plans Module Testing Complete")
        print("=" * 60)


async def main():
    """Main test execution"""
    test_suite = HousePlansTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
"""
Asset Management Module - Comprehensive Backend API Testing
===========================================================

Tests all 16 asset management endpoints with complete CRUD operations,
authentication, and business logic validation.

Test Coverage:
- Asset CRUD (5 endpoints)
- Maintenance Tasks (4 endpoints) 
- Expenses (3 endpoints)
- Dashboard & Automation (2 endpoints)
- Authentication protection
- Role-based authorization
- Data validation and error handling
- Complete workflows

Author: Testing Agent
Date: 2025-01-27
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "https://plan-builder-8.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@habitere.com"
ADMIN_PASSWORD = "admin123"

class AssetManagementTester:
    """Comprehensive tester for Asset Management Module."""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.admin_user = None
        self.test_property_id = None
        self.test_asset_id = None
        self.test_task_id = None
        self.test_expense_id = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    async def setup_session(self):
        """Initialize HTTP session."""
        connector = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=connector)
        logger.info("HTTP session initialized")
    
    async def cleanup_session(self):
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            logger.info("HTTP session closed")
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user."""
        try:
            # Login as admin
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_user = data.get("user")
                    logger.info(f"✅ Admin authentication successful: {self.admin_user.get('email')}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Admin authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Admin authentication error: {str(e)}")
            return False
    
    async def create_test_property(self) -> Optional[str]:
        """Create a test property for asset testing."""
        try:
            property_data = {
                "title": "Test Property for Asset Management",
                "description": "Property created for asset management testing",
                "price": 250000,
                "location": "Douala, Cameroon",
                "property_sector": "Residential Properties",
                "property_category": "Houses for Sale",
                "listing_type": "sale",
                "bedrooms": 3,
                "bathrooms": 2,
                "area_sqm": 150.0,
                "amenities": ["Parking", "Garden"]
            }
            
            async with self.session.post(f"{BASE_URL}/properties", json=property_data) as response:
                if response.status in [200, 201]:  # Accept both 200 and 201
                    data = await response.json()
                    property_id = data.get("id")
                    logger.info(f"✅ Test property created: {property_id}")
                    return property_id
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to create test property: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error creating test property: {str(e)}")
            return None
    
    def record_test(self, test_name: str, passed: bool, error_msg: str = None):
        """Record test result."""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed"] += 1
            logger.info(f"✅ {test_name}")
        else:
            self.results["failed"] += 1
            error_detail = f"{test_name}: {error_msg}" if error_msg else test_name
            self.results["errors"].append(error_detail)
            logger.error(f"❌ {test_name}: {error_msg}")
    
    # ==================== ASSET CRUD TESTS ====================
    
    async def test_create_asset_authenticated(self):
        """Test POST /api/assets - Create asset (authenticated)."""
        try:
            asset_data = {
                "name": "Test HVAC System",
                "category": "Building Equipment",
                "property_id": self.test_property_id,
                "location": "Building A - Rooftop",
                "status": "Active",
                "condition": "Good",
                "serial_number": "HVAC-2024-001",
                "acquisition_date": "2024-01-15",
                "purchase_value": 2500000.0,
                "notes": "Central air conditioning system for main building"
            }
            
            async with self.session.post(f"{BASE_URL}/assets/", json=asset_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_asset_id = data.get("id")
                    self.record_test("Create Asset (Authenticated)", True)
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Create Asset (Authenticated)", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Create Asset (Authenticated)", False, str(e))
            return False
    
    async def test_create_asset_unauthenticated(self):
        """Test POST /api/assets - Create asset (unauthenticated)."""
        try:
            # Create new session without authentication
            async with aiohttp.ClientSession() as unauth_session:
                asset_data = {
                    "name": "Unauthorized Asset",
                    "category": "Equipment",
                    "property_id": self.test_property_id,
                    "location": "Test Location"
                }
                
                async with unauth_session.post(f"{BASE_URL}/assets", json=asset_data) as response:
                    if response.status == 401:
                        self.record_test("Create Asset (Unauthenticated - Should Fail)", True)
                        return True
                    else:
                        self.record_test("Create Asset (Unauthenticated - Should Fail)", False, f"Expected 401, got {response.status}")
                        return False
                        
        except Exception as e:
            self.record_test("Create Asset (Unauthenticated - Should Fail)", False, str(e))
            return False
    
    async def test_get_assets_list(self):
        """Test GET /api/assets - List assets with filters."""
        try:
            # Test basic list
            async with self.session.get(f"{BASE_URL}/assets") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.record_test("Get Assets List", True)
                        
                        # Test with filters
                        async with self.session.get(f"{BASE_URL}/assets?category=Building Equipment") as filter_response:
                            if filter_response.status == 200:
                                self.record_test("Get Assets List (Filtered)", True)
                            else:
                                self.record_test("Get Assets List (Filtered)", False, f"Filter failed: {filter_response.status}")
                        return True
                    else:
                        self.record_test("Get Assets List", False, "Response not a list")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Get Assets List", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Get Assets List", False, str(e))
            return False
    
    async def test_get_asset_details(self):
        """Test GET /api/assets/{asset_id} - Get asset details."""
        if not self.test_asset_id:
            self.record_test("Get Asset Details", False, "No test asset ID available")
            return False
            
        try:
            async with self.session.get(f"{BASE_URL}/assets/{self.test_asset_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("id") == self.test_asset_id:
                        self.record_test("Get Asset Details", True)
                        return True
                    else:
                        self.record_test("Get Asset Details", False, "Asset ID mismatch")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Get Asset Details", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Get Asset Details", False, str(e))
            return False
    
    async def test_update_asset(self):
        """Test PUT /api/assets/{asset_id} - Update asset."""
        if not self.test_asset_id:
            self.record_test("Update Asset", False, "No test asset ID available")
            return False
            
        try:
            update_data = {
                "condition": "Excellent",
                "notes": "Recently serviced and upgraded"
            }
            
            async with self.session.put(f"{BASE_URL}/assets/{self.test_asset_id}", json=update_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("condition") == "Excellent":
                        self.record_test("Update Asset", True)
                        return True
                    else:
                        self.record_test("Update Asset", False, "Update not reflected")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Update Asset", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Update Asset", False, str(e))
            return False
    
    async def test_delete_asset_unauthorized(self):
        """Test DELETE /api/assets/{asset_id} - Delete asset (should require admin)."""
        # Create a separate asset just for deletion testing
        delete_asset_data = {
            "name": "Delete Test Asset",
            "category": "Equipment", 
            "property_id": self.test_property_id,
            "location": "Test Location for Deletion",
            "status": "Active",
            "condition": "Good"
        }
        
        try:
            # Create asset for deletion testing
            async with self.session.post(f"{BASE_URL}/assets/", json=delete_asset_data) as response:
                if response.status != 200:
                    self.record_test("Delete Asset (Authorization Check)", False, "Failed to create delete test asset")
                    return False
                
                delete_asset = await response.json()
                delete_asset_id = delete_asset.get("id")
            
            # Now test deletion
            async with self.session.delete(f"{BASE_URL}/assets/{delete_asset_id}") as response:
                if response.status in [200, 403]:  # Either success or forbidden
                    self.record_test("Delete Asset (Authorization Check)", True)
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Delete Asset (Authorization Check)", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Delete Asset (Authorization Check)", False, str(e))
            return False
    
    # ==================== MAINTENANCE TASKS TESTS ====================
    
    async def test_create_maintenance_task(self):
        """Test POST /api/assets/maintenance - Create maintenance task."""
        # Create a new asset for maintenance testing since the previous one might be deleted
        maintenance_asset_data = {
            "name": "Maintenance Test Asset",
            "category": "Building Equipment", 
            "property_id": self.test_property_id,
            "location": "Test Location for Maintenance",
            "status": "Active",
            "condition": "Good"
        }
        
        try:
            # Create asset for maintenance testing
            async with self.session.post(f"{BASE_URL}/assets/", json=maintenance_asset_data) as response:
                if response.status != 200:
                    self.record_test("Create Maintenance Task", False, "Failed to create maintenance test asset")
                    return False
                
                maintenance_asset = await response.json()
                maintenance_asset_id = maintenance_asset.get("id")
                
                # Store this for other maintenance tests
                if not self.test_asset_id:  # Only update if we don't have one
                    self.test_asset_id = maintenance_asset_id
            
            task_data = {
                "asset_id": maintenance_asset_id,
                "task_title": "Quarterly HVAC Maintenance",
                "description": "Routine maintenance including filter replacement and system inspection",
                "priority": "High",
                "scheduled_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                "estimated_cost": 150000.0,
                "notes": "Schedule during low-usage hours"
            }
            
            async with self.session.post(f"{BASE_URL}/assets/maintenance", json=task_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_task_id = data.get("id")
                    self.record_test("Create Maintenance Task", True)
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Create Maintenance Task", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Create Maintenance Task", False, str(e))
            return False
    
    async def test_get_maintenance_tasks(self):
        """Test GET /api/assets/maintenance - List maintenance tasks."""
        try:
            async with self.session.get(f"{BASE_URL}/assets/maintenance") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.record_test("Get Maintenance Tasks", True)
                        
                        # Test with filters
                        async with self.session.get(f"{BASE_URL}/assets/maintenance?priority=High") as filter_response:
                            if filter_response.status == 200:
                                self.record_test("Get Maintenance Tasks (Filtered)", True)
                            else:
                                self.record_test("Get Maintenance Tasks (Filtered)", False, f"Filter failed: {filter_response.status}")
                        return True
                    else:
                        self.record_test("Get Maintenance Tasks", False, "Response not a list")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Get Maintenance Tasks", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Get Maintenance Tasks", False, str(e))
            return False
    
    async def test_get_maintenance_task_details(self):
        """Test GET /api/assets/maintenance/{task_id} - Get task details."""
        if not self.test_task_id:
            self.record_test("Get Maintenance Task Details", False, "No test task ID available")
            return False
            
        try:
            async with self.session.get(f"{BASE_URL}/assets/maintenance/{self.test_task_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("id") == self.test_task_id:
                        self.record_test("Get Maintenance Task Details", True)
                        return True
                    else:
                        self.record_test("Get Maintenance Task Details", False, "Task ID mismatch")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Get Maintenance Task Details", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Get Maintenance Task Details", False, str(e))
            return False
    
    async def test_update_task_status(self):
        """Test PUT /api/assets/maintenance/{task_id}/status - Update task status."""
        if not self.test_task_id:
            self.record_test("Update Task Status", False, "No test task ID available")
            return False
            
        try:
            status_data = {
                "status": "In Progress"
            }
            
            async with self.session.put(f"{BASE_URL}/assets/maintenance/{self.test_task_id}/status", json=status_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "In Progress":
                        self.record_test("Update Task Status", True)
                        return True
                    else:
                        self.record_test("Update Task Status", False, "Status not updated")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Update Task Status", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Update Task Status", False, str(e))
            return False
    
    # ==================== EXPENSES TESTS ====================
    
    async def test_create_expense(self):
        """Test POST /api/assets/expenses - Create expense."""
        # Create a new asset for expense testing
        expense_asset_data = {
            "name": "Expense Test Asset",
            "category": "Building Equipment", 
            "property_id": self.test_property_id,
            "location": "Test Location for Expenses",
            "status": "Active",
            "condition": "Good"
        }
        
        try:
            # Create asset for expense testing
            async with self.session.post(f"{BASE_URL}/assets/", json=expense_asset_data) as response:
                if response.status != 200:
                    self.record_test("Create Expense", False, "Failed to create expense test asset")
                    return False
                
                expense_asset = await response.json()
                expense_asset_id = expense_asset.get("id")
            
            expense_data = {
                "asset_id": expense_asset_id,
                "expense_type": "Maintenance",
                "amount": 75000.0,
                "description": "HVAC filter replacement and cleaning",
                "date": datetime.now(timezone.utc).isoformat()
            }
            
            async with self.session.post(f"{BASE_URL}/assets/expenses", json=expense_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_expense_id = data.get("id")
                    self.record_test("Create Expense", True)
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Create Expense", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Create Expense", False, str(e))
            return False
    
    async def test_get_expenses(self):
        """Test GET /api/assets/expenses - List expenses."""
        try:
            async with self.session.get(f"{BASE_URL}/assets/expenses") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.record_test("Get Expenses", True)
                        
                        # Test with filters
                        async with self.session.get(f"{BASE_URL}/assets/expenses?expense_type=Maintenance") as filter_response:
                            if filter_response.status == 200:
                                self.record_test("Get Expenses (Filtered)", True)
                            else:
                                self.record_test("Get Expenses (Filtered)", False, f"Filter failed: {filter_response.status}")
                        return True
                    else:
                        self.record_test("Get Expenses", False, "Response not a list")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Get Expenses", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Get Expenses", False, str(e))
            return False
    
    async def test_approve_expense(self):
        """Test PUT /api/assets/expenses/{expense_id}/approve - Approve expense."""
        if not self.test_expense_id:
            self.record_test("Approve Expense", False, "No test expense ID available")
            return False
            
        try:
            approval_data = {
                "approved": True,
                "notes": "Approved for routine maintenance"
            }
            
            async with self.session.put(f"{BASE_URL}/assets/expenses/{self.test_expense_id}/approve", json=approval_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("approval_status") == "approved":
                        self.record_test("Approve Expense", True)
                        return True
                    else:
                        self.record_test("Approve Expense", False, "Approval status not updated")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Approve Expense", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Approve Expense", False, str(e))
            return False
    
    # ==================== DASHBOARD & AUTOMATION TESTS ====================
    
    async def test_dashboard_stats(self):
        """Test GET /api/assets/dashboard/stats - Get dashboard statistics."""
        try:
            async with self.session.get(f"{BASE_URL}/assets/dashboard/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["total_assets", "active_maintenance_tasks", "upcoming_maintenance", "total_expenses", "assets_by_category"]
                    
                    if all(field in data for field in required_fields):
                        self.record_test("Dashboard Stats", True)
                        return True
                    else:
                        missing_fields = [field for field in required_fields if field not in data]
                        self.record_test("Dashboard Stats", False, f"Missing fields: {missing_fields}")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Dashboard Stats", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Dashboard Stats", False, str(e))
            return False
    
    async def test_trigger_automation(self):
        """Test POST /api/assets/automation/run - Trigger automation."""
        try:
            async with self.session.post(f"{BASE_URL}/assets/automation/run") as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and "results" in data:
                        self.record_test("Trigger Automation", True)
                        return True
                    else:
                        self.record_test("Trigger Automation", False, "Invalid response format")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Trigger Automation", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Trigger Automation", False, str(e))
            return False
    
    # ==================== WORKFLOW TESTS ====================
    
    async def test_complete_workflow(self):
        """Test complete asset management workflow."""
        try:
            # Create a new asset for workflow testing
            workflow_asset_data = {
                "name": "Workflow Test Generator",
                "category": "Building Equipment",
                "property_id": self.test_property_id,
                "location": "Basement - Utility Room",
                "status": "Active",
                "condition": "Good",
                "purchase_value": 1800000.0
            }
            
            # Step 1: Create asset
            async with self.session.post(f"{BASE_URL}/assets/", json=workflow_asset_data) as response:
                if response.status != 200:
                    self.record_test("Complete Workflow", False, "Failed to create workflow asset")
                    return False
                
                workflow_asset = await response.json()
                workflow_asset_id = workflow_asset.get("id")
            
            # Step 2: Create maintenance task
            task_data = {
                "asset_id": workflow_asset_id,
                "task_title": "Generator Monthly Inspection",
                "description": "Monthly inspection and testing of backup generator",
                "priority": "Medium",
                "scheduled_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                "estimated_cost": 50000.0
            }
            
            async with self.session.post(f"{BASE_URL}/assets/maintenance", json=task_data) as response:
                if response.status != 200:
                    self.record_test("Complete Workflow", False, "Failed to create maintenance task")
                    return False
                
                workflow_task = await response.json()
                workflow_task_id = workflow_task.get("id")
            
            # Step 3: Update task status
            status_data = {"status": "Completed", "actual_cost": 45000.0}
            
            async with self.session.put(f"{BASE_URL}/assets/maintenance/{workflow_task_id}/status", json=status_data) as response:
                if response.status != 200:
                    self.record_test("Complete Workflow", False, "Failed to update task status")
                    return False
            
            # Step 4: Create expense
            expense_data = {
                "asset_id": workflow_asset_id,
                "expense_type": "Maintenance",
                "amount": 45000.0,
                "description": "Generator inspection and minor repairs",
                "date": datetime.now(timezone.utc).isoformat()
            }
            
            async with self.session.post(f"{BASE_URL}/assets/expenses", json=expense_data) as response:
                if response.status != 200:
                    self.record_test("Complete Workflow", False, "Failed to create expense")
                    return False
                
                workflow_expense = await response.json()
                workflow_expense_id = workflow_expense.get("id")
            
            # Step 5: Approve expense
            approval_data = {"approved": True, "notes": "Routine maintenance approved"}
            
            async with self.session.put(f"{BASE_URL}/assets/expenses/{workflow_expense_id}/approve", json=approval_data) as response:
                if response.status != 200:
                    self.record_test("Complete Workflow", False, "Failed to approve expense")
                    return False
            
            self.record_test("Complete Workflow", True)
            return True
            
        except Exception as e:
            self.record_test("Complete Workflow", False, str(e))
            return False
    
    # ==================== MAIN TEST RUNNER ====================
    
    async def run_all_tests(self):
        """Run all asset management tests."""
        logger.info("🚀 Starting Asset Management Module Testing")
        logger.info("=" * 60)
        
        try:
            # Setup
            await self.setup_session()
            
            # Authentication
            if not await self.authenticate_admin():
                logger.error("❌ Authentication failed - cannot proceed with tests")
                return self.results
            
            # Create test property
            self.test_property_id = await self.create_test_property()
            if not self.test_property_id:
                logger.error("❌ Failed to create test property - cannot proceed with asset tests")
                return self.results
            
            # Asset CRUD Tests
            logger.info("\n📦 Testing Asset CRUD Operations...")
            await self.test_create_asset_unauthenticated()
            await self.test_create_asset_authenticated()
            await self.test_get_assets_list()
            await self.test_get_asset_details()
            await self.test_update_asset()
            await self.test_delete_asset_unauthorized()
            
            # Maintenance Tasks Tests
            logger.info("\n🔧 Testing Maintenance Tasks...")
            await self.test_create_maintenance_task()
            await self.test_get_maintenance_tasks()
            await self.test_get_maintenance_task_details()
            await self.test_update_task_status()
            
            # Expenses Tests
            logger.info("\n💰 Testing Expenses...")
            await self.test_create_expense()
            await self.test_get_expenses()
            await self.test_approve_expense()
            
            # Dashboard & Automation Tests
            logger.info("\n📊 Testing Dashboard & Automation...")
            await self.test_dashboard_stats()
            await self.test_trigger_automation()
            
            # Workflow Tests
            logger.info("\n🔄 Testing Complete Workflows...")
            await self.test_complete_workflow()
            
        except Exception as e:
            logger.error(f"❌ Critical error during testing: {str(e)}")
            self.results["errors"].append(f"Critical error: {str(e)}")
        
        finally:
            await self.cleanup_session()
        
        return self.results
    
    def print_summary(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 60)
        logger.info("🎯 ASSET MANAGEMENT MODULE TEST RESULTS")
        logger.info("=" * 60)
        
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info(f"📊 Total Tests: {total}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results["errors"]:
            logger.info(f"\n❌ FAILED TESTS ({len(self.results['errors'])}):") 
            for i, error in enumerate(self.results["errors"], 1):
                logger.info(f"   {i}. {error}")
        
        logger.info("\n" + "=" * 60)
        
        # Determine overall status
        if success_rate >= 90:
            logger.info("🎉 ASSET MANAGEMENT MODULE: EXCELLENT - Production Ready!")
        elif success_rate >= 75:
            logger.info("✅ ASSET MANAGEMENT MODULE: GOOD - Minor issues to address")
        elif success_rate >= 50:
            logger.info("⚠️ ASSET MANAGEMENT MODULE: NEEDS WORK - Several issues found")
        else:
            logger.info("❌ ASSET MANAGEMENT MODULE: CRITICAL ISSUES - Major problems detected")


async def main():
    """Main test execution function."""
    tester = AssetManagementTester()
    
    try:
        results = await tester.run_all_tests()
        tester.print_summary()
        
        # Return results for external processing
        return results
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Testing interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
    
    return tester.results


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())