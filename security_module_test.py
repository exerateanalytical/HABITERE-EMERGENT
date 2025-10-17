#!/usr/bin/env python3
"""
Comprehensive Backend Testing - Homeland Security Module
========================================================

This script tests all 14 API endpoints of the new Homeland Security module
for the Habitere platform. Tests include:

1. Statistics (Public) - GET /api/security/stats
2. Service Marketplace (5 endpoints)
3. Guard Recruitment (4 endpoints) 
4. Booking System (4 endpoints)

Test Categories:
- Public endpoints (no auth required)
- Protected endpoints (auth required)
- Role-based authorization
- Data validation
- Error handling
- Complete workflows

Author: Testing Agent
Date: 2025-01-27
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fastapi-modules-1.preview.emergentagent.com')
BASE_URL = f"{BACKEND_URL}/api"

# Test data for realistic testing
TEST_USERS = {
    "admin": {
        "email": "admin@habitere.com",
        "password": "admin123",
        "name": "Admin User",
        "expected_role": "admin"
    },
    "security_provider": {
        "email": "security.provider@habitere.com", 
        "password": "SecurePass123!",
        "name": "Elite Security Services",
        "role": "security_provider"
    },
    "security_guard": {
        "email": "john.guard@habitere.com",
        "password": "GuardPass123!",
        "name": "John Doe",
        "role": "security_guard"
    },
    "regular_user": {
        "email": "client@habitere.com",
        "password": "ClientPass123!",
        "name": "Marie Dubois",
        "role": "property_seeker"
    }
}

# Test service data
TEST_SERVICE_DATA = {
    "title": "24/7 Armed Security Guards",
    "description": "Professional armed security guards with extensive training in residential and commercial protection. Available 24/7 with rapid response capabilities.",
    "service_type": "Security Guards",
    "price_range": "150,000 - 400,000 XAF/month",
    "location": "Douala",
    "images": ["https://example.com/guard1.jpg", "https://example.com/guard2.jpg"],
    "certifications": ["Armed Security License", "First Aid Certified", "Fire Safety Training"],
    "availability": "Available",
    "features": ["24/7 Service", "Armed Guards", "Rapid Response", "Professional Training"],
    "response_time": "15 minutes"
}

# Test guard application data
TEST_GUARD_APPLICATION = {
    "full_name": "Jean-Baptiste Mballa",
    "phone": "+237670123456",
    "email": "jb.mballa@gmail.com",
    "date_of_birth": "1985-03-15",
    "national_id": "123456789CM",
    "address": "Quartier Bonanjo, Rue des Palmiers",
    "city": "Douala",
    "experience_years": 8,
    "previous_employers": ["Securitas Cameroon", "G4S Security"],
    "certifications": ["Armed Security License", "First Aid Certificate"],
    "training": ["Defensive Tactics", "Emergency Response", "Customer Service"],
    "availability": "Full-time",
    "preferred_locations": ["Douala", "Yaoundé"]
}

# Test booking data
TEST_BOOKING_DATA = {
    "booking_type": "scheduled",
    "start_date": "2025-02-15",
    "end_date": "2025-03-15",
    "duration": "1 month",
    "location": "Residential Complex, Bonanjo",
    "num_guards": 2,
    "special_requirements": "Experience with residential security, French speaking required"
}

class SecurityModuleTestSuite:
    """Comprehensive test suite for Homeland Security module"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
        self.auth_tokens = {}
        self.created_resources = {
            "services": [],
            "applications": [],
            "bookings": []
        }
        
    async def setup_session(self):
        """Initialize HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=connector)
        
    async def cleanup_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, endpoint: str, method: str, status: str, details: str, response_data: Any = None):
        """Log test result"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {method} {endpoint} - {details}")
        
    async def authenticate_user(self, user_key: str) -> Optional[str]:
        """Authenticate user and return session token"""
        user_data = TEST_USERS[user_key]
        
        try:
            # Try to login first
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    # Extract session token from cookies
                    cookies = response.cookies
                    session_token = cookies.get('session_token')
                    if session_token:
                        self.auth_tokens[user_key] = session_token.value
                        self.log_test("/auth/login", "POST", "PASS", f"Login successful for {user_key}")
                        return session_token.value
                elif response.status == 403:
                    # User exists but email not verified - this is expected for new users
                    self.log_test("/auth/login", "POST", "INFO", f"User {user_key} exists but email not verified")
                    return None
                else:
                    # Try to register user
                    return await self.register_user(user_key)
                    
        except Exception as e:
            self.log_test("/auth/login", "POST", "FAIL", f"Login failed for {user_key}: {str(e)}")
            return await self.register_user(user_key)
            
    async def register_user(self, user_key: str) -> Optional[str]:
        """Register new user"""
        user_data = TEST_USERS[user_key]
        
        try:
            register_data = {
                "email": user_data["email"],
                "password": user_data["password"],
                "name": user_data["name"]
            }
            
            async with self.session.post(f"{BASE_URL}/auth/register", json=register_data) as response:
                if response.status in [200, 201]:
                    self.log_test("/auth/register", "POST", "PASS", f"Registration successful for {user_key}")
                    
                    # For testing purposes, we'll simulate email verification
                    # In production, this would require actual email verification
                    return await self.simulate_verification(user_key)
                else:
                    response_text = await response.text()
                    self.log_test("/auth/register", "POST", "FAIL", f"Registration failed for {user_key}: {response_text}")
                    return None
                    
        except Exception as e:
            self.log_test("/auth/register", "POST", "FAIL", f"Registration error for {user_key}: {str(e)}")
            return None
            
    async def simulate_verification(self, user_key: str) -> Optional[str]:
        """Simulate email verification for testing"""
        # Note: In a real scenario, we would need to verify email first
        # For testing, we'll try to login with admin credentials that should already be verified
        if user_key == "admin":
            return await self.authenticate_user("admin")
        
        self.log_test("/auth/verify", "POST", "INFO", f"Email verification needed for {user_key} (simulated)")
        return None
        
    def get_auth_headers(self, user_key: str) -> Dict[str, str]:
        """Get authentication headers for user"""
        token = self.auth_tokens.get(user_key)
        if token:
            return {"Cookie": f"session_token={token}"}
        return {}
        
    # ==================== STATISTICS TESTS ====================
    
    async def test_security_stats(self):
        """Test GET /api/security/stats (Public endpoint)"""
        try:
            async with self.session.get(f"{BASE_URL}/security/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    expected_keys = ["total_services", "available_guards", "total_bookings", "pending_applications"]
                    
                    if all(key in data for key in expected_keys):
                        self.log_test("/security/stats", "GET", "PASS", 
                                    f"Statistics retrieved successfully: {data}", data)
                    else:
                        self.log_test("/security/stats", "GET", "FAIL", 
                                    f"Missing expected keys in response: {data}")
                else:
                    response_text = await response.text()
                    self.log_test("/security/stats", "GET", "FAIL", 
                                f"Unexpected status {response.status}: {response_text}")
                                
        except Exception as e:
            self.log_test("/security/stats", "GET", "FAIL", f"Request failed: {str(e)}")
            
    # ==================== SERVICE MARKETPLACE TESTS ====================
    
    async def test_get_security_services(self):
        """Test GET /api/security/services (Public endpoint)"""
        try:
            # Test basic listing
            async with self.session.get(f"{BASE_URL}/security/services") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("/security/services", "GET", "PASS", 
                                f"Services listed successfully: {len(data)} services", data)
                else:
                    response_text = await response.text()
                    self.log_test("/security/services", "GET", "FAIL", 
                                f"Unexpected status {response.status}: {response_text}")
                                
            # Test with filters
            params = {
                "service_type": "Security Guards",
                "location": "Douala",
                "limit": 10
            }
            async with self.session.get(f"{BASE_URL}/security/services", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("/security/services", "GET", "PASS", 
                                f"Filtered services retrieved: {len(data)} services")
                else:
                    self.log_test("/security/services", "GET", "FAIL", 
                                f"Filtered request failed: {response.status}")
                                
        except Exception as e:
            self.log_test("/security/services", "GET", "FAIL", f"Request failed: {str(e)}")
            
    async def test_create_security_service(self):
        """Test POST /api/security/services (Auth required)"""
        # Test without authentication
        try:
            async with self.session.post(f"{BASE_URL}/security/services", json=TEST_SERVICE_DATA) as response:
                if response.status == 401:
                    self.log_test("/security/services", "POST", "PASS", 
                                "Correctly rejected unauthenticated request")
                else:
                    self.log_test("/security/services", "POST", "FAIL", 
                                f"Should reject unauthenticated request, got {response.status}")
        except Exception as e:
            self.log_test("/security/services", "POST", "FAIL", f"Auth test failed: {str(e)}")
            
        # Test with authentication (admin user)
        admin_token = await self.authenticate_user("admin")
        if admin_token:
            try:
                headers = self.get_auth_headers("admin")
                async with self.session.post(f"{BASE_URL}/security/services", 
                                           json=TEST_SERVICE_DATA, headers=headers) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        service_id = data.get("id")
                        if service_id:
                            self.created_resources["services"].append(service_id)
                        self.log_test("/security/services", "POST", "PASS", 
                                    f"Service created successfully: {service_id}", data)
                    else:
                        response_text = await response.text()
                        self.log_test("/security/services", "POST", "FAIL", 
                                    f"Service creation failed: {response.status} - {response_text}")
            except Exception as e:
                self.log_test("/security/services", "POST", "FAIL", f"Authenticated request failed: {str(e)}")
        else:
            self.log_test("/security/services", "POST", "SKIP", "No admin authentication available")
            
    async def test_get_security_service_details(self):
        """Test GET /api/security/services/{service_id}"""
        if not self.created_resources["services"]:
            self.log_test("/security/services/{id}", "GET", "SKIP", "No services created to test")
            return
            
        service_id = self.created_resources["services"][0]
        
        try:
            async with self.session.get(f"{BASE_URL}/security/services/{service_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if "service" in data and "provider" in data:
                        self.log_test("/security/services/{id}", "GET", "PASS", 
                                    f"Service details retrieved successfully", data)
                    else:
                        self.log_test("/security/services/{id}", "GET", "FAIL", 
                                    f"Invalid response structure: {data}")
                else:
                    response_text = await response.text()
                    self.log_test("/security/services/{id}", "GET", "FAIL", 
                                f"Request failed: {response.status} - {response_text}")
                                
        except Exception as e:
            self.log_test("/security/services/{id}", "GET", "FAIL", f"Request failed: {str(e)}")
            
        # Test with invalid ID
        try:
            async with self.session.get(f"{BASE_URL}/security/services/invalid-id") as response:
                if response.status == 404:
                    self.log_test("/security/services/{id}", "GET", "PASS", 
                                "Correctly returned 404 for invalid service ID")
                else:
                    self.log_test("/security/services/{id}", "GET", "FAIL", 
                                f"Should return 404 for invalid ID, got {response.status}")
        except Exception as e:
            self.log_test("/security/services/{id}", "GET", "FAIL", f"Invalid ID test failed: {str(e)}")
            
    async def test_update_security_service(self):
        """Test PUT /api/security/services/{service_id}"""
        if not self.created_resources["services"]:
            self.log_test("/security/services/{id}", "PUT", "SKIP", "No services created to test")
            return
            
        service_id = self.created_resources["services"][0]
        updated_data = TEST_SERVICE_DATA.copy()
        updated_data["title"] = "Updated 24/7 Armed Security Guards"
        updated_data["price_range"] = "200,000 - 500,000 XAF/month"
        
        # Test without authentication
        try:
            async with self.session.put(f"{BASE_URL}/security/services/{service_id}", 
                                      json=updated_data) as response:
                if response.status == 401:
                    self.log_test("/security/services/{id}", "PUT", "PASS", 
                                "Correctly rejected unauthenticated update request")
                else:
                    self.log_test("/security/services/{id}", "PUT", "FAIL", 
                                f"Should reject unauthenticated request, got {response.status}")
        except Exception as e:
            self.log_test("/security/services/{id}", "PUT", "FAIL", f"Auth test failed: {str(e)}")
            
        # Test with authentication
        admin_token = self.auth_tokens.get("admin")
        if admin_token:
            try:
                headers = self.get_auth_headers("admin")
                async with self.session.put(f"{BASE_URL}/security/services/{service_id}", 
                                          json=updated_data, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_test("/security/services/{id}", "PUT", "PASS", 
                                    "Service updated successfully", data)
                    else:
                        response_text = await response.text()
                        self.log_test("/security/services/{id}", "PUT", "FAIL", 
                                    f"Update failed: {response.status} - {response_text}")
            except Exception as e:
                self.log_test("/security/services/{id}", "PUT", "FAIL", f"Update request failed: {str(e)}")
        else:
            self.log_test("/security/services/{id}", "PUT", "SKIP", "No admin authentication available")
            
    async def test_delete_security_service(self):
        """Test DELETE /api/security/services/{service_id}"""
        if not self.created_resources["services"]:
            self.log_test("/security/services/{id}", "DELETE", "SKIP", "No services created to test")
            return
            
        service_id = self.created_resources["services"][0]
        
        # Test without authentication
        try:
            async with self.session.delete(f"{BASE_URL}/security/services/{service_id}") as response:
                if response.status == 401:
                    self.log_test("/security/services/{id}", "DELETE", "PASS", 
                                "Correctly rejected unauthenticated delete request")
                else:
                    self.log_test("/security/services/{id}", "DELETE", "FAIL", 
                                f"Should reject unauthenticated request, got {response.status}")
        except Exception as e:
            self.log_test("/security/services/{id}", "DELETE", "FAIL", f"Auth test failed: {str(e)}")
            
        # Test with authentication
        admin_token = self.auth_tokens.get("admin")
        if admin_token:
            try:
                headers = self.get_auth_headers("admin")
                async with self.session.delete(f"{BASE_URL}/security/services/{service_id}", 
                                             headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_test("/security/services/{id}", "DELETE", "PASS", 
                                    "Service deleted successfully", data)
                        # Remove from created resources since it's deleted
                        self.created_resources["services"].remove(service_id)
                    else:
                        response_text = await response.text()
                        self.log_test("/security/services/{id}", "DELETE", "FAIL", 
                                    f"Delete failed: {response.status} - {response_text}")
            except Exception as e:
                self.log_test("/security/services/{id}", "DELETE", "FAIL", f"Delete request failed: {str(e)}")
        else:
            self.log_test("/security/services/{id}", "DELETE", "SKIP", "No admin authentication available")
            
    # ==================== GUARD RECRUITMENT TESTS ====================
    
    async def test_apply_as_guard(self):
        """Test POST /api/security/guards/apply"""
        # Test without authentication
        try:
            async with self.session.post(f"{BASE_URL}/security/guards/apply", 
                                       json=TEST_GUARD_APPLICATION) as response:
                if response.status == 401:
                    self.log_test("/security/guards/apply", "POST", "PASS", 
                                "Correctly rejected unauthenticated application")
                else:
                    self.log_test("/security/guards/apply", "POST", "FAIL", 
                                f"Should reject unauthenticated request, got {response.status}")
        except Exception as e:
            self.log_test("/security/guards/apply", "POST", "FAIL", f"Auth test failed: {str(e)}")
            
        # Test with authentication
        admin_token = self.auth_tokens.get("admin")
        if admin_token:
            try:
                headers = self.get_auth_headers("admin")
                async with self.session.post(f"{BASE_URL}/security/guards/apply", 
                                           json=TEST_GUARD_APPLICATION, headers=headers) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        application_id = data.get("application_id")
                        if application_id:
                            self.created_resources["applications"].append(application_id)
                        self.log_test("/security/guards/apply", "POST", "PASS", 
                                    f"Guard application submitted successfully: {application_id}", data)
                    else:
                        response_text = await response.text()
                        self.log_test("/security/guards/apply", "POST", "FAIL", 
                                    f"Application failed: {response.status} - {response_text}")
            except Exception as e:
                self.log_test("/security/guards/apply", "POST", "FAIL", f"Application request failed: {str(e)}")
        else:
            self.log_test("/security/guards/apply", "POST", "SKIP", "No admin authentication available")
            
    async def test_get_guard_applications(self):
        """Test GET /api/security/guards/applications"""
        # Test without authentication
        try:
            async with self.session.get(f"{BASE_URL}/security/guards/applications") as response:
                if response.status == 401:
                    self.log_test("/security/guards/applications", "GET", "PASS", 
                                "Correctly rejected unauthenticated request")
                else:
                    self.log_test("/security/guards/applications", "GET", "FAIL", 
                                f"Should reject unauthenticated request, got {response.status}")
        except Exception as e:
            self.log_test("/security/guards/applications", "GET", "FAIL", f"Auth test failed: {str(e)}")
            
        # Test with authentication
        admin_token = self.auth_tokens.get("admin")
        if admin_token:
            try:
                headers = self.get_auth_headers("admin")
                async with self.session.get(f"{BASE_URL}/security/guards/applications", 
                                          headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_test("/security/guards/applications", "GET", "PASS", 
                                    f"Applications retrieved successfully: {len(data)} applications", data)
                    else:
                        response_text = await response.text()
                        self.log_test("/security/guards/applications", "GET", "FAIL", 
                                    f"Request failed: {response.status} - {response_text}")
            except Exception as e:
                self.log_test("/security/guards/applications", "GET", "FAIL", f"Request failed: {str(e)}")
        else:
            self.log_test("/security/guards/applications", "GET", "SKIP", "No admin authentication available")
            
    async def test_get_guard_profiles(self):
        """Test GET /api/security/guards/profiles (Public endpoint)"""
        try:
            async with self.session.get(f"{BASE_URL}/security/guards/profiles") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("/security/guards/profiles", "GET", "PASS", 
                                f"Guard profiles retrieved successfully: {len(data)} profiles", data)
                else:
                    response_text = await response.text()
                    self.log_test("/security/guards/profiles", "GET", "FAIL", 
                                f"Request failed: {response.status} - {response_text}")
                                
            # Test with filters
            params = {
                "location": "Douala",
                "availability": "Full-time",
                "limit": 10
            }
            async with self.session.get(f"{BASE_URL}/security/guards/profiles", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("/security/guards/profiles", "GET", "PASS", 
                                f"Filtered guard profiles retrieved: {len(data)} profiles")
                else:
                    self.log_test("/security/guards/profiles", "GET", "FAIL", 
                                f"Filtered request failed: {response.status}")
                                
        except Exception as e:
            self.log_test("/security/guards/profiles", "GET", "FAIL", f"Request failed: {str(e)}")
            
    async def test_approve_guard_application(self):
        """Test PUT /api/security/guards/applications/{app_id}/approve"""
        if not self.created_resources["applications"]:
            self.log_test("/security/guards/applications/{id}/approve", "PUT", "SKIP", 
                        "No applications created to test")
            return
            
        application_id = self.created_resources["applications"][0]
        
        # Test without authentication
        try:
            async with self.session.put(f"{BASE_URL}/security/guards/applications/{application_id}/approve") as response:
                if response.status == 401:
                    self.log_test("/security/guards/applications/{id}/approve", "PUT", "PASS", 
                                "Correctly rejected unauthenticated approval request")
                else:
                    self.log_test("/security/guards/applications/{id}/approve", "PUT", "FAIL", 
                                f"Should reject unauthenticated request, got {response.status}")
        except Exception as e:
            self.log_test("/security/guards/applications/{id}/approve", "PUT", "FAIL", f"Auth test failed: {str(e)}")
            
        # Test with authentication
        admin_token = self.auth_tokens.get("admin")
        if admin_token:
            try:
                headers = self.get_auth_headers("admin")
                async with self.session.put(f"{BASE_URL}/security/guards/applications/{application_id}/approve", 
                                          headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_test("/security/guards/applications/{id}/approve", "PUT", "PASS", 
                                    "Application approved successfully", data)
                    else:
                        response_text = await response.text()
                        self.log_test("/security/guards/applications/{id}/approve", "PUT", "FAIL", 
                                    f"Approval failed: {response.status} - {response_text}")
            except Exception as e:
                self.log_test("/security/guards/applications/{id}/approve", "PUT", "FAIL", 
                            f"Approval request failed: {str(e)}")
        else:
            self.log_test("/security/guards/applications/{id}/approve", "PUT", "SKIP", 
                        "No admin authentication available")
            
    # ==================== BOOKING SYSTEM TESTS ====================
    
    async def test_create_security_booking(self):
        """Test POST /api/security/bookings"""
        # First create a service to book
        await self.test_create_security_service()
        
        if not self.created_resources["services"]:
            self.log_test("/security/bookings", "POST", "SKIP", "No services available to book")
            return
            
        service_id = self.created_resources["services"][0]
        booking_data = TEST_BOOKING_DATA.copy()
        booking_data["service_id"] = service_id
        
        # Test without authentication
        try:
            async with self.session.post(f"{BASE_URL}/security/bookings", json=booking_data) as response:
                if response.status == 401:
                    self.log_test("/security/bookings", "POST", "PASS", 
                                "Correctly rejected unauthenticated booking request")
                else:
                    self.log_test("/security/bookings", "POST", "FAIL", 
                                f"Should reject unauthenticated request, got {response.status}")
        except Exception as e:
            self.log_test("/security/bookings", "POST", "FAIL", f"Auth test failed: {str(e)}")
            
        # Test with authentication
        admin_token = self.auth_tokens.get("admin")
        if admin_token:
            try:
                headers = self.get_auth_headers("admin")
                async with self.session.post(f"{BASE_URL}/security/bookings", 
                                           json=booking_data, headers=headers) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        booking_id = data.get("booking_id")
                        if booking_id:
                            self.created_resources["bookings"].append(booking_id)
                        self.log_test("/security/bookings", "POST", "PASS", 
                                    f"Booking created successfully: {booking_id}", data)
                    else:
                        response_text = await response.text()
                        self.log_test("/security/bookings", "POST", "FAIL", 
                                    f"Booking failed: {response.status} - {response_text}")
            except Exception as e:
                self.log_test("/security/bookings", "POST", "FAIL", f"Booking request failed: {str(e)}")
        else:
            self.log_test("/security/bookings", "POST", "SKIP", "No admin authentication available")
            
    async def test_get_security_bookings(self):
        """Test GET /api/security/bookings"""
        # Test without authentication
        try:
            async with self.session.get(f"{BASE_URL}/security/bookings") as response:
                if response.status == 401:
                    self.log_test("/security/bookings", "GET", "PASS", 
                                "Correctly rejected unauthenticated request")
                else:
                    self.log_test("/security/bookings", "GET", "FAIL", 
                                f"Should reject unauthenticated request, got {response.status}")
        except Exception as e:
            self.log_test("/security/bookings", "GET", "FAIL", f"Auth test failed: {str(e)}")
            
        # Test with authentication
        admin_token = self.auth_tokens.get("admin")
        if admin_token:
            try:
                headers = self.get_auth_headers("admin")
                async with self.session.get(f"{BASE_URL}/security/bookings", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_test("/security/bookings", "GET", "PASS", 
                                    f"Bookings retrieved successfully: {len(data)} bookings", data)
                    else:
                        response_text = await response.text()
                        self.log_test("/security/bookings", "GET", "FAIL", 
                                    f"Request failed: {response.status} - {response_text}")
            except Exception as e:
                self.log_test("/security/bookings", "GET", "FAIL", f"Request failed: {str(e)}")
        else:
            self.log_test("/security/bookings", "GET", "SKIP", "No admin authentication available")
            
    async def test_get_security_booking_details(self):
        """Test GET /api/security/bookings/{booking_id}"""
        if not self.created_resources["bookings"]:
            self.log_test("/security/bookings/{id}", "GET", "SKIP", "No bookings created to test")
            return
            
        booking_id = self.created_resources["bookings"][0]
        
        # Test without authentication
        try:
            async with self.session.get(f"{BASE_URL}/security/bookings/{booking_id}") as response:
                if response.status == 401:
                    self.log_test("/security/bookings/{id}", "GET", "PASS", 
                                "Correctly rejected unauthenticated request")
                else:
                    self.log_test("/security/bookings/{id}", "GET", "FAIL", 
                                f"Should reject unauthenticated request, got {response.status}")
        except Exception as e:
            self.log_test("/security/bookings/{id}", "GET", "FAIL", f"Auth test failed: {str(e)}")
            
        # Test with authentication
        admin_token = self.auth_tokens.get("admin")
        if admin_token:
            try:
                headers = self.get_auth_headers("admin")
                async with self.session.get(f"{BASE_URL}/security/bookings/{booking_id}", 
                                          headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_test("/security/bookings/{id}", "GET", "PASS", 
                                    "Booking details retrieved successfully", data)
                    else:
                        response_text = await response.text()
                        self.log_test("/security/bookings/{id}", "GET", "FAIL", 
                                    f"Request failed: {response.status} - {response_text}")
            except Exception as e:
                self.log_test("/security/bookings/{id}", "GET", "FAIL", f"Request failed: {str(e)}")
        else:
            self.log_test("/security/bookings/{id}", "GET", "SKIP", "No admin authentication available")
            
    async def test_confirm_security_booking(self):
        """Test PUT /api/security/bookings/{booking_id}/confirm"""
        if not self.created_resources["bookings"]:
            self.log_test("/security/bookings/{id}/confirm", "PUT", "SKIP", "No bookings created to test")
            return
            
        booking_id = self.created_resources["bookings"][0]
        
        # Test without authentication
        try:
            async with self.session.put(f"{BASE_URL}/security/bookings/{booking_id}/confirm") as response:
                if response.status == 401:
                    self.log_test("/security/bookings/{id}/confirm", "PUT", "PASS", 
                                "Correctly rejected unauthenticated confirmation request")
                else:
                    self.log_test("/security/bookings/{id}/confirm", "PUT", "FAIL", 
                                f"Should reject unauthenticated request, got {response.status}")
        except Exception as e:
            self.log_test("/security/bookings/{id}/confirm", "PUT", "FAIL", f"Auth test failed: {str(e)}")
            
        # Test with authentication
        admin_token = self.auth_tokens.get("admin")
        if admin_token:
            try:
                headers = self.get_auth_headers("admin")
                async with self.session.put(f"{BASE_URL}/security/bookings/{booking_id}/confirm", 
                                          headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_test("/security/bookings/{id}/confirm", "PUT", "PASS", 
                                    "Booking confirmed successfully", data)
                    else:
                        response_text = await response.text()
                        self.log_test("/security/bookings/{id}/confirm", "PUT", "FAIL", 
                                    f"Confirmation failed: {response.status} - {response_text}")
            except Exception as e:
                self.log_test("/security/bookings/{id}/confirm", "PUT", "FAIL", 
                            f"Confirmation request failed: {str(e)}")
        else:
            self.log_test("/security/bookings/{id}/confirm", "PUT", "SKIP", 
                        "No admin authentication available")
            
    # ==================== WORKFLOW TESTS ====================
    
    async def test_complete_workflow(self):
        """Test complete security service workflow"""
        print("\n🔄 Testing Complete Security Service Workflow...")
        
        # 1. Check initial statistics
        await self.test_security_stats()
        
        # 2. Create a security service
        await self.test_create_security_service()
        
        # 3. List services and verify creation
        await self.test_get_security_services()
        
        # 4. Submit guard application
        await self.test_apply_as_guard()
        
        # 5. Admin approves guard application
        await self.test_approve_guard_application()
        
        # 6. Check guard profiles
        await self.test_get_guard_profiles()
        
        # 7. Create booking for service
        await self.test_create_security_booking()
        
        # 8. Provider confirms booking
        await self.test_confirm_security_booking()
        
        # 9. Check final statistics
        await self.test_security_stats()
        
        print("✅ Complete workflow test finished")
        
    # ==================== MAIN TEST RUNNER ====================
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Homeland Security Module Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Authentication setup
            print("\n🔐 Setting up authentication...")
            await self.authenticate_user("admin")
            
            # 1. Statistics Tests (Public)
            print("\n📊 Testing Statistics Endpoints...")
            await self.test_security_stats()
            
            # 2. Service Marketplace Tests
            print("\n🏪 Testing Service Marketplace...")
            await self.test_get_security_services()
            await self.test_create_security_service()
            await self.test_get_security_service_details()
            await self.test_update_security_service()
            # Note: Delete test is last to preserve service for other tests
            
            # 3. Guard Recruitment Tests
            print("\n👮 Testing Guard Recruitment...")
            await self.test_apply_as_guard()
            await self.test_get_guard_applications()
            await self.test_get_guard_profiles()
            await self.test_approve_guard_application()
            
            # 4. Booking System Tests
            print("\n📅 Testing Booking System...")
            await self.test_create_security_booking()
            await self.test_get_security_bookings()
            await self.test_get_security_booking_details()
            await self.test_confirm_security_booking()
            
            # 5. Complete Workflow Test
            await self.test_complete_workflow()
            
            # 6. Cleanup Tests (Delete operations)
            print("\n🧹 Testing Delete Operations...")
            await self.test_delete_security_service()
            
        finally:
            await self.cleanup_session()
            
        # Generate summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("📋 HOMELAND SECURITY MODULE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        info_tests = len([r for r in self.test_results if r["status"] == "INFO"])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️ Skipped: {skipped_tests}")
        print(f"ℹ️ Info: {info_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / (total_tests - skipped_tests - info_tests)) * 100 if (total_tests - skipped_tests - info_tests) > 0 else 0
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Group results by endpoint
        print("\n📋 DETAILED RESULTS BY ENDPOINT:")
        print("-" * 80)
        
        endpoints = {}
        for result in self.test_results:
            endpoint = result["endpoint"]
            if endpoint not in endpoints:
                endpoints[endpoint] = []
            endpoints[endpoint].append(result)
            
        for endpoint, results in endpoints.items():
            passed = len([r for r in results if r["status"] == "PASS"])
            failed = len([r for r in results if r["status"] == "FAIL"])
            skipped = len([r for r in results if r["status"] == "SKIP"])
            
            status_emoji = "✅" if failed == 0 and passed > 0 else "❌" if failed > 0 else "⏭️"
            print(f"{status_emoji} {endpoint}: {passed}✅ {failed}❌ {skipped}⏭️")
            
        # Show failed tests details
        failed_results = [r for r in self.test_results if r["status"] == "FAIL"]
        if failed_results:
            print("\n❌ FAILED TESTS DETAILS:")
            print("-" * 80)
            for result in failed_results:
                print(f"❌ {result['method']} {result['endpoint']}")
                print(f"   Details: {result['details']}")
                print()
                
        # Show authentication status
        print("\n🔐 AUTHENTICATION STATUS:")
        print("-" * 80)
        for user_key, token in self.auth_tokens.items():
            status = "✅ Authenticated" if token else "❌ Failed"
            print(f"{status}: {user_key}")
            
        # Show created resources
        print("\n📦 CREATED RESOURCES:")
        print("-" * 80)
        for resource_type, resources in self.created_resources.items():
            print(f"{resource_type.title()}: {len(resources)} created")
            for resource_id in resources:
                print(f"  - {resource_id}")
                
        print("\n" + "=" * 80)
        print("🏁 HOMELAND SECURITY MODULE TESTING COMPLETE")
        print("=" * 80)


async def main():
    """Main test runner"""
    test_suite = SecurityModuleTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())