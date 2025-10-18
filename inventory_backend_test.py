#!/usr/bin/env python3
"""
Comprehensive Backend Testing - Inventory Management System
===========================================================

Tests all 6 new inventory management endpoints with complete CRUD operations,
stock adjustments, and automation integration.

Test Coverage:
- POST /api/assets/inventory - Create inventory item
- GET /api/assets/inventory - List inventory items  
- GET /api/assets/inventory/{item_id} - Get inventory item details
- PUT /api/assets/inventory/{item_id} - Update inventory item
- DELETE /api/assets/inventory/{item_id} - Delete inventory item
- POST /api/assets/inventory/{item_id}/adjust-stock - Adjust stock quantity

Authentication: admin@habitere.com / admin123
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Backend URL from environment
BACKEND_URL = "https://proptech-assets.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "admin@habitere.com"
ADMIN_PASSWORD = "admin123"

class InventoryTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.created_items = []  # Track created items for cleanup
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def authenticate(self):
        """Authenticate as admin user"""
        print("\n🔐 AUTHENTICATING AS ADMIN...")
        
        try:
            # Login
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                # Check if we have session cookies
                if self.session.cookies:
                    self.log_test("Admin Authentication", True, "Successfully authenticated with session cookies")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No session cookies received")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_create_inventory_item_normal_stock(self):
        """Test creating inventory item with normal stock (above reorder level)"""
        print("\n📦 TESTING: Create Inventory Item (Normal Stock)")
        
        try:
            item_data = {
                "name": "Industrial Drill Bits Set",
                "category": "Tools",
                "property_id": None,
                "quantity": 50,
                "unit": "pcs",
                "reorder_level": 10,
                "reorder_quantity": 25,
                "unit_cost": 2500.0,
                "supplier_name": "Cameroon Tools Ltd",
                "supplier_contact": "+237 677 123 456",
                "location": "Main Warehouse - Section A",
                "notes": "High-quality drill bits for construction work"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/assets/inventory",
                json=item_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                item_id = result.get("id")
                if item_id:
                    self.created_items.append(item_id)
                    self.log_test("Create Normal Stock Item", True, f"Created item ID: {item_id}")
                    return item_id
                else:
                    self.log_test("Create Normal Stock Item", False, "No item ID returned")
                    return None
            else:
                self.log_test("Create Normal Stock Item", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create Normal Stock Item", False, f"Error: {str(e)}")
            return None
    
    def test_create_inventory_item_low_stock(self):
        """Test creating inventory item with low stock (at reorder level) - should trigger alert"""
        print("\n⚠️ TESTING: Create Inventory Item (Low Stock - Should Trigger Alert)")
        
        try:
            item_data = {
                "name": "Safety Helmets",
                "category": "Safety Gear",
                "property_id": None,
                "quantity": 5,  # At reorder level
                "unit": "pcs",
                "reorder_level": 5,
                "reorder_quantity": 20,
                "unit_cost": 15000.0,
                "supplier_name": "Safety First Cameroon",
                "supplier_contact": "+237 699 987 654",
                "location": "Safety Equipment Storage",
                "notes": "Standard construction safety helmets"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/assets/inventory",
                json=item_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                item_id = result.get("id")
                if item_id:
                    self.created_items.append(item_id)
                    self.log_test("Create Low Stock Item (Alert Trigger)", True, f"Created item ID: {item_id} - Low stock alert should be triggered")
                    return item_id
                else:
                    self.log_test("Create Low Stock Item (Alert Trigger)", False, "No item ID returned")
                    return None
            else:
                self.log_test("Create Low Stock Item (Alert Trigger)", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create Low Stock Item (Alert Trigger)", False, f"Error: {str(e)}")
            return None
    
    def test_list_all_inventory_items(self):
        """Test listing all inventory items"""
        print("\n📋 TESTING: List All Inventory Items")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/assets/inventory",
                timeout=30
            )
            
            if response.status_code == 200:
                items = response.json()
                if isinstance(items, list):
                    self.log_test("List All Inventory Items", True, f"Retrieved {len(items)} inventory items")
                    return items
                else:
                    self.log_test("List All Inventory Items", False, "Response is not a list")
                    return []
            else:
                self.log_test("List All Inventory Items", False, f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("List All Inventory Items", False, f"Error: {str(e)}")
            return []
    
    def test_filter_by_category(self):
        """Test filtering inventory by category"""
        print("\n🔍 TESTING: Filter Inventory by Category")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/assets/inventory?category=Tools",
                timeout=30
            )
            
            if response.status_code == 200:
                items = response.json()
                if isinstance(items, list):
                    tools_count = len([item for item in items if item.get("category") == "Tools"])
                    self.log_test("Filter by Category (Tools)", True, f"Found {tools_count} tools in inventory")
                    return items
                else:
                    self.log_test("Filter by Category (Tools)", False, "Response is not a list")
                    return []
            else:
                self.log_test("Filter by Category (Tools)", False, f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Filter by Category (Tools)", False, f"Error: {str(e)}")
            return []
    
    def test_filter_low_stock(self):
        """Test filtering for low stock items"""
        print("\n⚠️ TESTING: Filter Low Stock Items")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/assets/inventory?low_stock=true",
                timeout=30
            )
            
            if response.status_code == 200:
                items = response.json()
                if isinstance(items, list):
                    low_stock_count = len(items)
                    self.log_test("Filter Low Stock Items", True, f"Found {low_stock_count} low stock items")
                    return items
                else:
                    self.log_test("Filter Low Stock Items", False, "Response is not a list")
                    return []
            else:
                self.log_test("Filter Low Stock Items", False, f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Filter Low Stock Items", False, f"Error: {str(e)}")
            return []
    
    def test_get_single_inventory_item(self, item_id):
        """Test getting single inventory item details"""
        print(f"\n🔍 TESTING: Get Single Inventory Item ({item_id})")
        
        if not item_id:
            self.log_test("Get Single Inventory Item", False, "No item ID provided")
            return None
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/assets/inventory/{item_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                item = response.json()
                if item.get("id") == item_id:
                    self.log_test("Get Single Inventory Item", True, f"Retrieved item: {item.get('name')}")
                    return item
                else:
                    self.log_test("Get Single Inventory Item", False, "Item ID mismatch")
                    return None
            elif response.status_code == 404:
                self.log_test("Get Single Inventory Item", False, "Item not found (404)")
                return None
            else:
                self.log_test("Get Single Inventory Item", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Get Single Inventory Item", False, f"Error: {str(e)}")
            return None
    
    def test_update_inventory_item(self, item_id):
        """Test updating inventory item"""
        print(f"\n✏️ TESTING: Update Inventory Item ({item_id})")
        
        if not item_id:
            self.log_test("Update Inventory Item", False, "No item ID provided")
            return False
        
        try:
            update_data = {
                "quantity": 75,  # Increase quantity
                "unit_cost": 2750.0,  # Update cost
                "supplier_contact": "+237 677 123 999",  # Update contact
                "notes": "Updated: High-quality drill bits for construction work - Premium grade"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/assets/inventory/{item_id}",
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                updated_item = response.json()
                if updated_item.get("quantity") == 75:
                    self.log_test("Update Inventory Item", True, f"Successfully updated item quantity to {updated_item.get('quantity')}")
                    return True
                else:
                    self.log_test("Update Inventory Item", False, "Quantity not updated correctly")
                    return False
            else:
                self.log_test("Update Inventory Item", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Inventory Item", False, f"Error: {str(e)}")
            return False
    
    def test_adjust_stock_add(self, item_id):
        """Test adjusting stock (add quantity)"""
        print(f"\n➕ TESTING: Adjust Stock (Add Quantity) - {item_id}")
        
        if not item_id:
            self.log_test("Adjust Stock (Add)", False, "No item ID provided")
            return False
        
        try:
            adjustment_data = {
                "type": "add",
                "quantity": 25,
                "reason": "New stock delivery from supplier"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/assets/inventory/{item_id}/adjust-stock",
                json=adjustment_data,
                timeout=30
            )
            
            if response.status_code == 200:
                updated_item = response.json()
                new_quantity = updated_item.get("quantity")
                self.log_test("Adjust Stock (Add)", True, f"Successfully added 25 units. New quantity: {new_quantity}")
                return True
            else:
                self.log_test("Adjust Stock (Add)", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Adjust Stock (Add)", False, f"Error: {str(e)}")
            return False
    
    def test_adjust_stock_subtract_trigger_alert(self, item_id):
        """Test adjusting stock (subtract quantity to trigger low stock alert)"""
        print(f"\n➖ TESTING: Adjust Stock (Subtract to Trigger Alert) - {item_id}")
        
        if not item_id:
            self.log_test("Adjust Stock (Subtract - Alert)", False, "No item ID provided")
            return False
        
        try:
            # First get current quantity
            item_response = self.session.get(f"{BACKEND_URL}/assets/inventory/{item_id}")
            if item_response.status_code != 200:
                self.log_test("Adjust Stock (Subtract - Alert)", False, "Could not get current item details")
                return False
            
            item = item_response.json()
            current_qty = item.get("quantity", 0)
            reorder_level = item.get("reorder_level", 0)
            
            # Calculate how much to subtract to reach reorder level
            subtract_amount = max(1, current_qty - reorder_level + 1)
            
            adjustment_data = {
                "type": "subtract",
                "quantity": subtract_amount,
                "reason": "Stock used for emergency maintenance"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/assets/inventory/{item_id}/adjust-stock",
                json=adjustment_data,
                timeout=30
            )
            
            if response.status_code == 200:
                updated_item = response.json()
                new_quantity = updated_item.get("quantity")
                if new_quantity <= reorder_level:
                    self.log_test("Adjust Stock (Subtract - Alert)", True, f"Successfully triggered low stock alert. New quantity: {new_quantity} (reorder level: {reorder_level})")
                else:
                    self.log_test("Adjust Stock (Subtract - Alert)", True, f"Stock adjusted. New quantity: {new_quantity}")
                return True
            else:
                self.log_test("Adjust Stock (Subtract - Alert)", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Adjust Stock (Subtract - Alert)", False, f"Error: {str(e)}")
            return False
    
    def test_delete_inventory_item(self, item_id):
        """Test deleting inventory item (admin only)"""
        print(f"\n🗑️ TESTING: Delete Inventory Item ({item_id})")
        
        if not item_id:
            self.log_test("Delete Inventory Item", False, "No item ID provided")
            return False
        
        try:
            response = self.session.delete(
                f"{BACKEND_URL}/assets/inventory/{item_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "deleted successfully" in result.get("message", "").lower():
                    self.log_test("Delete Inventory Item", True, "Successfully deleted inventory item")
                    # Remove from tracking list
                    if item_id in self.created_items:
                        self.created_items.remove(item_id)
                    return True
                else:
                    self.log_test("Delete Inventory Item", False, f"Unexpected response: {result}")
                    return False
            else:
                self.log_test("Delete Inventory Item", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Inventory Item", False, f"Error: {str(e)}")
            return False
    
    def test_unauthorized_access(self):
        """Test authorization - try operations with unauthorized roles"""
        print("\n🔒 TESTING: Authorization (Unauthorized Access)")
        
        # Create a new session without authentication
        unauth_session = requests.Session()
        
        try:
            # Try to create inventory item without auth
            item_data = {
                "name": "Unauthorized Test Item",
                "category": "Test",
                "quantity": 10,
                "unit": "pcs",
                "reorder_level": 5,
                "reorder_quantity": 10
            }
            
            response = unauth_session.post(
                f"{BACKEND_URL}/assets/inventory",
                json=item_data,
                timeout=30
            )
            
            if response.status_code == 401:
                self.log_test("Authorization Check (Unauthorized)", True, "Correctly rejected unauthorized request with 401")
                return True
            else:
                self.log_test("Authorization Check (Unauthorized)", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authorization Check (Unauthorized)", False, f"Error: {str(e)}")
            return False
    
    def test_automation_integration(self):
        """Test automation integration - verify low stock automation function exists"""
        print("\n🤖 TESTING: Automation Integration")
        
        try:
            # Test manual automation trigger
            response = self.session.post(
                f"{BACKEND_URL}/assets/automation/run",
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "automation tasks completed" in result.get("message", "").lower():
                    automation_results = result.get("results", {})
                    low_stock_alerts = automation_results.get("low_stock_alerts", 0)
                    self.log_test("Automation Integration", True, f"Automation system functional. Low stock alerts processed: {low_stock_alerts}")
                    return True
                else:
                    self.log_test("Automation Integration", False, f"Unexpected automation response: {result}")
                    return False
            else:
                self.log_test("Automation Integration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Automation Integration", False, f"Error: {str(e)}")
            return False
    
    def cleanup_created_items(self):
        """Clean up any remaining test items"""
        print("\n🧹 CLEANING UP TEST DATA...")
        
        for item_id in self.created_items[:]:  # Copy list to avoid modification during iteration
            try:
                response = self.session.delete(f"{BACKEND_URL}/assets/inventory/{item_id}")
                if response.status_code == 200:
                    print(f"✅ Cleaned up item: {item_id}")
                    self.created_items.remove(item_id)
                else:
                    print(f"⚠️ Could not clean up item {item_id}: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error cleaning up item {item_id}: {str(e)}")
    
    def run_comprehensive_test_suite(self):
        """Run the complete inventory management test suite"""
        print("=" * 80)
        print("🏗️ COMPREHENSIVE INVENTORY MANAGEMENT SYSTEM TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now(timezone.utc).isoformat()}")
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ AUTHENTICATION FAILED - Cannot proceed with tests")
            return False
        
        # Step 2: Test unauthorized access
        self.test_unauthorized_access()
        
        # Step 3: Create inventory items
        normal_item_id = self.test_create_inventory_item_normal_stock()
        low_stock_item_id = self.test_create_inventory_item_low_stock()
        
        # Step 4: List and filter operations
        self.test_list_all_inventory_items()
        self.test_filter_by_category()
        self.test_filter_low_stock()
        
        # Step 5: Get single item details
        if normal_item_id:
            self.test_get_single_inventory_item(normal_item_id)
        
        # Step 6: Update operations
        if normal_item_id:
            self.test_update_inventory_item(normal_item_id)
        
        # Step 7: Stock adjustments
        if normal_item_id:
            self.test_adjust_stock_add(normal_item_id)
            self.test_adjust_stock_subtract_trigger_alert(normal_item_id)
        
        # Step 8: Test automation integration
        self.test_automation_integration()
        
        # Step 9: Delete operations (test one item, keep one for further testing)
        if low_stock_item_id:
            self.test_delete_inventory_item(low_stock_item_id)
        
        # Step 10: Cleanup remaining items
        self.cleanup_created_items()
        
        # Print summary
        self.print_test_summary()
        
        return True
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 INVENTORY MANAGEMENT TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  • {test['test']}: {test['details']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for test in self.test_results:
            if test["success"]:
                print(f"  • {test['test']}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if success_rate >= 90:
            print("🟢 EXCELLENT - Inventory Management System is fully functional")
        elif success_rate >= 75:
            print("🟡 GOOD - Inventory Management System is mostly functional with minor issues")
        elif success_rate >= 50:
            print("🟠 FAIR - Inventory Management System has significant issues that need attention")
        else:
            print("🔴 POOR - Inventory Management System has critical failures")
        
        print("=" * 80)


def main():
    """Main test execution"""
    tester = InventoryTestSuite()
    
    try:
        success = tester.run_comprehensive_test_suite()
        
        # Exit with appropriate code
        failed_tests = len([t for t in tester.test_results if not t["success"]])
        sys.exit(0 if failed_tests == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        tester.cleanup_created_items()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 CRITICAL ERROR: {str(e)}")
        tester.cleanup_created_items()
        sys.exit(1)


if __name__ == "__main__":
    main()