"""
Reviews Routes Module
=====================
Handles all review and rating API endpoints for Habitere platform.

This module provides:
- Property and service reviews
- 5-star rating system
- Review CRUD operations
- Automatic rating aggregation
- Duplicate review prevention
- Reviewer information enrichment

Rating System:
- 1-5 star ratings (integer)
- Average rating calculation
- Review count tracking
- Real-time aggregation updates

Authorization:
- Any authenticated user can create reviews
- Users can only update/delete their own reviews
- Admins can delete any review
- Public access to view reviews

Dependencies:
- FastAPI for routing
- MongoDB for review storage with aggregation
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

# Create router for review endpoints
# All routes will be prefixed with /api
router = APIRouter(tags=["Reviews"])


# ==================== PYDANTIC MODELS ====================

class ReviewCreate(BaseModel):
    """
    Review creation model.
    
    Used for creating reviews on properties or services.
    Must specify either property_id or service_id (not both).
    """
    property_id: Optional[str] = None
    service_id: Optional[str] = None
    rating: int  # 1-5 stars
    comment: Optional[str] = None


# ==================== HELPER FUNCTIONS ====================

async def update_rating_aggregation(property_id: Optional[str], service_id: Optional[str]):
    """
    Update average rating and review count for a property or service.
    
    Uses MongoDB aggregation pipeline to calculate:
    - Average rating (rounded to 1 decimal place)
    - Total review count
    
    Updates the property or service document with calculated values.
    
    Args:
        property_id: UUID of property to update (if property review)
        service_id: UUID of service to update (if service review)
        
    Example:
        >>> await update_rating_aggregation(property_id="uuid", service_id=None)
    """
    db = get_database()
    
    try:
        if property_id:
            # Calculate average rating for property using aggregation
            pipeline = [
                {"$match": {"property_id": property_id}},
                {"$group": {
                    "_id": None,
                    "average_rating": {"$avg": "$rating"},
                    "review_count": {"$sum": 1}
                }}
            ]
            result = await db.reviews.aggregate(pipeline).to_list(length=1)
            
            if result:
                # Update property with calculated ratings
                await db.properties.update_one(
                    {"id": property_id},
                    {"$set": {
                        "average_rating": round(result[0]["average_rating"], 1),
                        "review_count": result[0]["review_count"]
                    }}
                )
            else:
                # No reviews - reset to 0
                await db.properties.update_one(
                    {"id": property_id},
                    {"$set": {"average_rating": 0.0, "review_count": 0}}
                )
        
        elif service_id:
            # Calculate average rating for service
            pipeline = [
                {"$match": {"service_id": service_id}},
                {"$group": {
                    "_id": None,
                    "average_rating": {"$avg": "$rating"},
                    "review_count": {"$sum": 1}
                }}
            ]
            result = await db.reviews.aggregate(pipeline).to_list(length=1)
            
            if result:
                # Update service with calculated ratings
                await db.professional_services.update_one(
                    {"id": service_id},
                    {"$set": {
                        "average_rating": round(result[0]["average_rating"], 1),
                        "review_count": result[0]["review_count"]
                    }}
                )
            else:
                # No reviews - reset to 0
                await db.professional_services.update_one(
                    {"id": service_id},
                    {"$set": {"average_rating": 0.0, "review_count": 0}}
                )
                
    except Exception as e:
        logger.error(f"Error updating rating aggregation: {e}")


# ==================== CREATE REVIEW ====================

@router.post("/reviews")
async def create_review(
    review_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new review for a property or service.
    
    Users can review:
    - Properties they have viewed or rented
    - Services they have used
    
    Business Rules:
    - Must specify either property_id OR service_id (not both)
    - Rating must be 1-5 (integer)
    - Users can only submit one review per property/service
    - Duplicate reviews are prevented
    
    After review creation, average rating is recalculated automatically.
    
    Args:
        review_data: Review details (property_id/service_id, rating, comment)
        current_user: Authenticated user (reviewer)
        
    Returns:
        Created review with generated ID
        
    Raises:
        HTTPException: 400 if validation fails or duplicate review
        HTTPException: 404 if property/service not found
        
    Example:
        POST /api/reviews
        {
            "property_id": "123e4567-e89b-12d3-a456-426614174000",
            "rating": 5,
            "comment": "Great property! Clean and well-maintained."
        }
    """
    db = get_database()
    
    try:
        # Validate that either property_id or service_id is provided
        if not review_data.get('property_id') and not review_data.get('service_id'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must specify either property_id or service_id"
            )
        
        # Cannot review both property and service
        if review_data.get('property_id') and review_data.get('service_id'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot review both property and service in one review"
            )
        
        # Validate rating (1-5 stars)
        rating = review_data.get('rating', 0)
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be an integer between 1 and 5"
            )
        
        # Check for duplicate review
        query = {"reviewer_id": current_user.get("id")}
        
        if review_data.get('property_id'):
            query["property_id"] = review_data['property_id']
            
            # Verify property exists
            property_doc = await db.properties.find_one({"id": review_data['property_id']})
            if not property_doc:
                logger.warning(f"Property not found: {review_data['property_id']}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Property not found"
                )
        else:
            query["service_id"] = review_data['service_id']
            
            # Verify service exists
            service_doc = await db.professional_services.find_one({"id": review_data['service_id']})
            if not service_doc:
                logger.warning(f"Service not found: {review_data['service_id']}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Service not found"
                )
        
        # Check if user already reviewed this item
        existing_review = await db.reviews.find_one(query)
        if existing_review:
            logger.warning(f"Duplicate review attempt by user {current_user.get('email')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this item"
            )
        
        # Create review document
        review = {
            "id": str(uuid.uuid4()),
            "reviewer_id": current_user.get("id"),
            "property_id": review_data.get('property_id'),
            "service_id": review_data.get('service_id'),
            "rating": rating,
            "comment": review_data.get('comment', ''),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert into database
        await db.reviews.insert_one(review)
        
        # Update average rating for the property/service
        await update_rating_aggregation(
            review_data.get('property_id'),
            review_data.get('service_id')
        )
        
        logger.info(f"Review created by {current_user.get('email')} for {'property' if review_data.get('property_id') else 'service'}")
        
        return {
            "message": "Review created successfully",
            "review": serialize_doc(review)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review"
        )


# ==================== GET REVIEWS ====================

@router.get("/reviews/property/{property_id}")
async def get_property_reviews(
    property_id: str,
    skip: int = 0,
    limit: int = 20
):
    """
    Get all reviews for a specific property.
    
    Returns reviews with reviewer information (name, picture).
    Sorted by creation date (newest first).
    
    Args:
        property_id: UUID of the property
        skip: Number of reviews to skip (pagination)
        limit: Maximum number of reviews to return
        
    Returns:
        List of reviews with pagination metadata
        
    Example:
        GET /api/reviews/property/123e4567-e89b-12d3-a456-426614174000?skip=0&limit=10
    """
    db = get_database()
    
    try:
        # Fetch reviews for property
        reviews_cursor = db.reviews.find(
            {"property_id": property_id}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        reviews = await reviews_cursor.to_list(length=limit)
        
        # Enrich with reviewer information
        for review in reviews:
            reviewer = await db.users.find_one({"id": review.get("reviewer_id")})
            if reviewer:
                review["reviewer_name"] = reviewer.get("name")
                review["reviewer_picture"] = reviewer.get("picture")
        
        # Get total count for pagination
        total = await db.reviews.count_documents({"property_id": property_id})
        
        logger.info(f"Retrieved {len(reviews)} reviews for property {property_id}")
        
        return {
            "reviews": [serialize_doc(review) for review in reviews],
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error fetching property reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reviews"
        )


@router.get("/reviews/service/{service_id}")
async def get_service_reviews(
    service_id: str,
    skip: int = 0,
    limit: int = 20
):
    """
    Get all reviews for a specific service.
    
    Returns reviews with reviewer information (name, picture).
    Sorted by creation date (newest first).
    
    Args:
        service_id: UUID of the service
        skip: Number of reviews to skip (pagination)
        limit: Maximum number of reviews to return
        
    Returns:
        List of reviews with pagination metadata
        
    Example:
        GET /api/reviews/service/123e4567-e89b-12d3-a456-426614174000?skip=0&limit=10
    """
    db = get_database()
    
    try:
        # Fetch reviews for service
        reviews_cursor = db.reviews.find(
            {"service_id": service_id}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        reviews = await reviews_cursor.to_list(length=limit)
        
        # Enrich with reviewer information
        for review in reviews:
            reviewer = await db.users.find_one({"id": review.get("reviewer_id")})
            if reviewer:
                review["reviewer_name"] = reviewer.get("name")
                review["reviewer_picture"] = reviewer.get("picture")
        
        # Get total count for pagination
        total = await db.reviews.count_documents({"service_id": service_id})
        
        logger.info(f"Retrieved {len(reviews)} reviews for service {service_id}")
        
        return {
            "reviews": [serialize_doc(review) for review in reviews],
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error fetching service reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reviews"
        )


@router.get("/reviews/user/{user_id}")
async def get_user_reviews(user_id: str):
    """
    Get all reviews created by a specific user.
    
    Returns reviews with property/service information.
    Sorted by creation date (newest first).
    
    Args:
        user_id: UUID of the reviewer
        
    Returns:
        List of user's reviews
        
    Example:
        GET /api/reviews/user/123e4567-e89b-12d3-a456-426614174000
    """
    db = get_database()
    
    try:
        # Fetch all reviews by user
        reviews_cursor = db.reviews.find(
            {"reviewer_id": user_id}
        ).sort("created_at", -1)
        
        reviews = await reviews_cursor.to_list(length=None)
        
        # Enrich with property/service information
        for review in reviews:
            if review.get('property_id'):
                prop = await db.properties.find_one({"id": review['property_id']})
                if prop:
                    review["property_title"] = prop.get("title")
            
            elif review.get('service_id'):
                service = await db.professional_services.find_one({"id": review['service_id']})
                if service:
                    review["service_title"] = service.get("title")
        
        logger.info(f"Retrieved {len(reviews)} reviews by user {user_id}")
        
        return {
            "reviews": [serialize_doc(review) for review in reviews]
        }
        
    except Exception as e:
        logger.error(f"Error fetching user reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reviews"
        )


# ==================== UPDATE REVIEW ====================

@router.put("/reviews/{review_id}")
async def update_review(
    review_id: str,
    review_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing review.
    
    Users can only update their own reviews.
    Can update rating and/or comment.
    
    Args:
        review_id: UUID of the review to update
        review_data: Updated review data (rating, comment)
        current_user: Authenticated user (must be reviewer)
        
    Returns:
        Updated review
        
    Raises:
        HTTPException: 404 if review not found
        HTTPException: 403 if not the reviewer
        HTTPException: 400 if invalid data
        
    Example:
        PUT /api/reviews/123e4567-e89b-12d3-a456-426614174000
        {
            "rating": 4,
            "comment": "Updated comment"
        }
    """
    db = get_database()
    
    try:
        review = await db.reviews.find_one({"id": review_id})
        
        if not review:
            logger.warning(f"Review not found: {review_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        
        # Check ownership
        if review.get("reviewer_id") != current_user.get("id"):
            logger.warning(f"User {current_user.get('id')} attempted to update review {review_id} by another user")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own reviews"
            )
        
        # Validate rating if provided
        if 'rating' in review_data:
            rating = review_data['rating']
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rating must be an integer between 1 and 5"
                )
        
        # Build update data
        update_data = {}
        if 'rating' in review_data:
            update_data['rating'] = review_data['rating']
        if 'comment' in review_data:
            update_data['comment'] = review_data['comment']
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )
        
        # Update review
        await db.reviews.update_one(
            {"id": review_id},
            {"$set": update_data}
        )
        
        # Update average rating if rating changed
        if 'rating' in review_data:
            await update_rating_aggregation(
                review.get('property_id'),
                review.get('service_id')
            )
        
        # Get updated review
        updated_review = await db.reviews.find_one({"id": review_id})
        
        logger.info(f"Review {review_id} updated by {current_user.get('email')}")
        
        return {
            "message": "Review updated successfully",
            "review": serialize_doc(updated_review)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update review"
        )


# ==================== DELETE REVIEW ====================

@router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a review.
    
    Users can delete their own reviews.
    Admins can delete any review.
    
    Args:
        review_id: UUID of the review to delete
        current_user: Authenticated user (reviewer or admin)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if review not found
        HTTPException: 403 if not authorized
        
    Example:
        DELETE /api/reviews/123e4567-e89b-12d3-a456-426614174000
    """
    db = get_database()
    
    try:
        review = await db.reviews.find_one({"id": review_id})
        
        if not review:
            logger.warning(f"Review not found: {review_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        
        # Check authorization: reviewer or admin
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        if review.get("reviewer_id") != user_id and user_role != "admin":
            logger.warning(f"User {user_id} attempted to delete review {review_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews"
            )
        
        # Store IDs for rating update
        property_id = review.get('property_id')
        service_id = review.get('service_id')
        
        # Delete review
        await db.reviews.delete_one({"id": review_id})
        
        # Update average rating
        await update_rating_aggregation(property_id, service_id)
        
        logger.info(f"Review {review_id} deleted by {current_user.get('email')}")
        
        return {"message": "Review deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete review"
        )
