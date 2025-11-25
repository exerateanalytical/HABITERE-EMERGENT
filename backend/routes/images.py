"""
Images Routes Module
=====================
Handles image upload and management API endpoints for Habitere platform.

This module provides:
- Multi-file image uploads with validation
- Automatic thumbnail generation
- Image retrieval by entity (property, service, profile)
- Primary image selection
- Image deletion with physical file cleanup

Image Types Supported:
- property: Property listing images
- service: Service provider images
- profile: User profile pictures
- chat: Chat/message attachments

Features:
- File validation (type, size)
- Automatic thumbnail generation (300x300)
- Physical file storage in /uploads
- Database tracking with metadata
- Primary image designation

Dependencies:
- FastAPI for routing with file upload support
- PIL (Pillow) for image processing
- aiofiles for async file operations
- MongoDB for image metadata storage

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import uuid
import logging
import mimetypes
import aiofiles
from PIL import Image, ImageDraw, ImageFont

# Import from parent modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from database import get_database
from utils import get_current_user, serialize_doc

# Setup logging
logger = logging.getLogger(__name__)

# Create router for image endpoints
# All routes will be prefixed with /api
router = APIRouter(tags=["Images"])


# ==================== IMAGE CONFIGURATION ====================

# Get upload directory from parent directory
ROOT_DIR = Path(__file__).parent.parent
UPLOAD_DIR = ROOT_DIR / "uploads"

# Image upload settings
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
THUMBNAIL_SIZE = (300, 300)
WATERMARK_TEXT = "Habitere.com"


# ==================== HELPER FUNCTIONS ====================

def add_watermark(image_path: Path) -> bool:
    """
    Add Habitere.com watermark to an image.
    
    Adds a semi-transparent watermark in the bottom-right corner
    of the image with white text and shadow for visibility.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGBA if not already (for transparency support)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Create a transparent layer for watermark
            watermark_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark_layer)
            
            # Calculate font size based on image dimensions
            img_width, img_height = img.size
            font_size = max(int(min(img_width, img_height) * 0.04), 20)  # 4% of smallest dimension, min 20px
            
            try:
                # Try to use a nice font if available
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Position watermark in bottom-right corner with margin
            margin = int(img_width * 0.02)  # 2% margin
            x = img_width - text_width - margin
            y = img_height - text_height - margin
            
            # Draw shadow for better visibility (slightly offset)
            shadow_offset = 2
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                WATERMARK_TEXT,
                font=font,
                fill=(0, 0, 0, 160)  # Black shadow with 160/255 opacity
            )
            
            # Draw main watermark text (white with transparency)
            draw.text(
                (x, y),
                WATERMARK_TEXT,
                font=font,
                fill=(255, 255, 255, 200)  # White text with 200/255 opacity
            )
            
            # Composite the watermark onto the original image
            watermarked = Image.alpha_composite(img, watermark_layer)
            
            # Convert back to RGB if original was RGB/JPEG
            if image_path.suffix.lower() in ['.jpg', '.jpeg']:
                watermarked = watermarked.convert('RGB')
            
            # Save the watermarked image
            watermarked.save(image_path, quality=95, optimize=True)
            
        logger.info(f"Watermark added to: {image_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding watermark: {e}")
        return False

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
    
    Creates a 300x300 thumbnail with optimized quality.
    
    Args:
        image_path: Path to original image
        thumbnail_path: Path where thumbnail should be saved
        
    Returns:
        bool: True if successful, False otherwise
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


# ==================== IMAGE UPLOAD ====================

