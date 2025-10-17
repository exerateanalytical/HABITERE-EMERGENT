"""
Services Routes Module
=======================
Handles all professional services API endpoints for Habitere platform.

This module provides:
- Service listing with filtering (category, location)
- Service details retrieval
- Service creation and management
- Service provider listings
- Service verification workflow (admin)

Service Categories Include:
- Construction Companies
- Bricklayers, Plumbers, Electricians
- Interior Designers, Architects
- Borehole Drillers, Cleaning Companies
- Painters, Carpenters, Evaluators
- Building Material Suppliers, Furnishing Shops

Authorization:
- Service creation: service provider roles + admin
- Service listing: public access
- Service management: service provider or admin

Dependencies:
- FastAPI for routing
- MongoDB for service storage
- Authentication middleware for protected endpoints

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
import uuid
import logging

# Import from parent modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_database
from utils import get_current_user, serialize_doc

# Setup logging
logger = logging.getLogger(__name__)

# Create router for service endpoints
# All routes will be prefixed with /api
router = APIRouter(tags=["Services"])


# ==================== PYDANTIC MODELS ====================

class ServiceCreate(BaseModel):
    """
    Service creation model.
    
    Used for creating new professional services.
    Service providers can list their services with details and pricing.
    """
    category: str  # e.g., "plumber", "electrician", "construction_company"
    title: str
    description: str
    price_range: Optional[str] = None  # e.g., "5000-10000 XAF/hour"
    location: str
    images: List[str] = []


# ==================== SERVICE LISTING & DETAILS ====================

@router.get("/services", response_model=List[Dict[str, Any]])
async def get_services(
    category: Optional[str] = None,
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
):
    """
    Get professional services with optional filtering.
    
    This endpoint provides flexible service search:
    - Filter by service category (plumber, electrician, etc.)
    - Filter by location (case-insensitive partial match)
    - Pagination with skip and limit
    
    Only shows available (active) services by default.
    
    Args:
        category: Filter by service category (e.g., "plumber", "electrician")
        location: Filter by location (case-insensitive regex search)
        skip: Number of items to skip (pagination)
        limit: Maximum number of items to return (default: 20)
    
    Returns:
        List of service documents matching the filters
        
    Example:
        GET /api/services?category=plumber&location=Douala&limit=10
    """
    db = get_database()
    
    # Build filters - only show available services by default
    filters = {"available": True}
    
    if category:
        filters["category"] = category
    
    if location:
        # Case-insensitive partial match for location
        filters["location"] = {"$regex": location, "$options": "i"}
    
    logger.info(f"Fetching services with filters: {filters}, skip={skip}, limit={limit}")
    
    # Query database with filters and pagination
    services = await db.services.find(filters).skip(skip).limit(limit).to_list(1000)
    
    logger.info(f"Found {len(services)} services matching filters")
    
    # Serialize documents (remove MongoDB _id, convert dates to ISO strings)
    return [serialize_doc(service) for service in services]


@router.get("/services/{service_id}", response_model=Dict[str, Any])
async def get_service(service_id: str):
    """
    Get single service by ID.
    
    Retrieves detailed information for a specific professional service.
    Public endpoint - no authentication required.
    
    Args:
        service_id: UUID of the service to retrieve
        
    Returns:
        Service document with all details
        
    Raises:
        HTTPException: 404 if service not found
        
    Example:
        GET /api/services/123e4567-e89b-12d3-a456-426614174000
    """
    db = get_database()
    
    # Find service by UUID
    service_doc = await db.services.find_one({"id": service_id})
    
    if not service_doc:
        logger.warning(f"Service not found: {service_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    logger.info(f"Retrieved service: {service_id}")
    
    return serialize_doc(service_doc)


# ==================== SERVICE CREATION ====================

@router.post("/services", response_model=Dict[str, Any]])
async def create_service(
    service_data: ServiceCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new professional service listing.
    
    Only users with service provider roles can create services:
    - construction_company
    - bricklayer
    - plumber
    - electrician
    - interior_designer
    - borehole_driller
    - cleaning_company
    - painter
    - architect
    - carpenter
    - evaluator
    - building_material_supplier
    - furnishing_shop
    - admin (can create any service)
    
    The service is automatically assigned to the authenticated user
    and starts with verification_status="pending" for admin approval.
    
    Args:
        service_data: Service details from request body
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        Created service document with generated ID
        
    Raises:
        HTTPException: 403 if user doesn't have permission to create services
        
    Example:
        POST /api/services
        {
            "category": "plumber",
            "title": "Professional Plumbing Services",
            "description": "Expert plumbing repairs and installations",
            "price_range": "5000-15000 XAF/hour",
            "location": "Douala",
            "images": []
        }
    """
    db = get_database()
    
    # Define service provider roles
    service_provider_roles = [
        "construction_company", "bricklayer", "plumber", "electrician", 
        "interior_designer", "borehole_driller", "cleaning_company", 
        "painter", "architect", "carpenter", "evaluator", 
        "building_material_supplier", "furnishing_shop"
    ]
    
    user_role = current_user.get("role")
    
    # Check if user has permission to create services
    if user_role not in service_provider_roles and user_role != "admin":
        logger.warning(f"User {current_user.get('email')} with role '{user_role}' attempted to create service")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create services. Must be a service provider or admin."
        )
    
    # Convert Pydantic model to dictionary
    service_doc = service_data.model_dump()
    
    # Add system-generated fields
    service_doc["id"] = str(uuid.uuid4())
    service_doc["provider_id"] = current_user.get("id")
    service_doc["created_at"] = datetime.now(timezone.utc).isoformat()
    service_doc["available"] = True
    service_doc["verified"] = False
    service_doc["verification_status"] = "pending"
    service_doc["average_rating"] = 0.0
    service_doc["review_count"] = 0
    
    # Insert into database
    await db.services.insert_one(service_doc)
    
    logger.info(f"Created service {service_doc['id']} by user {current_user.get('email')}")
    
    return serialize_doc(service_doc)


