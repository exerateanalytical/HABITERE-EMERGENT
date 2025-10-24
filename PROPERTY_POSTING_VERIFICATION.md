# PROPERTY POSTING FLOW - ARCHITECTURAL MAP
## Generated: 2025-10-18
## Purpose: Complete verification of property posting functionality

---

## **FLOW DIAGRAM**

```
START
  ↓
USER AUTHENTICATION (Login Required)
  ↓
DASHBOARD (/dashboard)
  ↓
CLICK "Add Property" Button
  ↓
NAVIGATE TO FORM (/properties/new)
  ↓
PROPERTY FORM RENDERS (PropertyForm.js)
  ↓
USER FILLS FORM FIELDS
  ├── Title (required)
  ├── Description (required)
  ├── Property Type (required)
  ├── Location (required)
  ├── Price (required)
  ├── Bedrooms, Bathrooms
  └── Images (upload)
  ↓
CLIENT-SIDE VALIDATION
  ↓
IMAGE UPLOAD (if images added)
  ├── POST /api/upload/images
  ├── Returns: image URLs
  └── Add URLs to form data
  ↓
FORM SUBMISSION
  ├── POST /api/properties
  └── Headers: Authentication cookie
  ↓
BACKEND PROCESSING
  ├── Authentication check
  ├── Role authorization
  ├── Data validation (Pydantic)
  ├── Owner ID assignment
  └── Database insertion
  ↓
DATABASE STORAGE (MongoDB)
  ├── Collection: properties
  ├── Fields: id, title, description, owner_id, etc.
  └── Timestamps: created_at, updated_at
  ↓
SUCCESS RESPONSE
  ↓
REDIRECT TO PROPERTY DETAILS or LIST
  ↓
PROPERTY VISIBLE IN LISTINGS
  ↓
END
```

---

## **FILES INVOLVED**

### **BACKEND FILES**
- `/app/backend/routes/properties.py` - Property API endpoints
- `/app/backend/routes/images.py` - Image upload endpoint
- `/app/backend/server.py` - Route registration
- `/app/backend/database.py` - MongoDB connection
- `/app/backend/utils/auth.py` - Authentication middleware

### **FRONTEND FILES**
- `/app/frontend/src/pages/PropertyForm.js` - Property creation form
- `/app/frontend/src/pages/PropertyEditForm.js` - Property edit form
- `/app/frontend/src/pages/PropertyDetails.js` - Property detail view
- `/app/frontend/src/pages/Dashboard.js` - Dashboard with "Add Property" button
- `/app/frontend/src/App.js` - Route configuration
- `/app/frontend/src/context/AuthContext.js` - Authentication context

---

## **API ENDPOINTS**

### **Property Endpoints**
1. `POST /api/properties` - Create property (authenticated)
2. `GET /api/properties` - List all properties (public)
3. `GET /api/properties/{property_id}` - Get property details (public)
4. `PUT /api/properties/{property_id}` - Update property (authenticated, owner/admin)
5. `DELETE /api/properties/{property_id}` - Delete property (authenticated, owner/admin)
6. `GET /api/users/me/properties` - Get current user's properties (authenticated)

### **Image Upload Endpoint**
1. `POST /api/upload/images` - Upload property images (authenticated)

---

## **DATABASE COLLECTIONS**

### **Properties Collection**
```
Collection: properties
Fields:
  - id: String (UUID)
  - title: String
  - description: String
  - property_type: String
  - location: String
  - price: Number
  - bedrooms: Number
  - bathrooms: Number
  - square_feet: Number
  - amenities: Array
  - images: Array[String]
  - owner_id: String (UUID)
  - verification_status: String
  - created_at: DateTime
  - updated_at: DateTime
```

---

## **AUTHORIZED ROLES FOR PROPERTY POSTING**

Allowed to create properties:
1. `property_owner` - Primary role for listing properties
2. `property_agent` - Real estate agents
3. `admin` - Full access

Validation location:
- Backend: `/app/backend/routes/properties.py` - Line 189+
- Frontend: Dashboard button visibility check

---

## **ROUTE REGISTRATION**

### **Backend**
- File: `/app/backend/server.py`
- Registration: `app.include_router(properties.router, prefix="/api", tags=["Properties"])`

### **Frontend**
- File: `/app/frontend/src/App.js`
- Route: `<Route path="/properties/new" element={<PropertyForm />} />`
- Protected: NO (⚠️ POTENTIAL GAP - Should be protected route)

---

## **NAVIGATION POINTS**

### **Dashboard**
- File: `/app/frontend/src/pages/Dashboard.js`
- Button: "Add Property" (visible for property_owner, property_agent)
- Link: `/properties/new`

### **Navbar**
- Currently: No direct link in navbar
- Recommendation: Add for quick access

---

## **IMAGE UPLOAD FLOW**

1. User selects images in PropertyForm
2. Frontend calls `POST /api/upload/images`
3. Backend validates file type and size
4. Images stored in `/app/backend/uploads/` or cloud storage
5. Backend returns array of image URLs
6. Frontend adds URLs to property data
7. Property created with image URLs array

---

## **VALIDATION LAYERS**

### **Frontend Validation (PropertyForm.js)**
- Required fields marked
- Input type validation
- Min/max lengths
- Price > 0
- Bedrooms/bathrooms >= 0

### **Backend Validation (properties.py)**
- Pydantic models
- Required fields check
- Data type enforcement
- Owner ID verification
- Image URL format validation

---

## **AUTHENTICATION FLOW**

1. User must be logged in
2. Session cookie sent with request
3. Backend validates session via `get_current_user`
4. User role checked against allowed roles
5. Owner ID automatically assigned from authenticated user

---

## **ERROR HANDLING**

### **Frontend**
- Form validation errors
- Network request failures
- Image upload failures
- Success/error toast notifications

### **Backend**
- 401: Not authenticated
- 403: Forbidden (wrong role)
- 400: Validation errors
- 500: Server errors

---

## **IDENTIFIED GAPS (Initial)**

### **P0 - CRITICAL**
1. ⚠️ `/properties/new` route NOT protected - anyone can access
2. Need to verify form validation completeness

### **P1 - HIGH PRIORITY**
1. Image upload component needs verification
2. Mobile responsiveness needs testing
3. Error handling needs verification

### **P2 - MEDIUM**
1. No direct navbar link to create property
2. Draft save functionality not present

---

## **NEXT STEPS**

1. Phase 2: Backend endpoint verification
2. Phase 3: Frontend form verification
3. Phase 4: End-to-end testing
4. Phase 5: Gap identification
5. Phase 6: Bug fixing
6. Phase 7: Comprehensive testing
7. Phase 8: Production readiness score

---

**STATUS: Architectural mapping complete. Proceeding to Phase 2.**
