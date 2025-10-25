"""
Properties Routes Module
=========================
Handles all property-related API endpoints for Habitere platform.

This module provides:
- Property listing with advanced filtering (type, location, price range)
- Property details retrieval
- Property CRUD operations (Create, Read, Update, Delete)
- Owner-specific property management
- Property cleanup utilities for development/testing
- User property listings (my properties, user properties)

Authorization:
- Property creation: property_owner, real_estate_agent, real_estate_company, admin
- Property update/delete: property owner or admin
- Property listing: public access
- Property cleanup: admin only

Dependencies:
- FastAPI for routing
- MongoDB for property storage
- Authentication middleware for protected endpoints

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
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

# Create router for property endpoints
# All routes will be prefixed with /api
router = APIRouter(tags=["Properties"])


# ==================== PYDANTIC MODELS ====================

class PropertyCreate(BaseModel):
    """
    Property creation/update model.
    
    Used for creating new properties or updating existing ones.
    All property fields except system-generated ones (id, owner_id, timestamps).
    
    Validation Rules:
    - title: 5-200 characters
    - description: 50-2000 characters
    - price: must be positive (> 0)
    - bedrooms: 0-50 (non-negative)
    - bathrooms: 0-50 (non-negative)
    - area_sqm: must be positive if provided
    """
    title: str = Field(..., min_length=5, max_length=200, description="Property title (5-200 characters)")
    description: str = Field(..., min_length=50, max_length=2000, description="Property description (50-2000 characters)")
    price: float = Field(..., gt=0, description="Property price (must be positive)")
    location: str = Field(..., min_length=3, max_length=200, description="Property location")
    property_type: Optional[str] = None  # Keeping for backward compatibility
    property_sector: Optional[str] = None  # New: Residential, Commercial, etc.
    property_category: Optional[str] = None  # New: Specific category
    listing_type: str  # sale, rent, lease, short_let, auction
    bedrooms: Optional[int] = Field(default=0, ge=0, le=50, description="Number of bedrooms (0-50)")
    bathrooms: Optional[int] = Field(default=0, ge=0, le=50, description="Number of bathrooms (0-50)")
    area_sqm: Optional[float] = Field(default=None, gt=0, description="Area in square meters (must be positive)")
    images: List[str] = []
    amenities: List[str] = []


# ==================== PROPERTY LISTING & DETAILS ====================

@router.get("/properties", response_model=List[Dict[str, Any]])
async def get_properties(
    property_type: Optional[str] = None,
    listing_type: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    user_location: Optional[str] = None,
    sort_by_location: bool = False,
    skip: int = 0,
    limit: int = 100
):
    """
    Get properties with optional filtering and location-based sorting.
    
    This endpoint provides flexible property search with multiple filter parameters:
    - Filter by property type (house, apartment, land, etc.)
    - Filter by listing type (sale, rent, lease, etc.)
    - Filter by location (case-insensitive partial match)
    - Filter by price range (min and/or max)
    - Sort by user location (show user's city properties first)
    - Pagination with skip and limit
    
    Args:
        property_type: Filter by property type (e.g., "apartment", "house")
        listing_type: Filter by listing type (e.g., "sale", "rent")
        location: Filter by specific location (case-insensitive regex search)
        min_price: Minimum price filter
        max_price: Maximum price filter
        user_location: User's current location for sorting (e.g., "Douala", "Yaounde")
        sort_by_location: If True, sort properties with user_location first
        skip: Number of items to skip (pagination)
        limit: Maximum number of items to return (default: 100)
    
    Returns:
        List of property documents matching the filters, sorted by location if requested
        
    Example:
        GET /api/properties?user_location=Douala&sort_by_location=true&limit=20
        GET /api/properties?location=Douala&listing_type=rent&min_price=100000&limit=10
    """
    db = get_database()
    
    # Build filters - only show available properties by default
    filters = {"available": True}
    
    if property_type:
        filters["property_type"] = property_type
    
    if listing_type:
        filters["listing_type"] = listing_type
    
    if location:
        # Case-insensitive partial match for location
        filters["location"] = {"$regex": location, "$options": "i"}
    
    # Price range filtering
    if min_price is not None:
        filters["price"] = {"$gte": min_price}
    
    if max_price is not None:
        if "price" in filters:
            # Combine with existing min_price filter
            filters["price"]["$lte"] = max_price
        else:
            filters["price"] = {"$lte": max_price}
    
    logger.info(f"Fetching properties with filters: {filters}, skip={skip}, limit={limit}")
    
    # Query database with filters and pagination
    properties = await db.properties.find(filters).skip(skip).limit(limit).to_list(1000)
    
    logger.info(f"Found {len(properties)} properties matching filters")
    
    # Serialize documents
    serialized_properties = [serialize_doc(prop) for prop in properties]
    
    # Sort by location if requested and user_location is provided
    if sort_by_location and user_location:
        # Normalize location for comparison
        user_loc_lower = user_location.lower().strip()
        
        # Sort: properties in user's location first, then others
        def location_sort_key(prop):
            prop_location = prop.get("location", "").lower().strip()
            # Return 0 if location matches (comes first), 1 if not (comes later)
            return 0 if user_loc_lower in prop_location else 1
        
        serialized_properties.sort(key=location_sort_key)
        logger.info(f"Properties sorted by location priority: {user_location}")
    
    return serialized_properties


@router.get("/properties/{property_id}", response_model=Dict[str, Any])
async def get_property(property_id: str):
    """
    Get single property by ID.
    
    Retrieves detailed information for a specific property.
    Public endpoint - no authentication required.
    
    Args:
        property_id: UUID of the property to retrieve
        
    Returns:
        Property document with all details
        
    Raises:
        HTTPException: 404 if property not found
        
    Example:
        GET /api/properties/123e4567-e89b-12d3-a456-426614174000
    """
    db = get_database()
    
    # Find property by UUID
    property_doc = await db.properties.find_one({"id": property_id})
    
    if not property_doc:
        logger.warning(f"Property not found: {property_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    logger.info(f"Retrieved property: {property_id}")
    
    return serialize_doc(property_doc)


# ==================== PROPERTY CRUD OPERATIONS ====================

@router.post("/properties", response_model=Dict[str, Any])
async def create_property(
    property_data: PropertyCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new property listing.
    
    Only users with specific roles can create properties:
    - property_owner
    - real_estate_agent
    - real_estate_company
    - admin
    
    The property is automatically assigned to the authenticated user
    and starts with verification_status="pending" for admin approval.
    
    Args:
        property_data: Property details from request body
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        Created property document with generated ID
        
    Raises:
        HTTPException: 403 if user doesn't have permission to create properties
        
    Example:
        POST /api/properties
        {
            "title": "Modern 3-Bedroom Apartment",
            "description": "Spacious apartment in city center",
            "price": 180000,
            "location": "Douala",
            "listing_type": "rent",
            "bedrooms": 3,
            "bathrooms": 2,
            "amenities": ["parking", "security"]
        }
    """
    db = get_database()
    
    # Check if user has permission to create properties
    allowed_roles = ["property_owner", "real_estate_agent", "real_estate_company", "admin"]
    user_role = current_user.get("role")
    
    if user_role not in allowed_roles:
        logger.warning(f"User {current_user.get('email')} with role '{user_role}' attempted to create property")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create properties. Required roles: property_owner, real_estate_agent, real_estate_company, or admin"
        )
    
    # Convert Pydantic model to dictionary
    property_doc = property_data.model_dump()
    
    # Add system-generated fields
    property_doc["id"] = str(uuid.uuid4())
    property_doc["owner_id"] = current_user.get("id")
    property_doc["created_at"] = datetime.now(timezone.utc).isoformat()
    property_doc["available"] = True
    property_doc["verified"] = False
    property_doc["verification_status"] = "pending"
    property_doc["views"] = 0
    property_doc["favorites"] = 0
    property_doc["average_rating"] = 0.0
    property_doc["review_count"] = 0
    
    # Insert into database
    await db.properties.insert_one(property_doc)
    
    logger.info(f"Created property {property_doc['id']} by user {current_user.get('email')}")
    
    return serialize_doc(property_doc)


