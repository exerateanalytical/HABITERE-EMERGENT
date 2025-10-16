# Habitere Platform - API Documentation

**Base URL:** `https://your-domain.com/api`  
**Authentication:** JWT Bearer Token (where required)

---

## 🔐 AUTHENTICATION ENDPOINTS

### Register User
```
POST /auth/register
Content-Type: application/json

Body:
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securePassword123"
}

Response: 201
{
  "message": "User registered successfully",
  "user_id": "uuid",
  "email_verification_required": true
}
```

### Login
```
POST /auth/login
Content-Type: application/json

Body:
{
  "email": "user@example.com",
  "password": "securePassword123"
}

Response: 200
{
  "user": { user_object },
  "session_token": "jwt_token",
  "expires_at": "timestamp"
}
```

### Get Current User
```
GET /auth/me
Authorization: Bearer {token}

Response: 200
{ user_object }
```

---

## 🏠 PROPERTY ENDPOINTS

### Get All Properties
```
GET /properties?skip=0&limit=20&listing_type=rent&location=Douala&min_price=50000&max_price=200000

Response: 200
{
  "properties": [{ property_objects }],
  "total": 123
}
```

### Get Property by ID
```
GET /properties/{property_id}

Response: 200
{ property_object }
```

### Create Property
```
POST /properties
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "title": "Modern 3BR Apartment",
  "description": "Beautiful apartment in Douala",
  "price": 150000,
  "currency": "XAF",
  "location": "Douala, Cameroon",
  "listing_type": "rent",
  "bedrooms": 3,
  "bathrooms": 2,
  "area_sqm": 120,
  "amenities": ["parking", "wifi", "security"],
  "images": ["url1", "url2"]
}

Response: 201
{ property_object }
```

### Update Property
```
PUT /properties/{property_id}
Authorization: Bearer {token}
Content-Type: application/json

Body: { fields_to_update }

Response: 200
{ updated_property }
```

### Delete Property
```
DELETE /properties/{property_id}
Authorization: Bearer {token}

Response: 200
{ "message": "Property deleted successfully" }
```

---

## 🔧 SERVICE ENDPOINTS

### Get All Services
```
GET /services?category=plumber&location=Douala

Response: 200
{
  "services": [{ service_objects }]
}
```

### Get Service by ID
```
GET /services/{service_id}

Response: 200
{ service_object }
```

### Create Service
```
POST /services
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "category": "plumber",
  "title": "Professional Plumbing Services",
  "description": "Expert plumber with 10 years experience",
  "price_range": "15,000 - 50,000 XAF",
  "location": "Douala",
  "images": ["url1"]
}

Response: 201
{ service_object }
```

---

## ⭐ REVIEW ENDPOINTS

### Create Review
```
POST /reviews
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "property_id": "uuid",  // OR "service_id": "uuid"
  "rating": 5,
  "comment": "Excellent property!"
}

Response: 201
{
  "message": "Review created successfully",
  "review": { review_object }
}
```

### Get Property Reviews
```
GET /reviews/property/{property_id}?skip=0&limit=20

Response: 200
{
  "reviews": [{ review_objects }],
  "total": 45
}
```

### Get Service Reviews
```
GET /reviews/service/{service_id}

Response: 200
{ reviews }
```

### Update Review
```
PUT /reviews/{review_id}
Authorization: Bearer {token}

Body:
{
  "rating": 4,
  "comment": "Updated review"
}

Response: 200
{ updated_review }
```

### Delete Review
```
DELETE /reviews/{review_id}
Authorization: Bearer {token}

Response: 200
{ "message": "Review deleted successfully" }
```

---

## 💬 MESSAGE ENDPOINTS

### Send Message
```
POST /messages
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "receiver_id": "user_uuid",
  "content": "Hello, is this property still available?"
}

Response: 201
{
  "message": "Message sent successfully",
  "data": { message_object }
}
```

### Get Conversations
```
GET /messages/conversations
Authorization: Bearer {token}

Response: 200
{
  "conversations": [
    {
      "user_id": "uuid",
      "user_name": "John Doe",
      "last_message": "Yes, it's available",
      "unread_count": 3
    }
  ]
}
```

### Get Message Thread
```
GET /messages/thread/{other_user_id}
Authorization: Bearer {token}

Response: 200
{
  "messages": [{ message_objects }],
  "other_user": { user_object }
}
```

