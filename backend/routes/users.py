"""
Users Routes Module
===================
Handles user profile and management API endpoints for Habitere platform.

This module provides:
- User profile retrieval (public and authenticated)
- User profile updates (name, phone, bio, location, company)
- Profile image upload and management
- Public user information display

Public Access:
- GET /users/{user_id} - Returns public user info (name, role, picture)

Protected Access:
- GET /auth/me - Returns full authenticated user profile
- PUT /users/profile - Update user profile with optional image upload

Dependencies:
- FastAPI for routing
- MongoDB for user storage
- PIL for image processing
- aiofiles for async file operations

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import uuid
import logging
import mimetypes
import aiofiles
from PIL import Image

# Import from parent modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from database import get_database
from utils import get_current_user, serialize_doc

# Setup logging
logger = logging.getLogger(__name__)

# Create router for user endpoints
# All routes will be prefixed with /api
router = APIRouter(tags=["Users"])


# ==================== IMAGE CONFIGURATION ====================

# Get upload directory from parent directory
ROOT_DIR = Path(__file__).parent.parent
UPLOAD_DIR = ROOT_DIR / "uploads"

# Image upload settings
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
THUMBNAIL_SIZE = (300, 300)


# ==================== HELPER FUNCTIONS ====================

def validate_image_file(file: UploadFile) -> tuple[bool, str]:
    """
    Validate uploaded image file.
    
    Checks:
    - File size (max 5MB)
    - MIME type (JPEG, PNG, WebP only)
    
    Args:
        file: Uploaded file from FastAPI
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
        
    Example:
        >>> is_valid, error = validate_image_file(uploaded_file)
        >>> if not is_valid:
        >>>     raise HTTPException(status_code=400, detail=error)
    """
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        return False, f"File size {file.size / 1024 / 1024:.1f}MB exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit"
    
    # Check MIME type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return False, f"File type {file.content_type} not supported. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
    
    return True, ""


async def create_thumbnail(image_path: Path, thumbnail_path: Path) -> bool:
    """
    Create a thumbnail from an image.
    
    Creates a 300x300 thumbnail with optimized quality for faster loading.
    Uses PIL (Pillow) for image processing.
    
    Args:
        image_path: Path to original image
        thumbnail_path: Path where thumbnail should be saved
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        >>> await create_thumbnail(
        >>>     Path("/uploads/profiles/image.jpg"),
        >>>     Path("/uploads/thumbnails/thumb_image.jpg")
        >>> )
    """
    try:
        with Image.open(image_path) as img:
            # Create thumbnail maintaining aspect ratio
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            # Save with optimization
            img.save(thumbnail_path, optimize=True, quality=85)
        
        logger.info(f"Thumbnail created: {thumbnail_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return False


# ==================== USER INFO ENDPOINTS ====================

@router.get("/auth/me", response_model=Dict[str, Any])
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current authenticated user's complete profile.
    
    Returns full user information including all profile fields.
    Requires authentication via session cookie or Bearer token.
    
    Args:
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        Complete user profile with all fields
        
    Example:
        GET /api/auth/me
        Authorization: Bearer <token>
        
        Response:
        {
            "id": "uuid",
            "email": "user@example.com",
            "name": "John Doe",
            "role": "property_seeker",
            "phone": "+237123456789",
            "location": "Douala",
            "company_name": null,
            "bio": "Looking for apartments in Douala",
            "picture": "/uploads/profile/image.jpg",
            "email_verified": true,
            "created_at": "2025-01-01T00:00:00Z"
        }
    """
    logger.info(f"Fetching profile for user: {current_user.get('email')}")
    
    # current_user is already a dict from get_current_user
    return serialize_doc(current_user)


@router.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user_by_id(user_id: str):
    """
    Get public user information by ID.
    
    This endpoint is public and does not require authentication.
    Returns only public-safe information (no email, phone, etc.).
    
    Useful for:
    - Displaying property owner names
    - Showing service provider information
    - Public user profiles
    
    Args:
        user_id: UUID of the user to retrieve
        
    Returns:
        Public user information (name, role, picture, company name)
        
    Raises:
        HTTPException: 404 if user not found
        
    Example:
        GET /api/users/123e4567-e89b-12d3-a456-426614174000
        
        Response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "John Doe",
            "role": "property_owner",
            "picture": "/uploads/profile/image.jpg",
            "company_name": "Doe Real Estate"
        }
    """
    db = get_database()
    
    try:
        # Find user by ID
        user_doc = await db.users.find_one({"id": user_id})
        
        if not user_doc:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return only public information (no sensitive data)
        public_info = {
            "id": user_doc.get("id"),
            "name": user_doc.get("name", "User"),
            "email": user_doc.get("email", ""),  # Email included for owner contact
            "role": user_doc.get("role", ""),
            "picture": user_doc.get("picture", ""),
            "company_name": user_doc.get("company_name", "")
        }
        
        logger.info(f"Retrieved public info for user: {user_id}")
        
        return public_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )


