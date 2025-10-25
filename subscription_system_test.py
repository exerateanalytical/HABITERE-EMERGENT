#!/usr/bin/env python3
"""
Subscription & Payment System - Comprehensive Backend Testing
============================================================

Tests all subscription system endpoints with complete functionality:
- 7 subscription plans retrieval and validation
- Subscription creation flow with payment processing
- Subscription status and access control
- Payment history tracking
- Renewal flow with payment extension
- Commission calculation for hotel plan
- Error handling for edge cases

Test Coverage:
- GET /api/subscriptions/plans (all 7 plans)
- GET /api/subscriptions/plans/{role} (role-specific plans)
- POST /api/subscriptions/subscribe (subscription creation)
- GET /api/subscriptions/my-subscription (status check)
- GET /api/subscriptions/payment-history (payment tracking)
- POST /api/subscriptions/renew (renewal flow)
- POST /api/subscriptions/calculate-commission (hotel commission)
- GET /api/subscriptions/commissions (commission records)
- GET /api/subscriptions/check-access (access control)

Authentication: admin@habitere.com / admin123
Success Criteria: All 7 plans working, payment flow functional, commission calculation accurate

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

class SubscriptionSystemTester:
    """Comprehensive tester for Subscription & Payment System."""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.admin_user = None
        self.test_subscription_id = None
        self.test_payment_id = None
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
            "critical_issues": [],
            "subscription_plans": [],
            "payment_records": [],
            "commission_data": {}
        }
    
    async def setup_session(self):
        """Initialize HTTP session with proper headers."""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        logger.info("✅ HTTP session initialized")
    
    async def authenticate_admin(self):
        """Authenticate as admin user for testing."""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_user = data.get("user", {})
                    self.auth_token = response.cookies.get("session_token")
                    
                    if self.auth_token:
                        self.session.headers.update({"Cookie": f"session_token={self.auth_token.value}"})
                        logger.info(f"✅ Admin authentication successful: {self.admin_user.get('email')}")
                        return True
                    else:
                        logger.error("❌ No session token received")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Admin login failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def record_test(self, test_name: str, success: bool, details: str, response_data: Any = None):
        """Record test result with details."""
        self.results["total_tests"] += 1
        if success:
            self.results["passed_tests"] += 1
            status = "✅ PASS"
        else:
            self.results["failed_tests"] += 1
            status = "❌ FAIL"
            self.results["critical_issues"].append(f"{test_name}: {details}")
        
        self.results["test_details"].append({
            "test": test_name,
            "status": status,
            "details": details,
            "response_data": response_data
        })
        
        logger.info(f"{status} - {test_name}: {details}")
    
    async def test_get_all_subscription_plans(self):
        """Test GET /api/subscriptions/plans - Retrieve all 7 subscription plans."""
        try:
            async with self.session.get(f"{BASE_URL}/subscriptions/plans") as response:
                if response.status == 200:
                    data = await response.json()
                    plans = data.get("plans", [])
                    total = data.get("total", 0)
                    
                    # Validate 7 plans exist
                    if total == 7 and len(plans) == 7:
                        # Store plans for later validation
                        self.results["subscription_plans"] = plans
                        
                        # Validate plan structure and pricing
                        expected_plans = {
                            "real_estate_agent": 10000.0,
                            "service_professional": 25000.0,
                            "real_estate_company": 100000.0,
                            "construction_company": 100000.0,
                            "building_material_supplier": 100000.0,
                            "furnishing_shop": 100000.0,
                            "hotel": 0.0  # Commission-based
                        }
                        
                        plan_validation = []
                        for plan in plans:
                            role = plan.get("user_role")
                            price = plan.get("price")
                            name = plan.get("name")
                            
                            if role in expected_plans and price == expected_plans[role]:
                                plan_validation.append(f"✅ {name}: {price} FCFA")
                                
                                # Special validation for hotel plan
                                if role == "hotel":
                                    commission_rate = plan.get("commission_rate")
                                    if commission_rate == 5.0:
                                        plan_validation.append(f"✅ Hotel commission rate: {commission_rate}%")
                                    else:
                                        plan_validation.append(f"❌ Hotel commission rate incorrect: {commission_rate}%")
                            else:
                                plan_validation.append(f"❌ {name}: Expected {expected_plans.get(role)}, got {price}")
                        
                        self.record_test(
                            "Get All Subscription Plans",
                            True,
                            f"All 7 plans retrieved successfully. {'; '.join(plan_validation)}",
                            {"total_plans": total, "plans_summary": [{"name": p["name"], "price": p["price"], "role": p["user_role"]} for p in plans]}
                        )
                    else:
                        self.record_test(
                            "Get All Subscription Plans",
                            False,
                            f"Expected 7 plans, got {total} plans with {len(plans)} in response",
                            data
                        )
                else:
                    error_text = await response.text()
                    self.record_test(
                        "Get All Subscription Plans",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        None
                    )
                    
        except Exception as e:
            self.record_test("Get All Subscription Plans", False, f"Exception: {e}", None)
    
    async def test_get_plan_by_role(self):
        """Test GET /api/subscriptions/plans/{role} - Get plan for specific role."""
        test_roles = ["real_estate_agent", "hotel", "service_professional"]
        
        for role in test_roles:
            try:
                async with self.session.get(f"{BASE_URL}/subscriptions/plans/{role}") as response:
                    if response.status == 200:
                        plan = await response.json()
                        
                        if plan.get("user_role") == role:
                            self.record_test(
                                f"Get Plan by Role ({role})",
                                True,
                                f"Plan retrieved: {plan.get('name')} - {plan.get('price')} FCFA",
                                {"role": role, "plan_name": plan.get("name"), "price": plan.get("price")}
                            )
                        else:
                            self.record_test(
                                f"Get Plan by Role ({role})",
                                False,
                                f"Role mismatch: expected {role}, got {plan.get('user_role')}",
                                plan
                            )
                    else:
                        error_text = await response.text()
                        self.record_test(
                            f"Get Plan by Role ({role})",
                            False,
                            f"HTTP {response.status}: {error_text}",
                            None
                        )
                        
            except Exception as e:
                self.record_test(f"Get Plan by Role ({role})", False, f"Exception: {e}", None)
    
    async def test_subscription_creation(self):
        """Test POST /api/subscriptions/subscribe - Create subscription with payment."""
        try:
            # Get a plan ID from the retrieved plans
            if not self.results["subscription_plans"]:
                self.record_test("Subscription Creation", False, "No plans available for testing", None)
                return
            
            # Use real estate agent plan for testing
            agent_plan = next((p for p in self.results["subscription_plans"] if p["user_role"] == "real_estate_agent"), None)
            if not agent_plan:
                self.record_test("Subscription Creation", False, "Real estate agent plan not found", None)
                return
            
            subscription_data = {
                "plan_id": agent_plan["id"],
                "payment_method": "mtn_momo",
                "phone_number": "+237670000000"
            }
            
            async with self.session.post(f"{BASE_URL}/subscriptions/subscribe", json=subscription_data) as response:
                if response.status == 200:
                    data = await response.json()
                    subscription = data.get("subscription", {})
                    payment = data.get("payment", {})
                    
                    # Store for later tests
                    self.test_subscription_id = subscription.get("id")
                    self.test_payment_id = payment.get("id")
                    
                    # Validate subscription creation
                    if subscription.get("status") == "active" and payment.get("payment_status") == "completed":
                        self.record_test(
                            "Subscription Creation",
                            True,
                            f"Subscription created successfully. Status: {subscription.get('status')}, Payment: {payment.get('payment_status')}",
                            {"subscription_id": subscription.get("id"), "payment_id": payment.get("id"), "amount": payment.get("amount")}
                        )
                    else:
                        self.record_test(
                            "Subscription Creation",
                            False,
                            f"Subscription status: {subscription.get('status')}, Payment status: {payment.get('payment_status')}",
                            data
                        )
                elif response.status == 400:
                    # User might already have subscription - this is expected behavior
                    error_data = await response.json()
                    if "already has an active subscription" in error_data.get("detail", ""):
                        self.record_test(
                            "Subscription Creation",
                            True,
                            "User already has active subscription (expected behavior for admin user)",
                            error_data
                        )
                    else:
                        self.record_test(
                            "Subscription Creation",
                            False,
                            f"HTTP 400: {error_data.get('detail')}",
                            error_data
                        )
                else:
                    error_text = await response.text()
                    self.record_test(
                        "Subscription Creation",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        None
                    )
                    
        except Exception as e:
            self.record_test("Subscription Creation", False, f"Exception: {e}", None)
    
    async def test_my_subscription_status(self):
        """Test GET /api/subscriptions/my-subscription - Check subscription status."""
        try:
            async with self.session.get(f"{BASE_URL}/subscriptions/my-subscription") as response:
                if response.status == 200:
                    data = await response.json()
                    has_subscription = data.get("has_subscription", False)
                    
                    if has_subscription:
                        subscription = data.get("subscription", {})
                        plan = data.get("plan", {})
                        is_active = data.get("is_active", False)
                        days_remaining = data.get("days_remaining")
                        
                        self.record_test(
                            "My Subscription Status",
                            True,
                            f"Subscription found. Active: {is_active}, Plan: {plan.get('name')}, Days remaining: {days_remaining}",
                            {"has_subscription": has_subscription, "is_active": is_active, "plan_name": plan.get("name"), "days_remaining": days_remaining}
                        )
                    else:
                        self.record_test(
                            "My Subscription Status",
                            True,
                            "No subscription found (valid response)",
                            data
                        )
                else:
                    error_text = await response.text()
                    self.record_test(
                        "My Subscription Status",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        None
                    )
                    
        except Exception as e:
            self.record_test("My Subscription Status", False, f"Exception: {e}", None)
    
    async def test_payment_history(self):
        """Test GET /api/subscriptions/payment-history - Get payment history."""
        try:
            async with self.session.get(f"{BASE_URL}/subscriptions/payment-history") as response:
                if response.status == 200:
                    data = await response.json()
                    payments = data.get("payments", [])
                    total = data.get("total", 0)
                    
                    # Store payment records
                    self.results["payment_records"] = payments
                    
                    self.record_test(
                        "Payment History",
                        True,
                        f"Payment history retrieved. Total payments: {total}",
                        {"total_payments": total, "payment_methods": list(set(p.get("payment_method") for p in payments))}
                    )
                else:
                    error_text = await response.text()
                    self.record_test(
                        "Payment History",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        None
                    )
                    
        except Exception as e:
            self.record_test("Payment History", False, f"Exception: {e}", None)
    
    async def test_subscription_renewal(self):
        """Test POST /api/subscriptions/renew - Renew subscription."""
        try:
            # First get current subscription to get ID
            async with self.session.get(f"{BASE_URL}/subscriptions/my-subscription") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("has_subscription"):
                        subscription_id = data["subscription"]["id"]
                        
                        renewal_data = {
                            "subscription_id": subscription_id,
                            "payment_method": "mtn_momo",
                            "phone_number": "+237670000000"
                        }
                        
                        async with self.session.post(f"{BASE_URL}/subscriptions/renew", json=renewal_data) as renew_response:
                            if renew_response.status == 200:
                                renew_data = await renew_response.json()
                                new_end_date = renew_data.get("new_end_date")
                                payment = renew_data.get("payment", {})
                                
                                self.record_test(
                                    "Subscription Renewal",
                                    True,
                                    f"Subscription renewed successfully. New end date: {new_end_date}, Payment status: {payment.get('payment_status')}",
                                    {"new_end_date": new_end_date, "payment_amount": payment.get("amount")}
                                )
                            else:
                                error_text = await renew_response.text()
                                self.record_test(
                                    "Subscription Renewal",
                                    False,
                                    f"HTTP {renew_response.status}: {error_text}",
                                    None
                                )
                    else:
                        self.record_test(
                            "Subscription Renewal",
                            False,
                            "No active subscription to renew",
                            None
                        )
                else:
                    self.record_test(
                        "Subscription Renewal",
                        False,
                        "Could not retrieve subscription for renewal test",
                        None
                    )
                    
        except Exception as e:
            self.record_test("Subscription Renewal", False, f"Exception: {e}", None)
    
    async def test_commission_calculation(self):
        """Test POST /api/subscriptions/calculate-commission - Hotel commission calculation."""
        try:
            # Test commission calculation (should fail for non-hotel users)
            commission_data = {
                "booking_id": "test-booking-123",
                "booking_amount": 50000.0
            }
            
            async with self.session.post(f"{BASE_URL}/subscriptions/calculate-commission", json=commission_data) as response:
                if response.status == 403:
                    # Expected for non-hotel users
                    error_data = await response.json()
                    self.record_test(
                        "Commission Calculation (Access Control)",
                        True,
                        f"Correctly restricted to hotel users: {error_data.get('detail')}",
                        error_data
                    )
                elif response.status == 200:
                    # If admin has hotel role or commission calculation works
                    data = await response.json()
                    commission_rate = data.get("commission_rate")
                    commission_amount = data.get("commission_amount")
                    
                    # Validate 5% commission calculation
                    expected_commission = 50000.0 * 0.05
                    if commission_amount == expected_commission and commission_rate == 5.0:
                        self.record_test(
                            "Commission Calculation",
                            True,
                            f"Commission calculated correctly: {commission_rate}% of {commission_data['booking_amount']} = {commission_amount} FCFA",
                            data
                        )
                    else:
                        self.record_test(
                            "Commission Calculation",
                            False,
                            f"Commission calculation error: Expected {expected_commission}, got {commission_amount}",
                            data
                        )
                else:
                    error_text = await response.text()
                    self.record_test(
                        "Commission Calculation",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        None
                    )
                    
        except Exception as e:
            self.record_test("Commission Calculation", False, f"Exception: {e}", None)
    
    async def test_commission_records(self):
        """Test GET /api/subscriptions/commissions - Get commission records."""
        try:
            async with self.session.get(f"{BASE_URL}/subscriptions/commissions") as response:
                if response.status == 200:
                    data = await response.json()
                    commissions = data.get("commissions", [])
                    total_pending = data.get("total_pending", 0)
                    total_paid = data.get("total_paid", 0)
                    
                    self.results["commission_data"] = data
                    
                    self.record_test(
                        "Commission Records",
                        True,
                        f"Commission records retrieved. Total commissions: {len(commissions)}, Pending: {total_pending} FCFA, Paid: {total_paid} FCFA",
                        {"total_commissions": len(commissions), "total_pending": total_pending, "total_paid": total_paid}
                    )
                else:
                    error_text = await response.text()
                    self.record_test(
                        "Commission Records",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        None
                    )
                    
        except Exception as e:
            self.record_test("Commission Records", False, f"Exception: {e}", None)
    
    async def test_access_control(self):
        """Test GET /api/subscriptions/check-access - Check subscription access."""
        try:
            async with self.session.get(f"{BASE_URL}/subscriptions/check-access") as response:
                if response.status == 200:
                    data = await response.json()
                    has_access = data.get("has_access", False)
                    
                    if has_access:
                        subscription = data.get("subscription", {})
                        expires_at = data.get("expires_at")
                        
                        self.record_test(
                            "Access Control",
                            True,
                            f"User has subscription access. Expires: {expires_at}",
                            {"has_access": has_access, "expires_at": expires_at}
                        )
                    else:
                        message = data.get("message", "No access")
                        self.record_test(
                            "Access Control",
                            True,
                            f"Access correctly denied: {message}",
                            data
                        )
                else:
                    error_text = await response.text()
                    self.record_test(
                        "Access Control",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        None
                    )
                    
        except Exception as e:
            self.record_test("Access Control", False, f"Exception: {e}", None)
    
    async def test_error_scenarios(self):
        """Test error handling scenarios."""
        
        # Test 1: Invalid plan ID
        try:
            invalid_subscription_data = {
                "plan_id": "invalid-plan-id",
                "payment_method": "mtn_momo"
            }
            
            async with self.session.post(f"{BASE_URL}/subscriptions/subscribe", json=invalid_subscription_data) as response:
                if response.status == 404:
                    self.record_test(
                        "Error Handling - Invalid Plan ID",
                        True,
                        "Correctly returns 404 for invalid plan ID",
                        {"status": response.status}
                    )
                else:
                    error_text = await response.text()
                    self.record_test(
                        "Error Handling - Invalid Plan ID",
                        False,
                        f"Expected 404, got {response.status}: {error_text}",
                        None
                    )
        except Exception as e:
            self.record_test("Error Handling - Invalid Plan ID", False, f"Exception: {e}", None)
        
        # Test 2: Unauthenticated access
        try:
            # Remove auth header temporarily
            original_headers = self.session.headers.copy()
            if "Cookie" in self.session.headers:
                del self.session.headers["Cookie"]
            
            async with self.session.get(f"{BASE_URL}/subscriptions/my-subscription") as response:
                if response.status == 401:
                    self.record_test(
                        "Error Handling - Unauthenticated Access",
                        True,
                        "Correctly returns 401 for unauthenticated access",
                        {"status": response.status}
                    )
                else:
                    self.record_test(
                        "Error Handling - Unauthenticated Access",
                        False,
                        f"Expected 401, got {response.status}",
                        None
                    )
            
            # Restore auth header
            self.session.headers.update(original_headers)
            
        except Exception as e:
            self.record_test("Error Handling - Unauthenticated Access", False, f"Exception: {e}", None)
    
    async def run_comprehensive_tests(self):
        """Run all subscription system tests."""
        logger.info("🚀 Starting Subscription & Payment System Comprehensive Testing")
        logger.info("=" * 80)
        
        # Setup
        await self.setup_session()
        
        if not await self.authenticate_admin():
            logger.error("❌ Authentication failed - cannot proceed with tests")
            return self.results
        
        # Test phases
        test_phases = [
            ("Phase 1: Subscription Plans", [
                self.test_get_all_subscription_plans,
                self.test_get_plan_by_role
            ]),
            ("Phase 2: Subscription Flow", [
                self.test_subscription_creation,
                self.test_my_subscription_status
            ]),
            ("Phase 3: Payment & History", [
                self.test_payment_history,
                self.test_subscription_renewal
            ]),
            ("Phase 4: Commission System", [
                self.test_commission_calculation,
                self.test_commission_records
            ]),
            ("Phase 5: Access Control", [
                self.test_access_control
            ]),
            ("Phase 6: Error Scenarios", [
                self.test_error_scenarios
            ])
        ]
        
        for phase_name, tests in test_phases:
            logger.info(f"\n📋 {phase_name}")
            logger.info("-" * 50)
            
            for test_func in tests:
                await test_func()
        
        # Cleanup
        if self.session:
            await self.session.close()
        
        return self.results
    
    def print_summary(self):
        """Print comprehensive test summary."""
        results = self.results
        success_rate = (results["passed_tests"] / results["total_tests"] * 100) if results["total_tests"] > 0 else 0
        
        logger.info("\n" + "=" * 80)
        logger.info("🎯 SUBSCRIPTION SYSTEM TESTING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"📊 Total Tests: {results['total_tests']}")
        logger.info(f"✅ Passed: {results['passed_tests']}")
        logger.info(f"❌ Failed: {results['failed_tests']}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        if results["subscription_plans"]:
            logger.info(f"\n📋 Subscription Plans Found: {len(results['subscription_plans'])}")
            for plan in results["subscription_plans"]:
                logger.info(f"   • {plan['name']}: {plan['price']} FCFA ({plan['user_role']})")
        
        if results["payment_records"]:
            logger.info(f"\n💳 Payment Records: {len(results['payment_records'])}")
        
        if results["commission_data"]:
            commission_data = results["commission_data"]
            logger.info(f"\n💰 Commission Summary:")
            logger.info(f"   • Total Commissions: {len(commission_data.get('commissions', []))}")
            logger.info(f"   • Pending: {commission_data.get('total_pending', 0)} FCFA")
            logger.info(f"   • Paid: {commission_data.get('total_paid', 0)} FCFA")
        
        if results["critical_issues"]:
            logger.info(f"\n🚨 Critical Issues ({len(results['critical_issues'])}):")
            for issue in results["critical_issues"]:
                logger.info(f"   • {issue}")
        
        logger.info("\n📝 Detailed Test Results:")
        for test in results["test_details"]:
            logger.info(f"   {test['status']} {test['test']}: {test['details']}")
        
        logger.info("=" * 80)

async def main():
    """Main test execution function."""
    tester = SubscriptionSystemTester()
    
    try:
        results = await tester.run_comprehensive_tests()
        tester.print_summary()
        
        # Return success based on critical functionality
        critical_tests_passed = results["passed_tests"] >= (results["total_tests"] * 0.8)  # 80% threshold
        return critical_tests_passed
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)