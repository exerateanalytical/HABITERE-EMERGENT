"""
Bookings Routes Module
=======================
Handles all booking-related API endpoints for Habitere platform.

This module provides:
- Property viewing bookings
- Service booking management
- Booking status workflow (pending → confirmed → completed/cancelled)
- Available time slot checking
- Received bookings for owners/providers
- Booking confirmation and cancellation

Booking Types:
- property_viewing: Schedule property viewings with owners
- service_booking: Book professional services from providers

Booking Lifecycle:
1. pending - Initial booking request
2. confirmed - Accepted by owner/provider
3. completed - Service/viewing completed
4. cancelled - Cancelled by either party

Authorization:
- Clients can create and view their bookings
- Owners/providers can view received bookings and manage status
- Admins have full access

Dependencies:
- FastAPI for routing
- MongoDB for booking storage
- Authentication middleware for protected endpoints

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, date, time
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

# Create router for booking endpoints
# All routes will be prefixed with /api
router = APIRouter(tags=["Bookings"])


# ==================== PYDANTIC MODELS ====================

class BookingCreate(BaseModel):
    """
    Booking creation model.
    
    Used for creating new bookings for properties or services.
    Requires either property_id or service_id based on booking_type.
    """
    booking_type: str  # "property_viewing" or "service_booking"
    property_id: Optional[str] = None
    service_id: Optional[str] = None
    scheduled_date: str  # ISO format date string
    scheduled_time: Optional[str] = None  # HH:MM format (e.g., "14:00")
    duration_hours: Optional[int] = 1
    notes: Optional[str] = None


# ==================== BOOKING CREATION ====================

@router.post("/bookings")
async def create_booking(
    booking_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new booking for property viewing or service.
    
    Clients can book:
    - Property viewings with property owners
    - Professional services from service providers
    
    The booking starts with status "pending" and requires confirmation
    from the owner/provider.
    
    Args:
        booking_data: Booking details including type, date, time, notes
        current_user: Authenticated user (client)
        
    Returns:
        Created booking with generated ID
        
    Raises:
        HTTPException: 400 if invalid booking type or missing required fields
        HTTPException: 404 if property/service not found
        
    Example:
        POST /api/bookings
        {
            "booking_type": "property_viewing",
            "property_id": "123e4567-e89b-12d3-a456-426614174000",
            "scheduled_date": "2025-01-15",
            "scheduled_time": "14:00",
            "notes": "Interested in viewing the property"
        }
    """
    db = get_database()
    
    try:
        # Validate booking type
        booking_type = booking_data.get('booking_type')
        if booking_type not in ['property_viewing', 'service_booking']:
            logger.warning(f"Invalid booking type: {booking_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid booking type. Must be 'property_viewing' or 'service_booking'"
            )
        
        # Validate that either property_id or service_id is provided
        property_id = booking_data.get('property_id')
        service_id = booking_data.get('service_id')
        
        if booking_type == 'property_viewing' and not property_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property ID required for property viewing"
            )
        
        if booking_type == 'service_booking' and not service_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service ID required for service booking"
            )
        
        # Verify property exists if property booking
        if property_id:
            property_doc = await db.properties.find_one({"id": property_id})
            if not property_doc:
                logger.warning(f"Property not found: {property_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Property not found"
                )
        
        # Verify service exists if service booking
        if service_id:
            service_doc = await db.professional_services.find_one({"id": service_id})
            if not service_doc:
                logger.warning(f"Service not found: {service_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service not found"
                )
        
        # Parse scheduled date
        scheduled_date_str = booking_data.get('scheduled_date')
        if not scheduled_date_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduled date is required"
            )
        
        try:
            # Parse ISO format date
            scheduled_date = datetime.fromisoformat(scheduled_date_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Invalid date format: {scheduled_date_str}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format (YYYY-MM-DD)"
            )
        
        # Create booking document
        booking = {
            "id": str(uuid.uuid4()),
            "client_id": current_user.get("id"),
            "property_id": property_id,
            "service_id": service_id,
            "booking_type": booking_type,
            "scheduled_date": scheduled_date.isoformat(),
            "scheduled_time": booking_data.get('scheduled_time'),
            "duration_hours": booking_data.get('duration_hours', 1),
            "status": "pending",
            "notes": booking_data.get('notes', ''),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert into database
        await db.bookings.insert_one(booking)
        
        logger.info(f"Booking created: {booking['id']} by user {current_user.get('email')}")
        
        return {
            "message": "Booking created successfully",
            "booking": serialize_doc(booking)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )


# ==================== BOOKING RETRIEVAL ====================

@router.get("/bookings")
async def get_user_bookings(
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = None
):
    """
    Get all bookings created by current user.
    
    Returns bookings with enriched data including:
    - Property/service details (title, location, price)
    - Provider information for service bookings
    
    Args:
        current_user: Authenticated user (client)
        status: Optional filter by booking status (pending, confirmed, completed, cancelled)
        
    Returns:
        List of user's bookings with related property/service details
        
    Example:
        GET /api/bookings?status=pending
    """
    db = get_database()
    
    try:
        # Build query
        query = {"client_id": current_user.get("id")}
        if status:
            query["status"] = status
        
        # Fetch bookings sorted by scheduled date (newest first)
        bookings_cursor = db.bookings.find(query).sort("scheduled_date", -1)
        bookings = await bookings_cursor.to_list(length=None)
        
        # Enrich bookings with property/service details
        for booking in bookings:
            # Add property details if property booking
            if booking.get('property_id'):
                prop = await db.properties.find_one({"id": booking['property_id']})
                if prop:
                    booking["property_title"] = prop.get("title")
                    booking["property_location"] = prop.get("location")
                    booking["property_price"] = prop.get("price")
            
            # Add service details if service booking
            if booking.get('service_id'):
                service = await db.professional_services.find_one({"id": booking['service_id']})
                if service:
                    booking["service_title"] = service.get("title")
                    booking["service_category"] = service.get("category")
                    
                    # Get provider info
                    provider = await db.users.find_one({"id": service.get("provider_id")})
                    if provider:
                        booking["provider_name"] = provider.get("name")
        
        logger.info(f"Retrieved {len(bookings)} bookings for user {current_user.get('email')}")
        
        return {
            "bookings": [serialize_doc(booking) for booking in bookings]
        }
        
    except Exception as e:
        logger.error(f"Error fetching bookings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bookings"
        )


@router.get("/bookings/received")
async def get_received_bookings(
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = None
):
    """
    Get bookings received by current user (property owner or service provider).
    
    Returns bookings for:
    - Properties owned by current user
    - Services provided by current user
    
    Includes client information for contact purposes.
    
    Args:
        current_user: Authenticated user (owner/provider)
        status: Optional filter by booking status
        
    Returns:
        List of received bookings with client and property/service details
        
    Example:
        GET /api/bookings/received?status=pending
    """
    db = get_database()
    
    try:
        # Find properties owned by current user
        properties = await db.properties.find({"owner_id": current_user.get("id")}).to_list(length=None)
        property_ids = [p["id"] for p in properties]
        
        # Find services provided by current user
        services = await db.professional_services.find({"provider_id": current_user.get("id")}).to_list(length=None)
        service_ids = [s["id"] for s in services]
        
        # Build query for bookings of user's properties/services
        query = {
            "$or": [
                {"property_id": {"$in": property_ids}},
                {"service_id": {"$in": service_ids}}
            ]
        }
        
        if status:
            query["status"] = status
        
        # Fetch bookings
        bookings_cursor = db.bookings.find(query).sort("scheduled_date", -1)
        bookings = await bookings_cursor.to_list(length=None)
        
        # Enrich with client and property/service details
        for booking in bookings:
            # Add client information
            client = await db.users.find_one({"id": booking.get('client_id')})
            if client:
                booking["client_name"] = client.get("name")
                booking["client_email"] = client.get("email")
                booking["client_phone"] = client.get("phone")
            
            # Add property details
            if booking.get('property_id'):
                prop = await db.properties.find_one({"id": booking['property_id']})
                if prop:
                    booking["property_title"] = prop.get("title")
                    booking["property_location"] = prop.get("location")
            
            # Add service details
            if booking.get('service_id'):
                service = await db.professional_services.find_one({"id": booking['service_id']})
                if service:
                    booking["service_title"] = service.get("title")
        
        logger.info(f"Retrieved {len(bookings)} received bookings for user {current_user.get('email')}")
        
        return {
            "bookings": [serialize_doc(booking) for booking in bookings]
        }
        
    except Exception as e:
        logger.error(f"Error fetching received bookings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bookings"
        )


@router.get("/bookings/{booking_id}")
async def get_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get booking details by ID.
    
    Authorization:
    - Clients can view their own bookings
    - Owners/providers can view bookings for their properties/services
    - Admins can view all bookings
    
    Args:
        booking_id: UUID of the booking
        current_user: Authenticated user
        
    Returns:
        Booking details
        
    Raises:
        HTTPException: 404 if booking not found
        HTTPException: 403 if not authorized to view booking
        
    Example:
        GET /api/bookings/123e4567-e89b-12d3-a456-426614174000
    """
    db = get_database()
    
    try:
        booking = await db.bookings.find_one({"id": booking_id})
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Check authorization
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        is_client = booking.get("client_id") == user_id
        
        # Check if user is property owner or service provider
        is_owner = False
        if booking.get('property_id'):
            prop = await db.properties.find_one({"id": booking['property_id']})
            is_owner = prop and prop.get("owner_id") == user_id
        elif booking.get('service_id'):
            service = await db.professional_services.find_one({"id": booking['service_id']})
            is_owner = service and service.get("provider_id") == user_id
        
        # Only client, owner/provider, or admin can view
        if not is_client and not is_owner and user_role != "admin":
            logger.warning(f"Unauthorized access to booking {booking_id} by user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this booking"
            )
        
        logger.info(f"Retrieved booking {booking_id} for user {current_user.get('email')}")
        
        return {
            "booking": serialize_doc(booking)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch booking"
        )


# ==================== BOOKING STATUS MANAGEMENT ====================

@router.put("/bookings/{booking_id}/confirm")
async def confirm_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Confirm a booking (property owner or service provider only).
    
    Changes booking status from "pending" to "confirmed".
    Only the owner/provider can confirm their bookings.
    
    Args:
        booking_id: UUID of the booking to confirm
        current_user: Authenticated user (owner/provider)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if booking not found
        HTTPException: 403 if not authorized (not the owner/provider)
        
    Example:
        PUT /api/bookings/123e4567-e89b-12d3-a456-426614174000/confirm
    """
    db = get_database()
    
    try:
        booking = await db.bookings.find_one({"id": booking_id})
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Check if user is owner/provider
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        is_authorized = False
        if booking.get('property_id'):
            prop = await db.properties.find_one({"id": booking['property_id']})
            is_authorized = prop and prop.get("owner_id") == user_id
        elif booking.get('service_id'):
            service = await db.professional_services.find_one({"id": booking['service_id']})
            is_authorized = service and service.get("provider_id") == user_id
        
        if not is_authorized and user_role != "admin":
            logger.warning(f"Unauthorized confirmation attempt for booking {booking_id} by user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to confirm this booking"
            )
        
        # Update booking status
        result = await db.bookings.update_one(
            {"id": booking_id},
            {
                "$set": {
                    "status": "confirmed",
                    "confirmed_by": user_id,
                    "confirmed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.modified_count:
            logger.info(f"Booking {booking_id} confirmed by user {current_user.get('email')}")
            return {"message": "Booking confirmed successfully"}
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to confirm booking"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm booking"
        )


@router.put("/bookings/{booking_id}/complete")
async def complete_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark booking as completed.
    
    Changes booking status to "completed".
    Only owner/provider or admin can complete bookings.
    
    Args:
        booking_id: UUID of the booking to complete
        current_user: Authenticated user (owner/provider)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if booking not found
        HTTPException: 403 if not authorized
        
    Example:
        PUT /api/bookings/123e4567-e89b-12d3-a456-426614174000/complete
    """
    db = get_database()
    
    try:
        booking = await db.bookings.find_one({"id": booking_id})
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Check authorization
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        is_authorized = False
        if booking.get('property_id'):
            prop = await db.properties.find_one({"id": booking['property_id']})
            is_authorized = prop and prop.get("owner_id") == user_id
        elif booking.get('service_id'):
            service = await db.professional_services.find_one({"id": booking['service_id']})
            is_authorized = service and service.get("provider_id") == user_id
        
        if not is_authorized and user_role != "admin":
            logger.warning(f"Unauthorized completion attempt for booking {booking_id} by user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to complete this booking"
            )
        
        # Update booking status
        result = await db.bookings.update_one(
            {"id": booking_id},
            {"$set": {"status": "completed"}}
        )
        
        if result.modified_count:
            logger.info(f"Booking {booking_id} completed by user {current_user.get('email')}")
            return {"message": "Booking marked as completed"}
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to complete booking"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete booking"
        )


@router.put("/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    reason: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel a booking.
    
    Both clients and owners/providers can cancel bookings.
    Optional cancellation reason can be provided.
    
    Args:
        booking_id: UUID of the booking to cancel
        reason: Optional cancellation reason
        current_user: Authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if booking not found
        HTTPException: 403 if not authorized
        
    Example:
        PUT /api/bookings/123e4567-e89b-12d3-a456-426614174000/cancel
        {
            "reason": "Schedule conflict"
        }
    """
    db = get_database()
    
    try:
        booking = await db.bookings.find_one({"id": booking_id})
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Check if user is client or owner/provider
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        is_client = booking.get("client_id") == user_id
        
        is_owner = False
        if booking.get('property_id'):
            prop = await db.properties.find_one({"id": booking['property_id']})
            is_owner = prop and prop.get("owner_id") == user_id
        elif booking.get('service_id'):
            service = await db.professional_services.find_one({"id": booking['service_id']})
            is_owner = service and service.get("provider_id") == user_id
        
        if not is_client and not is_owner and user_role != "admin":
            logger.warning(f"Unauthorized cancellation attempt for booking {booking_id} by user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this booking"
            )
        
        # Update booking status
        result = await db.bookings.update_one(
            {"id": booking_id},
            {
                "$set": {
                    "status": "cancelled",
                    "cancellation_reason": reason or "Cancelled by user"
                }
            }
        )
        
        if result.modified_count:
            logger.info(f"Booking {booking_id} cancelled by user {current_user.get('email')}")
            return {"message": "Booking cancelled successfully"}
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel booking"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking"
        )


# ==================== TIME SLOT AVAILABILITY ====================

@router.get("/bookings/property/{property_id}/slots")
async def get_available_slots(property_id: str, date: str):
    """
    Get available time slots for a property on a specific date.
    
    Returns hourly slots from 9 AM to 6 PM with availability status.
    Checks existing bookings to determine which slots are available.
    
    Args:
        property_id: UUID of the property
        date: Date in ISO format (YYYY-MM-DD)
        
    Returns:
        List of time slots with availability status
        
    Raises:
        HTTPException: 400 if invalid date format
        
    Example:
        GET /api/bookings/property/123e4567-e89b-12d3-a456-426614174000/slots?date=2025-01-15
        
        Response:
        {
            "date": "2025-01-15",
            "slots": [
                {"time": "09:00", "available": true},
                {"time": "10:00", "available": false},
                {"time": "11:00", "available": true},
                ...
            ]
        }
    """
    db = get_database()
    
    try:
        # Parse date
        try:
            target_date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
        except Exception as e:
            logger.warning(f"Invalid date format: {date}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format (YYYY-MM-DD)"
            )
        
        # Get all bookings for this property on this date
        start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        bookings = await db.bookings.find({
            "property_id": property_id,
            "scheduled_date": {
                "$gte": start_of_day.isoformat(),
                "$lte": end_of_day.isoformat()
            },
            "status": {"$in": ["pending", "confirmed"]}
        }).to_list(length=None)
        
        # Extract booked times
        booked_times = [b.get("scheduled_time") for b in bookings if b.get("scheduled_time")]
        
        # Generate time slots from 9 AM to 6 PM (9:00 to 17:00)
        all_slots = []
        for hour in range(9, 18):
            time_str = f"{hour:02d}:00"
            all_slots.append({
                "time": time_str,
                "available": time_str not in booked_times
            })
        
        logger.info(f"Retrieved {len(all_slots)} time slots for property {property_id} on {date}")
        
        return {
            "date": date,
            "slots": all_slots
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching available slots: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available slots"
        )
