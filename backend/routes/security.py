"""
Homeland Security Routes Module
=================================
Handles all security services API endpoints for Habitere platform.

This module provides:
- Security service marketplace (Guards, CCTV, Remote Monitoring, Patrol, K9, Emergency)
- Security guard profiles and applications
- Security service bookings
- Provider management
- Guard recruitment system

Features:
- Service listings with photos, certifications, ratings
- Instant booking and custom requests
- Emergency dispatch capability
- Guard application and verification process
- Provider and guard dashboards

Authorization:
- Service creation: security_provider, security_admin
- Guard applications: any authenticated user
- Bookings: any authenticated user
- Service management: security_provider, security_admin
- Application approval: security_admin

Dependencies:
- FastAPI for routing
- MongoDB for data storage
- Authentication middleware for protected endpoints

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid
import logging

# Import from parent modules
import sys
from pathlib import Path as FilePath
sys.path.append(str(FilePath(__file__).parent.parent))
from pathlib import Path

from database import get_database
from utils import get_current_user, serialize_doc
from utils.notifications import (
    create_in_app_notification,
    send_booking_confirmation_email,
    send_application_status_email,
    send_booking_confirmed_email
)

# Setup logging
logger = logging.getLogger(__name__)

# Create router for security endpoints
router = APIRouter(prefix="/security", tags=["Homeland Security"])


# ==================== PYDANTIC MODELS ====================

class SecurityServiceCreate(BaseModel):
    """
    Security service creation model.
    
    Used for creating new security service listings.
    """
    title: str
    description: str
    service_type: str  # Security Guards, CCTV Installation, Remote Monitoring, Patrol Units, K9 Units, Emergency Response
    price_range: str  # e.g., "50,000 - 200,000 XAF/month"
    location: str
    images: List[str] = []
    certifications: List[str] = []
    availability: str = "Available"  # Available, Unavailable, Limited
    features: List[str] = []  # e.g., ["24/7 Service", "Armed Guards", "Trained K9s"]
    response_time: Optional[str] = None  # e.g., "15 minutes"


class GuardApplicationCreate(BaseModel):
    """
    Guard application model.
    
    Used when individuals apply to become security guards.
    """
    full_name: str
    phone: str
    email: str
    date_of_birth: str
    national_id: str
    address: str
    city: str
    experience_years: int
    previous_employers: List[str] = []
    certifications: List[str] = []
    training: List[str] = []
    availability: str  # Full-time, Part-time, On-demand
    preferred_locations: List[str] = []
    id_document_url: Optional[str] = None
    photo_url: Optional[str] = None


class SecurityBookingCreate(BaseModel):
    """
    Security service booking model.
    
    Used for booking security services.
    """
    service_id: str
    booking_type: str  # instant, scheduled, emergency
    start_date: str
    end_date: Optional[str] = None
    duration: Optional[str] = None  # e.g., "1 month", "24 hours"
    location: str
    property_id: Optional[str] = None
    num_guards: int = 1
    special_requirements: Optional[str] = None
    emergency_contact: Optional[str] = None


class GuardProfileUpdate(BaseModel):
    """
    Guard profile update model.
    """
    availability: Optional[str] = None
    certifications: Optional[List[str]] = None
    training: Optional[List[str]] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None


# ==================== SECURITY SERVICE MARKETPLACE ====================

@router.get("/services")
async def get_security_services(
    service_type: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 20
):
    """
    Get all security services with optional filtering.
    
    Provides marketplace listing of all available security services including
    guards, CCTV, remote monitoring, patrol units, K9 units, and emergency response.
    
    Args:
        service_type: Filter by service type (Security Guards, CCTV Installation, etc.)
        location: Filter by location (case-insensitive)
        min_price: Minimum price filter
        max_price: Maximum price filter
        skip: Number of items to skip (pagination)
        limit: Maximum number of items to return
        
    Returns:
        List of security service listings
        
    Example:
        GET /api/security/services?service_type=Security Guards&location=Douala
    """
    db = get_database()
    
    # Build filters
    filters = {"availability": {"$ne": "Unavailable"}}
    
    if service_type:
        filters["service_type"] = service_type
    
    if location:
        filters["location"] = {"$regex": location, "$options": "i"}
    
    logger.info(f"Fetching security services with filters: {filters}")
    
    services = await db.security_services.find(filters).skip(skip).limit(limit).to_list(1000)
    
    logger.info(f"Found {len(services)} security services")
    
    return [serialize_doc(service) for service in services]


@router.get("/services/{service_id}")
async def get_security_service(service_id: str):
    """
    Get detailed information about a specific security service.
    
    Args:
        service_id: UUID of the security service
        
    Returns:
        Complete service details including provider info, ratings, and reviews
        
    Raises:
        HTTPException: 404 if service not found
    """
    db = get_database()
    
    service = await db.security_services.find_one({"id": service_id})
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security service not found"
        )
    
    # Get provider info
    provider = await db.users.find_one({"id": service["provider_id"]})
    
    return {
        "service": serialize_doc(service),
        "provider": serialize_doc(provider) if provider else None
    }


@router.post("/services", response_model=Dict[str, Any])
async def create_security_service(
    service_data: SecurityServiceCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new security service listing.
    
    Only security providers and admins can create service listings.
    
    Args:
        service_data: Security service details
        current_user: Authenticated user (must be security_provider or security_admin)
        
    Returns:
        Created service with ID
        
    Raises:
        HTTPException: 403 if user is not authorized
        
    Example:
        POST /api/security/services
        {
            "title": "24/7 Armed Guards",
            "service_type": "Security Guards",
            "price_range": "100,000 - 300,000 XAF/month",
            "location": "Douala"
        }
    """
    db = get_database()
    
    # Check authorization
    if current_user["role"] not in ["security_provider", "security_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only security providers can create services"
        )
    
    # Create service document
    service = {
        "id": str(uuid.uuid4()),
        "provider_id": current_user["id"],
        "provider_name": current_user["name"],
        **service_data.dict(),
        "verified": False,
        "average_rating": 0.0,
        "review_count": 0,
        "booking_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.security_services.insert_one(service)
    
    logger.info(f"Security service created: {service['id']} by {current_user['email']}")
    
    return serialize_doc(service)


@router.put("/services/{service_id}")
async def update_security_service(
    service_id: str,
    service_data: SecurityServiceCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing security service.
    
    Only the provider who created the service or admins can update it.
    
    Args:
        service_id: UUID of the service
        service_data: Updated service details
        current_user: Authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if service not found
        HTTPException: 403 if not authorized
    """
    db = get_database()
    
    service = await db.security_services.find_one({"id": service_id})
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security service not found"
        )
    
    # Check authorization
    if service["provider_id"] != current_user["id"] and current_user["role"] not in ["security_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this service"
        )
    
    # Update service
    await db.security_services.update_one(
        {"id": service_id},
        {"$set": service_data.dict()}
    )
    
    logger.info(f"Security service updated: {service_id}")
    
    return {"message": "Security service updated successfully"}


@router.delete("/services/{service_id}")
async def delete_security_service(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a security service listing.
    
    Args:
        service_id: UUID of the service
        current_user: Authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if service not found
        HTTPException: 403 if not authorized
    """
    db = get_database()
    
    service = await db.security_services.find_one({"id": service_id})
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security service not found"
        )
    
    # Check authorization
    if service["provider_id"] != current_user["id"] and current_user["role"] not in ["security_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this service"
        )
    
    await db.security_services.delete_one({"id": service_id})
    
    logger.info(f"Security service deleted: {service_id}")
    
    return {"message": "Security service deleted successfully"}


# ==================== GUARD APPLICATIONS ====================

@router.post("/guards/apply")
async def apply_as_guard(
    application_data: GuardApplicationCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit an application to become a security guard.
    
    Any authenticated user can apply. Applications go through verification
    by security admins before approval.
    
    Args:
        application_data: Guard application details
        current_user: Authenticated user
        
    Returns:
        Application confirmation with ID
        
    Example:
        POST /api/security/guards/apply
        {
            "full_name": "John Doe",
            "experience_years": 5,
            "certifications": ["First Aid", "Firearms Training"]
        }
    """
    db = get_database()
    
    # Check if user already has a pending or approved application
    existing = await db.guard_applications.find_one({
        "user_id": current_user["id"],
        "status": {"$in": ["pending", "approved"]}
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending or approved application"
        )
    
    # Create application
    application = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "user_email": current_user["email"],
        **application_data.dict(),
        "status": "pending",  # pending, approved, rejected
        "verified": False,
        "background_check": "pending",
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_at": None,
        "reviewed_by": None
    }
    
    await db.guard_applications.insert_one(application)
    
    logger.info(f"Guard application submitted: {application['id']} by {current_user['email']}")
    
    return {
        "message": "Application submitted successfully. You will be notified once reviewed.",
        "application_id": application["id"],
        "status": "pending"
    }


@router.get("/guards/applications")
async def get_guard_applications(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get guard applications.
    
    Regular users see their own applications. Admins see all applications.
    
    Args:
        status: Filter by status (pending, approved, rejected)
        current_user: Authenticated user
        
    Returns:
        List of applications
    """
    db = get_database()
    
    filters = {}
    
    # Regular users only see their own applications
    if current_user["role"] not in ["security_admin", "admin"]:
        filters["user_id"] = current_user["id"]
    
    if status:
        filters["status"] = status
    
    applications = await db.guard_applications.find(filters).to_list(1000)
    
    return [serialize_doc(app) for app in applications]


@router.get("/guards/profiles")
async def get_guard_profiles(
    location: Optional[str] = None,
    availability: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
):
    """
    Get approved guard profiles.
    
    Shows publicly available guards who have been verified and approved.
    
    Args:
        location: Filter by location
        availability: Filter by availability (Full-time, Part-time, On-demand)
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List of approved guard profiles
    """
    db = get_database()
    
    filters = {"status": "approved", "verified": True}
    
    if location:
        filters["preferred_locations"] = {"$regex": location, "$options": "i"}
    
    if availability:
        filters["availability"] = availability
    
    guards = await db.guard_applications.find(filters).skip(skip).limit(limit).to_list(1000)
    
    return [serialize_doc(guard) for guard in guards]


@router.put("/guards/applications/{application_id}/approve")
async def approve_guard_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Approve a guard application.
    
    Only security admins can approve applications.
    
    Args:
        application_id: UUID of the application
        current_user: Authenticated admin
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 403 if not admin
        HTTPException: 404 if application not found
    """
    db = get_database()
    
    # Check authorization
    if current_user["role"] not in ["security_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only security admins can approve applications"
        )
    
    application = await db.guard_applications.find_one({"id": application_id})
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Update application status
    await db.guard_applications.update_one(
        {"id": application_id},
        {"$set": {
            "status": "approved",
            "verified": True,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "reviewed_by": current_user["id"]
        }}
    )
    
    # Update user role
    await db.users.update_one(
        {"id": application["user_id"]},
        {"$set": {"role": "security_guard"}}
    )
    
    logger.info(f"Guard application approved: {application_id} by {current_user['email']}")
    
    # Send notifications
    try:
        # Email notification
        await send_application_status_email(application, application["email"], "approved")
        
        # In-app notification
        await create_in_app_notification(
            user_id=application["user_id"],
            title="Application Approved! 🎉",
            message="Congratulations! You are now a verified security guard",
            type="success",
            link="/dashboard"
        )
    except Exception as e:
        logger.error(f"Error sending approval notifications: {str(e)}")
    
    return {"message": "Application approved successfully"}


# ==================== SECURITY BOOKINGS ====================

@router.post("/bookings")
async def create_security_booking(
    booking_data: SecurityBookingCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new security service booking.
    
    Users can book security services with instant or scheduled options.
    
    Args:
        booking_data: Booking details
        current_user: Authenticated user
        
    Returns:
        Booking confirmation with ID
        
    Example:
        POST /api/security/bookings
        {
            "service_id": "123",
            "booking_type": "scheduled",
            "start_date": "2025-11-01",
            "duration": "1 month",
            "num_guards": 2
        }
    """
    db = get_database()
    
    # Verify service exists
    service = await db.security_services.find_one({"id": booking_data.service_id})
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security service not found"
        )
    
    # Create booking
    booking = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "user_name": current_user["name"],
        "user_email": current_user["email"],
        "provider_id": service["provider_id"],
        "service_title": service["title"],
        **booking_data.dict(),
        "status": "pending",  # pending, confirmed, active, completed, cancelled
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.security_bookings.insert_one(booking)
    
    # Update service booking count
    await db.security_services.update_one(
        {"id": booking_data.service_id},
        {"$inc": {"booking_count": 1}}
    )
    
    logger.info(f"Security booking created: {booking['id']} by {current_user['email']}")
    
    # Send notifications
    try:
        # Email notification
        await send_booking_confirmation_email(booking, current_user["email"], current_user["name"])
        
        # In-app notification for user
        await create_in_app_notification(
            user_id=current_user["id"],
            title="Booking Submitted",
            message=f"Your booking for {service['title']} has been submitted",
            type="success",
            link=f"/security/bookings/{booking['id']}"
        )
        
        # In-app notification for provider
        await create_in_app_notification(
            user_id=service["provider_id"],
            title="New Booking Request",
            message=f"New booking request from {current_user['name']} for {service['title']}",
            type="info",
            link=f"/provider/dashboard"
        )
    except Exception as e:
        logger.error(f"Error sending notifications: {str(e)}")
    
    return {
        "message": "Booking request submitted successfully",
        "booking_id": booking["id"],
        "status": "pending"
    }


@router.get("/bookings")
async def get_security_bookings(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's security bookings.
    
    Returns bookings created by the current user or for their services
    if they're a provider.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of bookings
    """
    db = get_database()
    
    # Users see their own bookings, providers see bookings for their services
    if current_user["role"] in ["security_provider", "security_admin", "admin"]:
        filters = {"$or": [
            {"user_id": current_user["id"]},
            {"provider_id": current_user["id"]}
        ]}
    else:
        filters = {"user_id": current_user["id"]}
    
    bookings = await db.security_bookings.find(filters).to_list(1000)
    
    return [serialize_doc(booking) for booking in bookings]


@router.get("/bookings/{booking_id}")
async def get_security_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of a specific security booking.
    
    Args:
        booking_id: UUID of the booking
        current_user: Authenticated user
        
    Returns:
        Booking details
        
    Raises:
        HTTPException: 404 if booking not found
        HTTPException: 403 if not authorized
    """
    db = get_database()
    
    booking = await db.security_bookings.find_one({"id": booking_id})
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check authorization
    if booking["user_id"] != current_user["id"] and booking["provider_id"] != current_user["id"] and current_user["role"] not in ["security_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this booking"
        )
    
    return serialize_doc(booking)


@router.put("/bookings/{booking_id}/confirm")
async def confirm_security_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Confirm a security booking.
    
    Providers can confirm bookings for their services.
    
    Args:
        booking_id: UUID of the booking
        current_user: Authenticated provider
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if booking not found
        HTTPException: 403 if not the provider
    """
    db = get_database()
    
    booking = await db.security_bookings.find_one({"id": booking_id})
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check authorization
    if booking["provider_id"] != current_user["id"] and current_user["role"] not in ["security_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the provider can confirm this booking"
        )
    
    await db.security_bookings.update_one(
        {"id": booking_id},
        {"$set": {
            "status": "confirmed",
            "confirmed_at": datetime.now(timezone.utc).isoformat(),
            "confirmed_by": current_user["id"]
        }}
    )
    
    logger.info(f"Security booking confirmed: {booking_id}")
    
    # Send notifications
    try:
        # Get user details
        user = await db.users.find_one({"id": booking["user_id"]})
        
        if user:
            # Email notification
            await send_booking_confirmed_email(booking, user["email"], user["name"])
            
            # In-app notification
            await create_in_app_notification(
                user_id=booking["user_id"],
                title="Booking Confirmed!",
                message=f"Your booking for {booking['service_title']} has been confirmed",
                type="success",
                link=f"/security/bookings/{booking_id}"
            )
    except Exception as e:
        logger.error(f"Error sending confirmation notifications: {str(e)}")
    
    return {"message": "Booking confirmed successfully"}


# ==================== IMAGE UPLOAD ====================

@router.post("/upload/image")
async def upload_security_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload an image for security services or guard profiles.
    
    Supports profile photos, service images, and ID documents.
    
    Args:
        file: Image file to upload
        current_user: Authenticated user
        
    Returns:
        Dict with image URL
        
    Raises:
        HTTPException: 400 if file type invalid
    """
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and WebP images allowed"
        )
    
    # Validate file size (max 5MB)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path("/app/backend/uploads/security")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = upload_dir / unique_filename
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    # Return URL (in production, this would be a CDN URL)
    image_url = f"/uploads/security/{unique_filename}"
    
    logger.info(f"Image uploaded: {unique_filename} by {current_user['email']}")
    
    return {
        "url": image_url,
        "filename": unique_filename
    }


# ==================== PAYMENT TRACKING ====================

@router.post("/bookings/{booking_id}/payment")
async def record_payment(
    booking_id: str,
    payment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Record payment for a security booking.
    
    Supports manual payment tracking for cash, bank transfer, or mobile money.
    
    Args:
        booking_id: UUID of the booking
        payment_data: Payment details (amount, method, reference, status)
        current_user: Authenticated user
        
    Returns:
        Payment confirmation
    """
    db = get_database()
    
    booking = await db.security_bookings.find_one({"id": booking_id})
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check authorization (user or provider)
    if booking["user_id"] != current_user["id"] and booking["provider_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Create payment record
    payment = {
        "id": str(uuid.uuid4()),
        "booking_id": booking_id,
        "amount": payment_data.get("amount"),
        "currency": payment_data.get("currency", "XAF"),
        "method": payment_data.get("method", "manual"),  # manual, mobile_money, bank_transfer
        "reference": payment_data.get("reference", ""),
        "status": payment_data.get("status", "pending"),  # pending, completed, failed
        "paid_by": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": payment_data.get("notes", "")
    }
    
    await db.security_payments.insert_one(payment)
    
    # Update booking payment status
    await db.security_bookings.update_one(
        {"id": booking_id},
        {"$set": {"payment_status": payment["status"], "payment_id": payment["id"]}}
    )
    
    logger.info(f"Payment recorded for booking {booking_id}: {payment['amount']} {payment['currency']}")
    
    return serialize_doc(payment)


@router.get("/bookings/{booking_id}/payments")
async def get_booking_payments(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all payment records for a booking."""
    db = get_database()
    
    booking = await db.security_bookings.find_one({"id": booking_id})
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check authorization
    if booking["user_id"] != current_user["id"] and booking["provider_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    payments = await db.security_payments.find({"booking_id": booking_id}).to_list(100)
    
    return [serialize_doc(p) for p in payments]


# ==================== DIGITAL CONTRACTS ====================

@router.post("/bookings/{booking_id}/contract")
async def create_contract(
    booking_id: str,
    contract_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a digital contract for a security booking.
    
    Args:
        booking_id: UUID of the booking
        contract_data: Contract terms and conditions
        current_user: Authenticated user (must be provider)
        
    Returns:
        Contract details
    """
    db = get_database()
    
    booking = await db.security_bookings.find_one({"id": booking_id})
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Only provider can create contract
    if booking["provider_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the provider can create a contract"
        )
    
    # Create contract
    contract = {
        "id": str(uuid.uuid4()),
        "booking_id": booking_id,
        "provider_id": current_user["id"],
        "client_id": booking["user_id"],
        "terms": contract_data.get("terms", ""),
        "start_date": booking["start_date"],
        "end_date": booking.get("end_date"),
        "duration": booking.get("duration"),
        "amount": contract_data.get("amount"),
        "payment_terms": contract_data.get("payment_terms", ""),
        "cancellation_policy": contract_data.get("cancellation_policy", ""),
        "status": "pending_signature",  # pending_signature, signed, active, completed, terminated
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provider_signed": False,
        "client_signed": False
    }
    
    await db.security_contracts.insert_one(contract)
    
    # Update booking with contract
    await db.security_bookings.update_one(
        {"id": booking_id},
        {"$set": {"contract_id": contract["id"], "contract_status": "pending_signature"}}
    )
    
    logger.info(f"Contract created for booking {booking_id}")
    
    return serialize_doc(contract)


@router.post("/contracts/{contract_id}/sign")
async def sign_contract(
    contract_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Sign a digital contract.
    
    Args:
        contract_id: UUID of the contract
        current_user: Authenticated user
        
    Returns:
        Updated contract
    """
    db = get_database()
    
    contract = await db.security_contracts.find_one({"id": contract_id})
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Check if user is authorized to sign
    is_provider = contract["provider_id"] == current_user["id"]
    is_client = contract["client_id"] == current_user["id"]
    
    if not (is_provider or is_client):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to sign this contract"
        )
    
    # Update signature
    update_data = {
        f"{'provider' if is_provider else 'client'}_signed": True,
        f"{'provider' if is_provider else 'client'}_signed_at": datetime.now(timezone.utc).isoformat()
    }
    
    # If both signed, activate contract
    if (is_provider and contract.get("client_signed")) or (is_client and contract.get("provider_signed")):
        update_data["status"] = "active"
        update_data["activated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.security_contracts.update_one(
        {"id": contract_id},
        {"$set": update_data}
    )
    
    logger.info(f"Contract {contract_id} signed by {current_user['email']}")
    
    # Get updated contract
    updated_contract = await db.security_contracts.find_one({"id": contract_id})
    
    return serialize_doc(updated_contract)


@router.get("/contracts/{contract_id}")
async def get_contract(
    contract_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get contract details."""
    db = get_database()
    
    contract = await db.security_contracts.find_one({"id": contract_id})
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Check authorization
    if contract["provider_id"] != current_user["id"] and contract["client_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this contract"
        )
    
    return serialize_doc(contract)


# ==================== NOTIFICATIONS ====================

@router.get("/notifications")
async def get_notifications(
    unread_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's notifications.
    
    Args:
        unread_only: If True, return only unread notifications
        current_user: Authenticated user
        
    Returns:
        List of notifications
    """
    db = get_database()
    
    filters = {"user_id": current_user["id"]}
    if unread_only:
        filters["read"] = False
    
    notifications = await db.notifications.find(filters).sort("created_at", -1).limit(50).to_list(50)
    
    return [serialize_doc(n) for n in notifications]


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read."""
    db = get_database()
    
    notification = await db.notifications.find_one({"id": notification_id})
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if notification["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    await db.notifications.update_one(
        {"id": notification_id},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Notification marked as read"}


@router.put("/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user)
):
    """Mark all notifications as read."""
    db = get_database()
    
    result = await db.notifications.update_many(
        {"user_id": current_user["id"], "read": False},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": f"{result.modified_count} notifications marked as read"}


# ==================== STATISTICS ====================

@router.get("/stats")
async def get_security_stats():
    """
    Get homeland security statistics.
    
    Public endpoint showing platform stats.
    
    Returns:
        Dictionary with security service statistics
    """
    db = get_database()
    
    total_services = await db.security_services.count_documents({})
    total_guards = await db.guard_applications.count_documents({"status": "approved"})
    total_bookings = await db.security_bookings.count_documents({})
    pending_applications = await db.guard_applications.count_documents({"status": "pending"})
    
    return {
        "total_services": total_services,
        "available_guards": total_guards,
        "total_bookings": total_bookings,
        "pending_applications": pending_applications
    }