### Get Unread Count
```
GET /messages/unread-count
Authorization: Bearer {token}

Response: 200
{ "unread_count": 5 }
```

---

## 📅 BOOKING ENDPOINTS

### Create Booking
```
POST /bookings
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "booking_type": "property_viewing",
  "property_id": "uuid",
  "scheduled_date": "2024-11-01T00:00:00Z",
  "scheduled_time": "10:00",
  "duration_hours": 1,
  "notes": "Looking forward to viewing"
}

Response: 201
{
  "message": "Booking created successfully",
  "booking": { booking_object }
}
```

### Get User Bookings
```
GET /bookings?status=pending
Authorization: Bearer {token}

Response: 200
{ "bookings": [{ booking_objects }] }
```

### Get Received Bookings (for owners/providers)
```
GET /bookings/received?status=pending
Authorization: Bearer {token}

Response: 200
{ "bookings": [{ booking_objects }] }
```

### Confirm Booking
```
PUT /bookings/{booking_id}/confirm
Authorization: Bearer {token}

Response: 200
{ "message": "Booking confirmed successfully" }
```

### Cancel Booking
```
PUT /bookings/{booking_id}/cancel?reason=Schedule%20conflict
Authorization: Bearer {token}

Response: 200
{ "message": "Booking cancelled successfully" }
```

### Get Available Time Slots
```
GET /bookings/property/{property_id}/slots?date=2024-11-01

Response: 200
{
  "date": "2024-11-01",
  "slots": [
    { "time": "09:00", "available": true },
    { "time": "10:00", "available": false },
    ...
  ]
}
```

---

## 👤 ADMIN ENDPOINTS

**Note:** All admin endpoints require admin role

### Get Admin Statistics
```
GET /admin/stats
Authorization: Bearer {admin_token}

Response: 200
{
  "users": { total, pending, approved },
  "properties": { total, pending, verified },
  "bookings": { total, pending },
  "revenue": { total, currency }
}
```

### Get All Users
```
GET /admin/users?role=property_owner&verification_status=pending
Authorization: Bearer {admin_token}

Response: 200
{
  "users": [{ user_objects }],
  "total": 150
}
```

### Approve User
```
PUT /admin/users/{user_id}/approve
Authorization: Bearer {admin_token}

Response: 200
{ "message": "User approved successfully" }
```

### Reject User
```
PUT /admin/users/{user_id}/reject?reason=Incomplete%20profile
Authorization: Bearer {admin_token}

Response: 200
{ "message": "User rejected" }
```

### Verify Property
```
PUT /admin/properties/{property_id}/verify
Authorization: Bearer {admin_token}

Response: 200
{ "message": "Property verified successfully" }
```

---

## 📊 DATA MODELS

### User Object
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "property_owner",
  "email_verified": true,
  "verification_status": "approved",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Property Object
```json
{
  "id": "uuid",
  "owner_id": "user_uuid",
  "title": "Modern 3BR Apartment",
  "description": "Beautiful...",
  "price": 150000,
  "currency": "XAF",
  "location": "Douala",
  "listing_type": "rent",
  "bedrooms": 3,
  "bathrooms": 2,
  "area_sqm": 120,
  "images": ["url1", "url2"],
  "amenities": ["parking", "wifi"],
  "average_rating": 4.5,
  "review_count": 10,
  "verified": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Review Object
```json
{
  "id": "uuid",
  "reviewer_id": "user_uuid",
  "property_id": "property_uuid",
  "rating": 5,
  "comment": "Excellent!",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Booking Object
```json
{
  "id": "uuid",
  "client_id": "user_uuid",
  "property_id": "property_uuid",
  "booking_type": "property_viewing",
  "scheduled_date": "2024-11-01T00:00:00Z",
  "scheduled_time": "10:00",
  "status": "pending",
  "notes": "Looking forward...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 🚨 ERROR RESPONSES

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 📝 NOTES

- All timestamps are in UTC ISO 8601 format
- Pagination uses `skip` and `limit` parameters
- Authentication uses JWT Bearer tokens
- File uploads use multipart/form-data
- All list endpoints return total count
- Review ratings are 1-5 stars

---

*API Version: 1.0.0*
*Last Updated: October 2024*