@router.post("/upload/images", response_model=Dict[str, Any])
async def upload_images(
    files: List[UploadFile] = File(...),
    entity_type: str = Form(...),  # 'property', 'service', 'profile', 'chat'
    entity_id: Optional[str] = Form(None),
    user: dict = Depends(get_current_user)
):
    """
    Upload multiple images with automatic thumbnail generation.
    
    Supports batch upload of up to 10 images at once.
    Each image is validated, stored, and a thumbnail is generated.
    
    Supported Entity Types:
    - property: Property listing images
    - service: Service provider images
    - profile: User profile pictures
    - chat: Chat message attachments
    
    Args:
        files: List of image files to upload (max 10)
        entity_type: Type of entity (property, service, profile, chat)
        entity_id: ID of the entity (optional for profile images)
        user: Authenticated user (uploader)
        
    Returns:
        List of uploaded images with URLs
        
    Raises:
        HTTPException: 400 if too many files or invalid file
        HTTPException: 401 if not authenticated
        
    Example:
        POST /api/upload/images
        Content-Type: multipart/form-data
        
        Form Data:
        - files: [file1.jpg, file2.png]
        - entity_type: "property"
        - entity_id: "123e4567-e89b-12d3-a456-426614174000"
    """
    db = get_database()
    
    logger.info(f"Image upload request from user {user.get('email')} for {entity_type}")
    
    try:
        # Limit maximum files per upload
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files allowed per upload"
            )
        
        uploaded_images = []
        
        for file in files:
            # Validate file
            is_valid, error_message = validate_image_file(file)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{file.filename}: {error_message}"
                )
            
            # Generate unique filename
            file_ext = Path(file.filename).suffix.lower()
            if not file_ext:
                # Guess extension from MIME type if not in filename
                file_ext = mimetypes.guess_extension(file.content_type) or '.jpg'
            
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            
            # Determine upload path based on entity type
            entity_dir = UPLOAD_DIR / entity_type.lower()
            entity_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
            
            thumbnails_dir = UPLOAD_DIR / "thumbnails"
            thumbnails_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = entity_dir / unique_filename
            thumbnail_path = thumbnails_dir / f"thumb_{unique_filename}"
            
            # Save original file
            content = await file.read()
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            logger.info(f"Saved image: {file_path}")
            
            # Create thumbnail
            await create_thumbnail(file_path, thumbnail_path)
            
            # Create image record in database
            image_data = {
                "id": str(uuid.uuid4()),
                "filename": unique_filename,
                "original_filename": file.filename,
                "file_path": str(file_path.relative_to(ROOT_DIR)),
                "thumbnail_path": str(thumbnail_path.relative_to(ROOT_DIR)),
                "file_size": file.size or len(content),
                "mime_type": file.content_type,
                "uploaded_by": user.get("id"),
                "entity_type": entity_type.lower(),
                "entity_id": entity_id,
                "is_primary": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Save to database
            result = await db.images.insert_one(image_data)
            
            # Build response object
            uploaded_images.append({
                "id": image_data["id"],
                "filename": image_data["filename"],
                "original_filename": image_data["original_filename"],
                "url": f"/uploads/{entity_type.lower()}/{unique_filename}",
                "thumbnail_url": f"/uploads/thumbnails/thumb_{unique_filename}",
                "file_size": image_data["file_size"],
                "mime_type": image_data["mime_type"]
            })
        
        logger.info(f"Successfully uploaded {len(uploaded_images)} images")
        
        return {
            "success": True,
            "message": f"Successfully uploaded {len(uploaded_images)} images",
            "images": uploaded_images
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading images: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload images: {str(e)}"
        )


# ==================== GET IMAGES ====================

@router.get("/images/{entity_type}/{entity_id}", response_model=List[Dict[str, Any]])
async def get_entity_images(entity_type: str, entity_id: str):
    """
    Get all images for a specific entity.
    
    Returns images sorted by creation date (oldest first).
    Includes image URLs for both original and thumbnail.
    
    Public endpoint - no authentication required.
    
    Args:
        entity_type: Type of entity (property, service, profile, chat)
        entity_id: UUID of the entity
        
    Returns:
        List of images with URLs and metadata
        
    Example:
        GET /api/images/property/123e4567-e89b-12d3-a456-426614174000
        
        Response:
        [
            {
                "id": "uuid",
                "filename": "unique_filename.jpg",
                "original_filename": "photo.jpg",
                "url": "/uploads/property/unique_filename.jpg",
                "thumbnail_url": "/uploads/thumbnails/thumb_unique_filename.jpg",
                "is_primary": true,
                "alt_text": null,
                "created_at": "2025-01-15T10:00:00Z"
            },
            ...
        ]
    """
    db = get_database()
    
    try:
        # Find images for entity
        images = await db.images.find({
            "entity_type": entity_type.lower(),
            "entity_id": entity_id
        }).sort("created_at", 1).to_list(length=None)
        
        # Build response with URLs
        result = [{
            "id": img.get("id"),
            "filename": img.get("filename"),
            "original_filename": img.get("original_filename"),
            "url": f"/uploads/{entity_type.lower()}/{img.get('filename')}",
            "thumbnail_url": f"/uploads/thumbnails/thumb_{img.get('filename')}",
            "is_primary": img.get("is_primary", False),
            "alt_text": img.get("alt_text"),
            "created_at": img.get("created_at")
        } for img in images]
        
        logger.info(f"Retrieved {len(result)} images for {entity_type}/{entity_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching images: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch images"
        )


# ==================== SET PRIMARY IMAGE ====================

@router.put("/images/{image_id}/primary")
async def set_primary_image(
    image_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Set an image as primary for its entity.
    
    Only one image can be primary per entity.
    This removes primary status from other images of the same entity.
    
    Authorization:
    - Image uploader can set primary
    - Admins can set any image as primary
    
    Args:
        image_id: UUID of the image to set as primary
        user: Authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if image not found
        HTTPException: 403 if not authorized
        
    Example:
        PUT /api/images/123e4567-e89b-12d3-a456-426614174000/primary
    """
    db = get_database()
    
    try:
        # Get the image
        image = await db.images.find_one({"id": image_id})
        
        if not image:
            logger.warning(f"Image not found: {image_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Check ownership or admin
        if image.get("uploaded_by") != user.get("id") and user.get("role") != "admin":
            logger.warning(f"User {user.get('id')} not authorized to set primary for image {image_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        # Remove primary status from other images of the same entity
        await db.images.update_many(
            {
                "entity_type": image.get("entity_type"),
                "entity_id": image.get("entity_id")
            },
            {"$set": {"is_primary": False}}
        )
        
        # Set this image as primary
        await db.images.update_one(
            {"id": image_id},
            {"$set": {"is_primary": True}}
        )
        
        logger.info(f"Image {image_id} set as primary by {user.get('email')}")
        
        return {
            "success": True,
            "message": "Primary image updated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting primary image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update primary image"
        )


# ==================== DELETE IMAGE ====================

@router.delete("/images/{image_id}")
async def delete_image(
    image_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Delete an uploaded image.
    
    Deletes both:
    - Physical image files (original and thumbnail)
    - Database record
    
    Authorization:
    - Image uploader can delete their images
    - Admins can delete any image
    
    Args:
        image_id: UUID of the image to delete
        user: Authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if image not found
        HTTPException: 403 if not authorized
        
    Example:
        DELETE /api/images/123e4567-e89b-12d3-a456-426614174000
    """
    db = get_database()
    
    try:
        # Get the image
        image = await db.images.find_one({"id": image_id})
        
        if not image:
            logger.warning(f"Image not found: {image_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Check ownership or admin
        if image.get("uploaded_by") != user.get("id") and user.get("role") != "admin":
            logger.warning(f"User {user.get('id')} not authorized to delete image {image_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        # Delete physical files
        file_path = ROOT_DIR / image.get("file_path", "")
        thumbnail_path = ROOT_DIR / image.get("thumbnail_path", "")
        
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            
            if thumbnail_path.exists():
                thumbnail_path.unlink()
                logger.info(f"Deleted thumbnail: {thumbnail_path}")
                
        except Exception as e:
            logger.warning(f"Error deleting physical files: {e}")
        
        # Delete database record
        await db.images.delete_one({"id": image_id})
        
        logger.info(f"Image {image_id} deleted by {user.get('email')}")
        
        return {
            "success": True,
            "message": "Image deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete image"
        )


# ==================== SERVE IMAGE FILE ====================

from fastapi.responses import FileResponse

@router.get("/serve/{folder}/{filename}")
async def serve_image(folder: str, filename: str):
    """
    Serve image files with proper CORS headers.
    
    This endpoint serves images from the uploads directory
    with proper Content-Type and CORS headers to ensure
    cross-origin requests work correctly.
    
    Public endpoint - no authentication required.
    
    Args:
        folder: Subfolder name (property, service, profile, etc.)
        filename: Image filename
        
    Returns:
        FileResponse with image content
        
    Example:
        GET /api/serve/property/abc123.png
    """
    try:
        file_path = UPLOAD_DIR / folder / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Get proper MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "image/jpeg"  # Default
        
        logger.info(f"Serving image: {file_path} with type {mime_type}")
        
        return FileResponse(
            path=str(file_path),
            media_type=mime_type,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=31536000"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to serve image"
        )