# ==================== SERVICE PROVIDER LISTINGS ====================

@router.get("/users/me/services", response_model=List[Dict[str, Any]])
async def get_current_user_services(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's services.
    
    Returns all services provided by the authenticated user.
    Useful for "My Services" pages in the frontend.
    
    Args:
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        List of services provided by the current user
        
    Example:
        GET /api/users/me/services
    """
    db = get_database()
    
    user_id = current_user.get("id")
    
    # Find all services provided by current user
    services = await db.services.find({"provider_id": user_id}).to_list(1000)
    
    logger.info(f"Retrieved {len(services)} services for user {current_user.get('email')}")
    
    return [serialize_doc(service) for service in services]


@router.get("/users/{user_id}/services", response_model=List[Dict[str, Any]])
async def get_user_services(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific user's services.
    
    Authorization:
    - Users can only view their own services
    - Admins can view any user's services
    - Public users can view verified services only
    
    Args:
        user_id: UUID of the user whose services to retrieve
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        List of services provided by the specified user
        
    Raises:
        HTTPException: 403 if trying to view another user's unverified services (non-admin)
        
    Example:
        GET /api/users/123e4567-e89b-12d3-a456-426614174000/services
    """
    db = get_database()
    
    current_user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    # Build query based on authorization
    query = {"provider_id": user_id}
    
    # If not the owner and not admin, only show verified services
    if user_id != current_user_id and user_role != "admin":
        query["verified"] = True
        query["available"] = True
    
    # Find services
    services = await db.services.find(query).to_list(1000)
    
    logger.info(f"Retrieved {len(services)} services for user {user_id}")
    
    return [serialize_doc(service) for service in services]


# ==================== SERVICE UPDATE & DELETE ====================

@router.put("/services/{service_id}", response_model=Dict[str, Any])
async def update_service(
    service_id: str,
    service_data: ServiceCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing service.
    
    Only the service provider or admins can update a service.
    System-generated fields (id, provider_id, created_at, etc.) are preserved.
    
    Args:
        service_id: UUID of the service to update
        service_data: Updated service details
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        Updated service document
        
    Raises:
        HTTPException: 404 if service not found
        HTTPException: 403 if user is not the provider or admin
        
    Example:
        PUT /api/services/123e4567-e89b-12d3-a456-426614174000
        {
            "title": "Updated Service Title",
            "price_range": "10000-20000 XAF/hour",
            ...
        }
    """
    db = get_database()
    
    # Find existing service
    service_doc = await db.services.find_one({"id": service_id})
    
    if not service_doc:
        logger.warning(f"Service not found for update: {service_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Check authorization: provider or admin only
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    if service_doc["provider_id"] != user_id and user_role != "admin":
        logger.warning(f"User {user_id} attempted unauthorized update of service {service_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this service"
        )
    
    # Convert Pydantic model to dictionary
    update_data = service_data.model_dump()
    
    # Update in database
    await db.services.update_one(
        {"id": service_id},
        {"$set": update_data}
    )
    
    # Retrieve and return updated document
    updated_doc = await db.services.find_one({"id": service_id})
    
    logger.info(f"Updated service {service_id} by user {current_user.get('email')}")
    
    return serialize_doc(updated_doc)


@router.delete("/services/{service_id}")
async def delete_service(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a service.
    
    Only the service provider or admins can delete a service.
    This is a hard delete - the service is permanently removed.
    
    Args:
        service_id: UUID of the service to delete
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if service not found
        HTTPException: 403 if user is not the provider or admin
        
    Example:
        DELETE /api/services/123e4567-e89b-12d3-a456-426614174000
    """
    db = get_database()
    
    # Find existing service
    service_doc = await db.services.find_one({"id": service_id})
    
    if not service_doc:
        logger.warning(f"Service not found for deletion: {service_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Check authorization: provider or admin only
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    if service_doc["provider_id"] != user_id and user_role != "admin":
        logger.warning(f"User {user_id} attempted unauthorized deletion of service {service_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this service"
        )
    
    # Delete from database
    await db.services.delete_one({"id": service_id})
    
    logger.info(f"Deleted service {service_id} by user {current_user.get('email')}")
    
    return {"message": "Service deleted successfully"}
