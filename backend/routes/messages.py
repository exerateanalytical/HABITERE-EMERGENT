"""
Messages Routes Module
=======================
Handles all messaging API endpoints for Habitere platform.

This module provides:
- Real-time messaging between users
- Conversation management and listing
- Message threading between two users
- Unread message tracking
- Read receipts
- Message deletion

Messaging Features:
- Direct messaging between property seekers and owners
- Communication between clients and service providers
- Conversation aggregation with MongoDB pipeline
- Automatic read marking when viewing threads
- Unread message counts

Authorization:
- All endpoints require authentication
- Users can only view/send their own messages
- Admins can delete any message

Dependencies:
- FastAPI for routing
- MongoDB for message storage with aggregation
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

# Create router for message endpoints
# All routes will be prefixed with /api
router = APIRouter(tags=["Messages"])


# ==================== PYDANTIC MODELS ====================

class MessageCreate(BaseModel):
    """
    Message creation model.
    
    Used for sending messages between users.
    """
    receiver_id: str
    content: str


# ==================== SEND MESSAGE ====================

@router.post("/messages")
async def send_message(
    message_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message to another user.
    
    Messages can be sent between:
    - Property seekers and property owners
    - Clients and service providers
    - Any authenticated users
    
    Args:
        message_data: Message details (receiver_id, content)
        current_user: Authenticated user (sender)
        
    Returns:
        Success response with created message
        
    Raises:
        HTTPException: 400 if receiver_id missing or content empty
        HTTPException: 400 if trying to message yourself
        HTTPException: 404 if receiver not found
        
    Example:
        POST /api/messages
        {
            "receiver_id": "123e4567-e89b-12d3-a456-426614174000",
            "content": "Hello, I'm interested in your property"
        }
    """
    db = get_database()
    
    try:
        receiver_id = message_data.get('receiver_id')
        content = message_data.get('content', '').strip()
        
        # Validate receiver_id
        if not receiver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Receiver ID is required"
            )
        
        # Validate content
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content cannot be empty"
            )
        
        # Verify receiver exists
        receiver = await db.users.find_one({"id": receiver_id})
        if not receiver:
            logger.warning(f"Receiver not found: {receiver_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver not found"
            )
        
        # Cannot message yourself
        if receiver_id == current_user.get("id"):
            logger.warning(f"User {current_user.get('email')} attempted to message themselves")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send message to yourself"
            )
        
        # Create message document
        message = {
            "id": str(uuid.uuid4()),
            "sender_id": current_user.get("id"),
            "receiver_id": receiver_id,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_read": False
        }
        
        # Insert into database
        await db.messages.insert_one(message)
        
        logger.info(f"Message sent from {current_user.get('email')} to {receiver.get('email')}")
        
        return {
            "message": "Message sent successfully",
            "data": serialize_doc(message)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


# ==================== CONVERSATIONS ====================

@router.get("/messages/conversations")
async def get_conversations(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all conversations for current user.
    
    Uses MongoDB aggregation pipeline to:
    - Find all unique users the current user has messaged with
    - Get the last message in each conversation
    - Count unread messages per conversation
    - Sort by most recent message
    
    Returns enriched conversation data including:
    - Other user details (name, picture, role)
    - Last message content and timestamp
    - Unread message count
    - Whether current user sent the last message
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of conversations sorted by last message time
        
    Example:
        GET /api/messages/conversations
        
        Response:
        {
            "conversations": [
                {
                    "user_id": "uuid",
                    "user_name": "John Doe",
                    "user_picture": "/uploads/profile/image.jpg",
                    "last_message": "Hello, is the property still available?",
                    "last_message_time": "2025-01-15T14:30:00Z",
                    "is_last_sender": false,
                    "unread_count": 2
                },
                ...
            ]
        }
    """
    db = get_database()
    
    try:
        # MongoDB aggregation pipeline to get conversations
        pipeline = [
            # Match messages involving current user
            {
                "$match": {
                    "$or": [
                        {"sender_id": current_user.get("id")},
                        {"receiver_id": current_user.get("id")}
                    ]
                }
            },
            # Sort by timestamp descending
            {
                "$sort": {"timestamp": -1}
            },
            # Group by the other user (not current user)
            {
                "$group": {
                    "_id": {
                        "$cond": [
                            {"$eq": ["$sender_id", current_user.get("id")]},
                            "$receiver_id",
                            "$sender_id"
                        ]
                    },
                    "last_message": {"$first": "$$ROOT"}
                }
            }
        ]
        
        conversations_data = await db.messages.aggregate(pipeline).to_list(length=None)
        
        # Enrich with user details and unread count
        conversations = []
        for conv in conversations_data:
            other_user_id = conv["_id"]
            last_message = conv["last_message"]
            
            # Get other user details
            other_user = await db.users.find_one({"id": other_user_id})
            if not other_user:
                continue
            
            # Count unread messages from this user
            unread_count = await db.messages.count_documents({
                "sender_id": other_user_id,
                "receiver_id": current_user.get("id"),
                "is_read": False
            })
            
            conversations.append({
                "user_id": other_user_id,
                "user_name": other_user.get("name"),
                "user_picture": other_user.get("picture"),
                "last_message": last_message.get("content"),
                "last_message_time": last_message.get("timestamp"),
                "is_last_sender": last_message.get("sender_id") == current_user.get("id"),
                "unread_count": unread_count
            })
        
        # Sort by last message time (most recent first)
        conversations.sort(key=lambda x: x["last_message_time"], reverse=True)
        
        logger.info(f"Retrieved {len(conversations)} conversations for user {current_user.get('email')}")
        
        return {"conversations": conversations}
        
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversations"
        )


# ==================== MESSAGE THREAD ====================

@router.get("/messages/thread/{other_user_id}")
async def get_message_thread(
    other_user_id: str,
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    skip: int = 0
):
    """
    Get message thread between current user and another user.
    
    Returns all messages between two users, sorted chronologically.
    Automatically marks messages from the other user as read.
    
    Args:
        other_user_id: UUID of the other user
        current_user: Authenticated user
        limit: Maximum number of messages to return (default: 50)
        skip: Number of messages to skip for pagination (default: 0)
        
    Returns:
        List of messages and other user details
        
    Raises:
        HTTPException: 404 if other user not found
        
    Example:
        GET /api/messages/thread/123e4567-e89b-12d3-a456-426614174000?limit=50&skip=0
        
        Response:
        {
            "messages": [
                {
                    "id": "uuid",
                    "sender_id": "uuid",
                    "receiver_id": "uuid",
                    "content": "Hello!",
                    "timestamp": "2025-01-15T10:00:00Z",
                    "is_read": true
                },
                ...
            ],
            "other_user": {
                "id": "uuid",
                "name": "John Doe",
                "picture": "/uploads/profile/image.jpg",
                "role": "property_owner"
            }
        }
    """
    db = get_database()
    
    try:
        # Verify other user exists
        other_user = await db.users.find_one({"id": other_user_id})
        if not other_user:
            logger.warning(f"User not found: {other_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get messages between the two users
        messages_cursor = db.messages.find({
            "$or": [
                {"sender_id": current_user.get("id"), "receiver_id": other_user_id},
                {"sender_id": other_user_id, "receiver_id": current_user.get("id")}
            ]
        }).sort("timestamp", -1).skip(skip).limit(limit)
        
        messages = await messages_cursor.to_list(length=limit)
        messages.reverse()  # Show oldest first for chat display
        
        # Mark messages from other user as read (auto-read receipt)
        await db.messages.update_many(
            {
                "sender_id": other_user_id,
                "receiver_id": current_user.get("id"),
                "is_read": False
            },
            {"$set": {"is_read": True}}
        )
        
        logger.info(f"Retrieved {len(messages)} messages between {current_user.get('email')} and {other_user.get('email')}")
        
        return {
            "messages": [serialize_doc(msg) for msg in messages],
            "other_user": {
                "id": other_user.get("id"),
                "name": other_user.get("name"),
                "picture": other_user.get("picture"),
                "role": other_user.get("role")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching message thread: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch messages"
        )


# ==================== UNREAD COUNT ====================

@router.get("/messages/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user)
):
    """
    Get total unread message count for current user.
    
    Useful for displaying notification badges in the UI.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Total number of unread messages
        
    Example:
        GET /api/messages/unread-count
        
        Response:
        {
            "unread_count": 5
        }
    """
    db = get_database()
    
    try:
        count = await db.messages.count_documents({
            "receiver_id": current_user.get("id"),
            "is_read": False
        })
        
        logger.info(f"User {current_user.get('email')} has {count} unread messages")
        
        return {"unread_count": count}
        
    except Exception as e:
        logger.error(f"Error fetching unread count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch unread count"
        )


# ==================== MARK AS READ ====================

@router.put("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a specific message as read.
    
    Only the message receiver can mark a message as read.
    
    Args:
        message_id: UUID of the message
        current_user: Authenticated user (must be receiver)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if message not found
        HTTPException: 403 if not the receiver
        
    Example:
        PUT /api/messages/123e4567-e89b-12d3-a456-426614174000/read
    """
    db = get_database()
    
    try:
        message = await db.messages.find_one({"id": message_id})
        
        if not message:
            logger.warning(f"Message not found: {message_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Only receiver can mark as read
        if message.get("receiver_id") != current_user.get("id"):
            logger.warning(f"User {current_user.get('id')} not authorized to mark message {message_id} as read")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to mark this message as read"
            )
        
        # Update message
        await db.messages.update_one(
            {"id": message_id},
            {"$set": {"is_read": True}}
        )
        
        logger.info(f"Message {message_id} marked as read by {current_user.get('email')}")
        
        return {"message": "Message marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark message as read"
        )


# ==================== DELETE MESSAGE ====================

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a message.
    
    Only the message sender or admins can delete messages.
    This is a hard delete - the message is permanently removed.
    
    Args:
        message_id: UUID of the message to delete
        current_user: Authenticated user (sender or admin)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if message not found
        HTTPException: 403 if not the sender or admin
        
    Example:
        DELETE /api/messages/123e4567-e89b-12d3-a456-426614174000
    """
    db = get_database()
    
    try:
        message = await db.messages.find_one({"id": message_id})
        
        if not message:
            logger.warning(f"Message not found: {message_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Only sender or admin can delete
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        if message.get("sender_id") != user_id and user_role != "admin":
            logger.warning(f"User {user_id} not authorized to delete message {message_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this message"
            )
        
        # Delete message
        await db.messages.delete_one({"id": message_id})
        
        logger.info(f"Message {message_id} deleted by {current_user.get('email')}")
        
        return {"message": "Message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message"
        )
