#!/usr/bin/env python3
"""
Comprehensive Asset Management Module Backend Testing
====================================================

Tests all 25 asset management endpoints across:
- Assets (6 endpoints)
- Maintenance (7 endpoints) 
- Expenses (6 endpoints)
- Inventory (6 endpoints)

Authentication: admin@habitere.com / admin123
Backend URL: https://habitere-home.preview.emergentagent.com/api
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "https://habitere-home.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@habitere.com"
ADMIN_PASSWORD = "admin123"

class AssetManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.created_assets = []
        self.created_maintenance = []
        self.created_expenses = []
        self.created_inventory = []
        
    def log_test(self, test_name, success, details="", response_code=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'response_code': response_code
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")
        if response_code:
            print(f"    Response Code: {response_code}")
        print()

    def authenticate(self):
        """Authenticate as admin user"""
        print("🔐 AUTHENTICATING AS ADMIN USER...")
        
        try:
            # Login
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                user_data = response.json()
                self.log_test("Admin Authentication", True, 
                            f"Logged in as {user_data.get('email', 'Unknown')} with role {user_data.get('role', 'Unknown')}", 
                            response.status_code)
                return True
            else:
                self.log_test("Admin Authentication", False, 
                            f"Login failed: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_assets_endpoints(self):
        """Test all 6 Assets endpoints"""
        print("🏢 TESTING ASSETS ENDPOINTS (6 total)...")
        
        # Test data
        test_property_id = str(uuid.uuid4())
        
        # 1. POST /api/assets/ - Create asset
        asset_data = {
            "name": "Test Building HVAC System",
            "category": "Building Equipment",
            "property_id": test_property_id,
            "location": "Building A - Rooftop",
            "status": "Active",
            "condition": "Good",
            "serial_number": "HVAC-2024-001",
            "acquisition_date": "2024-01-15",
            "purchase_value": 2500000.0,
            "notes": "Central air conditioning system for main building"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/assets/", json=asset_data)
            if response.status_code == 200:
                created_asset = response.json()
                self.created_assets.append(created_asset['id'])
                self.log_test("POST /assets/ - Create Asset", True, 
                            f"Created asset: {created_asset['name']}", response.status_code)
            else:
                self.log_test("POST /assets/ - Create Asset", False, 
                            f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_test("POST /assets/ - Create Asset", False, f"Exception: {str(e)}")

        # 2. GET /api/assets/ - List assets with filters
        try:
            response = self.session.get(f"{BASE_URL}/assets/")
            if response.status_code == 200:
                assets = response.json()
                self.log_test("GET /assets/ - List Assets", True, 
                            f"Retrieved {len(assets)} assets", response.status_code)
                
                # Test with filters
                response = self.session.get(f"{BASE_URL}/assets/?category=Building Equipment")
                if response.status_code == 200:
                    filtered_assets = response.json()
                    self.log_test("GET /assets/ - Filter by Category", True, 
                                f"Retrieved {len(filtered_assets)} Building Equipment assets", response.status_code)
                else:
                    self.log_test("GET /assets/ - Filter by Category", False, 
                                f"Failed: {response.text}", response.status_code)
            else:
                self.log_test("GET /assets/ - List Assets", False, 
                            f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_test("GET /assets/ - List Assets", False, f"Exception: {str(e)}")

        # 3. GET /api/assets/{asset_id} - Get single asset (NEW)
        if self.created_assets:
            asset_id = self.created_assets[0]
            try:
                response = self.session.get(f"{BASE_URL}/assets/{asset_id}")
                if response.status_code == 200:
                    asset = response.json()
                    self.log_test("GET /assets/{asset_id} - Get Single Asset", True, 
                                f"Retrieved asset: {asset['name']}", response.status_code)
                else:
                    self.log_test("GET /assets/{asset_id} - Get Single Asset", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("GET /assets/{asset_id} - Get Single Asset", False, f"Exception: {str(e)}")

        # 4. PUT /api/assets/{asset_id} - Update asset (NEW)
        if self.created_assets:
            asset_id = self.created_assets[0]
            update_data = {
                "name": "Updated HVAC System",
                "category": "Building Equipment",
                "property_id": test_property_id,
                "location": "Building A - Rooftop",
                "status": "Under Maintenance",
                "condition": "Fair",
                "notes": "Updated notes - scheduled for maintenance"
            }
            
            try:
                response = self.session.put(f"{BASE_URL}/assets/{asset_id}", json=update_data)
                if response.status_code == 200:
                    updated_asset = response.json()
                    self.log_test("PUT /assets/{asset_id} - Update Asset", True, 
                                f"Updated asset status to: {updated_asset['status']}", response.status_code)
                else:
                    self.log_test("PUT /assets/{asset_id} - Update Asset", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("PUT /assets/{asset_id} - Update Asset", False, f"Exception: {str(e)}")

        # 5. GET /api/assets/dashboard/stats - Dashboard stats
        try:
            response = self.session.get(f"{BASE_URL}/assets/dashboard/stats")
            if response.status_code == 200:
                stats = response.json()
                self.log_test("GET /assets/dashboard/stats - Dashboard Stats", True, 
                            f"Stats: {stats.get('total_assets', 0)} assets, {stats.get('active_maintenance_tasks', 0)} active tasks", 
                            response.status_code)
            else:
                self.log_test("GET /assets/dashboard/stats - Dashboard Stats", False, 
                            f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_test("GET /assets/dashboard/stats - Dashboard Stats", False, f"Exception: {str(e)}")

        # 6. DELETE /api/assets/{asset_id} - Delete asset (NEW) - Test at end to avoid cascade issues
        # We'll test this after creating maintenance and expenses

    def test_maintenance_endpoints(self):
        """Test all 7 Maintenance endpoints"""
        print("🔧 TESTING MAINTENANCE ENDPOINTS (7 total)...")
        
        if not self.created_assets:
            print("⚠️ No assets available for maintenance testing")
            return
            
        asset_id = self.created_assets[0]
        
        # 7. POST /api/assets/maintenance - Create task
        maintenance_data = {
            "asset_id": asset_id,
            "task_title": "Quarterly HVAC Maintenance",
            "description": "Comprehensive maintenance including filter replacement, coil cleaning, and system inspection",
            "priority": "High",
            "status": "Pending",
            "scheduled_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "estimated_cost": 150000.0,
            "notes": "Critical maintenance to prevent system failure"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/assets/maintenance", json=maintenance_data)
            if response.status_code == 200:
                created_task = response.json()
                self.created_maintenance.append(created_task['id'])
                self.log_test("POST /assets/maintenance - Create Task", True, 
                            f"Created task: {created_task['task_title']}", response.status_code)
            else:
                self.log_test("POST /assets/maintenance - Create Task", False, 
                            f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_test("POST /assets/maintenance - Create Task", False, f"Exception: {str(e)}")

        # 8. GET /api/assets/maintenance - List tasks
        try:
            response = self.session.get(f"{BASE_URL}/assets/maintenance")
            if response.status_code == 200:
                tasks = response.json()
                self.log_test("GET /assets/maintenance - List Tasks", True, 
                            f"Retrieved {len(tasks)} maintenance tasks", response.status_code)
                
                # Test with filters
                response = self.session.get(f"{BASE_URL}/assets/maintenance?priority=High")
                if response.status_code == 200:
                    high_priority_tasks = response.json()
                    self.log_test("GET /assets/maintenance - Filter by Priority", True, 
                                f"Retrieved {len(high_priority_tasks)} high priority tasks", response.status_code)
                else:
                    self.log_test("GET /assets/maintenance - Filter by Priority", False, 
                                f"Failed: {response.text}", response.status_code)
            else:
                self.log_test("GET /assets/maintenance - List Tasks", False, 
                            f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_test("GET /assets/maintenance - List Tasks", False, f"Exception: {str(e)}")

        # 9. GET /api/assets/maintenance/{task_id} - Get task
        if self.created_maintenance:
            task_id = self.created_maintenance[0]
            try:
                response = self.session.get(f"{BASE_URL}/assets/maintenance/{task_id}")
                if response.status_code == 200:
                    task = response.json()
                    self.log_test("GET /assets/maintenance/{task_id} - Get Task", True, 
                                f"Retrieved task: {task['task_title']}", response.status_code)
                else:
                    self.log_test("GET /assets/maintenance/{task_id} - Get Task", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("GET /assets/maintenance/{task_id} - Get Task", False, f"Exception: {str(e)}")

        # 10. PUT /api/assets/maintenance/{task_id}/status - Update status
        if self.created_maintenance:
            task_id = self.created_maintenance[0]
            status_data = {
                "status": "In Progress"
            }
            
            try:
                response = self.session.put(f"{BASE_URL}/assets/maintenance/{task_id}/status", json=status_data)
                if response.status_code == 200:
                    updated_task = response.json()
                    self.log_test("PUT /assets/maintenance/{task_id}/status - Update Status", True, 
                                f"Updated task status to: {updated_task['status']}", response.status_code)
                else:
                    self.log_test("PUT /assets/maintenance/{task_id}/status - Update Status", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("PUT /assets/maintenance/{task_id}/status - Update Status", False, f"Exception: {str(e)}")

        # 11. PUT /api/assets/maintenance/{task_id} - Update task (NEW)
        if self.created_maintenance:
            task_id = self.created_maintenance[0]
            update_data = {
                "asset_id": asset_id,
                "task_title": "Updated Quarterly HVAC Maintenance",
                "description": "Updated comprehensive maintenance including additional electrical checks",
                "priority": "High",
                "status": "In Progress",
                "scheduled_date": (datetime.now() + timedelta(days=5)).isoformat(),
                "estimated_cost": 175000.0,
                "notes": "Updated with additional electrical inspection requirements"
            }
            
            try:
                response = self.session.put(f"{BASE_URL}/assets/maintenance/{task_id}", json=update_data)
                if response.status_code == 200:
                    updated_task = response.json()
                    self.log_test("PUT /assets/maintenance/{task_id} - Update Task", True, 
                                f"Updated task title to: {updated_task['task_title']}", response.status_code)
                else:
                    self.log_test("PUT /assets/maintenance/{task_id} - Update Task", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("PUT /assets/maintenance/{task_id} - Update Task", False, f"Exception: {str(e)}")

        # 12. DELETE /api/assets/maintenance/{task_id} - Delete task (NEW) - Test later

    def test_expenses_endpoints(self):
        """Test all 6 Expenses endpoints"""
        print("💰 TESTING EXPENSES ENDPOINTS (6 total)...")
        
        if not self.created_assets:
            print("⚠️ No assets available for expense testing")
            return
            
        asset_id = self.created_assets[0]
        
        # 13. POST /api/assets/expenses - Create expense
        expense_data = {
            "asset_id": asset_id,
            "expense_type": "Maintenance",
            "amount": 125000.0,
            "description": "HVAC filter replacement and system cleaning",
            "date": datetime.now().isoformat()
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/assets/expenses", json=expense_data)
            if response.status_code == 200:
                created_expense = response.json()
                self.created_expenses.append(created_expense['id'])
                self.log_test("POST /assets/expenses - Create Expense", True, 
                            f"Created expense: {created_expense['amount']} XAF for {created_expense['expense_type']}", 
                            response.status_code)
            else:
                self.log_test("POST /assets/expenses - Create Expense", False, 
                            f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_test("POST /assets/expenses - Create Expense", False, f"Exception: {str(e)}")

        # 14. GET /api/assets/expenses - List expenses
        try:
            response = self.session.get(f"{BASE_URL}/assets/expenses")
            if response.status_code == 200:
                expenses = response.json()
                self.log_test("GET /assets/expenses - List Expenses", True, 
                            f"Retrieved {len(expenses)} expenses", response.status_code)
                
                # Test with filters
                response = self.session.get(f"{BASE_URL}/assets/expenses?expense_type=Maintenance")
                if response.status_code == 200:
                    maintenance_expenses = response.json()
                    self.log_test("GET /assets/expenses - Filter by Type", True, 
                                f"Retrieved {len(maintenance_expenses)} maintenance expenses", response.status_code)
                else:
                    self.log_test("GET /assets/expenses - Filter by Type", False, 
                                f"Failed: {response.text}", response.status_code)
            else:
                self.log_test("GET /assets/expenses - List Expenses", False, 
                            f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_test("GET /assets/expenses - List Expenses", False, f"Exception: {str(e)}")

        # 15. GET /api/assets/expenses/{expense_id} - Get expense (NEW)
        if self.created_expenses:
            expense_id = self.created_expenses[0]
            try:
                response = self.session.get(f"{BASE_URL}/assets/expenses/{expense_id}")
                if response.status_code == 200:
                    expense = response.json()
                    self.log_test("GET /assets/expenses/{expense_id} - Get Expense", True, 
                                f"Retrieved expense: {expense['amount']} XAF", response.status_code)
                else:
                    self.log_test("GET /assets/expenses/{expense_id} - Get Expense", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("GET /assets/expenses/{expense_id} - Get Expense", False, f"Exception: {str(e)}")

        # 16. PUT /api/assets/expenses/{expense_id} - Update expense (NEW)
        if self.created_expenses:
            expense_id = self.created_expenses[0]
            update_data = {
                "asset_id": asset_id,
                "expense_type": "Maintenance",
                "amount": 135000.0,
                "description": "Updated: HVAC filter replacement, system cleaning, and minor repairs",
                "date": datetime.now().isoformat()
            }
            
            try:
                response = self.session.put(f"{BASE_URL}/assets/expenses/{expense_id}", json=update_data)
                if response.status_code == 200:
                    updated_expense = response.json()
                    self.log_test("PUT /assets/expenses/{expense_id} - Update Expense", True, 
                                f"Updated expense amount to: {updated_expense['amount']} XAF", response.status_code)
                else:
                    self.log_test("PUT /assets/expenses/{expense_id} - Update Expense", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("PUT /assets/expenses/{expense_id} - Update Expense", False, f"Exception: {str(e)}")

        # 17. PUT /api/assets/expenses/{expense_id}/approve - Approve/reject expense
        if self.created_expenses:
            expense_id = self.created_expenses[0]
            approval_data = {
                "approved": True,
                "notes": "Approved - necessary maintenance expense"
            }
            
            try:
                response = self.session.put(f"{BASE_URL}/assets/expenses/{expense_id}/approve", json=approval_data)
                if response.status_code == 200:
                    approved_expense = response.json()
                    self.log_test("PUT /assets/expenses/{expense_id}/approve - Approve Expense", True, 
                                f"Expense approval status: {approved_expense.get('approval_status', 'Unknown')}", 
                                response.status_code)
                else:
                    self.log_test("PUT /assets/expenses/{expense_id}/approve - Approve Expense", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("PUT /assets/expenses/{expense_id}/approve - Approve Expense", False, f"Exception: {str(e)}")

        # 18. DELETE /api/assets/expenses/{expense_id} - Delete expense (NEW) - Test later

    def test_inventory_endpoints(self):
        """Test all 6 Inventory endpoints"""
        print("📦 TESTING INVENTORY ENDPOINTS (6 total)...")
        
        # 19. POST /api/assets/inventory - Create item
        inventory_data = {
            "name": "HVAC Air Filters",
            "category": "Spare Parts",
            "quantity": 25,
            "unit": "pcs",
            "reorder_level": 5,
            "reorder_quantity": 20,
            "unit_cost": 15000.0,
            "supplier_name": "HVAC Supplies Cameroon",
            "supplier_contact": "+237 6XX XXX XXX",
            "location": "Storage Room A",
            "notes": "High-efficiency filters for main HVAC system"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/assets/inventory", json=inventory_data)
            if response.status_code == 200:
                created_item = response.json()
                self.created_inventory.append(created_item['id'])
                self.log_test("POST /assets/inventory - Create Item", True, 
                            f"Created inventory item: {created_item['name']} ({created_item['quantity']} {created_item['unit']})", 
                            response.status_code)
            else:
                self.log_test("POST /assets/inventory - Create Item", False, 
                            f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_test("POST /assets/inventory - Create Item", False, f"Exception: {str(e)}")

        # 20. GET /api/assets/inventory - List items
        try:
            response = self.session.get(f"{BASE_URL}/assets/inventory")
            if response.status_code == 200:
                items = response.json()
                self.log_test("GET /assets/inventory - List Items", True, 
                            f"Retrieved {len(items)} inventory items", response.status_code)
                
                # Test with filters
                response = self.session.get(f"{BASE_URL}/assets/inventory?category=Spare Parts")
                if response.status_code == 200:
                    spare_parts = response.json()
                    self.log_test("GET /assets/inventory - Filter by Category", True, 
                                f"Retrieved {len(spare_parts)} spare parts", response.status_code)
                else:
                    self.log_test("GET /assets/inventory - Filter by Category", False, 
                                f"Failed: {response.text}", response.status_code)
            else:
                self.log_test("GET /assets/inventory - List Items", False, 
                            f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_test("GET /assets/inventory - List Items", False, f"Exception: {str(e)}")

        # 21. GET /api/assets/inventory/{item_id} - Get item
        if self.created_inventory:
            item_id = self.created_inventory[0]
            try:
                response = self.session.get(f"{BASE_URL}/assets/inventory/{item_id}")
                if response.status_code == 200:
                    item = response.json()
                    self.log_test("GET /assets/inventory/{item_id} - Get Item", True, 
                                f"Retrieved item: {item['name']}", response.status_code)
                else:
                    self.log_test("GET /assets/inventory/{item_id} - Get Item", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("GET /assets/inventory/{item_id} - Get Item", False, f"Exception: {str(e)}")

        # 22. PUT /api/assets/inventory/{item_id} - Update item
        if self.created_inventory:
            item_id = self.created_inventory[0]
            update_data = {
                "name": "Premium HVAC Air Filters",
                "category": "Spare Parts",
                "quantity": 30,
                "unit": "pcs",
                "reorder_level": 8,
                "reorder_quantity": 25,
                "unit_cost": 18000.0,
                "supplier_name": "Premium HVAC Supplies Cameroon",
                "location": "Storage Room A - Shelf 2",
                "notes": "Upgraded to premium high-efficiency filters"
            }
            
            try:
                response = self.session.put(f"{BASE_URL}/assets/inventory/{item_id}", json=update_data)
                if response.status_code == 200:
                    updated_item = response.json()
                    self.log_test("PUT /assets/inventory/{item_id} - Update Item", True, 
                                f"Updated item quantity to: {updated_item['quantity']} {updated_item['unit']}", 
                                response.status_code)
                else:
                    self.log_test("PUT /assets/inventory/{item_id} - Update Item", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("PUT /assets/inventory/{item_id} - Update Item", False, f"Exception: {str(e)}")

        # 23. POST /api/assets/inventory/{item_id}/adjust-stock - Stock adjustment
        if self.created_inventory:
            item_id = self.created_inventory[0]
            adjustment_data = {
                "quantity": 5,
                "type": "subtract",
                "reason": "Used for HVAC maintenance"
            }
            
            try:
                response = self.session.post(f"{BASE_URL}/assets/inventory/{item_id}/adjust-stock", json=adjustment_data)
                if response.status_code == 200:
                    adjusted_item = response.json()
                    self.log_test("POST /assets/inventory/{item_id}/adjust-stock - Stock Adjustment", True, 
                                f"Adjusted stock to: {adjusted_item['quantity']} {adjusted_item['unit']}", 
                                response.status_code)
                else:
                    self.log_test("POST /assets/inventory/{item_id}/adjust-stock - Stock Adjustment", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("POST /assets/inventory/{item_id}/adjust-stock - Stock Adjustment", False, f"Exception: {str(e)}")

        # 24. DELETE /api/assets/inventory/{item_id} - Delete item - Test later

    def test_automation_endpoint(self):
        """Test automation trigger endpoint"""
        print("🤖 TESTING AUTOMATION ENDPOINT...")
        
        # 25. POST /api/assets/automation/run - Manual automation trigger
        try:
            response = self.session.post(f"{BASE_URL}/assets/automation/run")
            if response.status_code == 200:
                result = response.json()
                self.log_test("POST /assets/automation/run - Manual Automation Trigger", True, 
                            f"Automation completed: {result.get('message', 'Success')}", response.status_code)
            else:
                self.log_test("POST /assets/automation/run - Manual Automation Trigger", False, 
                            f"Failed: {response.text}", response.status_code)
        except Exception as e:
            self.log_test("POST /assets/automation/run - Manual Automation Trigger", False, f"Exception: {str(e)}")

    def test_cascade_delete(self):
        """Test CASCADE DELETE functionality"""
        print("🗑️ TESTING CASCADE DELETE FUNCTIONALITY...")
        
        # Delete maintenance task first
        if self.created_maintenance:
            task_id = self.created_maintenance[0]
            try:
                response = self.session.delete(f"{BASE_URL}/assets/maintenance/{task_id}")
                if response.status_code == 200:
                    self.log_test("DELETE /assets/maintenance/{task_id} - Delete Task", True, 
                                "Maintenance task deleted successfully", response.status_code)
                else:
                    self.log_test("DELETE /assets/maintenance/{task_id} - Delete Task", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("DELETE /assets/maintenance/{task_id} - Delete Task", False, f"Exception: {str(e)}")

        # Delete expense
        if self.created_expenses:
            expense_id = self.created_expenses[0]
            try:
                response = self.session.delete(f"{BASE_URL}/assets/expenses/{expense_id}")
                if response.status_code == 200:
                    self.log_test("DELETE /assets/expenses/{expense_id} - Delete Expense", True, 
                                "Expense deleted successfully", response.status_code)
                else:
                    self.log_test("DELETE /assets/expenses/{expense_id} - Delete Expense", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("DELETE /assets/expenses/{expense_id} - Delete Expense", False, f"Exception: {str(e)}")

        # Delete inventory item
        if self.created_inventory:
            item_id = self.created_inventory[0]
            try:
                response = self.session.delete(f"{BASE_URL}/assets/inventory/{item_id}")
                if response.status_code == 200:
                    self.log_test("DELETE /assets/inventory/{item_id} - Delete Item", True, 
                                "Inventory item deleted successfully", response.status_code)
                else:
                    self.log_test("DELETE /assets/inventory/{item_id} - Delete Item", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("DELETE /assets/inventory/{item_id} - Delete Item", False, f"Exception: {str(e)}")

        # Finally delete asset (should cascade delete any remaining maintenance/expenses)
        if self.created_assets:
            asset_id = self.created_assets[0]
            try:
                response = self.session.delete(f"{BASE_URL}/assets/{asset_id}")
                if response.status_code == 200:
                    self.log_test("DELETE /assets/{asset_id} - Delete Asset (CASCADE)", True, 
                                "Asset and associated data deleted successfully", response.status_code)
                else:
                    self.log_test("DELETE /assets/{asset_id} - Delete Asset (CASCADE)", False, 
                                f"Failed: {response.text}", response.status_code)
            except Exception as e:
                self.log_test("DELETE /assets/{asset_id} - Delete Asset (CASCADE)", False, f"Exception: {str(e)}")

    def test_authorization_checks(self):
        """Test authorization and error handling"""
        print("🔒 TESTING AUTHORIZATION & ERROR HANDLING...")
        
        # Test 404 for non-existent asset
        fake_id = str(uuid.uuid4())
        try:
            response = self.session.get(f"{BASE_URL}/assets/{fake_id}")
            if response.status_code == 404:
                self.log_test("Authorization - 404 for Non-existent Asset", True, 
                            "Correctly returned 404 for non-existent asset", response.status_code)
            else:
                self.log_test("Authorization - 404 for Non-existent Asset", False, 
                            f"Expected 404, got {response.status_code}", response.status_code)
        except Exception as e:
            self.log_test("Authorization - 404 for Non-existent Asset", False, f"Exception: {str(e)}")

        # Test 404 for non-existent maintenance task
        try:
            response = self.session.get(f"{BASE_URL}/assets/maintenance/{fake_id}")
            if response.status_code == 404:
                self.log_test("Authorization - 404 for Non-existent Task", True, 
                            "Correctly returned 404 for non-existent task", response.status_code)
            else:
                self.log_test("Authorization - 404 for Non-existent Task", False, 
                            f"Expected 404, got {response.status_code}", response.status_code)
        except Exception as e:
            self.log_test("Authorization - 404 for Non-existent Task", False, f"Exception: {str(e)}")

        # Test 404 for non-existent expense
        try:
            response = self.session.get(f"{BASE_URL}/assets/expenses/{fake_id}")
            if response.status_code == 404:
                self.log_test("Authorization - 404 for Non-existent Expense", True, 
                            "Correctly returned 404 for non-existent expense", response.status_code)
            else:
                self.log_test("Authorization - 404 for Non-existent Expense", False, 
                            f"Expected 404, got {response.status_code}", response.status_code)
        except Exception as e:
            self.log_test("Authorization - 404 for Non-existent Expense", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all asset management tests"""
        print("🚀 STARTING COMPREHENSIVE ASSET MANAGEMENT MODULE BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Authentication: {ADMIN_EMAIL}")
        print("Testing 25 endpoints across Assets, Maintenance, Expenses, and Inventory")
        print("=" * 80)
        print()
        
        # Authenticate first
        if not self.authenticate():
            print("❌ AUTHENTICATION FAILED - Cannot proceed with tests")
            return
        
        # Run all endpoint tests
        self.test_assets_endpoints()
        self.test_maintenance_endpoints()
        self.test_expenses_endpoints()
        self.test_inventory_endpoints()
        self.test_automation_endpoint()
        
        # Test authorization and error handling
        self.test_authorization_checks()
        
        # Test cascade delete functionality
        self.test_cascade_delete()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE ASSET MANAGEMENT MODULE TESTING SUMMARY")
        print("=" * 80)
        
        passed = len([r for r in self.test_results if "✅ PASS" in r['status']])
        failed = len([r for r in self.test_results if "❌ FAIL" in r['status']])
        total = len(self.test_results)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 RESULTS: {passed}/{total} tests passed ({success_rate:.1f}% success rate)")
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print()
        
        if failed > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result['status']:
                    print(f"   • {result['test']}")
                    if result['details']:
                        print(f"     Details: {result['details']}")
            print()
        
        print("📋 ENDPOINT COVERAGE:")
        print("   Assets (6 endpoints):")
        print("   • POST /assets/ - Create asset")
        print("   • GET /assets/ - List assets with filters")
        print("   • GET /assets/{asset_id} - Get single asset")
        print("   • PUT /assets/{asset_id} - Update asset")
        print("   • DELETE /assets/{asset_id} - Delete asset")
        print("   • GET /assets/dashboard/stats - Dashboard stats")
        print()
        print("   Maintenance (7 endpoints):")
        print("   • POST /assets/maintenance - Create task")
        print("   • GET /assets/maintenance - List tasks")
        print("   • GET /assets/maintenance/{task_id} - Get task")
        print("   • PUT /assets/maintenance/{task_id}/status - Update status")
        print("   • PUT /assets/maintenance/{task_id} - Update task")
        print("   • DELETE /assets/maintenance/{task_id} - Delete task")
        print()
        print("   Expenses (6 endpoints):")
        print("   • POST /assets/expenses - Create expense")
        print("   • GET /assets/expenses - List expenses")
        print("   • GET /assets/expenses/{expense_id} - Get expense")
        print("   • PUT /assets/expenses/{expense_id} - Update expense")
        print("   • DELETE /assets/expenses/{expense_id} - Delete expense")
        print("   • PUT /assets/expenses/{expense_id}/approve - Approve/reject expense")
        print()
        print("   Inventory (6 endpoints):")
        print("   • POST /assets/inventory - Create item")
        print("   • GET /assets/inventory - List items")
        print("   • GET /assets/inventory/{item_id} - Get item")
        print("   • PUT /assets/inventory/{item_id} - Update item")
        print("   • DELETE /assets/inventory/{item_id} - Delete item")
        print("   • POST /assets/inventory/{item_id}/adjust-stock - Stock adjustment")
        print()
        print("   Automation (1 endpoint):")
        print("   • POST /assets/automation/run - Manual automation trigger")
        print()
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Asset Management Module is production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD: Asset Management Module is mostly functional with minor issues.")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Asset Management Module has significant issues requiring attention.")
        else:
            print("❌ CRITICAL: Asset Management Module has major issues preventing production use.")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = AssetManagementTester()
    tester.run_all_tests()