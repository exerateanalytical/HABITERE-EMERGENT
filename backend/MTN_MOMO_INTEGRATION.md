# MTN Mobile Money Integration Guide

## Overview

This document describes the MTN Mobile Money integration for the Habitere platform. The integration allows users to make payments using MTN Mobile Money services in Cameroon.

## Features

- **Real MTN MoMo API Integration**: Uses the official MTN Mobile Money API
- **Token Management**: Automatic access token management with refresh
- **Payment Processing**: Request payments from customers' mobile phones
- **Status Checking**: Real-time payment status verification
- **Callback Support**: Handle payment notifications from MTN
- **Sandbox & Production**: Support for both sandbox testing and production

## API Endpoints

### 1. Process Payment
```
POST /api/payments/mtn-momo
```

**Request Body:**
```json
{
  "amount": "1000",
  "currency": "EUR",
  "external_id": "booking_123",
  "payer_message": "Payment for Habitere booking",
  "payee_note": "Habitere payment",
  "phone": "237670000000"
}
```

**Response:**
```json
{
  "success": true,
  "payment_id": "uuid-payment-id",
  "reference_id": "uuid-reference-id",
  "status": "pending",
  "message": "Payment request sent to customer's mobile phone"
}
```

### 2. Check Payment Status
```
GET /api/payments/mtn-momo/status/{reference_id}
```

**Response:**
```json
{
  "success": true,
  "reference_id": "uuid-reference-id",
  "status": "successful",
  "amount": "1000",
  "currency": "EUR",
  "financial_transaction_id": "mtn-transaction-id",
  "reason": null
}
```

### 3. Payment Callback (Webhook)
```
POST /api/payments/mtn-momo/callback
```

This endpoint receives notifications from MTN when payment status changes.

## Setup Instructions

### 1. MTN Developer Account Setup

1. Visit [MTN MoMo Developer Portal](https://momodeveloper.mtn.com/)
2. Create an account and verify your email
3. Create a new application
4. Subscribe to the Collections API
5. Generate API credentials

### 2. Environment Configuration

Add the following variables to your `.env` file:

```env
# MTN Mobile Money Configuration
MTN_MOMO_API_USER_ID="your-api-user-id"
MTN_MOMO_API_KEY="your-api-key"
MTN_MOMO_SUBSCRIPTION_KEY="your-subscription-key"
MTN_MOMO_TARGET_ENVIRONMENT="sandbox"
MTN_MOMO_BASE_URL="https://sandbox.momodeveloper.mtn.com"
MTN_MOMO_CALLBACK_URL="https://your-domain.com/api/payments/mtn-momo/callback"
```

### 3. Production Configuration

For production deployment:

```env
MTN_MOMO_TARGET_ENVIRONMENT="mtncameroon"
MTN_MOMO_BASE_URL="https://momodeveloper.mtn.com"
```

## Currency Configuration

- **Sandbox**: Use `EUR` for testing
- **Production**: Use `XAF` (Central African CFA Franc)

## Phone Number Format

Phone numbers should be in international format without the `+` sign:
- Example: `237670000000` (for Cameroon)

## Payment Flow

1. **Initiate Payment**: Client sends payment request to `/api/payments/mtn-momo`
2. **API Request**: Server sends request to MTN MoMo API
3. **Customer Notification**: MTN sends USSD prompt to customer's phone
4. **Customer Approval**: Customer approves/rejects payment on their phone
5. **Status Update**: Server can check status via `/api/payments/mtn-momo/status/{reference_id}`
6. **Callback (Optional)**: MTN sends callback notification to your webhook

## Error Handling

The integration includes comprehensive error handling:

- **Authentication Errors**: Invalid API credentials
- **Request Errors**: Invalid payment parameters
- **Network Errors**: Connection timeouts or failures
- **Business Errors**: Insufficient funds, invalid phone numbers

## Security Considerations

1. **API Keys**: Store API credentials securely in environment variables
2. **HTTPS**: Always use HTTPS for production deployments
3. **Callback Validation**: Validate callback requests from MTN
4. **Rate Limiting**: Implement rate limiting for payment endpoints

## Testing

### Sandbox Testing

1. Use the provided test credentials from MTN Developer Portal
2. Use `EUR` as currency for sandbox
3. Use test phone numbers provided by MTN

### Test Script

Run the test script to verify configuration:

```bash
cd /app/backend
python test_mtn_momo.py
```

## Monitoring and Logging

The integration includes comprehensive logging:

- Token refresh events
- Payment request/response logs
- Error tracking
- Callback processing logs

Monitor these logs for troubleshooting and performance optimization.

## Support

For technical issues:
1. Check MTN MoMo Developer Documentation
2. Review server logs for error details
3. Contact MTN Developer Support for API-related issues

## API Reference

- [MTN MoMo Collections API](https://momodeveloper.mtn.com/docs/services/collection/)
- [MTN MoMo Developer Portal](https://momodeveloper.mtn.com/)