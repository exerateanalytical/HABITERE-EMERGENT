"""
Authentication Utilities Module
================================
Common authentication utilities for Habitere platform.

This module provides:
- User authentication middleware
- Session validation
- User retrieval helpers
- Permission checking utilities

Dependencies:
- FastAPI for request handling
- MongoDB for session/user lookup
- JWT for token validation

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from fastapi import HTTPException, status, Request, Depends, Cookie
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional
from datetime import datetime, timezone
import logging

# Import models and database
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_database

# Setup logging
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


# Import Pydantic models (will be defined in server.py)
# These need to be imported from server.py where they are defined
# For now, we'll use Any type and fix imports later
from typing import Any

User = Any  # Placeholder - will import from server.py


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(None)
) -> Any:
    """
    Get current authenticated user.
    
    This function validates the user's session by checking either:
    1. Session cookie (session_token)
    2. Authorization Bearer token
    
    Args:
        request: FastAPI request object
        credentials: Optional Bearer token from Authorization header
        session_token: Optional session token from cookie
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: 401 if not authenticated or session expired
        
    Example:
        >>> @app.get("/protected")
        >>> async def protected_route(user: User = Depends(get_current_user)):
        >>>     return {"user_id": user.id}
    """
    db = get_database()
    
    # Try to get session token from cookie first
    token = session_token
    
    # If no cookie, try Authorization header
    if not token and credentials:
        token = credentials.credentials
    
    # If still no token, raise unauthorized
    if not token:
        logger.warning("No authentication token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Validate session token
    session = await db.sessions.find_one({"session_token": token})
    if not session:
        logger.warning(f"Invalid session token: {token[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    # Check if session expired
    if session["expires_at"] < datetime.now(timezone.utc):
        logger.warning(f"Expired session for user: {session.get('user_id')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    # Get user
    user_doc = await db.users.find_one({"id": session["user_id"]})
    if not user_doc:
        logger.error(f"User not found for session: {session.get('user_id')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    logger.info(f"Authenticated user: {user_doc.get('email')}")
    
    # Return user document as dict (will be converted to User model by FastAPI)
    return user_doc


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(None)
) -> Optional[Any]:
    """
    Get current user if authenticated, None otherwise.
    
    This is useful for endpoints that work for both authenticated
    and unauthenticated users, but provide different features based
    on authentication status.
    
    Args:
        request: FastAPI request object
        credentials: Optional Bearer token from Authorization header
        session_token: Optional session token from cookie
        
    Returns:
        User or None: Authenticated user object or None if not authenticated
        
    Example:
        >>> @app.get("/properties")
        >>> async def list_properties(user: Optional[User] = Depends(get_current_user_optional)):
        >>>     if user:
        >>>         # Show personalized results
        >>>         pass
        >>>     else:
        >>>         # Show public results
        >>>         pass
    """
    try:
        return await get_current_user(request, credentials, session_token)
    except HTTPException:
        return None


async def require_admin(
    current_user: Any = Depends(get_current_user)
) -> Any:
    """
    Require admin role for endpoint access.
    
    Use this dependency to protect admin-only endpoints.
    
    Args:
        current_user: Current authenticated user (from get_current_user)
        
    Returns:
        User: Admin user object
        
    Raises:
        HTTPException: 403 if user is not an admin
        
    Example:
        >>> @app.get("/admin/stats")
        >>> async def admin_stats(admin: User = Depends(require_admin)):
        >>>     return {"admin_id": admin.id}
    """
    if current_user.get("role") != "admin":
        logger.warning(f"Non-admin user {current_user.get('email')} attempted admin access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


async def check_ownership(
    entity_owner_id: str,
    current_user: Any = Depends(get_current_user)
) -> bool:
    """
    Check if current user owns the entity or is an admin.
    
    Args:
        entity_owner_id: Owner ID of the entity to check
        current_user: Current authenticated user
        
    Returns:
        bool: True if user owns entity or is admin
        
    Raises:
        HTTPException: 403 if not authorized
        
    Example:
        >>> property_doc = await db.properties.find_one({"id": property_id})
        >>> await check_ownership(property_doc["owner_id"], current_user)
    """
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    if user_id != entity_owner_id and user_role != "admin":
        logger.warning(f"User {user_id} attempted unauthorized access to entity owned by {entity_owner_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    return True
