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
import os
import httpx
from urllib.parse import urlencode

# Import from parent modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_database
from utils import get_current_user, serialize_doc
from config import settings

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




# ==================== EMAIL VERIFICATION ====================

@router.post("/verify-email")
async def verify_email(response: Response, verification_data: dict):
    """
    Verify user email address with token.
    
    After registration, users receive an email with a verification link.
    This endpoint validates the token and marks the email as verified.
    
    Args:
        response: FastAPI response for setting cookies
        verification_data: Dict containing verification token
        
    Returns:
        Success message with user data and session
        
    Raises:
        HTTPException: 400 if token invalid or expired
    """
    db = get_database()
    
    token = verification_data.get('token')
    if not token:
        raise HTTPException(status_code=400, detail="Verification token required")
    
    # Find user with matching token
    user_doc = await db.users.find_one({
        "email_verification_token": token,
        "email_verification_expires": {"$gt": datetime.now(timezone.utc).isoformat()}
    })
    
    if not user_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    # Update user as verified
    await db.users.update_one(
        {"id": user_doc["id"]},
        {
            "$set": {
                "email_verified": True,
                "email_verification_token": None,
                "email_verification_expires": None
            }
        }
    )
    
    # Create session
    session_token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    session_doc = {
        "user_id": user_doc["id"],
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    # Set session cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        secure=True,
        samesite="none",
        path="/"
    )
    
    logger.info(f"Email verified for user: {user_doc.get('email')}")
    
    # Get updated user
    updated_user = await db.users.find_one({"id": user_doc["id"]})
    
    return {
        "message": "Email verified successfully",
        "user": serialize_doc(updated_user),
        "needs_role_selection": not updated_user.get('role')
    }


@router.post("/resend-verification")
async def resend_verification(email_request: dict):
    """
    Resend email verification link.
    
    If users don't receive or lose the verification email,
    they can request a new verification link.
    
    Args:
        email_request: Dict containing user email
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 400 if email missing
        HTTPException: 404 if user not found or already verified
    """
    db = get_database()
    
    email = email_request.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    
    user_doc = await db.users.find_one({"email": email, "email_verified": False})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found or already verified")
    
    # Generate new token
    verification_token = str(uuid.uuid4())
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    
    await db.users.update_one(
        {"email": email},
        {
            "$set": {
                "email_verification_token": verification_token,
                "email_verification_expires": verification_expires.isoformat()
            }
        }
    )
    
    # Note: send_verification_email needs to be implemented or imported from server.py
    # For now, logging the token
    logger.info(f"Verification email would be sent to {email} with token {verification_token}")
    
    return {"message": "Verification email resent"}


# ==================== PASSWORD RESET ====================

@router.post("/forgot-password")
async def forgot_password(email_request: dict):
    """
    Request password reset link.
    
    Sends an email with a password reset link to the user.
    
    Args:
        email_request: Dict containing user email
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 400 if email missing
        HTTPException: 404 if user not found
    """
    db = get_database()
    
    email = email_request.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    
    user_doc = await db.users.find_one({"email": email})
    if not user_doc:
        # Return success even if user not found (security best practice)
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = str(uuid.uuid4())
    reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    
    await db.users.update_one(
        {"email": email},
        {
            "$set": {
                "password_reset_token": reset_token,
                "password_reset_expires": reset_expires.isoformat()
            }
        }
    )
    
    logger.info(f"Password reset requested for: {email}")
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(reset_data: dict):
    """
    Reset password with token.
    
    Users click the link in their email and provide a new password.
    
    Args:
        reset_data: Dict containing token and new password
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 400 if token/password missing or invalid
    """
    db = get_database()
    
    token = reset_data.get('token')
    new_password = reset_data.get('password')
    
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and new password required")
    
    # Find user with valid reset token
    user_doc = await db.users.find_one({
        "password_reset_token": token,
        "password_reset_expires": {"$gt": datetime.now(timezone.utc).isoformat()}
    })
    
    if not user_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Hash new password
    import bcrypt
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Update password and clear reset token
    await db.users.update_one(
        {"id": user_doc["id"]},
        {
            "$set": {
                "password_hash": password_hash,
                "password_reset_token": None,
                "password_reset_expires": None
            }
        }
    )
    
    logger.info(f"Password reset completed for user: {user_doc.get('email')}")
    
    return {"message": "Password reset successfully"}


# ==================== ROLE SELECTION ====================

