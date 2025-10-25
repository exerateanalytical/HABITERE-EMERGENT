"""
Subscription & Payment Routes Module
=====================================
Handles subscription plans, payments, and commission tracking
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import logging

from database import get_database
from utils.auth import get_current_user

router = APIRouter(prefix="/subscriptions")
logger = logging.getLogger(__name__)

# Pydantic Models
class SubscriptionPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    user_role: str  # real_estate_agent, plumber, etc.
    price: float  # in FCFA
    billing_cycle: str  # "yearly" or "per_booking"
    commission_rate: Optional[float] = None  # For hotels (5%)
    features: List[str]
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plan_id: str
    status: str  # active, expired, cancelled, pending
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool = False
    payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subscription_id: Optional[str] = None
    amount: float
    currency: str = "FCFA"
    payment_method: str  # mtn_momo, orange_money, bank_transfer
    payment_status: str  # pending, completed, failed, refunded
    transaction_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Commission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str
    hotel_user_id: str
    booking_amount: float
    commission_rate: float  # 5%
    commission_amount: float
    status: str  # pending, paid
    invoice_sent: bool = False
    paid_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SubscribeRequest(BaseModel):
    plan_id: str
    payment_method: str  # mtn_momo, orange_money, bank_transfer
    phone_number: Optional[str] = None

class RenewSubscriptionRequest(BaseModel):
    subscription_id: str
    payment_method: str
    phone_number: Optional[str] = None

class CalculateCommissionRequest(BaseModel):
    booking_id: str
    booking_amount: float


# Initialize subscription plans
async def initialize_subscription_plans():
    """Initialize default subscription plans in database"""
    db = get_database()
    
    plans = [
        {
            "id": str(uuid.uuid4()),
            "name": "Real Estate Agent Plan",
            "user_role": "real_estate_agent",
            "price": 10000.0,
            "billing_cycle": "yearly",
            "features": [
                "Post unlimited properties",
                "Property management dashboard",
                "Priority listing in search results",
                "Customer support"
            ],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Service Professional Plan",
            "user_role": "service_professional",
            "price": 25000.0,
            "billing_cycle": "yearly",
            "features": [
                "Create service profile",
                "Accept service bookings",
                "Show in services directory",
                "Customer reviews & ratings",
                "Booking management"
            ],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Real Estate Company Plan",
            "user_role": "real_estate_company",
            "price": 100000.0,
            "billing_cycle": "yearly",
            "features": [
                "Multiple agent accounts",
                "Company branding on listings",
                "Advanced analytics dashboard",
                "Priority support",
                "Custom domain option"
            ],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Construction Company Plan",
            "user_role": "construction_company",
            "price": 100000.0,
            "billing_cycle": "yearly",
            "features": [
                "Project showcase",
                "Accept construction contracts",
                "Portfolio management",
                "Client testimonials",
                "Project tracking"
            ],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Building Materials Supplier Plan",
            "user_role": "building_material_supplier",
            "price": 100000.0,
            "billing_cycle": "yearly",
            "features": [
                "Product catalog",
                "Inventory management",
                "Order management system",
                "Bulk order handling",
                "Delivery tracking"
            ],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Furniture Shop Plan",
            "user_role": "furnishing_shop",
            "price": 100000.0,
            "billing_cycle": "yearly",
            "features": [
                "Product catalog",
                "Order management",
                "Delivery tracking",
                "Customer reviews",
                "Promotional campaigns"
            ],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Hotel & Guest House Plan",
            "user_role": "hotel",
            "price": 0.0,
            "billing_cycle": "per_booking",
            "commission_rate": 5.0,
            "features": [
                "5% commission per booking",
                "No annual fee",
                "Booking management",
                "Guest reviews",
                "Monthly commission invoice"
            ],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Check if plans already exist
    existing_plans = await db.subscription_plans.count_documents({})
    if existing_plans == 0:
        await db.subscription_plans.insert_many(plans)
        logger.info(f"Initialized {len(plans)} subscription plans")
    else:
        logger.info(f"Subscription plans already initialized ({existing_plans} plans exist)")


@router.get("/plans")
async def get_subscription_plans():
    """
    Get all active subscription plans
    """
    db = get_database()
    
    plans = await db.subscription_plans.find({"is_active": True}).to_list(length=None)
    
    # Remove MongoDB ObjectId for JSON serialization
    for plan in plans:
        if '_id' in plan:
            plan.pop('_id')
    
    return {
        "plans": plans,
        "total": len(plans)
    }


@router.get("/plans/{role}")
async def get_plan_by_role(role: str):
    """
    Get subscription plan for specific user role
    """
    db = get_database()
    
    plan = await db.subscription_plans.find_one({"user_role": role, "is_active": True})
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No subscription plan found for role: {role}"
        )
    
    # Remove MongoDB ObjectId for JSON serialization
    if '_id' in plan:
        plan.pop('_id')
    
    return plan


@router.post("/subscribe")
async def subscribe_to_plan(
    request: SubscribeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Subscribe user to a plan
    """
    db = get_database()
    
    # Get plan details
    plan = await db.subscription_plans.find_one({"id": request.plan_id})
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    # Check if user already has active subscription
    existing_sub = await db.user_subscriptions.find_one({
        "user_id": current_user["id"],
        "status": "active"
    })
    
    if existing_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active subscription"
        )
    
    # Create payment record
    payment_id = str(uuid.uuid4())
    payment_data = {
        "id": payment_id,
        "user_id": current_user["id"],
        "amount": plan["price"],
        "currency": "FCFA",
        "payment_method": request.payment_method,
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # For MVP, auto-complete payment (in production, integrate real payment gateway)
    if plan["billing_cycle"] == "yearly":
        payment_data["payment_status"] = "completed"
        payment_data["payment_date"] = datetime.now(timezone.utc).isoformat()
        payment_data["transaction_id"] = f"TXN-{str(uuid.uuid4())[:8]}"
    
    await db.payments.insert_one(payment_data)
    
    # Create subscription
    subscription_data = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "plan_id": request.plan_id,
        "status": "active" if payment_data["payment_status"] == "completed" else "pending",
        "start_date": datetime.now(timezone.utc).isoformat(),
        "end_date": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat() if plan["billing_cycle"] == "yearly" else None,
        "auto_renew": False,
        "payment_id": payment_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.user_subscriptions.insert_one(subscription_data)
    
    logger.info(f"User {current_user['email']} subscribed to {plan['name']}")
    
    return {
        "message": "Subscription created successfully",
        "subscription": subscription_data,
        "payment": payment_data
    }


@router.get("/my-subscription")
async def get_my_subscription(current_user: dict = Depends(get_current_user)):
    """
    Get current user's subscription
    """
    db = get_database()
    
    subscription = await db.user_subscriptions.find_one({"user_id": current_user["id"]})
    
    if not subscription:
        return {
            "has_subscription": False,
            "message": "No subscription found"
        }
    
    # Get plan details
    plan = await db.subscription_plans.find_one({"id": subscription["plan_id"]})
    
    # Check if expired
    if subscription.get("end_date"):
        end_date = datetime.fromisoformat(subscription["end_date"])
        if end_date < datetime.now(timezone.utc):
            subscription["status"] = "expired"
            await db.user_subscriptions.update_one(
                {"id": subscription["id"]},
                {"$set": {"status": "expired"}}
            )
    
    return {
        "has_subscription": True,
        "subscription": subscription,
        "plan": plan,
        "is_active": subscription["status"] == "active",
        "days_remaining": (datetime.fromisoformat(subscription["end_date"]) - datetime.now(timezone.utc)).days if subscription.get("end_date") else None
    }


@router.post("/renew")
async def renew_subscription(
    request: RenewSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Renew existing subscription
    """
    db = get_database()
    
    # Get subscription
    subscription = await db.user_subscriptions.find_one({
        "id": request.subscription_id,
        "user_id": current_user["id"]
    })
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Get plan
    plan = await db.subscription_plans.find_one({"id": subscription["plan_id"]})
    
    # Create payment
    payment_id = str(uuid.uuid4())
    payment_data = {
        "id": payment_id,
        "user_id": current_user["id"],
        "subscription_id": subscription["id"],
        "amount": plan["price"],
        "currency": "FCFA",
        "payment_method": request.payment_method,
        "payment_status": "completed",  # Auto-complete for MVP
        "payment_date": datetime.now(timezone.utc).isoformat(),
        "transaction_id": f"TXN-{str(uuid.uuid4())[:8]}",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.payments.insert_one(payment_data)
    
    # Extend subscription
    new_end_date = datetime.now(timezone.utc) + timedelta(days=365)
    
    await db.user_subscriptions.update_one(
        {"id": subscription["id"]},
        {
            "$set": {
                "status": "active",
                "end_date": new_end_date.isoformat(),
                "payment_id": payment_id
            }
        }
    )
    
    logger.info(f"User {current_user['email']} renewed subscription")
    
    return {
        "message": "Subscription renewed successfully",
        "new_end_date": new_end_date.isoformat(),
        "payment": payment_data
    }


@router.get("/payment-history")
async def get_payment_history(current_user: dict = Depends(get_current_user)):
    """
    Get user's payment history
    """
    db = get_database()
    
    payments = await db.payments.find({"user_id": current_user["id"]}).sort("created_at", -1).to_list(length=None)
    
    return {
        "payments": payments,
        "total": len(payments)
    }


@router.post("/calculate-commission")
async def calculate_commission(
    request: CalculateCommissionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculate commission for hotel booking
    """
    db = get_database()
    
    # Verify user is hotel
    if current_user.get("role") not in ["hotel", "property_owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hotels can calculate commissions"
        )
    
    # Get hotel plan
    plan = await db.subscription_plans.find_one({"user_role": "hotel"})
    commission_rate = plan.get("commission_rate", 5.0)
    
    commission_amount = (request.booking_amount * commission_rate) / 100
    
    # Store commission record
    commission_data = {
        "id": str(uuid.uuid4()),
        "booking_id": request.booking_id,
        "hotel_user_id": current_user["id"],
        "booking_amount": request.booking_amount,
        "commission_rate": commission_rate,
        "commission_amount": commission_amount,
        "status": "pending",
        "invoice_sent": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.commissions.insert_one(commission_data)
    
    return {
        "booking_amount": request.booking_amount,
        "commission_rate": commission_rate,
        "commission_amount": commission_amount,
        "net_amount": request.booking_amount - commission_amount
    }


@router.get("/commissions")
async def get_my_commissions(current_user: dict = Depends(get_current_user)):
    """
    Get hotel's commission records
    """
    db = get_database()
    
    commissions = await db.commissions.find({
        "hotel_user_id": current_user["id"]
    }).sort("created_at", -1).to_list(length=None)
    
    total_pending = sum(c["commission_amount"] for c in commissions if c["status"] == "pending")
    total_paid = sum(c["commission_amount"] for c in commissions if c["status"] == "paid")
    
    return {
        "commissions": commissions,
        "total_pending": total_pending,
        "total_paid": total_paid,
        "total_commissions": len(commissions)
    }


@router.get("/check-access")
async def check_subscription_access(current_user: dict = Depends(get_current_user)):
    """
    Check if user has active subscription and access to features
    """
    db = get_database()
    
    subscription = await db.user_subscriptions.find_one({
        "user_id": current_user["id"],
        "status": "active"
    })
    
    if not subscription:
        return {
            "has_access": False,
            "message": "No active subscription",
            "requires_subscription": True
        }
    
    # Check expiry
    if subscription.get("end_date"):
        end_date = datetime.fromisoformat(subscription["end_date"])
        if end_date < datetime.now(timezone.utc):
            return {
                "has_access": False,
                "message": "Subscription expired",
                "requires_renewal": True,
                "expired_date": subscription["end_date"]
            }
    
    return {
        "has_access": True,
        "subscription": subscription,
        "expires_at": subscription.get("end_date")
    }
