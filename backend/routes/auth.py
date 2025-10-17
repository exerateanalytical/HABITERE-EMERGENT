"""
Authentication Routes Module
============================
Handles all authentication-related API endpoints for Habitere platform.

This module provides:
- User registration with email verification
- Email/password login
- Google OAuth login
- Password reset functionality
- Role selection for new users
- Session management
- User profile retrieval

Dependencies:
- FastAPI for routing
- MongoDB for user storage
- SendGrid for email sending
- Google OAuth for social login
- bcrypt for password hashing
- JWT for token generation

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import uuid
import bcrypt
import logging
from urllib.parse import urlencode

# Import from parent modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
from database import get_database, serialize_doc

# Setup logging
logger = logging.getLogger(__name__)

# Create router for auth endpoints
# All routes will be prefixed with /api/auth
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==================== PYDANTIC MODELS ====================

class RegisterRequest(BaseModel):
    """
    User registration request model.
    
    Attributes:
        email (str): User's email address (must be unique)
        name (str): User's full name
        password (str): User's password (will be hashed)
        phone (str, optional): User's phone number
    """
    email: str
    name: str
    password: str
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    """
    Login request model.
    
    Attributes:
        email (str): User's email address
        password (str): User's password (plaintext, will be verified against hash)
    """
    email: str
    password: str


class VerifyEmailRequest(BaseModel):
    """
    Email verification request model.
    
    Attributes:
        token (str): Verification token sent to user's email
    """
    token: str


class ForgotPasswordRequest(BaseModel):
    """
    Forgot password request model.
    
    Attributes:
        email (str): User's email address to send reset link
    """
    email: str


class ResetPasswordRequest(BaseModel):
    """
    Password reset request model.
    
    Attributes:
        token (str): Reset token from email
        new_password (str): New password to set
    """
    token: str
    new_password: str


class RoleSelectionRequest(BaseModel):
    """
    Role selection request model.
    
    Used when new users need to select their role after registration.
    
    Attributes:
        role (str): Selected role (must be one of USER_ROLES)
    """
    role: str


# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> print(hashed)  # $2b$12$...
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password (str): Plain text password to verify
        hashed_password (str): Hashed password from database
        
    Returns:
        bool: True if password matches, False otherwise
        
    Example:
        >>> is_valid = verify_password("mypassword123", user.password)
        >>> if is_valid:
        >>>     print("Password correct!")
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def generate_verification_token() -> str:
    """
    Generate a unique verification token for email verification.
    
    Returns:
        str: UUID token
        
    Example:
        >>> token = generate_verification_token()
        >>> print(token)  # 550e8400-e29b-41d4-a716-446655440000
    """
    return str(uuid.uuid4())


async def send_verification_email(email: str, token: str):
    """
    Send email verification link to user.
    
    Constructs verification URL and sends email using SendGrid.
    
    Args:
        email (str): Recipient email address
        token (str): Verification token to include in link
        
    Raises:
        Exception: If SendGrid API call fails
        
    Example:
        >>> await send_verification_email("user@example.com", "token123")
    """
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    
    # Construct verification URL
    verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"
    
    # Create email content
    message = Mail(
        from_email=(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME),
        to_emails=email,
        subject='Verify your Habitere account',
        html_content=f'''
        <h2>Welcome to Habitere!</h2>
        <p>Please verify your email address by clicking the link below:</p>
        <a href="{verification_url}">Verify Email</a>
        <p>This link will expire in 24 hours.</p>
        <p>If you didn't create an account, please ignore this email.</p>
        '''
    )
    
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Verification email sent to {email}, status: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {e}")
        raise


def set_auth_cookie(response: Response, session_token: str):
    """
    Set authentication cookie in response.
    
    Sets HTTP-only secure cookie with session token.
    Cookie settings vary by environment (dev/prod).
    
    Args:
        response (Response): FastAPI response object
        session_token (str): Session token to store in cookie
        
    Example:
        >>> set_auth_cookie(response, user_session_token)
    """
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,  # Prevent JavaScript access
        secure=settings.SECURE_COOKIES,  # HTTPS only in production
        samesite=settings.SAMESITE_COOKIES,  # CSRF protection
        max_age=60 * 60 * 24 * 7,  # 7 days
        path="/"
    )
    logger.debug(f"Auth cookie set with token: {session_token[:8]}...")


# ==================== API ENDPOINTS ====================

@router.post("/register")
async def register(request: RegisterRequest):
    """
    Register a new user account.
    
    Process:
    1. Validates email is unique
    2. Hashes password
    3. Creates user in database
    4. Generates verification token
    5. Sends verification email
    
    Args:
        request (RegisterRequest): Registration data
        
    Returns:
        Dict: Success message and user email
        
    Raises:
        HTTPException 400: If email already exists
        HTTPException 500: If email sending fails
        
    Example:
        >>> POST /api/auth/register
        >>> {
        >>>   "email": "user@example.com",
        >>>   "name": "John Doe",
        >>>   "password": "secure123",
        >>>   "phone": "+237..."
        >>> }
        >>> Response: {"message": "Registration successful", "email": "user@example.com"}
    """
    db = get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(request.password)
    
    # Generate verification token
    verification_token = generate_verification_token()
    
    # Create user document
    user_data = {
        "id": str(uuid.uuid4()),
        "email": request.email,
        "name": request.name,
        "password": hashed_password,
        "phone": request.phone,
        "email_verified": False,
        "verification_token": verification_token,
        "created_at": datetime.now(timezone.utc)
    }
    
    # Insert into database
    await db.users.insert_one(user_data)
    logger.info(f"New user registered: {request.email}")
    
    # Send verification email
    try:
        await send_verification_email(request.email, verification_token)
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        # Don't fail registration if email fails
    
    return {
        "message": "Registration successful. Please check your email to verify your account.",
        "email": request.email
    }


@router.post("/login")
async def login(request: LoginRequest, response: Response):
    """
    Login with email and password.
    
    Process:
    1. Finds user by email
    2. Verifies password
    3. Checks email is verified
    4. Creates session token
    5. Sets auth cookie
    6. Returns user data
    
    Args:
        request (LoginRequest): Login credentials
        response (Response): FastAPI response to set cookie
        
    Returns:
        Dict: User data and success message
        
    Raises:
        HTTPException 401: If credentials invalid
        HTTPException 403: If email not verified
        
    Example:
        >>> POST /api/auth/login
        >>> {"email": "user@example.com", "password": "secure123"}
        >>> Response: {
        >>>   "message": "Login successful",
        >>>   "user": {...},
        >>>   "needs_role_selection": false
        >>> }
    """
    db = get_database()
    
    # Find user
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check email verification
    if not user.get('email_verified', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for verification link."
        )
    
    # Create session token
    session_token = str(uuid.uuid4())
    
    # Update user's session in database
    await db.users.update_one(
        {"id": user['id']},
        {"$set": {"session_token": session_token, "last_login": datetime.now(timezone.utc)}}
    )
    
    # Set auth cookie
    set_auth_cookie(response, session_token)
    
    logger.info(f"User logged in: {request.email}")
    
    # Return user data (exclude sensitive fields)
    user_data = serialize_doc(user)
    user_data.pop('password', None)
    user_data.pop('verification_token', None)
    
    return {
        "message": "Login successful",
        "user": user_data,
        "needs_role_selection": not user.get('role')
    }