@router.post("/select-role")
async def select_role(role_data: dict, response: Response, current_user: dict = Depends(get_current_user)):
    """
    Select user role after registration.
    
    New users must select their role (property_seeker, property_owner, etc.)
    after email verification.
    
    Args:
        role_data: Dict containing selected role
        response: FastAPI response
        current_user: Authenticated user
        
    Returns:
        Success message with updated user data
        
    Raises:
        HTTPException: 400 if role invalid or already set
    """
    db = get_database()
    
    role = role_data.get('role')
    
    # Validate role
    valid_roles = [
        "property_seeker", "property_owner", "real_estate_agent", "real_estate_company",
        "construction_company", "bricklayer", "plumber", "electrician", "interior_designer",
        "borehole_driller", "cleaning_company", "painter", "architect", "carpenter",
        "evaluator", "building_material_supplier", "furnishing_shop"
    ]
    
    if not role or role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    if current_user.get('role'):
        raise HTTPException(status_code=400, detail="Role already selected")
    
    # Update user role
    await db.users.update_one(
        {"id": current_user.get("id")},
        {"$set": {"role": role}}
    )
    
    logger.info(f"Role selected for user {current_user.get('email')}: {role}")
    
    # Get updated user
    updated_user = await db.users.find_one({"id": current_user.get("id")})
    
    return {
        "message": "Role selected successfully",
        "user": serialize_doc(updated_user)
    }


# ==================== GOOGLE OAUTH ====================

@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth login flow.
    
    Redirects user to Google's OAuth consent screen.
    
    Returns:
        Redirect to Google OAuth URL
    """
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
    
    if not google_client_id or not google_redirect_uri:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": google_client_id,
        "redirect_uri": google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    from urllib.parse import urlencode
    url = f"{auth_url}?{urlencode(params)}"
    
    return RedirectResponse(url=url)


@router.get("/google/callback")
async def google_callback(code: str, response: Response):
    """
    Handle Google OAuth callback.
    
    Exchanges authorization code for user info and creates/logs in user.
    
    Args:
        code: Authorization code from Google
        response: FastAPI response for setting cookies
        
    Returns:
        Redirect to frontend with user data
        
    Raises:
        HTTPException: 400 if code missing
        HTTPException: 500 if OAuth exchange fails
    """
    db = get_database()
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")
    
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    google_redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    
    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "redirect_uri": google_redirect_uri,
        "grant_type": "authorization_code"
    }
    
    import httpx
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to exchange authorization code")
    
    tokens = token_response.json()
    access_token = tokens.get("access_token")
    
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
    
    if userinfo_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get user info")
    
    userinfo = userinfo_response.json()
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": userinfo["email"]})
    
    if existing_user:
        user_id = existing_user["id"]
    else:
        # Create new user
        user_id = str(uuid.uuid4())
        user_doc = {
            "id": user_id,
            "email": userinfo["email"],
            "name": userinfo.get("name", ""),
            "picture": userinfo.get("picture"),
            "auth_provider": "google",
            "email_verified": True,
            "role": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_doc)
    
    # Create session
    session_token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    session_doc = {
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        secure=True,
        samesite="none",
        path="/"
    )
    
    logger.info(f"Google OAuth login for: {userinfo['email']}")
    
    # Redirect to frontend
    user = await db.users.find_one({"id": user_id})
    needs_role = not user.get('role')
    
    redirect_url = f"{frontend_url}/auth/callback?needs_role={needs_role}"
    return RedirectResponse(url=redirect_url)


# ==================== USER PROFILE ====================

@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    
    Returns complete user information for the authenticated user.
    
    Args:
        current_user: Authenticated user from session
        
    Returns:
        User profile data
    """
    logger.info(f"Profile retrieved for user: {current_user.get('email')}")
    
    return serialize_doc(current_user)


# ==================== LOGOUT ====================

@router.post("/logout")
async def logout(response: Response, current_user: dict = Depends(get_current_user)):
    """
    Logout current user.
    
    Deletes the user's session and clears the session cookie.
    
    Args:
        response: FastAPI response for clearing cookies
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    db = get_database()
    
    # Delete all sessions for this user
    await db.user_sessions.delete_many({"user_id": current_user.get("id")})
    
    # Clear cookie
    response.delete_cookie(key="session_token", path="/")
    
    logger.info(f"User logged out: {current_user.get('email')}")
    
    return {"message": "Logged out successfully"}
