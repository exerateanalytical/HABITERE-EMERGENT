"""
Helper Utilities Module
========================
Common helper functions for Habitere platform.

This module provides:
- Document serialization
- Data transformation utilities
- Common validation helpers
- Date/time utilities

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from datetime import datetime, date
from typing import Any, Dict, List, Union
import logging

# Setup logging
logger = logging.getLogger(__name__)


def serialize_doc(doc: Union[Dict, List, Any]) -> Union[Dict, List, None]:
    """
    Convert MongoDB document to JSON serializable format.
    
    This function handles:
    - Removing MongoDB's _id field
    - Converting datetime objects to ISO format strings
    - Recursively serializing nested documents and lists
    - Handling None values gracefully
    
    Args:
        doc: MongoDB document, list of documents, or any value
        
    Returns:
        Serialized document/data suitable for JSON response
        
    Example:
        >>> user = await db.users.find_one({"email": "test@example.com"})
        >>> serialized = serialize_doc(user)
        >>> return JSONResponse(serialized)
        
        >>> properties = await db.properties.find().to_list(100)
        >>> serialized = serialize_doc(properties)
    """
    if doc is None:
        return None
    
    # Handle lists by recursively serializing each item
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    
    # Handle dictionaries (MongoDB documents)
    if isinstance(doc, dict):
        serialized = {}
        for key, value in doc.items():
            # Skip MongoDB's _id field (not JSON serializable and not needed)
            if key == "_id":
                continue
            
            # Recursively serialize nested documents
            if isinstance(value, dict):
                serialized[key] = serialize_doc(value)
            # Serialize lists
            elif isinstance(value, list):
                serialized[key] = serialize_doc(value)
            # Convert datetime to ISO format string
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            # Convert date to ISO format string
            elif isinstance(value, date):
                serialized[key] = value.isoformat()
            # Keep other values as-is
            else:
                serialized[key] = value
        
        return serialized
    
    # For non-dict, non-list values, return as-is
    return doc


def prepare_for_mongo(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare data for MongoDB storage.
    
    Converts Python date/time objects to ISO strings before storing
    in MongoDB to ensure consistent serialization.
    
    Args:
        data: Dictionary of data to store in MongoDB
        
    Returns:
        Dictionary with date/time objects converted to ISO strings
        
    Example:
        >>> booking_data = {
        >>>     "scheduled_date": datetime.now(),
        >>>     "created_at": datetime.now(timezone.utc)
        >>> }
        >>> mongo_ready = prepare_for_mongo(booking_data)
        >>> await db.bookings.insert_one(mongo_ready)
    """
    prepared = {}
    
    for key, value in data.items():
        # Convert datetime objects to ISO format strings
        if isinstance(value, datetime):
            prepared[key] = value.isoformat()
        # Convert date objects to ISO format strings
        elif isinstance(value, date):
            prepared[key] = value.isoformat()
        # Recursively prepare nested dictionaries
        elif isinstance(value, dict):
            prepared[key] = prepare_for_mongo(value)
        # Keep other values as-is
        else:
            prepared[key] = value
    
    return prepared


def parse_from_mongo(item: Dict[str, Any], date_fields: List[str] = None) -> Dict[str, Any]:
    """
    Parse data retrieved from MongoDB.
    
    Converts ISO string dates back to Python datetime/date objects
    for fields specified in date_fields.
    
    Args:
        item: Dictionary retrieved from MongoDB
        date_fields: List of field names that should be converted to datetime
        
    Returns:
        Dictionary with specified fields converted to datetime objects
        
    Example:
        >>> booking = await db.bookings.find_one({"id": booking_id})
        >>> parsed = parse_from_mongo(booking, ["scheduled_date", "created_at"])
    """
    if not date_fields:
        return item
    
    parsed = item.copy()
    
    for field in date_fields:
        if field in parsed and isinstance(parsed[field], str):
            try:
                parsed[field] = datetime.fromisoformat(parsed[field])
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse date field '{field}': {e}")
    
    return parsed


def validate_uuid(value: str) -> bool:
    """
    Validate if a string is a valid UUID.
    
    Args:
        value: String to validate
        
    Returns:
        bool: True if valid UUID, False otherwise
        
    Example:
        >>> if validate_uuid(property_id):
        >>>     property = await db.properties.find_one({"id": property_id})
    """
    import re
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(value))


def paginate_results(
    items: List[Any],
    skip: int = 0,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Paginate a list of items and return pagination metadata.
    
    Args:
        items: List of items to paginate
        skip: Number of items to skip
        limit: Maximum number of items per page
        
    Returns:
        Dictionary with paginated items and metadata
        
    Example:
        >>> properties = await db.properties.find().to_list(1000)
        >>> result = paginate_results(properties, skip=0, limit=20)
        >>> return result
    """
    total = len(items)
    paginated_items = items[skip:skip + limit]
    
    return {
        "items": paginated_items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }
