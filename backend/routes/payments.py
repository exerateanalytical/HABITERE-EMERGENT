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

MTN MoMo Integration:
- Sandbox environment support
- OAuth token management with auto-refresh
- Request-to-pay API
- Payment status tracking
- Webhook callbacks for real-time updates

Payment Flow:
1. Client initiates payment request
2. System sends request to MTN MoMo API
3. Customer receives mobile prompt
4. Customer approves/rejects on phone
5. System receives webhook callback
6. Payment status updated in database

Dependencies:
- FastAPI for routing
- MongoDB for payment storage
- requests for external API calls
- Environment variables for MTN MoMo credentials

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

# Import from parent modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_database
from utils import get_current_user, serialize_doc

# Setup logging
logger = logging.getLogger(__name__)

# Create router for payment endpoints
# All routes will be prefixed with /api
router = APIRouter(tags=["Payments"])


# ==================== MTN MOMO CONFIGURATION ====================

class MTNMoMoConfig:
    """
    MTN Mobile Money API configuration.
    
    Loads credentials and settings from environment variables.
    Supports both sandbox and production environments.
    """
    def __init__(self):
        self.api_user_id = os.getenv('MTN_MOMO_API_USER_ID', '')
        self.api_key = os.getenv('MTN_MOMO_API_KEY', '')
        self.subscription_key = os.getenv('MTN_MOMO_SUBSCRIPTION_KEY', '')
        self.target_environment = os.getenv('MTN_MOMO_TARGET_ENVIRONMENT', 'sandbox')
        self.base_url = os.getenv('MTN_MOMO_BASE_URL', 'https://sandbox.momodeveloper.mtn.com')
        self.callback_url = os.getenv('MTN_MOMO_CALLBACK_URL', '')


# Global config instance
mtn_config = MTNMoMoConfig()


class MTNMoMoTokenManager:
    """
    Manages OAuth access tokens for MTN MoMo API.
    
    Features:
    - Automatic token refresh when expired
    - Token caching with expiry tracking
    - Error handling and logging
    """
    def __init__(self):
        self.access_token = None
        self.token_expires_at = None
    
    async def get_access_token(self) -> str:
        """
        Get valid access token, refresh if needed.
        
        Returns cached token if still valid, otherwise requests new token.
        Tokens expire after 1 hour, but refreshed 1 minute early for safety.
        
        Returns:
            str: Valid access token, or None if request fails
        """
        # Return cached token if still valid
        if self.access_token and self.token_expires_at:
            if datetime.now(timezone.utc) < self.token_expires_at:
                return self.access_token
        
        # Request new token from MTN MoMo API
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
                expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
                
                # Set expiry with 1 minute buffer
                self.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)
                
                logger.info("MTN MoMo access token refreshed successfully")
                return self.access_token
            else:
                logger.error(f"MTN MoMo token request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"MTN MoMo token request error: {e}")
            return None


# Global token manager instance
token_manager = MTNMoMoTokenManager()


# ==================== PYDANTIC MODELS ====================

class PaymentRequest(BaseModel):
    """
    Payment request model for MTN MoMo.
    
    Currency notes:
    - EUR for sandbox testing
    - XAF for production (Cameroon)
    """
    amount: str
    currency: str = "EUR"  # EUR for sandbox, XAF for production
    external_id: str  # Your internal transaction ID
    payer_message: str  # Message shown to payer
    payee_note: str  # Internal note for payee
    phone: str  # Phone number in format: 237XXXXXXXXX


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
    """
    Process MTN Mobile Money payment using sandbox/production API.
    
    Flow:
    1. Get valid OAuth access token
    2. Generate unique reference ID
    3. Send request-to-pay to MTN MoMo API
    4. Store payment record in database
    5. Customer receives mobile prompt
    6. Return reference ID for status tracking
    
    Args:
        payment_request: Payment details (amount, phone, messages)
        user: Authenticated user
        
    Returns:
        Payment response with reference ID for tracking
        
    Raises:
        HTTPException: 500 if authentication fails
        HTTPException: 400 if payment request fails
        
    Example:
        POST /api/payments/mtn-momo
        {
            amount: 100,
            currency: EUR,
            external_id: booking_123,
            payer_message: Payment for property viewing,
            payee_note: Property booking payment,
            phone: 237650000000
        }
    """
    db = get_database()
    
    try:
        # Get access token
        access_token = await token_manager.get_access_token()
        if not access_token:
            logger.error("Failed to get MTN MoMo access token")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to authenticate with MTN MoMo API"
            )
        
        # Generate unique reference ID for this transaction
        reference_id = str(uuid.uuid4())
        
        # Prepare request payload
        payload = {
            amount: payment_request.amount,
            currency: payment_request.currency,
            externalId: payment_request.external_id,
            payer: {
                partyIdType: MSISDN,
                partyId: payment_request.phone
            },
            payerMessage: payment_request.payer_message,
            payeeNote: payment_request.payee_note
        }
        
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Reference-Id': reference_id,
            'X-Target-Environment': mtn_config.target_environment,
            'Ocp-Apim-Subscription-Key': mtn_config.subscription_key,
            'Content-Type': 'application/json'
        }
        
        # Add callback URL if configured
        if mtn_config.callback_url:
            headers['X-Callback-Url'] = mtn_config.callback_url
        
        # Create payment record in database
        payment_data = {
            id: str(uuid.uuid4()),
            user_id: user.get(id),
            amount: float(payment_request.amount),
            currency: payment_request.currency,
            method: mtn_momo,
            status: pending,
            reference_id: reference_id,
            external_id: payment_request.external_id,
            phone: payment_request.phone,
            created_at: datetime.now(timezone.utc).isoformat()
        }
        
        # Send request to MTN MoMo API
        response = requests.post(
            f{mtn_config.base_url}/collection/v1_0/requesttopay,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 202:
            # Payment request accepted - customer will receive mobile prompt
            await db.payments.insert_one(payment_data)
            
            logger.info(fMTN MoMo payment request created: {reference_id} for user {user.get('email')})
            
            return PaymentResponse(
                success=True,
                payment_id=payment_data[id],
                reference_id=reference_id,
                status=pending,
                message=Payment request sent to customer's mobile phone
            )
        else:
            logger.error(fMTN MoMo payment request failed: {response.status_code} - {response.text})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=fPayment request failed: {response.text}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(fMTN MoMo payment error: {e})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Payment processing failed
        )


# ==================== CHECK PAYMENT STATUS ====================

@router.get(/payments/mtn-momo/status/{reference_id})
async def check_mtn_momo_payment_status(
    reference_id: str,
    user: dict = Depends(get_current_user)
):
    
    Check MTN Mobile Money payment status.
    
    Queries MTN MoMo API for current payment status and updates local record.
    
    Possible statuses:
    - pending: Payment request sent, awaiting customer action
    - successful: Payment completed successfully
    - failed: Payment failed or rejected
    
    Args:
        reference_id: MTN MoMo reference ID from payment request
        user: Authenticated user
        
    Returns:
        Payment status with transaction details
        
    Raises:
        HTTPException: 500 if authentication fails
        HTTPException: 400 if status check fails
        
    Example:
        GET /api/payments/mtn-momo/status/123e4567-e89b-12d3-a456-426614174000
    
    db = get_database()
    
    try:
        # Get access token
        access_token = await token_manager.get_access_token()
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=Failed to authenticate with MTN MoMo API
            )
        
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Target-Environment': mtn_config.target_environment,
            'Ocp-Apim-Subscription-Key': mtn_config.subscription_key
        }
        
        # Check status with MTN MoMo API
        response = requests.get(
            f{mtn_config.base_url}/collection/v1_0/requesttopay/{reference_id},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            status_data = response.json()
            
            # Update local payment record
            await db.payments.update_one(
                {reference_id: reference_id},
                {
                    $set: {
                        status: status_data[status].lower(),
                        transaction_id: status_data.get(financialTransactionId),
                        updated_at: datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            logger.info(fMTN MoMo payment status checked: {reference_id} - {status_data['status']})
            
            return {
                success: True,
                reference_id: reference_id,
                status: status_data[status].lower(),
                amount: status_data.get(amount),
                currency: status_data.get(currency),
                financial_transaction_id: status_data.get(financialTransactionId),
                reason: status_data.get(reason)
            }
        else:
            logger.error(fMTN MoMo status check failed: {response.status_code} - {response.text})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=fStatus check failed: {response.text}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(fMTN MoMo status check error: {e})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Status check failed
        )


# ==================== PAYMENT WEBHOOK ====================

@router.post(/payments/mtn-momo/callback)
async def mtn_momo_callback(request: Request):
    
    Handle MTN Mobile Money callback notifications.
    
    MTN MoMo sends webhook callbacks when payment status changes.
    This endpoint processes those callbacks and updates payment records.
    
    Note: This endpoint should be configured in MTN MoMo dashboard
    or sent in X-Callback-Url header with each request.
    
    Args:
        request: FastAPI request with callback data
        
    Returns:
        Success/failure response
        
    Example callback payload:
        {
            referenceId: 123e4567-e89b-12d3-a456-426614174000,
            status: SUCCESSFUL,
            financialTransactionId: 123456789,
            amount: 100,
            currency: EUR
        }
    
    db = get_database()
    
    try:
        callback_data = await request.json()
        
        # Extract reference ID and status
        reference_id = callback_data.get(referenceId)
        status_value = callback_data.get(status, ).lower()
        
        if not reference_id:
            logger.warning(MTN MoMo callback missing reference ID)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Missing reference ID in callback
            )
        
        # Prepare update data
        update_data = {
            status: status_value,
            updated_at: datetime.now(timezone.utc).isoformat()
        }
        
        if callback_data.get(financialTransactionId):
            update_data[transaction_id] = callback_data[financialTransactionId]
        
        if callback_data.get(reason):
            update_data[failure_reason] = callback_data[reason]
        
        # Update payment record
        result = await db.payments.update_one(
            {reference_id: reference_id},
            {$set: update_data}
        )
        
        if result.matched_count > 0:
            logger.info(fMTN MoMo callback processed for reference {reference_id}: {status_value})
            return {success: True, message: Callback processed}
        else:
            logger.warning(fNo payment found for reference ID: {reference_id})
            return {success: False, message: Payment not found}
            
    except Exception as e:
        logger.error(fMTN MoMo callback error: {e})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=Callback processing failed
        )


# ==================== GENERAL PAYMENT STATUS ====================

@router.get(/payments/{payment_id}/status)
async def get_payment_status(
    payment_id: str,
    current_user: dict = Depends(get_current_user)
):
    
    Get payment status by payment ID.
    
    Returns local payment record from database.
    Users can only view their own payments.
    
    Args:
        payment_id: Internal payment ID (not MTN reference ID)
        current_user: Authenticated user
        
    Returns:
        Payment status and details
        
    Raises:
        HTTPException: 404 if payment not found
        
    Example:
        GET /api/payments/123e4567-e89b-12d3-a456-426614174000/status
    
    db = get_database()
    
    # Find payment record
    payment_doc = await db.payments.find_one({
        id: payment_id,
        user_id: current_user.get(id)
    })
    
    if not payment_doc:
        logger.warning(fPayment not found: {payment_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Payment not found
        )
    
    logger.info(fPayment status retrieved: {payment_id} for user {current_user.get('email')})
    
    return serialize_doc(payment_doc)
