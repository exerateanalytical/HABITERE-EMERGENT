"""
Database Module
===============
MongoDB database connection and management for Habitere platform.

This module handles:
- Database connection initialization
- Connection lifecycle management
- Database client singleton
- Collection references

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

from config import settings

# Setup logging
logger = logging.getLogger(__name__)

# ==================== DATABASE CLIENT ====================

# Global database client (singleton pattern)
client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


def get_database_client() -> AsyncIOMotorClient:
    """
    Get MongoDB client instance.
    
    Creates a new client if one doesn't exist (singleton pattern).
    
    Returns:
        AsyncIOMotorClient: MongoDB client instance
        
    Example:
        >>> client = get_database_client()
        >>> db = client[settings.DB_NAME]
    """
    global client
    
    if client is None:
        logger.info(f"Initializing MongoDB connection to {settings.MONGO_URL}")
        client = AsyncIOMotorClient(settings.MONGO_URL)
        logger.info("MongoDB client initialized successfully")
    
    return client


def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance.
    
    Returns:
        AsyncIOMotorDatabase: Database instance
        
    Example:
        >>> db = get_database()
        >>> users = await db.users.find().to_list(100)
    """
    global db
    
    if db is None:
        client = get_database_client()
        db = client[settings.DB_NAME]
        logger.info(f"Connected to database: {settings.DB_NAME}")
    
    return db


async def close_database_connection():
    """
    Close database connection.
    
    Should be called on application shutdown to properly close
    the database connection and release resources.
    
    Example:
        >>> await close_database_connection()
    """
    global client, db
    
    if client is not None:
        logger.info("Closing MongoDB connection...")
        client.close()
        client = None
        db = None
        logger.info("MongoDB connection closed")


async def ping_database() -> bool:
    """
    Ping database to check connection health.
    
    Returns:
        bool: True if connection is healthy, False otherwise
        
    Example:
        >>> is_healthy = await ping_database()
        >>> print(f"Database healthy: {is_healthy}")
    """
    try:
        client = get_database_client()
        await client.admin.command('ping')
        logger.info("Database ping successful")
        return True
    except Exception as e:
        logger.error(f"Database ping failed: {e}")
        return False


# ==================== COLLECTION REFERENCES ====================

class Collections:
    """
    MongoDB collection names.
    
    Centralized collection name constants to avoid typos and
    ensure consistency across the application.
    """
    
    USERS = "users"
    PROPERTIES = "properties"
    SERVICES = "services"
    PROFESSIONAL_SERVICES = "professional_services"
    BOOKINGS = "bookings"
    MESSAGES = "messages"
    REVIEWS = "reviews"
    NOTIFICATIONS = "notifications"


# ==================== HELPER FUNCTIONS ====================

def serialize_doc(doc: dict) -> dict:
    """
    Serialize MongoDB document for JSON response.
    
    Removes MongoDB's _id field which is not JSON serializable.
    
    Args:
        doc (dict): MongoDB document
        
    Returns:
        dict: Serialized document without _id
        
    Example:
        >>> user = await db.users.find_one({"email": "test@example.com"})
        >>> serialized = serialize_doc(user)
        >>> return JSONResponse(serialized)
    """
    if doc and '_id' in doc:
        doc.pop('_id')
    return doc
