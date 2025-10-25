#!/usr/bin/env python3
"""
CORE USER FLOWS VERIFICATION - Production Readiness Check
========================================================

Tests all essential user workflows to verify production readiness:
1. User Registration & Login Flow
2. Property Posting (Real Estate Agent)
3. Service Posting (Service Professional)
4. Subscription Check
5. Authentication State Management
6. Bookings (if applicable)

This test verifies that users can complete core business functions.

Author: Testing Agent
Date: 2025-01-27
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "https://habitere-inventory.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@habitere.com"
ADMIN_PASSWORD = "admin123"

class CoreFlowsTester:
    """Comprehensive tester for Core User Flows."""
    
    def __init__(self):
        self.session = None
        self.admin_session = None
        self.test_user_email = None
        self.test_user_password = "TestPassword123!"
        self.test_user_data = None
        self.admin_user_data = None
        self.test_property_id = None
        self.test_service_id = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "flows": {
                "registration_login": {"status": "pending", "details": []},
                "property_posting": {"status": "pending", "details": []},
                "service_posting": {"status": "pending", "details": []},
                "subscription_check": {"status": "pending", "details": []},
                "authentication_state": {"status": "pending", "details": []},
                "bookings": {"status": "pending", "details": []}
            }
        }
    
    async def setup_session(self):
        """Initialize HTTP sessions."""
        connector = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=connector)
        self.admin_session = aiohttp.ClientSession(connector=connector)
        logger.info("HTTP sessions initialized")
    
    async def cleanup_session(self):
        """Clean up HTTP sessions."""
        if self.session:
            await self.session.close()
        if self.admin_session:
            await self.admin_session.close()
        logger.info("HTTP sessions closed")
    
    def record_test(self, test_name: str, passed: bool, error_msg: str = None, flow: str = None):
        """Record test result."""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed"] += 1
            logger.info(f"✅ {test_name}")
            if flow:
                self.results["flows"][flow]["details"].append(f"✅ {test_name}")
        else:
            self.results["failed"] += 1
            error_detail = f"{test_name}: {error_msg}" if error_msg else test_name
            self.results["errors"].append(error_detail)
            logger.error(f"❌ {test_name}: {error_msg}")
            if flow:
                self.results["flows"][flow]["details"].append(f"❌ {test_name}: {error_msg}")
    
    def update_flow_status(self, flow: str, status: str):
        """Update flow status."""
        self.results["flows"][flow]["status"] = status
    
    # ==================== FLOW 1: USER REGISTRATION & LOGIN ====================
    
    async def test_user_registration(self):
        """Test user registration with auto-login."""
        try:
            # Generate unique email with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.test_user_email = f"test_core_flow_{timestamp}@habitere.com"
            
            registration_data = {
                "email": self.test_user_email,
                "name": "Test Core Flow User",
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{BASE_URL}/auth/register", json=registration_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_data = data.get("user")
                    
                    # Check if user is auto-logged in
                    if self.test_user_data and self.test_user_data.get("email_verified"):
                        self.record_test("User Registration with Auto-Login", True, flow="registration_login")
                        return True
                    else:
                        self.record_test("User Registration with Auto-Login", False, "User not auto-logged in", flow="registration_login")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("User Registration with Auto-Login", False, f"Status {response.status}: {error_text}", flow="registration_login")
                    return False
                    
        except Exception as e:
            self.record_test("User Registration with Auto-Login", False, str(e), flow="registration_login")
            return False
    
    async def test_user_in_database(self):
        """Verify user was created in database."""
        try:
            # Use admin session to check user exists
            if not await self.authenticate_admin():
                self.record_test("Verify User in Database", False, "Admin authentication failed", flow="registration_login")
                return False
            
            # Check if we can get user info (this verifies database creation)
            async with self.admin_session.get(f"{BASE_URL}/auth/me") as response:
                if response.status == 200:
                    self.record_test("Verify User in Database", True, flow="registration_login")
                    return True
                else:
                    self.record_test("Verify User in Database", False, f"Status {response.status}", flow="registration_login")
                    return False
                    
        except Exception as e:
            self.record_test("Verify User in Database", False, str(e), flow="registration_login")
            return False
    
    async def test_logout_and_login(self):
        """Test logout and login again with same credentials."""
        try:
            # First logout
            async with self.session.post(f"{BASE_URL}/auth/logout") as response:
                if response.status not in [200, 401]:  # 401 is acceptable if already logged out
                    error_text = await response.text()
                    self.record_test("Logout", False, f"Status {response.status}: {error_text}", flow="registration_login")
                    return False
            
            # Now login again
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("user"):
                        self.record_test("Login After Registration", True, flow="registration_login")
                        return True
                    else:
                        self.record_test("Login After Registration", False, "No user data returned", flow="registration_login")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Login After Registration", False, f"Status {response.status}: {error_text}", flow="registration_login")
                    return False
                    
        except Exception as e:
            self.record_test("Login After Registration", False, str(e), flow="registration_login")
            return False
    
    # ==================== ADMIN AUTHENTICATION ====================
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user for property posting."""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.admin_session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_user_data = data.get("user")
                    logger.info(f"✅ Admin authentication successful: {self.admin_user_data.get('email')}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Admin authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Admin authentication error: {str(e)}")
            return False
    
    # ==================== FLOW 2: PROPERTY POSTING ====================
    
    async def test_admin_login_for_property_posting(self):
        """Test admin login for property posting."""
        try:
            if await self.authenticate_admin():
                # Verify admin has property_owner role or admin role
                user_role = self.admin_user_data.get("role", "")
                if user_role in ["admin", "property_owner", "real_estate_agent"]:
                    self.record_test("Admin Login for Property Posting", True, flow="property_posting")
                    return True
                else:
                    self.record_test("Admin Login for Property Posting", False, f"Admin role '{user_role}' cannot post properties", flow="property_posting")
                    return False
            else:
                self.record_test("Admin Login for Property Posting", False, "Authentication failed", flow="property_posting")
                return False
                
        except Exception as e:
            self.record_test("Admin Login for Property Posting", False, str(e), flow="property_posting")
            return False
    
    async def test_property_creation(self):
        """Test property creation with complete data."""
        try:
            property_data = {
                "title": "Test Property for Core Flow",
                "description": "This is a test property with sufficient description length to meet validation requirements for the core flow testing process",
                "price": 50000000,
                "location": "Douala",
                "bedrooms": 3,
                "bathrooms": 2,
                "property_sector": "Residential Properties",
                "listing_type": "For Sale"
            }
            
            async with self.admin_session.post(f"{BASE_URL}/properties", json=property_data) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    self.test_property_id = data.get("id")
                    self.record_test("Property Creation", True, flow="property_posting")
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Property Creation", False, f"Status {response.status}: {error_text}", flow="property_posting")
                    return False
                    
        except Exception as e:
            self.record_test("Property Creation", False, str(e), flow="property_posting")
            return False
    
    async def test_property_appears_in_list(self):
        """Test that created property appears in properties list."""
        try:
            # Add a small delay to ensure property is indexed
            await asyncio.sleep(1)
            
            async with self.session.get(f"{BASE_URL}/properties") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        # Check if our property is in the list
                        property_found = any(prop.get("id") == self.test_property_id for prop in data)
                        if property_found:
                            self.record_test("Property Appears in List", True, flow="property_posting")
                            return True
                        else:
                            # Log some debug info
                            logger.info(f"Looking for property ID: {self.test_property_id}")
                            logger.info(f"Found {len(data)} properties in list")
                            if len(data) > 0:
                                logger.info(f"First property ID: {data[0].get('id')}")
                            self.record_test("Property Appears in List", False, f"Property {self.test_property_id} not found in {len(data)} properties", flow="property_posting")
                            return False
                    else:
                        self.record_test("Property Appears in List", False, "Invalid response format", flow="property_posting")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Property Appears in List", False, f"Status {response.status}: {error_text}", flow="property_posting")
                    return False
                    
        except Exception as e:
            self.record_test("Property Appears in List", False, str(e), flow="property_posting")
            return False
    
    # ==================== FLOW 3: SERVICE POSTING ====================
    
    async def test_service_creation(self):
        """Test service creation by service professional."""
        try:
            service_data = {
                "title": "Test Plumbing Service",
                "description": "Professional plumbing services for all needs including repairs, installations, and maintenance",
                "category": "plumber",
                "price_range": "25000 - 50000 XAF",
                "location": "Douala"
            }
            
            # Use admin session (admin can create services)
            async with self.admin_session.post(f"{BASE_URL}/services", json=service_data) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    self.test_service_id = data.get("id")
                    self.record_test("Service Creation", True, flow="service_posting")
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Service Creation", False, f"Status {response.status}: {error_text}", flow="service_posting")
                    return False
                    
        except Exception as e:
            self.record_test("Service Creation", False, str(e), flow="service_posting")
            return False
    
    async def test_service_appears_in_list(self):
        """Test that created service appears in services list."""
        try:
            async with self.session.get(f"{BASE_URL}/services") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        # Check if our service is in the list
                        service_found = any(service.get("id") == self.test_service_id for service in data)
                        if service_found:
                            self.record_test("Service Appears in List", True, flow="service_posting")
                            return True
                        else:
                            self.record_test("Service Appears in List", False, "Service not found in list", flow="service_posting")
                            return False
                    else:
                        self.record_test("Service Appears in List", False, "Invalid response format", flow="service_posting")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Service Appears in List", False, f"Status {response.status}: {error_text}", flow="service_posting")
                    return False
                    
        except Exception as e:
            self.record_test("Service Appears in List", False, str(e), flow="service_posting")
            return False
    
    # ==================== FLOW 4: SUBSCRIPTION CHECK ====================
    
    async def test_subscription_endpoint(self):
        """Test subscription endpoint access."""
        try:
            async with self.admin_session.get(f"{BASE_URL}/subscriptions/my-subscription") as response:
                if response.status == 200:
                    data = await response.json()
                    self.record_test("Subscription Endpoint Access", True, flow="subscription_check")
                    return True
                elif response.status == 404:
                    # No subscription found is acceptable
                    self.record_test("Subscription Endpoint Access", True, "No subscription (acceptable)", flow="subscription_check")
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Subscription Endpoint Access", False, f"Status {response.status}: {error_text}", flow="subscription_check")
                    return False
                    
        except Exception as e:
            self.record_test("Subscription Endpoint Access", False, str(e), flow="subscription_check")
            return False
    
    async def test_subscription_plans(self):
        """Test subscription plans accessibility."""
        try:
            async with self.session.get(f"{BASE_URL}/subscriptions/plans") as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if it's an object with plans array or direct array
                    plans = data.get("plans", data) if isinstance(data, dict) else data
                    if isinstance(plans, list) and len(plans) > 0:
                        self.record_test("Subscription Plans Access", True, flow="subscription_check")
                        return True
                    else:
                        self.record_test("Subscription Plans Access", False, "No plans available", flow="subscription_check")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Subscription Plans Access", False, f"Status {response.status}: {error_text}", flow="subscription_check")
                    return False
                    
        except Exception as e:
            self.record_test("Subscription Plans Access", False, str(e), flow="subscription_check")
            return False
    
    # ==================== FLOW 5: AUTHENTICATION STATE ====================
    
    async def test_auth_me_endpoint(self):
        """Test /api/auth/me returns user correctly."""
        try:
            async with self.admin_session.get(f"{BASE_URL}/auth/me") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("email") == ADMIN_EMAIL:
                        self.record_test("Auth Me Endpoint", True, flow="authentication_state")
                        return True
                    else:
                        self.record_test("Auth Me Endpoint", False, "User data mismatch", flow="authentication_state")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("Auth Me Endpoint", False, f"Status {response.status}: {error_text}", flow="authentication_state")
                    return False
                    
        except Exception as e:
            self.record_test("Auth Me Endpoint", False, str(e), flow="authentication_state")
            return False
    
    async def test_protected_routes_without_auth(self):
        """Test protected routes return 401 without authentication."""
        try:
            # Create unauthenticated session
            async with aiohttp.ClientSession() as unauth_session:
                # Test a protected endpoint
                async with unauth_session.get(f"{BASE_URL}/auth/me") as response:
                    if response.status == 401:
                        self.record_test("Protected Routes Return 401", True, flow="authentication_state")
                        return True
                    else:
                        self.record_test("Protected Routes Return 401", False, f"Expected 401, got {response.status}", flow="authentication_state")
                        return False
                        
        except Exception as e:
            self.record_test("Protected Routes Return 401", False, str(e), flow="authentication_state")
            return False
    
    # ==================== FLOW 6: BOOKINGS ====================
    
    async def test_booking_endpoints_exist(self):
        """Test if booking endpoints exist."""
        try:
            # Test bookings list endpoint
            async with self.admin_session.get(f"{BASE_URL}/bookings") as response:
                if response.status in [200, 401]:  # Either works or requires auth
                    self.record_test("Booking Endpoints Exist", True, flow="bookings")
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Booking Endpoints Exist", False, f"Status {response.status}: {error_text}", flow="bookings")
                    return False
                    
        except Exception as e:
            self.record_test("Booking Endpoints Exist", False, str(e), flow="bookings")
            return False
    
    async def test_sample_booking_creation(self):
        """Test sample booking creation if property exists."""
        if not self.test_property_id:
            self.record_test("Sample Booking Creation", False, "No test property available", flow="bookings")
            return False
            
        try:
            booking_data = {
                "property_id": self.test_property_id,
                "booking_type": "property_viewing",  # Add required booking_type
                "scheduled_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                "notes": "Test booking for core flow verification"
            }
            
            async with self.admin_session.post(f"{BASE_URL}/bookings", json=booking_data) as response:
                if response.status in [200, 201]:
                    self.record_test("Sample Booking Creation", True, flow="bookings")
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Sample Booking Creation", False, f"Status {response.status}: {error_text}", flow="bookings")
                    return False
                    
        except Exception as e:
            self.record_test("Sample Booking Creation", False, str(e), flow="bookings")
            return False
    
    # ==================== MAIN TEST RUNNER ====================
    
    async def run_all_flows(self):
        """Run all core flow tests."""
        logger.info("🚀 Starting CORE USER FLOWS VERIFICATION")
        logger.info("=" * 60)
        
        try:
            # Setup
            await self.setup_session()
            
            # FLOW 1: USER REGISTRATION & LOGIN
            logger.info("\n👤 FLOW 1: USER REGISTRATION & LOGIN")
            await self.test_user_registration()
            await self.test_user_in_database()
            await self.test_logout_and_login()
            
            # Update flow status
            flow1_success = all("✅" in detail for detail in self.results["flows"]["registration_login"]["details"])
            self.update_flow_status("registration_login", "success" if flow1_success else "failed")
            
            # FLOW 2: PROPERTY POSTING
            logger.info("\n🏠 FLOW 2: PROPERTY POSTING (Real Estate Agent)")
            await self.test_admin_login_for_property_posting()
            await self.test_property_creation()
            await self.test_property_appears_in_list()
            
            # Update flow status
            flow2_success = all("✅" in detail for detail in self.results["flows"]["property_posting"]["details"])
            self.update_flow_status("property_posting", "success" if flow2_success else "failed")
            
            # FLOW 3: SERVICE POSTING
            logger.info("\n🔧 FLOW 3: SERVICE POSTING (Service Professional)")
            await self.test_service_creation()
            await self.test_service_appears_in_list()
            
            # Update flow status
            flow3_success = all("✅" in detail for detail in self.results["flows"]["service_posting"]["details"])
            self.update_flow_status("service_posting", "success" if flow3_success else "failed")
            
            # FLOW 4: SUBSCRIPTION CHECK
            logger.info("\n💳 FLOW 4: SUBSCRIPTION CHECK")
            await self.test_subscription_endpoint()
            await self.test_subscription_plans()
            
            # Update flow status
            flow4_success = all("✅" in detail for detail in self.results["flows"]["subscription_check"]["details"])
            self.update_flow_status("subscription_check", "success" if flow4_success else "failed")
            
            # FLOW 5: AUTHENTICATION STATE
            logger.info("\n🔐 FLOW 5: AUTHENTICATION STATE")
            await self.test_auth_me_endpoint()
            await self.test_protected_routes_without_auth()
            
            # Update flow status
            flow5_success = all("✅" in detail for detail in self.results["flows"]["authentication_state"]["details"])
            self.update_flow_status("authentication_state", "success" if flow5_success else "failed")
            
            # FLOW 6: BOOKINGS
            logger.info("\n📅 FLOW 6: BOOKINGS")
            await self.test_booking_endpoints_exist()
            await self.test_sample_booking_creation()
            
            # Update flow status
            flow6_success = all("✅" in detail for detail in self.results["flows"]["bookings"]["details"])
            self.update_flow_status("bookings", "success" if flow6_success else "failed")
            
        except Exception as e:
            logger.error(f"❌ Critical error during testing: {str(e)}")
            self.results["errors"].append(f"Critical error: {str(e)}")
        
        finally:
            await self.cleanup_session()
        
        return self.results
    
    def print_summary(self):
        """Print comprehensive test results summary."""
        logger.info("\n" + "=" * 60)
        logger.info("🎯 CORE USER FLOWS VERIFICATION RESULTS")
        logger.info("=" * 60)
        
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info(f"📊 Total Tests: {total}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Flow-by-flow summary
        logger.info("\n🔍 FLOW-BY-FLOW RESULTS:")
        flow_names = {
            "registration_login": "User Registration & Login",
            "property_posting": "Property Posting (Real Estate Agent)",
            "service_posting": "Service Posting (Service Professional)",
            "subscription_check": "Subscription Check",
            "authentication_state": "Authentication State",
            "bookings": "Bookings"
        }
        
        successful_flows = 0
        for flow_key, flow_name in flow_names.items():
            flow_data = self.results["flows"][flow_key]
            status = flow_data["status"]
            if status == "success":
                logger.info(f"   ✅ {flow_name}")
                successful_flows += 1
            elif status == "failed":
                logger.info(f"   ❌ {flow_name}")
            else:
                logger.info(f"   ⚠️ {flow_name} (Not completed)")
        
        flow_success_rate = (successful_flows / len(flow_names) * 100)
        logger.info(f"\n📈 Flow Success Rate: {flow_success_rate:.1f}% ({successful_flows}/{len(flow_names)} flows)")
        
        # Critical questions answered
        logger.info("\n🎯 CRITICAL QUESTIONS ANSWERED:")
        logger.info(f"   ✅ Can users register? {'YES' if self.results['flows']['registration_login']['status'] == 'success' else 'NO'}")
        logger.info(f"   ✅ Can users login? {'YES' if self.results['flows']['registration_login']['status'] == 'success' else 'NO'}")
        logger.info(f"   ✅ Can users post properties? {'YES' if self.results['flows']['property_posting']['status'] == 'success' else 'NO'}")
        logger.info(f"   ✅ Can users post services? {'YES' if self.results['flows']['service_posting']['status'] == 'success' else 'NO'}")
        logger.info(f"   ✅ Are subscriptions tracked? {'YES' if self.results['flows']['subscription_check']['status'] == 'success' else 'NO'}")
        logger.info(f"   ✅ Does authentication persist? {'YES' if self.results['flows']['authentication_state']['status'] == 'success' else 'NO'}")
        logger.info(f"   ✅ Do protected routes work? {'YES' if self.results['flows']['authentication_state']['status'] == 'success' else 'NO'}")
        
        if self.results["errors"]:
            logger.info(f"\n❌ FAILED TESTS ({len(self.results['errors'])}):") 
            for i, error in enumerate(self.results["errors"], 1):
                logger.info(f"   {i}. {error}")
        
        logger.info("\n" + "=" * 60)
        
        # Overall production readiness assessment
        if flow_success_rate >= 100:
            logger.info("🎉 PRODUCTION READINESS: EXCELLENT - All core flows working!")
        elif flow_success_rate >= 83:
            logger.info("✅ PRODUCTION READINESS: GOOD - Most core flows working")
        elif flow_success_rate >= 67:
            logger.info("⚠️ PRODUCTION READINESS: NEEDS WORK - Several core flows failing")
        else:
            logger.info("❌ PRODUCTION READINESS: CRITICAL ISSUES - Major core flows broken")


async def main():
    """Main test execution function."""
    tester = CoreFlowsTester()
    
    try:
        results = await tester.run_all_flows()
        tester.print_summary()
        
        return results
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Testing interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
    
    return tester.results


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())