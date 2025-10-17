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

# Import route modules
from routes import auth, properties, services, users, bookings, messages, reviews, core, images, payments, admin

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

# ==================== REGISTER ROUTE MODULES ====================
# Register all modular route handlers
# Each module is a separate file in /routes with focused functionality

# Core utilities (health checks, root endpoint)
app.include_router(core.router, prefix="/api", tags=["Core"])

# Authentication & user management
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(users.router, prefix="/api", tags=["Users"])

# Properties & services
app.include_router(properties.router, prefix="/api", tags=["Properties"])
app.include_router(services.router, prefix="/api", tags=["Services"])

# Bookings & messaging
app.include_router(bookings.router, prefix="/api", tags=["Bookings"])
app.include_router(messages.router, prefix="/api", tags=["Messages"])

# Reviews & ratings
app.include_router(reviews.router, prefix="/api", tags=["Reviews"])

# Image upload & management
app.include_router(images.router, prefix="/api", tags=["Images"])

# Payment processing
app.include_router(payments.router, prefix="/api", tags=["Payments"])

# Admin dashboard and moderation
app.include_router(admin.router, prefix="/api", tags=["Admin"])

# Legacy api_router (for any remaining routes not yet extracted)
app.include_router(api_router)

# CORS middleware - DISABLED
# Kubernetes ingress handles CORS headers to prevent duplication
# Previously caused: "The 'Access-Control-Allow-Origin' header contains multiple values" error
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["*"]
# )

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



# Auto-cleanup function for old properties
async def cleanup_old_properties():
    """Delete properties older than 1 hour"""
    try:
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        result = await db.properties.delete_many({
            "created_at": {"$lt": one_hour_ago}
        })
        if result.deleted_count > 0:
            logger.info(f"Deleted {result.deleted_count} properties older than 1 hour")
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error during property cleanup: {e}")
        return 0

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Application starting up...")
    
    # Run initial cleanup
    deleted = await cleanup_old_properties()
    logger.info(f"Initial cleanup: {deleted} old properties removed")
    logger.info("Property auto-cleanup active (properties older than 1 hour will be removed)")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()