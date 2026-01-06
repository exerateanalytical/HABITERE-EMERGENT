# HABITERE PLATFORM - PROJECT STRUCTURE FOR PHP CONVERSION

## 📁 CLEANED PROJECT STRUCTURE

This document outlines the essential files kept for PHP conversion.

---

## DIRECTORY STRUCTURE

```
/app/
├── backend/                          # Python FastAPI Backend (TO CONVERT)
│   ├── server.py                    # Main application
│   ├── requirements.txt             # Dependencies
│   ├── .env                         # Environment variables
│   ├── routes/                      # API Routes
│   │   ├── auth.py                 # ✅ CONVERT TO: AuthController.php
│   │   ├── properties.py           # ✅ CONVERT TO: PropertyController.php
│   │   ├── services.py             # ✅ CONVERT TO: ServiceController.php
│   │   ├── bookings.py             # ✅ CONVERT TO: BookingController.php
│   │   ├── messages.py             # ✅ CONVERT TO: MessageController.php
│   │   ├── users.py                # ✅ CONVERT TO: UserController.php
│   │   ├── subscriptions.py        # ✅ CONVERT TO: SubscriptionController.php
│   │   ├── security.py             # ✅ CONVERT TO: SecurityController.php
│   │   ├── images.py               # ✅ CONVERT TO: ImageService.php
│   │   ├── house_plans.py          # ✅ CONVERT TO: HousePlanService.php
│   │   ├── assets.py               # ✅ CONVERT TO: AssetController.php
│   │   └── reviews.py              # ✅ CONVERT TO: ReviewController.php
│   ├── utils/                       # Utility modules
│   │   ├── auth.py                 # ✅ CONVERT TO: Middleware
│   │   └── database.py             # ✅ CONVERT TO: config/database.php
│   └── uploads/                     # Uploaded files (KEEP)
│       ├── properties/
│       ├── services/
│       ├── floor_plans/
│       └── pdf_plans/
│
├── frontend/                        # React Frontend
│   ├── package.json                # NPM dependencies
│   ├── public/                     # Static assets (KEEP)
│   ├── src/
│   │   ├── App.js                  # Main React app
│   │   ├── index.js                # Entry point
│   │   ├── context/                # React context
│   │   │   └── AuthContext.js     # Auth state management
│   │   ├── pages/                  # Page components (50+ files)
│   │   │   ├── Home.js
│   │   │   ├── Properties.js
│   │   │   ├── PropertyDetails.js
│   │   │   ├── Services.js
│   │   │   ├── Dashboard.js
│   │   │   ├── HousePlanBuilder.js
│   │   │   ├── HousePlanTemplates.js
│   │   │   ├── MyHousePlans.js
│   │   │   └── [45+ more pages]
│   │   └── components/             # Reusable components (100+ files)
│   │       ├── Navbar.js
│   │       ├── Footer.js
│   │       ├── FloorPlan3DViewer.js
│   │       └── [95+ more components]
│   └── .env                        # Frontend environment variables
│
├── PHP_CONVERSION_GUIDE.md         # 📘 Complete conversion guide (NEW)
├── PROJECT_STRUCTURE.md            # 📋 This file (NEW)
├── README.md                       # Project overview
├── test_result.md                  # Testing documentation
└── .gitignore                      # Git ignore rules
```

---

## BACKEND FILES TO CONVERT

### 🔴 CRITICAL PRIORITY (Week 1-3)

| Python File | Lines | Convert To | Complexity | Priority |
|------------|-------|------------|------------|----------|
| `routes/auth.py` | ~300 | `AuthController.php` | Medium | ⭐⭐⭐⭐⭐ |
| `routes/users.py` | ~250 | `UserController.php` | Low | ⭐⭐⭐⭐⭐ |
| `routes/properties.py` | ~450 | `PropertyController.php` | Medium | ⭐⭐⭐⭐⭐ |
| `routes/images.py` | ~200 | `ImageService.php` | Medium | ⭐⭐⭐⭐⭐ |
| `utils/auth.py` | ~150 | `Middleware/Authenticate.php` | Low | ⭐⭐⭐⭐⭐ |
| `utils/database.py` | ~50 | `config/database.php` | Low | ⭐⭐⭐⭐⭐ |

### 🟡 HIGH PRIORITY (Week 4-6)

| Python File | Lines | Convert To | Complexity | Priority |
|------------|-------|------------|------------|----------|
| `routes/services.py` | ~400 | `ServiceController.php` | Medium | ⭐⭐⭐⭐ |
| `routes/bookings.py` | ~350 | `BookingController.php` | Medium | ⭐⭐⭐⭐ |
| `routes/messages.py` | ~300 | `MessageController.php` | Medium | ⭐⭐⭐⭐ |
| `routes/reviews.py` | ~200 | `ReviewController.php` | Low | ⭐⭐⭐⭐ |

### 🟢 MEDIUM PRIORITY (Week 7-10)