@router.put("/properties/{property_id}", response_model=Dict[str, Any])
async def update_property(
    property_id: str,
    property_data: PropertyCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing property.
    
    Only the property owner or admins can update a property.
    System-generated fields (id, owner_id, created_at, etc.) are preserved.
    
    Args:
        property_id: UUID of the property to update
        property_data: Updated property details
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        Updated property document
        
    Raises:
        HTTPException: 404 if property not found
        HTTPException: 403 if user is not the owner or admin
        
    Example:
        PUT /api/properties/123e4567-e89b-12d3-a456-426614174000
        {
            "title": "Updated Title",
            "price": 200000,
            ...
        }
    """
    db = get_database()
    
    # Find existing property
    property_doc = await db.properties.find_one({"id": property_id})
    
    if not property_doc:
        logger.warning(f"Property not found for update: {property_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check authorization: owner or admin only
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    if property_doc["owner_id"] != user_id and user_role != "admin":
        logger.warning(f"User {user_id} attempted unauthorized update of property {property_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this property"
        )
    
    # Convert Pydantic model to dictionary
    update_data = property_data.model_dump()
    
    # Update in database
    await db.properties.update_one(
        {"id": property_id},
        {"$set": update_data}
    )
    
    # Retrieve and return updated document
    updated_doc = await db.properties.find_one({"id": property_id})
    
    logger.info(f"Updated property {property_id} by user {current_user.get('email')}")
    
    return serialize_doc(updated_doc)


@router.delete("/properties/{property_id}")
async def delete_property(
    property_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a property.
    
    Only the property owner or admins can delete a property.
    This is a hard delete - the property is permanently removed.
    
    Args:
        property_id: UUID of the property to delete
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if property not found
        HTTPException: 403 if user is not the owner or admin
        
    Example:
        DELETE /api/properties/123e4567-e89b-12d3-a456-426614174000
    """
    db = get_database()
    
    # Find existing property
    property_doc = await db.properties.find_one({"id": property_id})
    
    if not property_doc:
        logger.warning(f"Property not found for deletion: {property_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check authorization: owner or admin only
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    if property_doc["owner_id"] != user_id and user_role != "admin":
        logger.warning(f"User {user_id} attempted unauthorized deletion of property {property_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this property"
        )
    
    # Delete from database
    await db.properties.delete_one({"id": property_id})
    
    logger.info(f"Deleted property {property_id} by user {current_user.get('email')}")
    
    return {"message": "Property deleted successfully"}


# ==================== PROPERTY CLEANUP (DEVELOPMENT) ====================

async def cleanup_old_properties() -> int:
    """
    Delete properties older than 1 hour.
    
    This is a utility function for development/testing to automatically
    clean up test properties. In production, you may want to disable this
    or adjust the time threshold.
    
    Returns:
        Number of properties deleted
        
    Note:
        This function is called automatically on application startup
        and can be triggered manually via the cleanup endpoint (admin only).
    """
    db = get_database()
    
    try:
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        
        # Delete properties created more than 1 hour ago
        result = await db.properties.delete_many({
            "created_at": {"$lt": one_hour_ago.isoformat()}
        })
        
        if result.deleted_count > 0:
            logger.info(f"Deleted {result.deleted_count} properties older than 1 hour")
        
        return result.deleted_count
        
    except Exception as e:
        logger.error(f"Error during property cleanup: {e}")
        return 0


@router.delete("/properties/cleanup/old")
async def cleanup_old_properties_endpoint(
    current_user: dict = Depends(get_current_user)
):
    """
    Manually trigger cleanup of old properties (Admin only).
    
    Deletes all properties created more than 1 hour ago.
    Useful for clearing test data in development/staging environments.
    
    Args:
        current_user: Authenticated user (must be admin)
        
    Returns:
        Cleanup result with count of deleted properties
        
    Raises:
        HTTPException: 403 if user is not an admin
        
    Example:
        DELETE /api/properties/cleanup/old
    """
    # Check if user is admin
    if current_user.get("role") != "admin":
        logger.warning(f"Non-admin user {current_user.get('email')} attempted property cleanup")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for property cleanup"
        )
    
    # Run cleanup
    deleted_count = await cleanup_old_properties()
    
    logger.info(f"Manual cleanup triggered by {current_user.get('email')}: {deleted_count} properties deleted")
    
    return {
        "success": True,
        "message": f"Cleanup completed successfully",
        "deleted_count": deleted_count
    }


# ==================== USER PROPERTY LISTINGS ====================

@router.get("/users/me/properties", response_model=List[Dict[str, Any]])
async def get_current_user_properties(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's properties.
    
    Returns all properties owned by the authenticated user.
    Useful for "My Properties" pages in the frontend.
    
    Args:
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        List of properties owned by the current user
        
    Example:
        GET /api/users/me/properties
    """
    db = get_database()
    
    user_id = current_user.get("id")
    
    # Find all properties owned by current user
    properties = await db.properties.find({"owner_id": user_id}).to_list(1000)
    
    logger.info(f"Retrieved {len(properties)} properties for user {current_user.get('email')}")
    
    return [serialize_doc(prop) for prop in properties]


@router.get("/users/{user_id}/properties", response_model=List[Dict[str, Any]])
async def get_user_properties(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific user's properties.
    
    Authorization:
    - Users can only view their own properties
    - Admins can view any user's properties
    
    Args:
        user_id: UUID of the user whose properties to retrieve
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        List of properties owned by the specified user
        
    Raises:
        HTTPException: 403 if trying to view another user's properties (non-admin)
        
    Example:
        GET /api/users/123e4567-e89b-12d3-a456-426614174000/properties
    """
    db = get_database()
    
    # Check authorization: user can only view own properties unless admin
    current_user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    if user_id != current_user_id and user_role != "admin":
        logger.warning(f"User {current_user_id} attempted to view properties of user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view other users' properties"
        )
    
    # Find all properties owned by specified user
    properties = await db.properties.find({"owner_id": user_id}).to_list(1000)
    
    logger.info(f"Retrieved {len(properties)} properties for user {user_id}")
    
    return [serialize_doc(prop) for prop in properties]
