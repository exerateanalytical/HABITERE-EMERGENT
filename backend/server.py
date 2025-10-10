from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Habitere API", description="Real Estate and Home Services Platform for Cameroon")
api_router = APIRouter(prefix="/api")

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
    picture: Optional[str] = None
    role: str
    phone: Optional[str] = None
    location: Optional[str] = None
    company_name: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool = False
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
    property_type: str  # house, apartment, land, commercial
    listing_type: str  # rent, sale, lease
    bedrooms: Optional[int] = 0
    bathrooms: Optional[int] = 0
    area_sqm: Optional[float] = None
    images: List[str] = []
    amenities: List[str] = []
    available: bool = True
    verified: bool = False
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Booking(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    property_id: Optional[str] = None
    service_id: Optional[str] = None
    scheduled_date: datetime
    status: str = "pending"  # pending, confirmed, completed, cancelled
    notes: Optional[str] = None
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

# Request Models
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
    property_type: str
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

# Authentication Routes
@api_router.get("/auth/session-data")
async def get_session_data(request: Request):
    """Get session data from emergent auth"""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=400, detail="Invalid session ID")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session validation error: {str(e)}")

@api_router.post("/auth/complete")
async def complete_authentication(
    request: Request,
    response: Response,
    user_data: dict,
    role: str
):
    """Complete authentication and create/update user"""
    if role not in USER_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data["email"]})
    
    if existing_user:
        user = User(**existing_user)
    else:
        # Create new user
        user_doc = {
            "id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "role": role,
            "created_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(user_doc)
        user = User(**user_doc)
    
    # Create session
    session_token = user_data["session_token"]
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    session_doc = {
        "user_id": user.id,
        "session_token": session_token,
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc)
    }
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=7 * 24 * 60 * 60,  # 7 days
        httponly=True,
        secure=True,
        samesite="none",
        path="/"
    )
    
    return {"user": serialize_doc(user.model_dump()), "message": "Authentication complete"}

@api_router.get("/auth/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return serialize_doc(current_user.model_dump())

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
        secure=True,
        samesite="none"
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
@api_router.post("/payments/mtn-momo", response_model=Dict[str, Any])
async def create_mtn_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user)
):
    """Create MTN MoMo payment"""
    if payment_data.method != "mtn_momo":
        raise HTTPException(status_code=400, detail="Invalid payment method")
    
    if not payment_data.phone_number:
        raise HTTPException(status_code=400, detail="Phone number required for MTN MoMo")
    
    # Create payment record
    payment_doc = payment_data.model_dump()
    payment_doc["id"] = str(uuid.uuid4())
    payment_doc["user_id"] = current_user.id
    payment_doc["reference_id"] = str(uuid.uuid4())
    payment_doc["created_at"] = datetime.now(timezone.utc)
    
    await db.payments.insert_one(payment_doc)
    
    # Request payment from MTN MoMo
    try:
        mtn_response = await mtn_client.request_to_pay(
            amount=payment_data.amount,
            phone_number=payment_data.phone_number,
            external_id=payment_doc["id"]
        )
        
        # Update payment with MTN reference
        await db.payments.update_one(
            {"id": payment_doc["id"]},
            {"$set": {"transaction_id": mtn_response["reference_id"]}}
        )
        
        return {
            "payment_id": payment_doc["id"],
            "reference_id": mtn_response["reference_id"],
            "status": "pending",
            "message": "Payment request sent. Please approve on your phone."
        }
        
    except Exception as e:
        await db.payments.update_one(
            {"id": payment_doc["id"]},
            {"$set": {"status": "failed"}}
        )
        raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")

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
    
    # Check if services already exist
    existing_services = await db.services.count_documents({})
    if existing_services == 0:
        await db.services.insert_many(sample_services)
        logger.info(f"Inserted {len(sample_services)} sample services")

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

# Include router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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