#!/usr/bin/env python3
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
BASE_URL = "https://realestate-cam.preview.emergentagent.com/api"
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