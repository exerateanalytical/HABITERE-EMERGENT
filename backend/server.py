from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request, Response, Cookie, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pathlib import Path
import os
import uuid
import logging
import httpx
import json
import base64
import shutil
import aiofiles
from PIL import Image
import mimetypes
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from urllib.parse import urlencode
import bcrypt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Environment configuration
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')
IS_DEVELOPMENT = ENVIRONMENT == 'development'

# Cookie security settings based on environment
COOKIE_SECURE = not IS_DEVELOPMENT  # False in dev, True in production
COOKIE_SAMESITE = "lax" if IS_DEVELOPMENT else "None"  # lax in dev, None in production

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# SendGrid Email configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@habitere.com')
SENDGRID_FROM_NAME = os.environ.get('SENDGRID_FROM_NAME', 'Habitere')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# Image upload configuration
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Create subdirectories for different image types
(UPLOAD_DIR / "properties").mkdir(exist_ok=True)
(UPLOAD_DIR / "services").mkdir(exist_ok=True)
(UPLOAD_DIR / "profiles").mkdir(exist_ok=True)
(UPLOAD_DIR / "chat").mkdir(exist_ok=True)
(UPLOAD_DIR / "thumbnails").mkdir(exist_ok=True)

# Image upload settings
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
THUMBNAIL_SIZE = (300, 300)

# Create the main app
app = FastAPI(title="Habitere API", description="Real Estate and Home Services Platform for Cameroon")
api_router = APIRouter(prefix="/api")

# Mount static files for serving uploaded images
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Security scheme
security = HTTPBearer(auto_error=False)

# User roles
USER_ROLES = [
    "property_seeker", "property_owner", "real_estate_agent", "real_estate_company",
    "construction_company", "bricklayer", "plumber", "electrician", "interior_designer",
    "borehole_driller", "cleaning_company", "painter", "architect", "carpenter",
    "evaluator", "building_material_supplier", "furnishing_shop", "admin"
]