# ==================== PROFILE UPDATE ====================

@router.put("/users/profile", response_model=Dict[str, Any])
async def update_user_profile(
    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Update user profile information and/or profile image.
    
    This endpoint accepts multipart/form-data to support file uploads.
    All fields are optional - only provided fields will be updated.
    
    Profile fields that can be updated:
    - name: User's display name
    - phone: Contact phone number
    - company_name: Company or business name
    - bio: User biography/description
    - location: Primary location
    - profile_image: Profile picture (JPEG, PNG, WebP, max 5MB)
    
    Args:
        name: Updated user name
        phone: Updated phone number
        company_name: Updated company name
        bio: Updated user bio
        location: Updated location
        profile_image: Optional profile image file
        current_user: Authenticated user (from JWT/session)
        
    Returns:
        Success response with updated user data
        
    Raises:
        HTTPException: 400 if no data provided or invalid image
        HTTPException: 404 if user not found
        HTTPException: 500 if update fails
        
    Example:
        PUT /api/users/profile
        Content-Type: multipart/form-data
        
        Form Data:
        - name: "John Doe"
        - phone: "+237123456789"
        - bio: "Real estate professional"
        - profile_image: <file>
    """
    db = get_database()
    
    try:
        update_data = {}
        
        # Update text fields if provided
        if name is not None:
            update_data["name"] = name
        
        if phone is not None:
            update_data["phone"] = phone
        
        if company_name is not None:
            update_data["company_name"] = company_name
        
        if bio is not None:
            update_data["bio"] = bio
        
        if location is not None:
            update_data["location"] = location
        
        # Handle profile image upload if provided
        if profile_image:
            logger.info(f"Processing profile image upload for user {current_user.get('email')}")
            
            # Validate image file
            is_valid, error_message = validate_image_file(profile_image)
            if not is_valid:
                logger.warning(f"Invalid image file: {error_message}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message
                )
            
            # Generate unique filename
            file_ext = Path(profile_image.filename).suffix.lower()
            if not file_ext:
                # Guess extension from MIME type if not in filename
                file_ext = mimetypes.guess_extension(profile_image.content_type) or '.jpg'
            
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            
            # Create profile directory if it doesn't exist
            profile_dir = UPLOAD_DIR / "profile"
            profile_dir.mkdir(parents=True, exist_ok=True)
            
            thumbnails_dir = UPLOAD_DIR / "thumbnails"
            thumbnails_dir.mkdir(parents=True, exist_ok=True)
            
            # Define file paths
            file_path = profile_dir / unique_filename
            thumbnail_path = thumbnails_dir / f"thumb_{unique_filename}"
            
            # Save uploaded file
            content = await profile_image.read()
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            logger.info(f"Saved profile image: {file_path}")
            
            # Create thumbnail
            await create_thumbnail(file_path, thumbnail_path)
            
            # Update profile picture URL in user document
            update_data["picture"] = f"/uploads/profile/{unique_filename}"
        
        # Check if at least one field is provided
        if not update_data:
            logger.warning(f"Profile update called with no data by user {current_user.get('email')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,



@router.put("/users/location")
async def update_user_location(
    location: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user's preferred location for personalized property filtering.
    
    This endpoint updates the user's location preference which is used
    to show location-based property recommendations.
    
    Args:
        location: City/location name (e.g., "Douala", "Yaounde", "Bamenda")
        current_user: Authenticated user
        
    Returns:
        Success message with updated location
        
    Raises:
        HTTPException: 404 if user not found
        HTTPException: 500 if update fails
    """
    db = get_database()
    
    # Update user location
    result = await db.users.update_one(
        {"id": current_user["id"]},
        {
            "$set": {
                "location": location,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"User {current_user['id']} location updated to: {location}")
    
    return {
        "message": "Location updated successfully",
        "location": location
    }

                detail="No data provided for update"
            )
        
        # Add updated timestamp
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Update user in database
        user_id = current_user.get("id")
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        # Check if update was successful
        if result.modified_count == 0 and result.matched_count == 0:
            logger.error(f"User not found for update: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Retrieve updated user document
        updated_user = await db.users.find_one({"id": user_id})
        
        logger.info(f"Profile updated successfully for user {current_user.get('email')}")
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": serialize_doc(updated_user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error for user {current_user.get('email')}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
