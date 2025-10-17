"""
Payments Routes Module
=======================
Handles payment processing API endpoints for Habitere platform.

This module provides:
- MTN Mobile Money (MTN MoMo) payment integration
- Payment request processing
- Payment status checking
- Webhook callback handling
- Token management for MTN MoMo API

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import uuid
import logging
import os
import requests

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_database
from utils import get_current_user, serialize_doc

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Payments"])


# ==================== MTN MOMO CONFIGURATION ====================

class MTNMoMoConfig:
    """MTN Mobile Money API configuration."""
    def __init__(self):
        self.api_user_id = os.getenv('MTN_MOMO_API_USER_ID', '')
        self.api_key = os.getenv('MTN_MOMO_API_KEY', '')
        self.subscription_key = os.getenv('MTN_MOMO_SUBSCRIPTION_KEY', '')
        self.target_environment = os.getenv('MTN_MOMO_TARGET_ENVIRONMENT', 'sandbox')
        self.base_url = os.getenv('MTN_MOMO_BASE_URL', 'https://sandbox.momodeveloper.mtn.com')
        self.callback_url = os.getenv('MTN_MOMO_CALLBACK_URL', '')

mtn_config = MTNMoMoConfig()


class MTNMoMoTokenManager:
    """Manages OAuth access tokens for MTN MoMo API."""
    def __init__(self):
        self.access_token = None
        self.token_expires_at = None
    
    async def get_access_token(self) -> str:
        """Get valid access token, refresh if needed."""
        if self.access_token and self.token_expires_at:
            if datetime.now(timezone.utc) < self.token_expires_at:
                return self.access_token
        
        auth = (mtn_config.api_user_id, mtn_config.api_key)
        headers = {
            'Ocp-Apim-Subscription-Key': mtn_config.subscription_key,
            'X-Target-Environment': mtn_config.target_environment
        }
        
        try:
            response = requests.post(
                f"{mtn_config.base_url}/collection/token/",
                auth=auth,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)
                logger.info("MTN MoMo access token refreshed successfully")
                return self.access_token
            else:
                logger.error(f"MTN MoMo token request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"MTN MoMo token request error: {e}")
            return None

token_manager = MTNMoMoTokenManager()


# ==================== PYDANTIC MODELS ====================

class PaymentRequest(BaseModel):
    """Payment request model for MTN MoMo."""
    amount: str
    currency: str = "EUR"
    external_id: str
    payer_message: str
    payee_note: str
    phone: str


class PaymentResponse(BaseModel):
    """Payment response model."""
    success: bool
    payment_id: str
    reference_id: str
    status: str
    message: str


# ==================== PROCESS PAYMENT ====================

@router.post("/payments/mtn-momo", response_model=PaymentResponse)
async def process_mtn_momo_payment(
    payment_request: PaymentRequest,
    user: dict = Depends(get_current_user)
):
    """Process MTN Mobile Money payment."""
    db = get_database()
    
    try:
        access_token = await token_manager.get_access_token()
        if not access_token:
            logger.error("Failed to get MTN MoMo access token")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to authenticate with MTN MoMo API"
            )
        
        reference_id = str(uuid.uuid4())
        
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
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Reference-Id': reference_id,
            'X-Target-Environment': mtn_config.target_environment,
            'Ocp-Apim-Subscription-Key': mtn_config.subscription_key,
            'Content-Type': 'application/json'
        }
        
        if mtn_config.callback_url:
            headers['X-Callback-Url'] = mtn_config.callback_url
        
        payment_data = {
            "id": str(uuid.uuid4()),
            "user_id": user.get("id"),
            "amount": float(payment_request.amount),
            "currency": payment_request.currency,
            "method": "mtn_momo",
            "status": "pending",
            "reference_id": reference_id,
            "external_id": payment_request.external_id,
            "phone": payment_request.phone,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        response = requests.post(
            f"{mtn_config.base_url}/collection/v1_0/requesttopay",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 202:
            await db.payments.insert_one(payment_data)
            
            logger.info(f"MTN MoMo payment request created: {reference_id} for user {user.get('email')}")
            
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment request failed: {response.text}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MTN MoMo payment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment processing failed"
        )


# ==================== CHECK PAYMENT STATUS ====================

@router.get("/payments/mtn-momo/status/{reference_id}")
async def check_mtn_momo_payment_status(
    reference_id: str,
    user: dict = Depends(get_current_user)
):
    """Check MTN Mobile Money payment status."""
    db = get_database()
    
    try:
        access_token = await token_manager.get_access_token()
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to authenticate with MTN MoMo API"
            )
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Target-Environment': mtn_config.target_environment,
            'Ocp-Apim-Subscription-Key': mtn_config.subscription_key
        }
        
        response = requests.get(
            f"{mtn_config.base_url}/collection/v1_0/requesttopay/{reference_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            status_data = response.json()
            
            await db.payments.update_one(
                {"reference_id": reference_id},
                {
                    "$set": {
                        "status": status_data["status"].lower(),
                        "transaction_id": status_data.get("financialTransactionId"),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            logger.info(f"MTN MoMo payment status checked: {reference_id} - {status_data['status']}")
            
            return {
                "success": True,
                "reference_id": reference_id,
                "status": status_data["status"].lower(),
                "amount": status_data.get("amount"),
                "currency": status_data.get("currency"),
                "financial_transaction_id": status_data.get("financialTransactionId"),
                "reason": status_data.get("reason")
            }
        else:
            logger.error(f"MTN MoMo status check failed: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status check failed: {response.text}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MTN MoMo status check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Status check failed"
        )


# ==================== PAYMENT WEBHOOK ====================

@router.post("/payments/mtn-momo/callback")
async def mtn_momo_callback(request: Request):
    """Handle MTN Mobile Money callback notifications."""
    db = get_database()
    
    try:
        callback_data = await request.json()
        
        reference_id = callback_data.get("referenceId")
        status_value = callback_data.get("status", "").lower()
        
        if not reference_id:
            logger.warning("MTN MoMo callback missing reference ID")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing reference ID in callback"
            )
        
        update_data = {
            "status": status_value,
            "updated_at": datetime.now(timezone.utc).isoformat()
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
            logger.info(f"MTN MoMo callback processed for reference {reference_id}: {status_value}")
            return {"success": True, "message": "Callback processed"}
        else:
            logger.warning(f"No payment found for reference ID: {reference_id}")
            return {"success": False, "message": "Payment not found"}
            
    except Exception as e:
        logger.error(f"MTN MoMo callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Callback processing failed"
        )


# ==================== GENERAL PAYMENT STATUS ====================

@router.get("/payments/{payment_id}/status")
async def get_payment_status(
    payment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get payment status by payment ID."""
    db = get_database()
    
    payment_doc = await db.payments.find_one({
        "id": payment_id,
        "user_id": current_user.get("id")
    })
    
    if not payment_doc:
        logger.warning(f"Payment not found: {payment_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    logger.info(f"Payment status retrieved: {payment_id} for user {current_user.get('email')}")
    
    return serialize_doc(payment_doc)