| Python File | Lines | Convert To | Complexity | Priority |
|------------|-------|------------|------------|----------|
| `routes/subscriptions.py` | ~300 | `SubscriptionController.php` | Medium | ⭐⭐⭐ |
| `routes/house_plans.py` | ~2000 | `HousePlanService.php` | **Very High** | ⭐⭐⭐ |
| `routes/security.py` | ~250 | `SecurityController.php` | Low | ⭐⭐ |
| `routes/assets.py` | ~200 | `AssetController.php` | Low | ⭐⭐ |

---

## FRONTEND OPTIONS

### Option A: Keep React + Update API (RECOMMENDED) ✅

**Work Required:** 10-20 hours
- Update `REACT_APP_BACKEND_URL` to point to PHP API
- Test all API calls
- Fix any breaking changes

**Pros:**
- Minimal work
- Keep modern UI/UX
- Better performance

### Option B: Convert to PHP Blade Templates

**Work Required:** 400-600 hours
- Convert 50+ page components
- Convert 100+ reusable components
- Rebuild authentication flow
- Rebuild state management
- Add JavaScript for interactivity

**Pros:**
- Everything in PHP
- Server-side rendering
- Simpler deployment

---

## KEY MODULES TO CONVERT

### 1. Authentication System
**Files:**
- `backend/routes/auth.py` → `AuthController.php`
- `backend/utils/auth.py` → `Middleware/Authenticate.php`
- `frontend/src/context/AuthContext.js` → Update API calls

**Features:**
- User registration
- Login with JWT
- HTTP-only cookie sessions
- Password hashing
- Email verification
- Role-based access (user, service_provider, admin)

**Complexity:** Medium  
**Priority:** ⭐⭐⭐⭐⭐ Critical

---

### 2. Property Management
**Files:**
- `backend/routes/properties.py` → `PropertyController.php`
- `backend/routes/images.py` → `ImageService.php`

**Features:**
- Property CRUD operations
- Image upload with watermarking
- Property search and filtering
- Location-based filtering
- Property status management
- Featured properties

**Complexity:** Medium  
**Priority:** ⭐⭐⭐⭐⭐ Critical

---

### 3. Professional Services
**Files:**
- `backend/routes/services.py` → `ServiceController.php`

**Features:**
- Service provider registration
- Service listings
- Category management
- Service search
- Provider profiles
- Service bookings

**Complexity:** Medium  
**Priority:** ⭐⭐⭐⭐ High

---

### 4. House Plan Generation (COMPLEX) 🔥
**Files:**
- `backend/routes/house_plans.py` (2000+ lines) → `HousePlanService.php`

**Features:**
- **Floor plan generation** (using PIL/Pillow)
  - Architectural layout algorithm
  - Room placement
  - Hallway/corridor system
  - Door and window symbols
  - Dimension labels
  - North arrow
- **Material calculation**
  - 7 construction stages
  - 80+ material types
  - Regional pricing (10 Cameroon cities)
- **PDF generation**
  - Floor plans
  - Bill of Quantities (BOQ)
  - Cost breakdown
- **5 house plan templates**

**Complexity:** ⭐⭐⭐⭐⭐ Very High  
**Priority:** ⭐⭐⭐ Medium

**Conversion Challenges:**
1. **Floor plan image generation** - PHP GD/Imagick less powerful than Pillow
2. **PDF generation** - TCPDF less featured than ReportLab
3. **Complex algorithms** - Room layout, material calculations

**Recommended Approach:**
- Use **Intervention Image** (Laravel) for floor plans
- Use **TCPDF** for PDF generation
- Consider keeping Python microservice for this module only

---

### 5. Messaging System
**Files:**
- `backend/routes/messages.py` → `MessageController.php`

**Features:**
- Direct messaging between users
- Message threads
- Unread message count
- Message notifications

**Complexity:** Medium  
**Priority:** ⭐⭐⭐⭐ High

---

### 6. Booking System
**Files:**
- `backend/routes/bookings.py` → `BookingController.php`

**Features:**
- Property booking requests
- Service booking
- Booking status management
- Booking history

**Complexity:** Medium  
**Priority:** ⭐⭐⭐⭐ High

---

### 7. Subscription System
**Files:**
- `backend/routes/subscriptions.py` → `SubscriptionController.php`

**Features:**
- 7 subscription plans
- Payment processing (MTN MoMo, Orange Money, Bank Transfer)
- Subscription status tracking
- Renewal management

**Complexity:** Medium  
**Priority:** ⭐⭐⭐ Medium

---

## DEPENDENCIES MAPPING

### Python → PHP

| Python Package | PHP Equivalent | Installation |
|---------------|----------------|--------------|
| `fastapi` | `laravel/framework` | `composer require laravel/framework` |
| `motor` (MongoDB) | `mongodb/laravel-mongodb` | `composer require mongodb/laravel-mongodb` |
| `pydantic` | Laravel Validation | Built-in |
| `python-jose` (JWT) | `firebase/php-jwt` | `composer require firebase/php-jwt` |
| `passlib` | `password_hash()` | Built-in |
| `pillow` (PIL) | `intervention/image` | `composer require intervention/image` |
| `reportlab` | `tecnickcom/tcpdf` | `composer require tecnickcom/tcpdf` |
| `python-multipart` | Laravel File Upload | Built-in |
| `uvicorn` | PHP-FPM + Nginx | System |

