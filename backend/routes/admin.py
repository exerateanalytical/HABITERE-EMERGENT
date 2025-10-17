"""
Admin Routes Module
===================
Handles administrative API endpoints for Habitere platform.

This module provides:
- Dashboard statistics and analytics
- User management and moderation
- Property verification workflow
- Service verification workflow
- Platform analytics and reporting

Admin Access:
- All endpoints require admin role
- Protected by require_admin dependency
- Comprehensive logging of admin actions

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import logging

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_database
from utils import require_admin, serialize_doc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])


# ==================== DASHBOARD STATISTICS ====================

@router.get("/stats")
async def get_admin_stats(admin: dict = Depends(require_admin)):
    """
    Get comprehensive dashboard statistics for admin panel.
    
    Provides overview of:
    - User counts by status
    - Property counts by verification status
    - Service counts by verification status
    - Booking statistics
    - Revenue metrics
    - Weekly activity trends
    
    Returns:
        Dictionary with categorized statistics
    """
    db = get_database()
    
    try:
        # User statistics
        total_users = await db.users.count_documents({})
        pending_users = await db.users.count_documents({
            "verification_status": "pending",
            "role": {"$ne": "admin"}
        })
        approved_users = await db.users.count_documents({"verification_status": "approved"})
        
        # Property statistics
        total_properties = await db.properties.count_documents({})
        pending_properties = await db.properties.count_documents({"verification_status": "pending"})
        verified_properties = await db.properties.count_documents({"verification_status": "verified"})
        
        # Service statistics
        total_services = await db.professional_services.count_documents({})
        pending_services = await db.professional_services.count_documents({"verification_status": "pending"})
        verified_services = await db.professional_services.count_documents({"verification_status": "verified"})
        
        # Booking statistics
        total_bookings = await db.bookings.count_documents({})
        pending_bookings = await db.bookings.count_documents({"status": "pending"})
        
        # Revenue calculation
        pipeline = [
            {"$match": {"status": "successful"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        revenue_result = await db.payments.aggregate(pipeline).to_list(length=1)
        total_revenue = revenue_result[0]["total"] if revenue_result else 0
        
        # Weekly activity
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        new_users_week = await db.users.count_documents({"created_at": {"$gte": seven_days_ago.isoformat()}})
        new_properties_week = await db.properties.count_documents({"created_at": {"$gte": seven_days_ago.isoformat()}})
        new_bookings_week = await db.bookings.count_documents({"created_at": {"$gte": seven_days_ago.isoformat()}})
        
        logger.info(f"Admin stats retrieved by {admin.get('email')}")
        
        return {
            "users": {
                "total": total_users,
                "pending": pending_users,
                "approved": approved_users,
                "new_this_week": new_users_week
            },
            "properties": {
                "total": total_properties,
                "pending": pending_properties,
                "verified": verified_properties,
                "new_this_week": new_properties_week
            },
            "services": {
                "total": total_services,
                "pending": pending_services,
                "verified": verified_services
            },
            "bookings": {
                "total": total_bookings,
                "pending": pending_bookings,
                "new_this_week": new_bookings_week
            },
            "revenue": {
                "total": total_revenue,
                "currency": "XAF"
            }
        }
    except Exception as e:
        logger.error(f"Error fetching admin stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


# ==================== USER MANAGEMENT ====================

@router.get("/users")
async def get_all_users(
    admin: dict = Depends(require_admin),
    skip: int = 0,
    limit: int = 50,
    role: str = None,
    status: str = None
):
    """Get all users with filtering options."""
    db = get_database()
    
    try:
        filters = {}
        if role:
            filters["role"] = role
        if status:
            filters["verification_status"] = status
        
        users_cursor = db.users.find(filters).sort("created_at", -1).skip(skip).limit(limit)
        users = await users_cursor.to_list(length=limit)
        
        total = await db.users.count_documents(filters)
        
        logger.info(f"Admin retrieved {len(users)} users")
        
        return {
            "users": [serialize_doc(user) for user in users],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")


@router.put("/users/{user_id}/approve")
async def approve_user(
    user_id: str,
    admin: dict = Depends(require_admin)
):
    """Approve a pending user."""
    db = get_database()
    
    try:
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": {"verification_status": "approved"}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"User {user_id} approved by admin {admin.get('email')}")
        
        return {"success": True, "message": "User approved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving user: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve user")


@router.put("/users/{user_id}/reject")
async def reject_user(
    user_id: str,
    reason: str,
    admin: dict = Depends(require_admin)
):
    """Reject a pending user with reason."""
    db = get_database()
    
    try:
        result = await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "verification_status": "rejected",
                    "rejection_reason": reason
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"User {user_id} rejected by admin {admin.get('email')}")
        
        return {"success": True, "message": "User rejected"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject user")


# ==================== PROPERTY MANAGEMENT ====================

@router.get("/properties")
async def get_all_properties(
    admin: dict = Depends(require_admin),
    skip: int = 0,
    limit: int = 50,
    verification_status: str = None
):
    """Get all properties with filtering."""
    db = get_database()
    
    try:
        filters = {}
        if verification_status:
            filters["verification_status"] = verification_status
        
        properties_cursor = db.properties.find(filters).sort("created_at", -1).skip(skip).limit(limit)
        properties = await properties_cursor.to_list(length=limit)
        
        # Enrich with owner information
        for prop in properties:
            owner = await db.users.find_one({"id": prop.get("owner_id")})
            if owner:
                prop["owner_name"] = owner.get("name")
                prop["owner_email"] = owner.get("email")
        
        total = await db.properties.count_documents(filters)
        
        logger.info(f"Admin retrieved {len(properties)} properties")
        
        return {
            "properties": [serialize_doc(prop) for prop in properties],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error fetching properties: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch properties")


@router.put("/properties/{property_id}/verify")
async def verify_property(
    property_id: str,
    admin: dict = Depends(require_admin)
):
    """Verify a pending property."""
    db = get_database()
    
    try:
        result = await db.properties.update_one(
            {"id": property_id},
            {
                "$set": {
                    "verification_status": "verified",
                    "verified": True
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Property not found")
        
        logger.info(f"Property {property_id} verified by admin {admin.get('email')}")
        
        return {"success": True, "message": "Property verified successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying property: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify property")


@router.put("/properties/{property_id}/reject")
async def reject_property(
    property_id: str,
    reason: str,
    admin: dict = Depends(require_admin)
):
    """Reject a pending property with reason."""
    db = get_database()
    
    try:
        result = await db.properties.update_one(
            {"id": property_id},
            {
                "$set": {
                    "verification_status": "rejected",
                    "verified": False,
                    "rejection_reason": reason
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Property not found")
        
        logger.info(f"Property {property_id} rejected by admin {admin.get('email')}")
        
        return {"success": True, "message": "Property rejected"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting property: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject property")


# ==================== SERVICE MANAGEMENT ====================

@router.get("/services")
async def get_all_services(
    admin: dict = Depends(require_admin),
    skip: int = 0,
    limit: int = 50,
    verification_status: str = None
):
    """Get all services with filtering."""
    db = get_database()
    
    try:
        filters = {}
        if verification_status:
            filters["verification_status"] = verification_status
        
        services_cursor = db.professional_services.find(filters).sort("created_at", -1).skip(skip).limit(limit)
        services = await services_cursor.to_list(length=limit)
        
        # Enrich with provider information
        for service in services:
            provider = await db.users.find_one({"id": service.get("provider_id")})
            if provider:
                service["provider_name"] = provider.get("name")
                service["provider_email"] = provider.get("email")
        
        total = await db.professional_services.count_documents(filters)
        
        logger.info(f"Admin retrieved {len(services)} services")
        
        return {
            "services": [serialize_doc(service) for service in services],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error fetching services: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch services")


@router.put("/services/{service_id}/verify")
async def verify_service(
    service_id: str,
    admin: dict = Depends(require_admin)
):
    """Verify a pending service."""
    db = get_database()
    
    try:
        result = await db.professional_services.update_one(
            {"id": service_id},
            {
                "$set": {
                    "verification_status": "verified",
                    "verified": True
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        
        logger.info(f"Service {service_id} verified by admin {admin.get('email')}")
        
        return {"success": True, "message": "Service verified successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying service: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify service")


@router.put("/services/{service_id}/reject")
async def reject_service(
    service_id: str,
    reason: str,
    admin: dict = Depends(require_admin)
):
    """Reject a pending service with reason."""
    db = get_database()
    
    try:
        result = await db.professional_services.update_one(
            {"id": service_id},
            {
                "$set": {
                    "verification_status": "rejected",
                    "verified": False,
                    "rejection_reason": reason
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        
        logger.info(f"Service {service_id} rejected by admin {admin.get('email')}")
        
        return {"success": True, "message": "Service rejected"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting service: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject service")


# ==================== ANALYTICS ====================

@router.get("/analytics/users")
async def get_user_analytics(
    admin: dict = Depends(require_admin),
    days: int = 30
):
    """Get user analytics for the specified period."""
    db = get_database()
    
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # User registration trend
        pipeline = [
            {"$match": {"created_at": {"$gte": start_date.isoformat()}}},
            {
                "$group": {
                    "_id": {"$substr": ["$created_at", 0, 10]},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        registration_trend = await db.users.aggregate(pipeline).to_list(length=None)
        
        # Users by role
        role_pipeline = [
            {
                "$group": {
                    "_id": "$role",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        users_by_role = await db.users.aggregate(role_pipeline).to_list(length=None)
        
        logger.info(f"User analytics retrieved by admin {admin.get('email')}")
        
        return {
            "registration_trend": registration_trend,
            "users_by_role": users_by_role,
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Error fetching user analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")


@router.get("/analytics/properties")
async def get_property_analytics(
    admin: dict = Depends(require_admin),
    days: int = 30
):
    """Get property analytics for the specified period."""
    db = get_database()
    
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Property listing trend
        pipeline = [
            {"$match": {"created_at": {"$gte": start_date.isoformat()}}},
            {
                "$group": {
                    "_id": {"$substr": ["$created_at", 0, 10]},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        listing_trend = await db.properties.aggregate(pipeline).to_list(length=None)
        
        # Properties by type
        type_pipeline = [
            {
                "$group": {
                    "_id": "$property_type",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        properties_by_type = await db.properties.aggregate(type_pipeline).to_list(length=None)
        
        # Properties by listing type
        listing_type_pipeline = [
            {
                "$group": {
                    "_id": "$listing_type",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        properties_by_listing_type = await db.properties.aggregate(listing_type_pipeline).to_list(length=None)
        
        logger.info(f"Property analytics retrieved by admin {admin.get('email')}")
        
        return {
            "listing_trend": listing_trend,
            "properties_by_type": properties_by_type,
            "properties_by_listing_type": properties_by_listing_type,
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Error fetching property analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")