# Pydantic Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    password_hash: Optional[str] = None  # For email/password auth
    auth_provider: str = "email"  # email, google
    picture: Optional[str] = None
    role: Optional[str] = None  # Made optional, set after role selection
    role_verified: bool = False
    email_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_expires: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    company_name: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool = False
    verification_status: str = "pending"  # pending, approved, rejected
    verified_by: Optional[str] = None  # Admin user ID who verified
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Property(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str
    title: str
    description: str
    price: float
    currency: str = "XAF"
    location: str
    property_type: Optional[str] = None  # Keeping for backward compatibility
    property_sector: Optional[str] = None  # Residential Properties, Commercial Properties, etc.
    property_category: Optional[str] = None  # Houses for Sale, Apartments for Rent, etc.
    listing_type: str  # sale, rent, lease, short_let, auction
    bedrooms: Optional[int] = 0
    bathrooms: Optional[int] = 0
    area_sqm: Optional[float] = None
    images: List[str] = []
    amenities: List[str] = []
    available: bool = True
    verified: bool = False
    verification_status: str = "pending"  # pending, verified, rejected
    verified_by: Optional[str] = None  # Admin user ID who verified
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    views: int = 0
    favorites: int = 0
    average_rating: float = 0.0
    review_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProfessionalService(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider_id: str
    category: str
    title: str
    description: str
    price_range: Optional[str] = None
    location: str
    images: List[str] = []
    available: bool = True
    verified: bool = False
    verification_status: str = "pending"  # pending, verified, rejected
    verified_by: Optional[str] = None  # Admin user ID who verified
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    average_rating: float = 0.0
    review_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Booking(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    property_id: Optional[str] = None
    service_id: Optional[str] = None
    booking_type: str  # property_viewing, service_booking
    scheduled_date: datetime
    scheduled_time: Optional[str] = None  # e.g., "10:00", "14:30"
    duration_hours: Optional[int] = 1
    status: str = "pending"  # pending, confirmed, completed, cancelled
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    confirmed_by: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Payment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str
    user_id: str
    amount: float
    currency: str = "XAF"
    method: str  # mtn_momo, bank_transfer
    status: str = "pending"  # pending, successful, failed
    transaction_id: Optional[str] = None
    reference_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Review(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reviewer_id: str
    property_id: Optional[str] = None
    service_id: Optional[str] = None
    rating: int  # 1-5
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    receiver_id: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_read: bool = False

class ImageUpload(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by: str
    entity_type: str  # 'property', 'service', 'profile', 'chat'
    entity_id: Optional[str] = None
    is_primary: bool = False
    alt_text: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request Models
class UserRegister(BaseModel):
    email: str
    name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class EmailVerification(BaseModel):
    token: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordReset(BaseModel):
    token: str
    new_password: str

class RoleSelection(BaseModel):
    role: str

class UserCreate(BaseModel):
    email: str
    name: str
    role: str
    phone: Optional[str] = None
    location: Optional[str] = None
    company_name: Optional[str] = None
    bio: Optional[str] = None

class PropertyCreate(BaseModel):
    title: str
    description: str
    price: float
    location: str
    property_type: Optional[str] = None  # Keeping for backward compatibility
    property_sector: Optional[str] = None  # New: Residential, Commercial, etc.
    property_category: Optional[str] = None  # New: Specific category
    listing_type: str
    bedrooms: Optional[int] = 0
    bathrooms: Optional[int] = 0
    area_sqm: Optional[float] = None
    images: List[str] = []
    amenities: List[str] = []

class ServiceCreate(BaseModel):
    category: str
    title: str
    description: str
    price_range: Optional[str] = None
    location: str
    images: List[str] = []

class BookingCreate(BaseModel):
    property_id: Optional[str] = None
    service_id: Optional[str] = None
    scheduled_date: datetime
    notes: Optional[str] = None

class PaymentCreate(BaseModel):
    booking_id: str
    amount: float
    method: str
    phone_number: Optional[str] = None  # For MTN MoMo

class ReviewCreate(BaseModel):
    property_id: Optional[str] = None
    service_id: Optional[str] = None
    rating: int
    comment: Optional[str] = None

class MessageCreate(BaseModel):
    receiver_id: str
    content: str

# MTN MoMo Client Class
class MTNMoMoClient:
    def __init__(self):
        self.base_url = "https://sandbox.momodeveloper.mtn.com"  # Change to production URL
        self.subscription_key = os.getenv("MTN_SUBSCRIPTION_KEY")
        self.api_user = os.getenv("MTN_API_USER")
        self.api_key = os.getenv("MTN_API_KEY")
        self.target_environment = "sandbox"  # Change to "mtncameroon" for production
        
    async def get_access_token(self):
        """Get access token for MTN MoMo API"""
        try:
            auth_string = f"{self.api_user}:{self.api_key}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Ocp-Apim-Subscription-Key": self.subscription_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/collection/token/",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()["access_token"]
                else:
                    raise HTTPException(status_code=500, detail="Failed to get MTN MoMo access token")
                    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MTN MoMo auth error: {str(e)}")
    
    async def request_to_pay(self, amount: float, phone_number: str, external_id: str):
        """Request payment from customer"""
        try:
            access_token = await self.get_access_token()
            reference_id = str(uuid.uuid4())
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Reference-Id": reference_id,
                "X-Target-Environment": self.target_environment,
                "Ocp-Apim-Subscription-Key": self.subscription_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "amount": str(amount),
                "currency": "EUR",  # Change to "XAF" for production
                "externalId": external_id,
                "payer": {
                    "partyIdType": "MSISDN",
                    "partyId": phone_number
                },
                "payerMessage": "Payment for Habitere booking",
                "payeeNote": "Habitere payment"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/collection/v1_0/requesttopay",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 202:
                    return {"reference_id": reference_id, "status": "pending"}
                else:
                    raise HTTPException(status_code=500, detail="Payment request failed")
                    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Payment error: {str(e)}")
    
    async def get_payment_status(self, reference_id: str):
        """Check payment status"""
        try:
            access_token = await self.get_access_token()
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Target-Environment": self.target_environment,
                "Ocp-Apim-Subscription-Key": self.subscription_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/collection/v1_0/requesttopay/{reference_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(status_code=404, detail="Payment not found")
                    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Status check error: {str(e)}")

# Initialize MTN MoMo client
mtn_client = MTNMoMoClient()

# Authentication functions
async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(None)
) -> User:
    """Get current authenticated user"""
    token = None
    
    # First try to get token from cookie
    if session_token:
        token = session_token
    # Then try Authorization header
    elif credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Find session in database
    session_doc = await db.user_sessions.find_one({
        "session_token": token,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not session_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    # Get user
    user_doc = await db.users.find_one({"id": session_doc["user_id"]})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(**user_doc)

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify that current user is an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(None)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    try:
        return await get_current_user(request, credentials, session_token)
    except HTTPException:
        return None

# Helper functions
def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        serialized = {}
        for key, value in doc.items():
            if key == "_id":
                continue  # Skip MongoDB _id
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                serialized[key] = serialize_doc(value)
            else:
                serialized[key] = value
        return serialized
    return doc

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

async def send_verification_email(email: str, name: str, token: str):
    """Send email verification email"""
    verification_url = f"{FRONTEND_URL}/auth/verify-email?token={token}"
    
    message = Mail(
        from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
        to_emails=email,
        subject='Verify your Habitere account',
        html_content=f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">Welcome to Habitere, {name}!</h2>
            <p>Thank you for registering. Please verify your email address to complete your registration.</p>
            <p>Click the button below to verify your email:</p>
            <a href="{verification_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin: 20px 0;">
                Verify Email
            </a>
            <p>Or copy and paste this link into your browser:</p>
            <p style="color: #6b7280; word-break: break-all;">{verification_url}</p>
            <p style="color: #6b7280; font-size: 14px; margin-top: 40px;">
                This link will expire in 24 hours. If you didn't create this account, you can safely ignore this email.
            </p>
        </div>
        '''
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logging.info(f"Verification email sent to {email}, status code: {response.status_code}")
        return True
    except Exception as e:
        logging.error(f"Error sending verification email: {str(e)}")
        return False

async def send_password_reset_email(email: str, name: str, token: str):
    """Send password reset email"""
    reset_url = f"{FRONTEND_URL}/auth/reset-password?token={token}"
    
    message = Mail(
        from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
        to_emails=email,
        subject='Reset your Habitere password',
        html_content=f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">Password Reset Request</h2>
            <p>Hello {name},</p>
            <p>We received a request to reset your password. Click the button below to create a new password:</p>
            <a href="{reset_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin: 20px 0;">
                Reset Password
            </a>
            <p>Or copy and paste this link into your browser:</p>
            <p style="color: #6b7280; word-break: break-all;">{reset_url}</p>
            <p style="color: #6b7280; font-size: 14px; margin-top: 40px;">
                This link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.
            </p>
        </div>
        '''
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logging.info(f"Password reset email sent to {email}, status code: {response.status_code}")
        return True
    except Exception as e:
        logging.error(f"Error sending password reset email: {str(e)}")
        return False

# Authentication Routes

# ==================== EMAIL/PASSWORD AUTHENTICATION ====================

@api_router.post("/auth/register")
async def register_user(user_register: UserRegister):
    """Register a new user with email and password"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_register.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = hash_password(user_register.password)
    
    # Generate verification token
    verification_token = str(uuid.uuid4())
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    
    # Create new user
    user_doc = {
        "id": str(uuid.uuid4()),
        "email": user_register.email,
        "name": user_register.name,
        "password_hash": password_hash,
        "auth_provider": "email",
        "role": None,  # Will be set after role selection
        "role_verified": False,
        "email_verified": False,
        "email_verification_token": verification_token,
        "email_verification_expires": verification_expires,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.users.insert_one(user_doc)
    
    # Send verification email
    await send_verification_email(user_register.email, user_register.name, verification_token)
    
    return {
        "message": "Registration successful. Please check your email to verify your account.",
        "email": user_register.email
    }

@api_router.post("/auth/verify-email")
async def verify_email(response: Response, verification: EmailVerification):
    """Verify email address"""
    user_doc = await db.users.find_one({
        "email_verification_token": verification.token,
        "email_verification_expires": {"$gt": datetime.now(timezone.utc)}
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
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc)
    }
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        secure=True,  # Production with HTTPS
        samesite="None",  # Required for cross-site cookies
        path="/"
    )
    
    # Get updated user
    updated_user = await db.users.find_one({"id": user_doc["id"]})
    user = User(**updated_user)
    
    return {
        "message": "Email verified successfully",
        "user": serialize_doc(user.model_dump()),
        "needs_role_selection": user.role is None
    }

@api_router.post("/auth/resend-verification")
async def resend_verification(email_request: dict):
    """Resend verification email"""
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
                "email_verification_expires": verification_expires
            }
        }
    )
    
    # Send verification email
    await send_verification_email(email, user_doc["name"], verification_token)
    
    return {"message": "Verification email resent"}

@api_router.post("/auth/login")
async def login_user(response: Response, user_login: UserLogin):
    """Login with email and password"""
    # Find user
    user_doc = await db.users.find_one({"email": user_login.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if user used Google OAuth
    if user_doc.get("auth_provider") == "google":
        raise HTTPException(status_code=400, detail="Please login with Google")
    
    # Verify password
    if not user_doc.get("password_hash") or not verify_password(user_login.password, user_doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if email is verified
    if not user_doc.get("email_verified"):
        raise HTTPException(status_code=403, detail="Please verify your email first")
    
    # Create session
    session_token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    session_doc = {
        "user_id": user_doc["id"],
        "session_token": session_token,
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc)
    }
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        secure=True,  # Production with HTTPS
        samesite="None",  # Required for cross-site cookies
        path="/"
    )
    
    user = User(**user_doc)
    return {
        "message": "Login successful",
        "user": serialize_doc(user.model_dump()),
        "needs_role_selection": user.role is None
    }

@api_router.post("/auth/forgot-password")
async def forgot_password(password_request: PasswordResetRequest):
    """Request password reset"""
    user_doc = await db.users.find_one({"email": password_request.email})
    if not user_doc:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Check if user used Google OAuth
    if user_doc.get("auth_provider") == "google":
        raise HTTPException(status_code=400, detail="Google accounts cannot reset password. Please login with Google.")
    
    # Generate reset token
    reset_token = str(uuid.uuid4())
    reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    
    await db.users.update_one(
        {"email": password_request.email},
        {
            "$set": {
                "password_reset_token": reset_token,
                "password_reset_expires": reset_expires
            }
        }
    )
    
    # Send reset email
    await send_password_reset_email(password_request.email, user_doc["name"], reset_token)
    
    return {"message": "If the email exists, a password reset link has been sent"}

@api_router.post("/auth/reset-password")
async def reset_password(password_reset: PasswordReset):
    """Reset password with token"""
    user_doc = await db.users.find_one({
        "password_reset_token": password_reset.token,
        "password_reset_expires": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not user_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Hash new password
    password_hash = hash_password(password_reset.new_password)
    
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
    
    return {"message": "Password reset successful. Please login with your new password."}

# ==================== ROLE SELECTION ====================

@api_router.post("/auth/select-role")
async def select_role(
    role_selection: RoleSelection,
    current_user: User = Depends(get_current_user)
):
    """Select user role (first-time or role change)"""
    if role_selection.role not in USER_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Update user role
    await db.users.update_one(
        {"id": current_user.id},
        {
            "$set": {
                "role": role_selection.role,
                "role_verified": True
            }
        }
    )
    
    # Get updated user
    updated_user = await db.users.find_one({"id": current_user.id})
    user = User(**updated_user)
    
    return {
        "message": "Role selected successfully",
        "user": serialize_doc(user.model_dump())
    }

# ==================== GOOGLE OAUTH ====================

@api_router.get("/auth/google/login")
async def google_login():
    """Initiate Google OAuth flow"""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "select_account"
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return {"auth_url": auth_url}

@api_router.get("/auth/google/callback")
async def google_callback(response: Response, code: str):
    """Handle Google OAuth callback"""
    try:
        # Exchange authorization code for tokens
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
        
        # Get user info
        access_token = tokens.get("access_token")
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = await client.get(GOOGLE_USER_INFO_URL, headers=headers)
            user_response.raise_for_status()
            google_user = user_response.json()
        
        # Check if user exists
        email = google_user.get("email")
        existing_user = await db.users.find_one({"email": email})
        
        if existing_user:
            user_id = existing_user["id"]
            # Update profile picture if changed
            if google_user.get("picture") and google_user["picture"] != existing_user.get("picture"):
                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {"picture": google_user["picture"]}}
                )
        else:
            # Create new user
            user_id = str(uuid.uuid4())
            user_doc = {
                "id": user_id,
                "email": email,
                "name": google_user.get("name", ""),
                "picture": google_user.get("picture", ""),
                "role": None,  # Will be set in role selection
                "role_verified": False,
                "email_verified": True,  # Google already verified
                "auth_provider": "google",
                "created_at": datetime.now(timezone.utc)
            }
            await db.users.insert_one(user_doc)
        
        # Create session
        session_token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        session_doc = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc)
        }
        await db.user_sessions.insert_one(session_doc)
        
        # Set cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=7 * 24 * 60 * 60,
            httponly=True,
            secure=True,  # Production with HTTPS
            samesite="None",  # Required for cross-site cookies
            path="/"
        )
        
        # Get user to check if they need role selection
        user_doc = await db.users.find_one({"id": user_id})
        needs_role = user_doc.get("role") is None
        
        # Redirect based on role status
        redirect_url = f"{FRONTEND_URL}/choose-role" if needs_role else f"{FRONTEND_URL}/dashboard"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logging.error(f"Google OAuth error: {str(e)}")
        # Redirect to login with error
        return RedirectResponse(url=f"{FRONTEND_URL}/auth/login?error=auth_failed")

# ==================== USER INFO & LOGOUT ====================


@api_router.get("/auth/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return serialize_doc(current_user.model_dump())


@api_router.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user_by_id(user_id: str):
    """Get user information by ID (public endpoint for displaying user names)"""
    try:
        user_doc = await db.users.find_one({"id": user_id})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return only public information
        public_info = {
            "id": user_doc.get("id"),
            "name": user_doc.get("name", "User"),
            "email": user_doc.get("email", ""),
            "role": user_doc.get("role", ""),
            "picture": user_doc.get("picture", ""),
            "company_name": user_doc.get("company_name", "")
        }
        return public_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user")


@api_router.post("/auth/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    session_token: Optional[str] = Cookie(None)
):
    """Logout user"""
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(
        key="session_token",
        path="/",
        secure=True,  # Production with HTTPS
        samesite="None"  # Required for cross-site cookies
    )
    
    return {"message": "Logged out successfully"}

# Property Routes
@api_router.get("/properties", response_model=List[Dict[str, Any]])
async def get_properties(
    property_type: Optional[str] = None,
    listing_type: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 20
):
    """Get properties with filtering"""
    filters = {"available": True}
    
    if property_type:
        filters["property_type"] = property_type
    if listing_type:
        filters["listing_type"] = listing_type
    if location:
        filters["location"] = {"$regex": location, "$options": "i"}
    if min_price is not None:
        filters["price"] = {"$gte": min_price}
    if max_price is not None:
        if "price" in filters:
            filters["price"]["$lte"] = max_price
        else:
            filters["price"] = {"$lte": max_price}
    
    properties = await db.properties.find(filters).skip(skip).limit(limit).to_list(1000)
    return [serialize_doc(prop) for prop in properties]

@api_router.get("/properties/{property_id}", response_model=Dict[str, Any])
async def get_property(property_id: str):
    """Get single property"""
    property_doc = await db.properties.find_one({"id": property_id})
    if not property_doc:
        raise HTTPException(status_code=404, detail="Property not found")
    return serialize_doc(property_doc)

@api_router.post("/properties", response_model=Dict[str, Any])
async def create_property(
    property_data: PropertyCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new property"""
    if current_user.role not in ["property_owner", "real_estate_agent", "real_estate_company", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to create properties")
    
    property_doc = property_data.model_dump()
    property_doc["id"] = str(uuid.uuid4())
    property_doc["owner_id"] = current_user.id
    property_doc["created_at"] = datetime.now(timezone.utc)
    
    await db.properties.insert_one(property_doc)
    return serialize_doc(property_doc)

@api_router.put("/properties/{property_id}", response_model=Dict[str, Any])
async def update_property(
    property_id: str,
    property_data: PropertyCreate,
    current_user: User = Depends(get_current_user)
):
    """Update property"""
    property_doc = await db.properties.find_one({"id": property_id})
    if not property_doc:
        raise HTTPException(status_code=404, detail="Property not found")
    
    if property_doc["owner_id"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = property_data.model_dump()
    await db.properties.update_one({"id": property_id}, {"$set": update_data})
    
    updated_doc = await db.properties.find_one({"id": property_id})
    return serialize_doc(updated_doc)

@api_router.delete("/properties/{property_id}")
async def delete_property(
    property_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete property"""
    property_doc = await db.properties.find_one({"id": property_id})
    if not property_doc:
        raise HTTPException(status_code=404, detail="Property not found")
    
    if property_doc["owner_id"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.properties.delete_one({"id": property_id})
    return {"message": "Property deleted"}


# User Properties Routes
@api_router.get("/users/me/properties", response_model=List[Dict[str, Any]])
async def get_current_user_properties(
    current_user: User = Depends(get_current_user)
):
    """Get current user's properties"""
    properties = await db.properties.find({"owner_id": current_user.id}).to_list(1000)
    return [serialize_doc(prop) for prop in properties]

@api_router.get("/users/{user_id}/properties", response_model=List[Dict[str, Any]])
async def get_user_properties(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific user's properties (admin or public view)"""
    # Allow admins to view any user's properties, others can only view their own
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    properties = await db.properties.find({"owner_id": user_id}).to_list(1000)
    return [serialize_doc(prop) for prop in properties]

# Service Routes
@api_router.get("/services", response_model=List[Dict[str, Any]])
async def get_services(
    category: Optional[str] = None,
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
):
    """Get professional services"""
    filters = {"available": True}
    
    if category:
        filters["category"] = category
    if location:
        filters["location"] = {"$regex": location, "$options": "i"}
    
    services = await db.services.find(filters).skip(skip).limit(limit).to_list(1000)
    return [serialize_doc(service) for service in services]

@api_router.get("/services/{service_id}", response_model=Dict[str, Any])
async def get_service(service_id: str):
    """Get single service"""
    service_doc = await db.services.find_one({"id": service_id})
    if not service_doc:
        raise HTTPException(status_code=404, detail="Service not found")
    return serialize_doc(service_doc)

@api_router.post("/services", response_model=Dict[str, Any])
async def create_service(
    service_data: ServiceCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new service"""
    service_provider_roles = [
        "construction_company", "bricklayer", "plumber", "electrician", 
        "interior_designer", "borehole_driller", "cleaning_company", 
        "painter", "architect", "carpenter", "evaluator", 
        "building_material_supplier", "furnishing_shop"
    ]
    
    if current_user.role not in service_provider_roles and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create services")
    
    service_doc = service_data.model_dump()
    service_doc["id"] = str(uuid.uuid4())
    service_doc["provider_id"] = current_user.id
    service_doc["created_at"] = datetime.now(timezone.utc)
    
    await db.services.insert_one(service_doc)
    return serialize_doc(service_doc)

# Booking Routes
@api_router.get("/bookings", response_model=List[Dict[str, Any]])
async def get_bookings(current_user: User = Depends(get_current_user)):
    """Get user's bookings"""
    bookings = await db.bookings.find({"client_id": current_user.id}).to_list(1000)
    return [serialize_doc(booking) for booking in bookings]

@api_router.post("/bookings", response_model=Dict[str, Any])
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new booking"""
    booking_doc = booking_data.model_dump()
    booking_doc["id"] = str(uuid.uuid4())
    booking_doc["client_id"] = current_user.id
    booking_doc["created_at"] = datetime.now(timezone.utc)
    
    await db.bookings.insert_one(booking_doc)
    return serialize_doc(booking_doc)

# Payment Routes
# MTN Mobile Money Configuration and Models
class MTNMoMoConfig:
    def __init__(self):
        self.api_user_id = os.getenv('MTN_MOMO_API_USER_ID', '')
        self.api_key = os.getenv('MTN_MOMO_API_KEY', '')
        self.subscription_key = os.getenv('MTN_MOMO_SUBSCRIPTION_KEY', '')
        self.target_environment = os.getenv('MTN_MOMO_TARGET_ENVIRONMENT', 'sandbox')
        self.base_url = os.getenv('MTN_MOMO_BASE_URL', 'https://sandbox.momodeveloper.mtn.com')
        self.callback_url = os.getenv('MTN_MOMO_CALLBACK_URL', '')

mtn_config = MTNMoMoConfig()

class MTNMoMoTokenManager:
    def __init__(self):
        self.access_token = None
        self.token_expires_at = None
    
    async def get_access_token(self):
        """Get valid access token, refresh if needed"""
        if self.access_token and self.token_expires_at and datetime.now(timezone.utc) < self.token_expires_at:
            return self.access_token
        
        # Request new token
        auth = (mtn_config.api_user_id, mtn_config.api_key)
        headers = {
            'Ocp-Apim-Subscription-Key': mtn_config.subscription_key,
            'X-Target-Environment': mtn_config.target_environment
        }
        
        try:
            import requests
            response = requests.post(
                f"{mtn_config.base_url}/collection/token/",
                auth=auth,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
                self.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)  # 1 min buffer
                return self.access_token
            else:
                logger.error(f"MTN MoMo token request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"MTN MoMo token request error: {e}")
            return None

# Global token manager instance
token_manager = MTNMoMoTokenManager()

class PaymentRequest(BaseModel):
    amount: str
    currency: str = "EUR"  # EUR for sandbox, XAF for production
    external_id: str
    payer_message: str
    payee_note: str
    phone: str
    
class PaymentResponse(BaseModel):
    success: bool
    payment_id: str
    reference_id: str
    status: str
    message: str
    
@api_router.post("/payments/mtn-momo", response_model=PaymentResponse)
async def process_mtn_momo_payment(
    payment_request: PaymentRequest,
    user: User = Depends(get_current_user)
):
    """Process MTN Mobile Money payment using sandbox API"""
    try:
        # Get access token
        access_token = await token_manager.get_access_token()
        if not access_token:
            raise HTTPException(status_code=500, detail="Failed to authenticate with MTN MoMo API")
        
        # Generate reference ID
        reference_id = str(uuid.uuid4())
        
        # Prepare request payload
        payload = {
            "amount": payment_request.amount,
            "currency": payment_request.currency,
            "externalId": payment_request.external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": payment_request.phone
            },
            "payerMessage": payment_request.payer_message,
            "payeeNote": payment_request.payee_note
        }
        
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Reference-Id': reference_id,
            'X-Target-Environment': mtn_config.target_environment,
            'Ocp-Apim-Subscription-Key': mtn_config.subscription_key,
            'Content-Type': 'application/json'
        }
        
        if mtn_config.callback_url:
            headers['X-Callback-Url'] = mtn_config.callback_url
        
        # Create payment record in database
        payment_data = {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "amount": float(payment_request.amount),
            "currency": payment_request.currency,
            "method": "mtn_momo",
            "status": "pending",
            "reference_id": reference_id,
            "external_id": payment_request.external_id,
            "phone": payment_request.phone,
            "created_at": datetime.now(timezone.utc)
        }
        
        # Send request to MTN MoMo API
        import requests
        response = requests.post(
            f"{mtn_config.base_url}/collection/v1_0/requesttopay",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 202:
            # Payment request accepted
            await db.payments.insert_one(payment_data)
            
            return PaymentResponse(
                success=True,
                payment_id=payment_data["id"],
                reference_id=reference_id,
                status="pending",
                message="Payment request sent to customer's mobile phone"
            )
        else:
            logger.error(f"MTN MoMo payment request failed: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=400, 
                detail=f"Payment request failed: {response.text}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MTN MoMo payment error: {e}")
        raise HTTPException(status_code=500, detail="Payment processing failed")

@api_router.get("/payments/mtn-momo/status/{reference_id}")
async def check_mtn_momo_payment_status(
    reference_id: str,
    user: User = Depends(get_current_user)
):
    """Check MTN Mobile Money payment status"""
    try:
        # Get access token
        access_token = await token_manager.get_access_token()
        if not access_token:
            raise HTTPException(status_code=500, detail="Failed to authenticate with MTN MoMo API")
        
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Target-Environment': mtn_config.target_environment,
            'Ocp-Apim-Subscription-Key': mtn_config.subscription_key
        }
        
        # Check status with MTN MoMo API
        import requests
        response = requests.get(
            f"{mtn_config.base_url}/collection/v1_0/requesttopay/{reference_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            status_data = response.json()
            
            # Update local payment record
            await db.payments.update_one(
                {"reference_id": reference_id},
                {
                    "$set": {
                        "status": status_data["status"].lower(),
                        "transaction_id": status_data.get("financialTransactionId"),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            return {
                "success": True,
                "reference_id": reference_id,
                "status": status_data["status"].lower(),
                "amount": status_data["amount"],
                "currency": status_data["currency"],
                "financial_transaction_id": status_data.get("financialTransactionId"),
                "reason": status_data.get("reason")
            }
        else:
            logger.error(f"MTN MoMo status check failed: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=400,
                detail=f"Status check failed: {response.text}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MTN MoMo status check error: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

@api_router.post("/payments/mtn-momo/callback")
async def mtn_momo_callback(request: Request):
    """Handle MTN Mobile Money callback notifications"""
    try:
        callback_data = await request.json()
        
        # Extract reference ID and status
        reference_id = callback_data.get("referenceId")
        status = callback_data.get("status", "").lower()
        
        if not reference_id:
            raise HTTPException(status_code=400, detail="Missing reference ID in callback")
        
        # Update payment record
        update_data = {
            "status": status,
            "updated_at": datetime.now(timezone.utc)
        }
        
        if callback_data.get("financialTransactionId"):
            update_data["transaction_id"] = callback_data["financialTransactionId"]
        
        if callback_data.get("reason"):
            update_data["failure_reason"] = callback_data["reason"]
        
        result = await db.payments.update_one(
            {"reference_id": reference_id},
            {"$set": update_data}
        )
        
        if result.matched_count > 0:
            logger.info(f"MTN MoMo callback processed for reference {reference_id}: {status}")
            return {"success": True, "message": "Callback processed"}
        else:
            logger.warning(f"No payment found for reference ID: {reference_id}")
            return {"success": False, "message": "Payment not found"}
            
    except Exception as e:
        logger.error(f"MTN MoMo callback error: {e}")
        raise HTTPException(status_code=500, detail="Callback processing failed")

@api_router.get("/payments/{payment_id}/status")
async def get_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get payment status"""
    payment_doc = await db.payments.find_one({"id": payment_id, "user_id": current_user.id})
    if not payment_doc:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment_doc["method"] == "mtn_momo" and payment_doc["transaction_id"]:
        try:
            mtn_status = await mtn_client.get_payment_status(payment_doc["transaction_id"])
            
            # Update local status based on MTN response
            new_status = "pending"
            if mtn_status["status"] == "SUCCESSFUL":
                new_status = "successful"
            elif mtn_status["status"] in ["FAILED", "REJECTED"]:
                new_status = "failed"
            
            if new_status != payment_doc["status"]:
                await db.payments.update_one(
                    {"id": payment_id},
                    {"$set": {"status": new_status}}
                )
            
            return {
                "payment_id": payment_id,
                "status": new_status,
                "amount": payment_doc["amount"],
                "mtn_status": mtn_status
            }
            
        except Exception as e:
            return {
                "payment_id": payment_id,
                "status": payment_doc["status"],
                "error": str(e)
            }
    
    return serialize_doc(payment_doc)

# Review Routes
@api_router.get("/reviews", response_model=List[Dict[str, Any]])
async def get_reviews(
    property_id: Optional[str] = None,
    service_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
):
    """Get reviews"""
    filters = {}
    if property_id:
        filters["property_id"] = property_id
    if service_id:
        filters["service_id"] = service_id
    
    reviews = await db.reviews.find(filters).skip(skip).limit(limit).to_list(1000)
    return [serialize_doc(review) for review in reviews]

@api_router.post("/reviews", response_model=Dict[str, Any])
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new review"""
    review_doc = review_data.model_dump()
    review_doc["id"] = str(uuid.uuid4())
    review_doc["reviewer_id"] = current_user.id
    review_doc["created_at"] = datetime.now(timezone.utc)
    
    await db.reviews.insert_one(review_doc)
    return serialize_doc(review_doc)

# Message Routes
@api_router.get("/messages", response_model=List[Dict[str, Any]])
async def get_messages(current_user: User = Depends(get_current_user)):
    """Get user's messages"""
    messages = await db.messages.find({
        "$or": [
            {"sender_id": current_user.id},
            {"receiver_id": current_user.id}
        ]
    }).sort("timestamp", -1).to_list(1000)
    
    return [serialize_doc(msg) for msg in messages]

@api_router.post("/messages", response_model=Dict[str, Any])
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    """Send message"""
    message_doc = message_data.model_dump()
    message_doc["id"] = str(uuid.uuid4())
    message_doc["sender_id"] = current_user.id
    message_doc["timestamp"] = datetime.now(timezone.utc)
    
    await db.messages.insert_one(message_doc)
    return serialize_doc(message_doc)

# Sample data initialization
async def init_sample_data():
    """Initialize sample services for demonstration"""
    # Sample properties
    sample_properties = [
        {
            "id": str(uuid.uuid4()),
            "owner_id": "sample-owner-1",
            "title": "Modern 3-Bedroom Apartment in Douala",
            "description": "Beautiful modern apartment with city views, fully furnished, close to shopping centers and business district. Features include air conditioning, modern kitchen, and secure parking.",
            "price": 180000,
            "currency": "XAF",
            "location": "Akwa, Douala, Littoral",
            "property_type": "apartment",
            "listing_type": "rent",
            "bedrooms": 3,
            "bathrooms": 2,
            "area_sqm": 120,
            "images": ["https://images.unsplash.com/photo-1560448204-e02f11c3d0e2", "https://images.unsplash.com/photo-1571055107559-3e67626fa8be"],
            "amenities": ["Air Conditioning", "Furnished", "Parking", "Security", "Internet"],
            "available": True,
            "verified": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "owner_id": "sample-owner-2", 
            "title": "Spacious Family House for Sale",
            "description": "Large family house with garden, perfect for growing families. Located in quiet residential area with good access to schools and healthcare facilities.",
            "price": 45000000,
            "currency": "XAF",
            "location": "Bastos, Yaoundé, Centre",
            "property_type": "house",
            "listing_type": "sale",
            "bedrooms": 4,
            "bathrooms": 3,
            "area_sqm": 250,
            "images": ["https://images.unsplash.com/photo-1580587771525-78b9dba3b914", "https://images.unsplash.com/photo-1605146769289-440113cc3d00"],
            "amenities": ["Garden", "Garage", "Modern Kitchen", "Study Room", "Guest Room"],
            "available": True,
            "verified": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "owner_id": "sample-owner-3",
            "title": "Commercial Office Space",
            "description": "Prime commercial office space in business district, suitable for companies and startups. Modern facilities with meeting rooms and parking.",
            "price": 350000,
            "currency": "XAF", 
            "location": "Bonanjo, Douala, Littoral",
            "property_type": "commercial",
            "listing_type": "rent",
            "bedrooms": 0,
            "bathrooms": 2,
            "area_sqm": 180,
            "images": ["https://images.unsplash.com/photo-1497366216548-37526070297c", "https://images.unsplash.com/photo-1497366811353-6870744d04b2"],
            "amenities": ["Meeting Rooms", "Parking", "Internet", "Reception Area", "Security"],
            "available": True,
            "verified": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "owner_id": "sample-owner-4",
            "title": "Cozy Studio Apartment",
            "description": "Perfect studio for students or young professionals. Located near university campus with easy access to public transportation.",
            "price": 85000,
            "currency": "XAF",
            "location": "Ngoa-Ekelle, Yaoundé, Centre", 
            "property_type": "apartment",
            "listing_type": "rent",
            "bedrooms": 1,
            "bathrooms": 1,
            "area_sqm": 45,
            "images": ["https://images.unsplash.com/photo-1522708323590-d24dbb6b0267", "https://images.unsplash.com/photo-1560448075-bb485b067938"],
            "amenities": ["Furnished", "Internet", "Near Campus", "Public Transport"],
            "available": True,
            "verified": True,
            "created_at": datetime.now(timezone.utc)
        }
    ]

    sample_services = [
        {
            "id": str(uuid.uuid4()),
            "provider_id": "sample-provider-1",
            "category": "plumbing",
            "title": "Expert Plumbing Services",
            "description": "Professional plumbing installation, repair, and maintenance services for residential and commercial properties.",
            "price_range": "15,000 - 75,000 XAF",
            "location": "Douala, Littoral",
            "images": ["https://images.unsplash.com/photo-1621905252507-b35492cc74b4"],
            "available": True,
            "verified": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "provider_id": "sample-provider-2", 
            "category": "electrical",
            "title": "Licensed Electrician Services",
            "description": "Certified electrical installations, repairs, and safety inspections for homes and businesses.",
            "price_range": "20,000 - 100,000 XAF",
            "location": "Yaoundé, Centre",
            "images": ["https://images.unsplash.com/photo-1621905251918-48416bd8575a"],
            "available": True,
            "verified": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "provider_id": "sample-provider-3",
            "category": "construction",
            "title": "Premium Construction Company",
            "description": "Full-service construction company specializing in residential and commercial building projects.",
            "price_range": "Contact for quote",
            "location": "Bafoussam, Ouest",
            "images": ["https://images.unsplash.com/photo-1504307651254-35680f356dfd"],
            "available": True,
            "verified": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "provider_id": "sample-provider-4",
            "category": "interior_design",
            "title": "Modern Interior Design Studio", 
            "description": "Creative interior design solutions for homes, offices, and commercial spaces with modern aesthetics.",
            "price_range": "50,000 - 500,000 XAF",
            "location": "Douala, Littoral",
            "images": ["https://images.unsplash.com/photo-1586023492125-27b2c045efd7"],
            "available": True,
            "verified": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "provider_id": "sample-provider-5",
            "category": "painting",
            "title": "Professional Painting Services",
            "description": "High-quality interior and exterior painting services for residential and commercial properties.",
            "price_range": "25,000 - 150,000 XAF",
            "location": "Bamenda, Nord-Ouest",
            "images": ["https://images.unsplash.com/photo-1562259949-e8e7689d7828"],
            "available": True,
            "verified": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "provider_id": "sample-provider-6",
            "category": "carpentry",
            "title": "Custom Carpentry & Woodwork",
            "description": "Skilled carpentry services including custom furniture, cabinets, and wooden structures.",
            "price_range": "30,000 - 200,000 XAF",
            "location": "Garoua, Nord",
            "images": ["https://images.unsplash.com/photo-1503387762-592deb58ef4e"],
            "available": True,
            "verified": True,
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    # Check if properties already exist
    existing_properties = await db.properties.count_documents({})
    if existing_properties == 0:
        await db.properties.insert_many(sample_properties)
        logger.info(f"Inserted {len(sample_properties)} sample properties")
    
    # Check if services already exist
    existing_services = await db.services.count_documents({})
    if existing_services == 0:
        await db.services.insert_many(sample_services)
        logger.info(f"Inserted {len(sample_services)} sample services")

# Image Upload Helper Functions
async def create_thumbnail(image_path: Path, thumbnail_path: Path):
    """Create a thumbnail from an image"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, optimize=True, quality=85)
        return True
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return False

def validate_image_file(file: UploadFile) -> tuple[bool, str]:
    """Validate uploaded image file"""
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        return False, f"File size {file.size / 1024 / 1024:.1f}MB exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit"
    
    # Check mime type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return False, f"File type {file.content_type} not supported. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
    
    return True, ""

# Image Upload Routes
@api_router.post("/upload/images", response_model=Dict[str, Any])
async def upload_images(
    files: List[UploadFile] = File(...),
    entity_type: str = Form(...),  # 'property', 'service', 'profile', 'chat'
    entity_id: Optional[str] = Form(None),
    user: User = Depends(get_current_user)
):
    """Upload multiple images with automatic thumbnail generation"""
    logger.info(f"Image upload request from user {user.email} for {entity_type}")
    try:
        if len(files) > 10:  # Max 10 files at once
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed per upload")
        
        uploaded_images = []
        
        for file in files:
            # Validate file
            is_valid, error_message = validate_image_file(file)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"{file.filename}: {error_message}")
            
            # Generate unique filename
            file_ext = Path(file.filename).suffix.lower()
            if not file_ext:
                file_ext = mimetypes.guess_extension(file.content_type) or '.jpg'
            
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            
            # Determine upload path based on entity type
            entity_dir = UPLOAD_DIR / entity_type.lower()
            entity_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
            
            file_path = entity_dir / unique_filename
            thumbnail_path = UPLOAD_DIR / "thumbnails" / f"thumb_{unique_filename}"
            
            # Save original file
            content = await file.read()
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Create thumbnail
            await create_thumbnail(file_path, thumbnail_path)
            
            # Create image record
            image_data = {
                "id": str(uuid.uuid4()),
                "filename": unique_filename,
                "original_filename": file.filename,
                "file_path": str(file_path.relative_to(ROOT_DIR)),
                "thumbnail_path": str(thumbnail_path.relative_to(ROOT_DIR)),
                "file_size": file.size or len(content),
                "mime_type": file.content_type,
                "uploaded_by": user.id,
                "entity_type": entity_type.lower(),
                "entity_id": entity_id,
                "is_primary": False,
                "created_at": datetime.now(timezone.utc)
            }
            
            # Save to database
            result = await db.images.insert_one(image_data)
            image_data["_id"] = str(result.inserted_id)
            
            uploaded_images.append({
                "id": image_data["id"],
                "filename": image_data["filename"],
                "original_filename": image_data["original_filename"],
                "url": f"/uploads/{entity_type.lower()}/{unique_filename}",
                "thumbnail_url": f"/uploads/thumbnails/thumb_{unique_filename}",
                "file_size": image_data["file_size"],
                "mime_type": image_data["mime_type"]
            })
        
        return {
            "success": True,
            "message": f"Successfully uploaded {len(uploaded_images)} images",
            "images": uploaded_images
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading images: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload images: {str(e)}")

@api_router.get("/images/{entity_type}/{entity_id}", response_model=List[Dict[str, Any]])
async def get_entity_images(entity_type: str, entity_id: str):
    """Get all images for a specific entity"""
    try:
        images = await db.images.find({
            "entity_type": entity_type.lower(),
            "entity_id": entity_id
        }).sort("created_at", 1).to_list(length=None)
        
        return [{
            "id": img["id"],
            "filename": img["filename"],
            "original_filename": img["original_filename"],
            "url": f"/uploads/{entity_type.lower()}/{img['filename']}",
            "thumbnail_url": f"/uploads/thumbnails/thumb_{img['filename']}",
            "is_primary": img.get("is_primary", False),
            "alt_text": img.get("alt_text"),
            "created_at": img["created_at"].isoformat()
        } for img in images]
        
    except Exception as e:
        logger.error(f"Error fetching images: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch images")

@api_router.put("/images/{image_id}/primary")
async def set_primary_image(image_id: str, user: User = Depends(get_current_user)):
    """Set an image as primary for its entity"""
    try:
        # Get the image
        image = await db.images.find_one({"id": image_id})
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Check ownership or admin
        if image["uploaded_by"] != user.id and user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Remove primary status from other images of the same entity
        await db.images.update_many(
            {
                "entity_type": image["entity_type"],
                "entity_id": image["entity_id"]
            },
            {"$set": {"is_primary": False}}
        )
        
        # Set this image as primary
        await db.images.update_one(
            {"id": image_id},
            {"$set": {"is_primary": True}}
        )
        
        return {"success": True, "message": "Primary image updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting primary image: {e}")
        raise HTTPException(status_code=500, detail="Failed to update primary image")

@api_router.delete("/images/{image_id}")
async def delete_image(image_id: str, user: User = Depends(get_current_user)):
    """Delete an uploaded image"""
    try:
        # Get the image
        image = await db.images.find_one({"id": image_id})
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Check ownership or admin
        if image["uploaded_by"] != user.id and user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Delete physical files
        file_path = ROOT_DIR / image["file_path"]
        thumbnail_path = ROOT_DIR / image.get("thumbnail_path", "")
        
        try:
            if file_path.exists():
                file_path.unlink()
            if thumbnail_path.exists():
                thumbnail_path.unlink()
        except Exception as e:
            logger.warning(f"Error deleting physical files: {e}")
        
        # Delete database record
        await db.images.delete_one({"id": image_id})
        
        return {"success": True, "message": "Image deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete image")

# Utility Routes
@api_router.get("/")
async def root():
    """API root"""
    return {"message": "Habitere API - Real Estate and Home Services Platform"}

@api_router.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@api_router.post("/init-sample-data")
async def initialize_sample_data():
    """Initialize sample data for demonstration"""
    await init_sample_data()
    return {"message": "Sample data initialized"}

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@api_router.get("/admin/stats")
async def get_admin_stats(admin: User = Depends(get_admin_user)):
    """Get dashboard statistics for admin"""
    try:
        # Count users by status
        total_users = await db.users.count_documents({})
        pending_users = await db.users.count_documents({"verification_status": "pending", "role": {"$ne": "admin"}})
        approved_users = await db.users.count_documents({"verification_status": "approved"})
        
        # Count properties by status
        total_properties = await db.properties.count_documents({})
        pending_properties = await db.properties.count_documents({"verification_status": "pending"})
        verified_properties = await db.properties.count_documents({"verification_status": "verified"})
        
        # Count services by status
        total_services = await db.professional_services.count_documents({})
        pending_services = await db.professional_services.count_documents({"verification_status": "pending"})
        verified_services = await db.professional_services.count_documents({"verification_status": "verified"})
        
        # Count bookings
        total_bookings = await db.bookings.count_documents({})
        pending_bookings = await db.bookings.count_documents({"status": "pending"})
        
        # Calculate revenue (from successful payments)
        pipeline = [
            {"$match": {"status": "successful"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        revenue_result = await db.payments.aggregate(pipeline).to_list(length=1)
        total_revenue = revenue_result[0]["total"] if revenue_result else 0
        
        # Recent activity - last 7 days
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        new_users_week = await db.users.count_documents({"created_at": {"$gte": seven_days_ago}})
        new_properties_week = await db.properties.count_documents({"created_at": {"$gte": seven_days_ago}})
        new_bookings_week = await db.bookings.count_documents({"created_at": {"$gte": seven_days_ago}})
        
        return {
            "users": {
                "total": total_users,
                "pending": pending_users,
                "approved": approved_users,
                "new_this_week": new_users_week
            },
            "properties": {
                "total": total_properties,
                "pending": pending_properties,
                "verified": verified_properties,
                "new_this_week": new_properties_week
            },
            "services": {
                "total": total_services,
                "pending": pending_services,
                "verified": verified_services
            },
            "bookings": {
                "total": total_bookings,
                "pending": pending_bookings,
                "new_this_week": new_bookings_week
            },
            "revenue": {
                "total": total_revenue,
                "currency": "XAF"
            }
        }
    except Exception as e:
        logger.error(f"Error fetching admin stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@api_router.get("/admin/users")
async def get_all_users(
    admin: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 50,
    role: Optional[str] = None,
    verification_status: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all users with filters"""
    try:
        query = {"role": {"$ne": "admin"}}  # Don't show admin users
        
        if role:
            query["role"] = role
        if verification_status:
            query["verification_status"] = verification_status
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"company_name": {"$regex": search, "$options": "i"}}
            ]
        
        total = await db.users.count_documents(query)
        users_cursor = db.users.find(query).sort("created_at", -1).skip(skip).limit(limit)
        users = await users_cursor.to_list(length=limit)
        
        # Remove sensitive fields
        for user in users:
            user.pop("password_hash", None)
            user.pop("email_verification_token", None)
            user.pop("password_reset_token", None)
        
        return {
            "total": total,
            "users": [User(**user) for user in users],
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@api_router.put("/admin/users/{user_id}/approve")
async def approve_user(user_id: str, admin: User = Depends(get_admin_user)):
    """Approve a user account"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        result = await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "verification_status": "approved",
                    "is_verified": True,
                    "verified_by": admin.id,
                    "verified_at": datetime.now(timezone.utc),
                    "rejection_reason": None
                }
            }
        )
        
        if result.modified_count:
            return {"message": "User approved successfully", "user_id": user_id}
        raise HTTPException(status_code=400, detail="Failed to approve user")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving user: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve user")

@api_router.put("/admin/users/{user_id}/reject")
async def reject_user(
    user_id: str,
    reason: str,
    admin: User = Depends(get_admin_user)
):
    """Reject a user account"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        result = await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "verification_status": "rejected",
                    "is_verified": False,
                    "verified_by": admin.id,
                    "verified_at": datetime.now(timezone.utc),
                    "rejection_reason": reason
                }
            }
        )
        
        if result.modified_count:
            return {"message": "User rejected", "user_id": user_id}
        raise HTTPException(status_code=400, detail="Failed to reject user")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject user")

@api_router.get("/admin/properties")
async def get_all_properties_admin(
    admin: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 50,
    verification_status: Optional[str] = None,
    property_type: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all properties for admin moderation"""
    try:
        query = {}
        
        if verification_status:
            query["verification_status"] = verification_status
        if property_type:
            query["listing_type"] = property_type
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"location": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        total = await db.properties.count_documents(query)
        properties_cursor = db.properties.find(query).sort("created_at", -1).skip(skip).limit(limit)
        properties = await properties_cursor.to_list(length=limit)
        
        # Fetch owner info for each property
        for prop in properties:
            owner = await db.users.find_one({"id": prop["owner_id"]})
            prop["owner_name"] = owner["name"] if owner else "Unknown"
            prop["owner_email"] = owner["email"] if owner else "Unknown"
        
        return {
            "total": total,
            "properties": [Property(**prop) for prop in properties],
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error fetching properties: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch properties")

@api_router.put("/admin/properties/{property_id}/verify")
async def verify_property(property_id: str, admin: User = Depends(get_admin_user)):
    """Verify/approve a property listing"""
    try:
        prop = await db.properties.find_one({"id": property_id})
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")
        
        result = await db.properties.update_one(
            {"id": property_id},
            {
                "$set": {
                    "verification_status": "verified",
                    "verified": True,
                    "verified_by": admin.id,
                    "verified_at": datetime.now(timezone.utc),
                    "rejection_reason": None
                }
            }
        )
        
        if result.modified_count:
            return {"message": "Property verified successfully", "property_id": property_id}
        raise HTTPException(status_code=400, detail="Failed to verify property")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying property: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify property")

@api_router.put("/admin/properties/{property_id}/reject")
async def reject_property(
    property_id: str,
    reason: str,
    admin: User = Depends(get_admin_user)
):
    """Reject a property listing"""
    try:
        prop = await db.properties.find_one({"id": property_id})
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")
        
        result = await db.properties.update_one(
            {"id": property_id},
            {
                "$set": {
                    "verification_status": "rejected",
                    "verified": False,
                    "verified_by": admin.id,
                    "verified_at": datetime.now(timezone.utc),
                    "rejection_reason": reason
                }
            }
        )
        
        if result.modified_count:
            return {"message": "Property rejected", "property_id": property_id}
        raise HTTPException(status_code=400, detail="Failed to reject property")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting property: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject property")

@api_router.get("/admin/services")
async def get_all_services_admin(
    admin: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 50,
    verification_status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all professional services for admin moderation"""
    try:
        query = {}
        
        if verification_status:
            query["verification_status"] = verification_status
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"location": {"$regex": search, "$options": "i"}}
            ]
        
        total = await db.professional_services.count_documents(query)
        services_cursor = db.professional_services.find(query).sort("created_at", -1).skip(skip).limit(limit)
        services = await services_cursor.to_list(length=limit)
        
        # Fetch provider info for each service
        for service in services:
            provider = await db.users.find_one({"id": service["provider_id"]})
            service["provider_name"] = provider["name"] if provider else "Unknown"
            service["provider_email"] = provider["email"] if provider else "Unknown"
        
        return {
            "total": total,
            "services": [ProfessionalService(**service) for service in services],
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error fetching services: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch services")

@api_router.put("/admin/services/{service_id}/verify")
async def verify_service(service_id: str, admin: User = Depends(get_admin_user)):
    """Verify/approve a professional service"""
    try:
        service = await db.professional_services.find_one({"id": service_id})
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        result = await db.professional_services.update_one(
            {"id": service_id},
            {
                "$set": {
                    "verification_status": "verified",
                    "verified": True,
                    "verified_by": admin.id,
                    "verified_at": datetime.now(timezone.utc),
                    "rejection_reason": None
                }
            }
        )
        
        if result.modified_count:
            return {"message": "Service verified successfully", "service_id": service_id}
        raise HTTPException(status_code=400, detail="Failed to verify service")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying service: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify service")

@api_router.put("/admin/services/{service_id}/reject")
async def reject_service(
    service_id: str,
    reason: str,
    admin: User = Depends(get_admin_user)
):
    """Reject a professional service"""
    try:
        service = await db.professional_services.find_one({"id": service_id})
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        result = await db.professional_services.update_one(
            {"id": service_id},
            {
                "$set": {
                    "verification_status": "rejected",
                    "verified": False,
                    "verified_by": admin.id,
                    "verified_at": datetime.now(timezone.utc),
                    "rejection_reason": reason
                }
            }
        )
        
        if result.modified_count:
            return {"message": "Service rejected", "service_id": service_id}
        raise HTTPException(status_code=400, detail="Failed to reject service")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting service: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject service")

@api_router.get("/admin/analytics/users")
async def get_user_analytics(admin: User = Depends(get_admin_user), days: int = 30):
    """Get user registration analytics"""
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # User registration trend
        pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        registrations = await db.users.aggregate(pipeline).to_list(length=days)
        
        # User distribution by role
        role_pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        role_distribution = await db.users.aggregate(role_pipeline).to_list(length=None)
        
        return {
            "registration_trend": registrations,
            "role_distribution": role_distribution,
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Error fetching user analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

@api_router.get("/admin/analytics/properties")
async def get_property_analytics(admin: User = Depends(get_admin_user), days: int = 30):
    """Get property listing analytics"""
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Property listing trend
        pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        listings_trend = await db.properties.aggregate(pipeline).to_list(length=days)
        
        # Property distribution by type
        type_pipeline = [
            {"$group": {"_id": "$listing_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        type_distribution = await db.properties.aggregate(type_pipeline).to_list(length=None)
        
        # Most viewed properties
        most_viewed = await db.properties.find().sort("views", -1).limit(10).to_list(length=10)
        
        return {
            "listings_trend": listings_trend,
            "type_distribution": type_distribution,
            "most_viewed_properties": [Property(**prop) for prop in most_viewed],
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Error fetching property analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

# ============================================================================
# REVIEWS & RATINGS ENDPOINTS
# ============================================================================

@api_router.post("/reviews")
async def create_review(
    review_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new review for a property or service"""
    try:
        # Validate that either property_id or service_id is provided
        if not review_data.get('property_id') and not review_data.get('service_id'):
            raise HTTPException(status_code=400, detail="Must specify either property_id or service_id")
        
        if review_data.get('property_id') and review_data.get('service_id'):
            raise HTTPException(status_code=400, detail="Cannot review both property and service in one review")
        
        # Validate rating
        rating = review_data.get('rating', 0)
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Check if user already reviewed this item
        query = {"reviewer_id": current_user.id}
        if review_data.get('property_id'):
            query["property_id"] = review_data['property_id']
            # Verify property exists
            property_doc = await db.properties.find_one({"id": review_data['property_id']})
            if not property_doc:
                raise HTTPException(status_code=404, detail="Property not found")
        else:
            query["service_id"] = review_data['service_id']
            # Verify service exists
            service_doc = await db.professional_services.find_one({"id": review_data['service_id']})
            if not service_doc:
                raise HTTPException(status_code=404, detail="Service not found")
        
        existing_review = await db.reviews.find_one(query)
        if existing_review:
            raise HTTPException(status_code=400, detail="You have already reviewed this item")
        
        # Create review
        review = {
            "id": str(uuid.uuid4()),
            "reviewer_id": current_user.id,
            "property_id": review_data.get('property_id'),
            "service_id": review_data.get('service_id'),
            "rating": rating,
            "comment": review_data.get('comment', ''),
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.reviews.insert_one(review)
        
        # Update average rating
        await update_rating_aggregation(
            review_data.get('property_id'),
            review_data.get('service_id')
        )
        
        return {"message": "Review created successfully", "review": Review(**review)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {e}")
        raise HTTPException(status_code=500, detail="Failed to create review")

@api_router.get("/reviews/property/{property_id}")
async def get_property_reviews(property_id: str, skip: int = 0, limit: int = 20):
    """Get all reviews for a property"""
    try:
        reviews_cursor = db.reviews.find({"property_id": property_id}).sort("created_at", -1).skip(skip).limit(limit)
        reviews = await reviews_cursor.to_list(length=limit)
        
        # Fetch reviewer info for each review
        for review in reviews:
            reviewer = await db.users.find_one({"id": review["reviewer_id"]})
            if reviewer:
                review["reviewer_name"] = reviewer["name"]
                review["reviewer_picture"] = reviewer.get("picture")
        
        total = await db.reviews.count_documents({"property_id": property_id})
        
        return {
            "reviews": [Review(**review) for review in reviews],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error fetching property reviews: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reviews")

@api_router.get("/reviews/service/{service_id}")
async def get_service_reviews(service_id: str, skip: int = 0, limit: int = 20):
    """Get all reviews for a service"""
    try:
        reviews_cursor = db.reviews.find({"service_id": service_id}).sort("created_at", -1).skip(skip).limit(limit)
        reviews = await reviews_cursor.to_list(length=limit)
        
        # Fetch reviewer info for each review
        for review in reviews:
            reviewer = await db.users.find_one({"id": review["reviewer_id"]})
            if reviewer:
                review["reviewer_name"] = reviewer["name"]
                review["reviewer_picture"] = reviewer.get("picture")
        
        total = await db.reviews.count_documents({"service_id": service_id})
        
        return {
            "reviews": [Review(**review) for review in reviews],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error fetching service reviews: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reviews")

@api_router.get("/reviews/user/{user_id}")
async def get_user_reviews(user_id: str):
    """Get all reviews by a user"""
    try:
        reviews_cursor = db.reviews.find({"reviewer_id": user_id}).sort("created_at", -1)
        reviews = await reviews_cursor.to_list(length=None)
        
        # Fetch property/service info for each review
        for review in reviews:
            if review.get('property_id'):
                prop = await db.properties.find_one({"id": review['property_id']})
                if prop:
                    review["property_title"] = prop["title"]
            elif review.get('service_id'):
                service = await db.professional_services.find_one({"id": review['service_id']})
                if service:
                    review["service_title"] = service["title"]
        
        return {"reviews": [Review(**review) for review in reviews]}
    except Exception as e:
        logger.error(f"Error fetching user reviews: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reviews")

@api_router.put("/reviews/{review_id}")
async def update_review(
    review_id: str,
    review_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update a review"""
    try:
        review = await db.reviews.find_one({"id": review_id})
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Check if user owns the review
        if review["reviewer_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only update your own reviews")
        
        # Validate rating if provided
        if 'rating' in review_data:
            rating = review_data['rating']
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Update review
        update_data = {}
        if 'rating' in review_data:
            update_data['rating'] = review_data['rating']
        if 'comment' in review_data:
            update_data['comment'] = review_data['comment']
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        await db.reviews.update_one({"id": review_id}, {"$set": update_data})
        
        # Update average rating if rating changed
        if 'rating' in review_data:
            await update_rating_aggregation(
                review.get('property_id'),
                review.get('service_id')
            )
        
        updated_review = await db.reviews.find_one({"id": review_id})
        return {"message": "Review updated successfully", "review": Review(**updated_review)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating review: {e}")
        raise HTTPException(status_code=500, detail="Failed to update review")

@api_router.delete("/reviews/{review_id}")
async def delete_review(review_id: str, current_user: User = Depends(get_current_user)):
    """Delete a review"""
    try:
        review = await db.reviews.find_one({"id": review_id})
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Check if user owns the review or is admin
        if review["reviewer_id"] != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="You can only delete your own reviews")
        
        property_id = review.get('property_id')
        service_id = review.get('service_id')
        
        await db.reviews.delete_one({"id": review_id})
        
        # Update average rating
        await update_rating_aggregation(property_id, service_id)
        
        return {"message": "Review deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete review")

async def update_rating_aggregation(property_id: Optional[str], service_id: Optional[str]):
    """Update average rating and review count for a property or service"""
    try:
        if property_id:
            # Calculate average rating for property
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
                await db.properties.update_one(
                    {"id": property_id},
                    {"$set": {
                        "average_rating": round(result[0]["average_rating"], 1),
                        "review_count": result[0]["review_count"]
                    }}
                )
            else:
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
                await db.professional_services.update_one(
                    {"id": service_id},
                    {"$set": {
                        "average_rating": round(result[0]["average_rating"], 1),
                        "review_count": result[0]["review_count"]
                    }}
                )
            else:
                await db.professional_services.update_one(
                    {"id": service_id},
                    {"$set": {"average_rating": 0.0, "review_count": 0}}
                )
    except Exception as e:
        logger.error(f"Error updating rating aggregation: {e}")

# ============================================================================
# MESSAGING ENDPOINTS
# ============================================================================

@api_router.post("/messages")
async def send_message(
    message_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Send a message to another user"""
    try:
        receiver_id = message_data.get('receiver_id')
        content = message_data.get('content', '').strip()
        
        if not receiver_id:
            raise HTTPException(status_code=400, detail="Receiver ID is required")
        
        if not content:
            raise HTTPException(status_code=400, detail="Message content cannot be empty")
        
        # Verify receiver exists
        receiver = await db.users.find_one({"id": receiver_id})
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver not found")
        
        # Cannot message yourself
        if receiver_id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot send message to yourself")
        
        # Create message
        message = {
            "id": str(uuid.uuid4()),
            "sender_id": current_user.id,
            "receiver_id": receiver_id,
            "content": content,
            "timestamp": datetime.now(timezone.utc),
            "is_read": False
        }
        
        await db.messages.insert_one(message)
        
        return {"message": "Message sent successfully", "data": Message(**message)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@api_router.get("/messages/conversations")
async def get_conversations(current_user: User = Depends(get_current_user)):
    """Get all conversations for current user"""
    try:
        # Get all unique users the current user has messaged with
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"sender_id": current_user.id},
                        {"receiver_id": current_user.id}
                    ]
                }
            },
            {
                "$sort": {"timestamp": -1}
            },
            {
                "$group": {
                    "_id": {
                        "$cond": [
                            {"$eq": ["$sender_id", current_user.id]},
                            "$receiver_id",
                            "$sender_id"
                        ]
                    },
                    "last_message": {"$first": "$$ROOT"}
                }
            }
        ]
        
        conversations_data = await db.messages.aggregate(pipeline).to_list(length=None)
        
        # Fetch user details and unread count for each conversation
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
                "receiver_id": current_user.id,
                "is_read": False
            })
            
            conversations.append({
                "user_id": other_user_id,
                "user_name": other_user["name"],
                "user_picture": other_user.get("picture"),
                "last_message": last_message["content"],
                "last_message_time": last_message["timestamp"],
                "is_last_sender": last_message["sender_id"] == current_user.id,
                "unread_count": unread_count
            })
        
        # Sort by last message time
        conversations.sort(key=lambda x: x["last_message_time"], reverse=True)
        
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

@api_router.get("/messages/thread/{other_user_id}")
async def get_message_thread(
    other_user_id: str,
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    skip: int = 0
):
    """Get message thread between current user and another user"""
    try:
        # Verify other user exists
        other_user = await db.users.find_one({"id": other_user_id})
        if not other_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get messages between the two users
        messages_cursor = db.messages.find({
            "$or": [
                {"sender_id": current_user.id, "receiver_id": other_user_id},
                {"sender_id": other_user_id, "receiver_id": current_user.id}
            ]
        }).sort("timestamp", -1).skip(skip).limit(limit)
        
        messages = await messages_cursor.to_list(length=limit)
        messages.reverse()  # Show oldest first
        
        # Mark messages from other user as read
        await db.messages.update_many(
            {
                "sender_id": other_user_id,
                "receiver_id": current_user.id,
                "is_read": False
            },
            {"$set": {"is_read": True}}
        )
        
        return {
            "messages": [Message(**msg) for msg in messages],
            "other_user": {
                "id": other_user["id"],
                "name": other_user["name"],
                "picture": other_user.get("picture"),
                "role": other_user.get("role")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching message thread: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")

@api_router.get("/messages/unread-count")
async def get_unread_count(current_user: User = Depends(get_current_user)):
    """Get total unread message count"""
    try:
        count = await db.messages.count_documents({
            "receiver_id": current_user.id,
            "is_read": False
        })
        return {"unread_count": count}
    except Exception as e:
        logger.error(f"Error fetching unread count: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch unread count")

@api_router.put("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark a message as read"""
    try:
        message = await db.messages.find_one({"id": message_id})
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Only receiver can mark as read
        if message["receiver_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        await db.messages.update_one(
            {"id": message_id},
            {"$set": {"is_read": True}}
        )
        
        return {"message": "Message marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark message as read")

@api_router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a message (sender only)"""
    try:
        message = await db.messages.find_one({"id": message_id})
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Only sender or admin can delete
        if message["sender_id"] != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        await db.messages.delete_one({"id": message_id})
        
        return {"message": "Message deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete message")

# ============================================================================
# BOOKING ENDPOINTS
# ============================================================================

@api_router.post("/bookings")
async def create_booking(
    booking_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new booking for property viewing or service"""
    try:
        # Validate booking type
        booking_type = booking_data.get('booking_type')
        if booking_type not in ['property_viewing', 'service_booking']:
            raise HTTPException(status_code=400, detail="Invalid booking type")
        
        # Validate that either property_id or service_id is provided
        property_id = booking_data.get('property_id')
        service_id = booking_data.get('service_id')
        
        if booking_type == 'property_viewing' and not property_id:
            raise HTTPException(status_code=400, detail="Property ID required for property viewing")
        
        if booking_type == 'service_booking' and not service_id:
            raise HTTPException(status_code=400, detail="Service ID required for service booking")
        
        # Verify property or service exists
        if property_id:
            property_doc = await db.properties.find_one({"id": property_id})
            if not property_doc:
                raise HTTPException(status_code=404, detail="Property not found")
        
        if service_id:
            service_doc = await db.professional_services.find_one({"id": service_id})
            if not service_doc:
                raise HTTPException(status_code=404, detail="Service not found")
        
        # Parse scheduled date
        scheduled_date_str = booking_data.get('scheduled_date')
        if not scheduled_date_str:
            raise HTTPException(status_code=400, detail="Scheduled date is required")
        
        try:
            scheduled_date = datetime.fromisoformat(scheduled_date_str.replace('Z', '+00:00'))
        except:
            raise HTTPException(status_code=400, detail="Invalid date format")
        
        # Create booking
        booking = {
            "id": str(uuid.uuid4()),
            "client_id": current_user.id,
            "property_id": property_id,
            "service_id": service_id,
            "booking_type": booking_type,
            "scheduled_date": scheduled_date,
            "scheduled_time": booking_data.get('scheduled_time'),
            "duration_hours": booking_data.get('duration_hours', 1),
            "status": "pending",
            "notes": booking_data.get('notes', ''),
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.bookings.insert_one(booking)
        
        return {"message": "Booking created successfully", "booking": Booking(**booking)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        raise HTTPException(status_code=500, detail="Failed to create booking")

@api_router.get("/bookings")
async def get_user_bookings(
    current_user: User = Depends(get_current_user),
    status: Optional[str] = None
):
    """Get all bookings for current user"""
    try:
        query = {"client_id": current_user.id}
        if status:
            query["status"] = status
        
        bookings_cursor = db.bookings.find(query).sort("scheduled_date", -1)
        bookings = await bookings_cursor.to_list(length=None)
        
        # Fetch property/service details for each booking
        for booking in bookings:
            if booking.get('property_id'):
                prop = await db.properties.find_one({"id": booking['property_id']})
                if prop:
                    booking["property_title"] = prop["title"]
                    booking["property_location"] = prop["location"]
                    booking["property_price"] = prop["price"]
            
            if booking.get('service_id'):
                service = await db.professional_services.find_one({"id": booking['service_id']})
                if service:
                    booking["service_title"] = service["title"]
                    booking["service_category"] = service["category"]
                    
                    # Get provider info
                    provider = await db.users.find_one({"id": service["provider_id"]})
                    if provider:
                        booking["provider_name"] = provider["name"]
        
        return {"bookings": [Booking(**booking) for booking in bookings]}
    except Exception as e:
        logger.error(f"Error fetching bookings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bookings")

@api_router.get("/bookings/received")
async def get_received_bookings(
    current_user: User = Depends(get_current_user),
    status: Optional[str] = None
):
    """Get bookings received (for property owners and service providers)"""
    try:
        # Find properties/services owned by current user
        properties = await db.properties.find({"owner_id": current_user.id}).to_list(length=None)
        property_ids = [p["id"] for p in properties]
        
        services = await db.professional_services.find({"provider_id": current_user.id}).to_list(length=None)
        service_ids = [s["id"] for s in services]
        
        # Find bookings for these properties/services
        query = {
            "$or": [
                {"property_id": {"$in": property_ids}},
                {"service_id": {"$in": service_ids}}
            ]
        }
        
        if status:
            query["status"] = status
        
        bookings_cursor = db.bookings.find(query).sort("scheduled_date", -1)
        bookings = await bookings_cursor.to_list(length=None)
        
        # Fetch client and property/service details
        for booking in bookings:
            client = await db.users.find_one({"id": booking['client_id']})
            if client:
                booking["client_name"] = client["name"]
                booking["client_email"] = client["email"]
                booking["client_phone"] = client.get("phone")
            
            if booking.get('property_id'):
                prop = await db.properties.find_one({"id": booking['property_id']})
                if prop:
                    booking["property_title"] = prop["title"]
                    booking["property_location"] = prop["location"]
            
            if booking.get('service_id'):
                service = await db.professional_services.find_one({"id": booking['service_id']})
                if service:
                    booking["service_title"] = service["title"]
        
        return {"bookings": [Booking(**booking) for booking in bookings]}
    except Exception as e:
        logger.error(f"Error fetching received bookings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bookings")

@api_router.get("/bookings/{booking_id}")
async def get_booking(booking_id: str, current_user: User = Depends(get_current_user)):
    """Get booking details"""
    try:
        booking = await db.bookings.find_one({"id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Check authorization
        is_client = booking["client_id"] == current_user.id
        
        # Check if user is property owner or service provider
        is_owner = False
        if booking.get('property_id'):
            prop = await db.properties.find_one({"id": booking['property_id']})
            is_owner = prop and prop["owner_id"] == current_user.id
        elif booking.get('service_id'):
            service = await db.professional_services.find_one({"id": booking['service_id']})
            is_owner = service and service["provider_id"] == current_user.id
        
        if not is_client and not is_owner and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return {"booking": Booking(**booking)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching booking: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch booking")

@api_router.put("/bookings/{booking_id}/confirm")
async def confirm_booking(booking_id: str, current_user: User = Depends(get_current_user)):
    """Confirm a booking (property owner or service provider only)"""
    try:
        booking = await db.bookings.find_one({"id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Check if user is owner/provider
        is_authorized = False
        if booking.get('property_id'):
            prop = await db.properties.find_one({"id": booking['property_id']})
            is_authorized = prop and prop["owner_id"] == current_user.id
        elif booking.get('service_id'):
            service = await db.professional_services.find_one({"id": booking['service_id']})
            is_authorized = service and service["provider_id"] == current_user.id
        
        if not is_authorized and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        result = await db.bookings.update_one(
            {"id": booking_id},
            {
                "$set": {
                    "status": "confirmed",
                    "confirmed_by": current_user.id,
                    "confirmed_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count:
            return {"message": "Booking confirmed successfully"}
        raise HTTPException(status_code=400, detail="Failed to confirm booking")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming booking: {e}")
        raise HTTPException(status_code=500, detail="Failed to confirm booking")

@api_router.put("/bookings/{booking_id}/complete")
async def complete_booking(booking_id: str, current_user: User = Depends(get_current_user)):
    """Mark booking as completed"""
    try:
        booking = await db.bookings.find_one({"id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Check authorization (owner/provider or admin)
        is_authorized = False
        if booking.get('property_id'):
            prop = await db.properties.find_one({"id": booking['property_id']})
            is_authorized = prop and prop["owner_id"] == current_user.id
        elif booking.get('service_id'):
            service = await db.professional_services.find_one({"id": booking['service_id']})
            is_authorized = service and service["provider_id"] == current_user.id
        
        if not is_authorized and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        result = await db.bookings.update_one(
            {"id": booking_id},
            {"$set": {"status": "completed"}}
        )
        
        if result.modified_count:
            return {"message": "Booking marked as completed"}
        raise HTTPException(status_code=400, detail="Failed to complete booking")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing booking: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete booking")

@api_router.put("/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Cancel a booking"""
    try:
        booking = await db.bookings.find_one({"id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Check if user is client or owner/provider
        is_client = booking["client_id"] == current_user.id
        
        is_owner = False
        if booking.get('property_id'):
            prop = await db.properties.find_one({"id": booking['property_id']})
            is_owner = prop and prop["owner_id"] == current_user.id
        elif booking.get('service_id'):
            service = await db.professional_services.find_one({"id": booking['service_id']})
            is_owner = service and service["provider_id"] == current_user.id
        
        if not is_client and not is_owner and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        result = await db.bookings.update_one(
            {"id": booking_id},
            {
                "$set": {
                    "status": "cancelled",
                    "cancellation_reason": reason or "Cancelled by user"
                }
            }
        )
        
        if result.modified_count:
            return {"message": "Booking cancelled successfully"}
        raise HTTPException(status_code=400, detail="Failed to cancel booking")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling booking: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel booking")

@api_router.get("/bookings/property/{property_id}/slots")
async def get_available_slots(property_id: str, date: str):
    """Get available time slots for a property on a specific date"""
    try:
        # Parse date
        try:
            target_date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
        except:
            raise HTTPException(status_code=400, detail="Invalid date format")
        
        # Get all bookings for this property on this date
        start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        bookings = await db.bookings.find({
            "property_id": property_id,
            "scheduled_date": {"$gte": start_of_day, "$lte": end_of_day},
            "status": {"$in": ["pending", "confirmed"]}
        }).to_list(length=None)
        
        # Generate time slots (9 AM to 6 PM)
        booked_times = [b.get("scheduled_time") for b in bookings if b.get("scheduled_time")]
        
        all_slots = []
        for hour in range(9, 18):
            time_str = f"{hour:02d}:00"
            all_slots.append({
                "time": time_str,
                "available": time_str not in booked_times
            })
        
        return {"date": date, "slots": all_slots}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching available slots: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch available slots")

# Include router
app.include_router(api_router)

# CORS middleware - Production Configuration
# Support multiple domains for preview and production
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Local development
    "https://property-platform-12.preview.emergentagent.com",  # Preview
    "https://habitere.com",  # Production
    "https://www.habitere.com"  # Production with www
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()