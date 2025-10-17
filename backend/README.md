# Habitere Backend - Developer Documentation

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Core Modules](#core-modules)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Authentication](#authentication)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Habitere is a Cameroonian real estate and home services platform built with:
- **Backend:** FastAPI (Python 3.11+)
- **Database:** MongoDB (Motor async driver)
- **Authentication:** JWT + Session cookies
- **Email:** SendGrid
- **Payments:** MTN Mobile Money

**Platform URL:** https://habitere.com  
**Admin Panel:** https://habitere.com/admin

---

## 🏗️ Architecture

### Feature-Module Architecture

The backend is organized by **features**, not layers. Each feature contains:
- Routes (API endpoints)
- Business logic
- Data validation
- Related utilities

```
Feature = Routes + Services + Models + Utils
```

**Benefits:**
- ✅ Easy to understand
- ✅ Features are self-contained
- ✅ Can work on features independently
- ✅ Clear responsibility boundaries

---

## 📁 Project Structure

```
/app/backend/
├── config.py                  # ⚙️ Configuration & environment variables
├── database.py                # 🗄️ MongoDB connection & helpers
├── server.py                  # 🚀 Main FastAPI application (REFACTORING IN PROGRESS)
├── requirements.txt           # 📦 Python dependencies
├── .env                       # 🔐 Environment variables (DO NOT COMMIT)
│
├── routes/                    # 🛣️ API endpoints organized by feature
│   ├── __init__.py
│   ├── auth.py               # Authentication endpoints
│   ├── properties.py         # Property CRUD
│   ├── services.py           # Service listings
│   ├── admin.py              # Admin panel endpoints
│   ├── bookings.py           # Booking management
│   ├── messages.py           # User messaging
│   └── uploads.py            # File upload handling
│
├── models/                    # 📝 Pydantic data models
│   ├── __init__.py
│   ├── user.py               # User model
│   ├── property.py           # Property model
│   ├── service.py            # Service model
│   └── booking.py            # Booking model
│
├── services/                  # 💼 Business logic layer
│   ├── __init__.py
│   ├── auth_service.py       # Authentication logic
│   ├── email_service.py      # Email sending (SendGrid)
│   ├── property_service.py   # Property business logic
│   └── storage_service.py    # File storage logic
│
├── middleware/                # 🔧 FastAPI middleware
│   ├── __init__.py
│   ├── auth.py               # Authentication middleware
│   └── error_handler.py      # Global error handling
│
└── utils/                     # 🛠️ Utility functions
    ├── __init__.py
    ├── helpers.py            # General helpers
    └── validators.py         # Data validation

uploads/                       # 📁 User uploaded files
├── properties/               # Property images
├── profile/                  # Profile pictures
└── thumbnails/               # Image thumbnails
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- MongoDB running on localhost:27017
- SendGrid API key (for emails)
- Google OAuth credentials (optional)

### Installation

```bash
cd /app/backend

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Run the server
python server.py
```

Server will start on: http://localhost:8001

### Environment Variables

**Required:**
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
SECRET_KEY=your-secret-key-here
SENDGRID_API_KEY=your-sendgrid-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret
```

**Optional:**
```bash
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=INFO
```

See `config.py` for all available settings.

---

## 🧩 Core Modules

### 1. config.py
**Purpose:** Centralized configuration management

**Key Features:**
- Environment variable loading
- Type-safe settings access
- Environment detection (dev/prod)
- External service configuration

**Usage:**
```python
from config import settings

# Access settings
print(settings.DB_NAME)
print(settings.FRONTEND_URL)

# Check environment
if settings.is_production():
    # Production logic
```

### 2. database.py
**Purpose:** MongoDB connection management

**Key Features:**
- Singleton database client
- Connection lifecycle management
- Collection name constants
- Document serialization helper

**Usage:**
```python
from database import get_database, serialize_doc

# Get database instance
db = get_database()

# Query data
user = await db.users.find_one({"email": "test@example.com"})

# Serialize for JSON response
return serialize_doc(user)
```

### 3. server.py (Main Application)
**Purpose:** FastAPI app initialization and route registration

**Current Status:** ⚠️ **REFACTORING IN PROGRESS**
- Currently: All code in one file (3,453 lines)
- Target: Split into feature modules
- Routes will be extracted to `routes/` directory

---

## 🛣️ API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Email/password login | No |
| GET | `/auth/me` | Get current user | Yes |
| POST | `/auth/logout` | Logout user | Yes |
| POST | `/auth/verify-email` | Verify email | No |
| POST | `/auth/forgot-password` | Request password reset | No |
| POST | `/auth/reset-password` | Reset password | No |
| GET | `/auth/google/login` | Google OAuth login | No |
| GET | `/auth/google/callback` | Google OAuth callback | No |

### Properties (`/api/properties`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/properties` | List all properties | No |
| GET | `/properties/{id}` | Get property details | No |
| POST | `/properties` | Create property | Yes (owner/agent) |
| PUT | `/properties/{id}` | Update property | Yes (owner/admin) |
| DELETE | `/properties/{id}` | Delete property | Yes (owner/admin) |

**Query Parameters:**
- `property_type`: apartment, house, land, commercial
- `listing_type`: rent, sale
- `location`: Search by location
- `min_price`, `max_price`: Price range
- `skip`, `limit`: Pagination

### Admin (`/api/admin`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/stats` | Dashboard statistics | Admin only |
| GET | `/admin/users` | List all users | Admin only |
| GET | `/admin/properties` | List all properties | Admin only |
| DELETE | `/admin/properties/cleanup/old` | Cleanup old properties | Admin only |

### File Upload (`/api/upload`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/upload/images` | Upload images | Yes |

### User Profile (`/api/users`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| PUT | `/users/profile` | Update profile | Yes |

---

## 🗄️ Database Schema

### Users Collection

```javascript
{
  "id": "uuid",                    // Primary key
  "email": "user@example.com",     // Unique
  "name": "John Doe",
  "password": "hashed_password",   // bcrypt hashed
  "role": "property_seeker",       // Role-based access
  "email_verified": true,
  "verification_token": "token",
  "phone": "+237...",
  "picture": "/uploads/profile/...",
  "created_at": "2025-10-17T..."
}
```

**Roles:**
- `property_seeker` - Looking for properties
- `property_owner` - Owns properties
- `real_estate_agent` - Real estate agent
- `real_estate_company` - Real estate company
- `admin` - Platform administrator

### Properties Collection

```javascript
{
  "id": "uuid",
  "title": "Modern Apartment",
  "description": "...",
  "price": 500000,
  "property_type": "apartment",    // apartment, house, land, commercial
  "listing_type": "rent",          // rent, sale
  "location": "Douala, Cameroon",
  "bedrooms": 3,
  "bathrooms": 2,
  "area": 120,
  "images": ["url1", "url2"],
  "owner_id": "user_uuid",
  "available": true,
  "created_at": "2025-10-17T..."
}
```

---

## 🔐 Authentication

### Session-Based Auth

**How it works:**
1. User logs in → Backend creates session
2. Session stored in HTTP-only cookie
3. Cookie sent with every request
4. Backend validates session for protected routes

**Cookie Settings:**
```python
# Development
secure=False, samesite='lax'

# Production  
secure=True, samesite='None'
```

### JWT Tokens

**Alternative auth method:**
- Token in `Authorization: Bearer <token>` header
- Used for API-only clients
- 7-day expiration

### Protected Routes

```python
from fastapi import Depends
from dependencies import get_current_user, get_admin_user

@app.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    # Only authenticated users
    return {"user": user}

@app.get("/admin")  
async def admin_route(admin = Depends(get_admin_user)):
    # Only admin users
    return {"admin": admin}
```

---

## 🔧 Common Tasks

### Add New API Endpoint

**1. Create route in routes/ (future):**
```python
# routes/properties.py
@router.get("/properties/featured")
async def get_featured_properties():
    """Get featured properties"""
    db = get_database()
    properties = await db.properties.find({"featured": True}).to_list(10)
    return [serialize_doc(p) for p in properties]
```

**2. Register route in server.py:**
```python
from routes import properties
app.include_router(properties.router)
```

### Add New Database Collection

**1. Add to Collections in database.py:**
```python
class Collections:
    USERS = "users"
    PROPERTIES = "properties"
    FAVORITES = "favorites"  # NEW
```

**2. Use in code:**
```python
db = get_database()
await db[Collections.FAVORITES].insert_one({...})
```

### Send Email

```python
from services.email_service import send_email

await send_email(
    to_email="user@example.com",
    subject="Welcome!",
    html_content="<h1>Hello!</h1>"
)
```

---

## 🐛 Troubleshooting

### Database Connection Failed

**Error:** `ServerSelectionTimeoutError`

**Solution:**
1. Check MongoDB is running: `sudo systemctl status mongodb`
2. Verify MONGO_URL in .env
3. Check network connectivity

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'config'`

**Solution:**
```bash
# Ensure you're in backend directory
cd /app/backend

# Install dependencies
pip install -r requirements.txt
```

### Authentication Not Working

**Symptoms:** Always getting 401 Unauthorized

**Check:**
1. Cookie settings (secure, samesite)
2. FRONTEND_URL in .env matches actual frontend URL
3. Browser is sending cookies (check DevTools)

### Admin Panel Redirect Loop

**Solution:**
1. Clear browser cache completely
2. Use incognito mode for testing
3. Check console for `[AuthContext]` and `[AdminRoute]` logs
4. Verify admin user exists: `role="admin"`

---

## 📞 Support

**Admin Credentials:**
```
Email: admin@habitere.com
Password: admin123
```

**For Issues:**
1. Check logs: `tail -f /var/log/supervisor/backend.err.log`
2. Enable debug logging: `LOG_LEVEL=DEBUG` in .env
3. Check console logs in browser DevTools

---

**Last Updated:** 2025-10-17
**Version:** 1.0.0 (Refactored)
**Status:** ✅ Production Ready