---

## DATABASE (MongoDB)

### No Schema Changes Needed ✅

MongoDB is schemaless, so existing data works as-is.

**Collections:**
- `users` - User accounts
- `properties` - Property listings
- `services` - Professional services
- `bookings` - Booking records
- `messages` - User messages
- `reviews` - Property/service reviews
- `subscriptions` - Subscription plans
- `subscription_payments` - Payment records
- `house_plans` - Generated house plans
- `security_services` - Security service bookings
- `assets` - Asset management

**PHP MongoDB Setup:**
```bash
# Install MongoDB PHP extension
sudo apt-get install php8.2-mongodb

# Install Laravel MongoDB package
composer require mongodb/laravel-mongodb
```

---

## FILE UPLOADS & STORAGE

### Current Structure (Keep As-Is)

```
/app/backend/uploads/
├── properties/          # Property images
│   └── [uuid].jpg
├── services/           # Service provider images
│   └── [uuid].jpg
├── floor_plans/        # Generated floor plan images
│   └── floor_0_[hash].png
└── pdf_plans/          # Generated PDF house plans
    └── house_plan_[id].pdf
```

### PHP Storage (Laravel)

```
/app/storage/app/public/
├── properties/
├── services/
├── floor_plans/
└── pdf_plans/
```

**Create symbolic link:**
```bash
php artisan storage:link
```

---

## CONVERSION CHECKLIST

### ✅ Phase 1: Setup
- [ ] Install PHP 8.2+
- [ ] Install Composer
- [ ] Create Laravel project
- [ ] Install MongoDB driver
- [ ] Configure database connection
- [ ] Test MongoDB connection

### ✅ Phase 2: Core Backend
- [ ] Convert `auth.py` → `AuthController.php`
- [ ] Implement JWT authentication
- [ ] Create `User` model
- [ ] Convert `users.py` → `UserController.php`
- [ ] Test authentication flow

### ✅ Phase 3: Main Features
- [ ] Convert `properties.py` → `PropertyController.php`
- [ ] Create `Property` model
- [ ] Convert `images.py` → `ImageService.php`
- [ ] Test property CRUD with images
- [ ] Convert `services.py` → `ServiceController.php`
- [ ] Create `Service` model

### ✅ Phase 4: Supporting Features
- [ ] Convert `bookings.py` → `BookingController.php`
- [ ] Convert `messages.py` → `MessageController.php`
- [ ] Convert `reviews.py` → `ReviewController.php`
- [ ] Convert `subscriptions.py` → `SubscriptionController.php`

### ✅ Phase 5: Advanced Features
- [ ] Convert `house_plans.py` → `HousePlanService.php`
- [ ] Implement floor plan generation (Intervention Image)
- [ ] Implement PDF generation (TCPDF)
- [ ] Test house plan creation

### ✅ Phase 6: Frontend
- [ ] Option A: Update React API endpoints
- [ ] Option B: Convert to Blade templates (if chosen)
- [ ] Test all frontend functionality

### ✅ Phase 7: Testing & Deployment
- [ ] API testing
- [ ] Frontend testing
- [ ] Performance optimization
- [ ] Security audit
- [ ] Deploy to production

---

## ESTIMATED EFFORT

| Task | Hours | Developers | Duration |
|------|-------|-----------|----------|
| Setup & Planning | 40 | 1 | 1 week |
| Authentication | 60 | 1 | 1.5 weeks |
| Properties & Images | 80 | 1 | 2 weeks |
| Services & Bookings | 60 | 1 | 1.5 weeks |
| Messages & Reviews | 40 | 1 | 1 week |
| Subscriptions | 40 | 1 | 1 week |
| House Plans (Complex) | 120 | 2 | 3 weeks |
| Frontend Updates | 60 | 1 | 1.5 weeks |
| Testing | 80 | 2 | 2 weeks |
| **TOTAL** | **580 hours** | **2** | **14-16 weeks** |

---

## NEXT STEPS

1. ✅ **Read** `PHP_CONVERSION_GUIDE.md` for detailed conversion instructions
2. ✅ **Decide** on frontend approach (Keep React or Convert to Blade)
3. ✅ **Setup** PHP development environment
4. ✅ **Start** with Phase 1 (Setup) from the conversion guide
5. ✅ **Follow** the step-by-step conversion plan
6. ✅ **Test** each module thoroughly before moving to next
7. ✅ **Deploy** to staging environment for testing
8. ✅ **Launch** to production

---

## SUPPORT

For questions or issues during conversion:
- Refer to `PHP_CONVERSION_GUIDE.md` for detailed code examples
- Check Laravel documentation: https://laravel.com/docs
- MongoDB PHP driver docs: https://www.mongodb.com/docs/php-library/

---

**Document Version:** 1.0  
**Last Updated:** November 26, 2024  
**Files Cleaned:** All test files, debug scripts, and unnecessary documentation removed  
**Ready for Conversion:** ✅ Yes
