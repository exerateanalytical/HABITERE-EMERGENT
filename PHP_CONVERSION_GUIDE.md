# HABITERE PLATFORM - PHP CONVERSION GUIDE
## Complete Migration from FastAPI (Python) + React to PHP

---

## 📋 TABLE OF CONTENTS
1. [Overview](#overview)
2. [Current Architecture](#current-architecture)
3. [Target PHP Architecture](#target-php-architecture)
4. [Backend Conversion (FastAPI → PHP)](#backend-conversion)
5. [Frontend Conversion (React → PHP)](#frontend-conversion)
6. [Database Migration](#database-migration)
7. [File Structure](#file-structure)
8. [Step-by-Step Conversion Plan](#conversion-plan)
9. [Code Examples](#code-examples)
10. [Testing Strategy](#testing-strategy)

---

## 1. OVERVIEW

### Current Stack
- **Backend:** FastAPI (Python 3.11)
- **Frontend:** React 18 + Tailwind CSS
- **Database:** MongoDB
- **Authentication:** JWT + HTTP-Only Cookies
- **File Storage:** Local filesystem
- **Image Processing:** Pillow (PIL)
- **PDF Generation:** ReportLab

### Target Stack
- **Backend:** PHP 8.2+ (Laravel or Symfony recommended)
- **Frontend:** PHP (Blade templates) or Keep React with PHP API
- **Database:** MongoDB (with PHP MongoDB driver)
- **Authentication:** Laravel Sanctum or JWT-PHP
- **File Storage:** Local filesystem
- **Image Processing:** GD Library or Imagick
- **PDF Generation:** TCPDF or DomPDF

---

## 2. CURRENT ARCHITECTURE

### Backend Structure
```
/app/backend/
├── server.py                 # Main FastAPI application
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── routes/                   # API endpoints
│   ├── auth.py              # Authentication routes
│   ├── properties.py        # Property management
│   ├── services.py          # Professional services
│   ├── bookings.py          # Booking system
│   ├── messages.py          # Messaging system
│   ├── users.py             # User management
│   ├── subscriptions.py     # Subscription plans
│   ├── security.py          # Security services
│   ├── images.py            # Image handling
│   ├── house_plans.py       # House plan generation
│   ├── assets.py            # Asset management
│   └── reviews.py           # Review system
├── utils/                    # Utility modules
│   ├── auth.py              # Auth utilities
│   └── database.py          # MongoDB connection
└── uploads/                  # Uploaded files
    ├── properties/
    ├── services/
    ├── floor_plans/
    └── pdf_plans/
```

### Frontend Structure
```
/app/frontend/
├── package.json             # NPM dependencies
├── public/                  # Static assets
├── src/
│   ├── App.js              # Main React app
│   ├── index.js            # Entry point
│   ├── context/            # React context
│   │   └── AuthContext.js  # Authentication state
│   ├── pages/              # Page components
│   │   ├── Home.js
│   │   ├── Properties.js
│   │   ├── PropertyDetails.js
│   │   ├── Services.js
│   │   ├── Dashboard.js
│   │   ├── HousePlanBuilder.js
│   │   ├── HousePlanTemplates.js
│   │   └── [50+ more pages]
│   └── components/         # Reusable components
│       ├── Navbar.js
│       ├── Footer.js
│       └── [100+ components]
```

---

## 3. TARGET PHP ARCHITECTURE

### Recommended: Laravel Framework

```
/app/
├── app/
│   ├── Http/
│   │   ├── Controllers/         # API Controllers
│   │   │   ├── AuthController.php
│   │   │   ├── PropertyController.php
│   │   │   ├── ServiceController.php
│   │   │   ├── HousePlanController.php
│   │   │   └── [all other controllers]
│   │   ├── Middleware/          # Middleware
│   │   │   └── Authenticate.php
│   │   └── Requests/            # Form validation
│   ├── Models/                  # Eloquent models (for MongoDB)
│   │   ├── User.php
│   │   ├── Property.php
│   │   ├── Service.php
│   │   └── [all models]
│   ├── Services/                # Business logic
│   │   ├── HousePlanService.php
│   │   ├── ImageService.php
│   │   └── PDFService.php
│   └── Helpers/                 # Helper functions
├── config/                      # Configuration files
│   ├── database.php
│   ├── auth.php
│   └── cors.php
├── database/
│   └── migrations/              # Database migrations
├── public/                      # Public assets
│   ├── index.php
│   ├── uploads/
│   └── assets/
├── resources/
│   ├── views/                   # Blade templates (if not using React)
│   └── js/                      # Frontend JS (if keeping React)
├── routes/
│   ├── api.php                  # API routes
│   └── web.php                  # Web routes
├── storage/
│   └── app/                     # File storage
├── .env
├── composer.json
└── artisan                      # Laravel CLI
```

---

## 4. BACKEND CONVERSION (FastAPI → PHP)

### 4.1 Core Dependencies

**Python (requirements.txt) → PHP (composer.json)**

| Python Package | PHP Equivalent | Purpose |
|---------------|----------------|---------|
| fastapi | laravel/framework | Web framework |
| motor | mongodb/mongodb | MongoDB driver |
| pydantic | laravel/validation | Data validation |
| python-jose | firebase/php-jwt | JWT handling |
| passlib | - (use password_hash) | Password hashing |
| pillow | intervention/image | Image processing |
| reportlab | tecnickcom/tcpdf | PDF generation |
| python-multipart | - (built-in) | File uploads |

**composer.json example:**
```json
{
    "require": {
        "php": "^8.2",
        "laravel/framework": "^11.0",
        "mongodb/laravel-mongodb": "^4.0",
        "firebase/php-jwt": "^6.0",
        "intervention/image": "^3.0",
        "tecnickcom/tcpdf": "^6.6",
        "laravel/sanctum": "^4.0"
    }
}
```

### 4.2 Database Connection

**Python (utils/database.py):**
```python
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(MONGO_URL)
db = client.habitere
```

**PHP (config/database.php):**
```php
<?php
return [
    'mongodb' => [
        'driver' => 'mongodb',
        'host' => env('MONGO_HOST', '127.0.0.1'),
        'port' => env('MONGO_PORT', 27017),
        'database' => env('MONGO_DATABASE', 'habitere'),
        'username' => env('MONGO_USERNAME'),
        'password' => env('MONGO_PASSWORD'),
        'options' => [
            'database' => env('MONGO_AUTH_DATABASE', 'admin'),
        ],
    ],
];
```

### 4.3 Authentication System

**Python (routes/auth.py):**
```python
from fastapi import APIRouter, HTTPException, Response
from passlib.context import CryptContext
import jwt

@router.post("/login")
async def login(credentials: LoginRequest):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not pwd_context.verify(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode({"user_id": user["id"]}, SECRET_KEY)
    response.set_cookie("session", token, httponly=True)
    return {"success": True}
```

**PHP (app/Http/Controllers/AuthController.php):**
```php
<?php
namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Firebase\JWT\JWT;

class AuthController extends Controller
{
    public function login(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
            'password' => 'required'
        ]);

        $user = User::where('email', $request->email)->first();

        if (!$user || !Hash::check($request->password, $user->password)) {
            return response()->json([
                'error' => 'Invalid credentials'
            ], 401);
        }

        $token = JWT::encode([
            'user_id' => $user->_id,
            'exp' => time() + (60 * 60 * 24) // 24 hours
        ], env('JWT_SECRET'), 'HS256');

        return response()->json([
            'success' => true,
            'user' => $user
        ])->cookie('session', $token, 60 * 24, '/', null, true, true); // httpOnly
    }

    public function register(Request $request)
    {
        $request->validate([
            'email' => 'required|email|unique:users',
            'password' => 'required|min:6',
            'name' => 'required'
        ]);

        $user = User::create([
            'email' => $request->email,
            'password' => Hash::make($request->password),
            'name' => $request->name,
            'role' => 'user',
            'created_at' => now()
        ]);

        return response()->json([
            'success' => true,
            'user' => $user
        ], 201);
    }
}
```

### 4.4 Property Management API

**Python (routes/properties.py):**
```python
@router.get("/properties")
async def get_properties(
    limit: int = 20,
    location: Optional[str] = None
):
    query = {}
    if location:
        query["location"] = location
    
    properties = await db.properties.find(query).limit(limit).to_list(length=None)
    return properties
```

**PHP (app/Http/Controllers/PropertyController.php):**
```php
<?php
namespace App\Http\Controllers;

use App\Models\Property;
use Illuminate\Http\Request;

class PropertyController extends Controller
{
    public function index(Request $request)
    {
        $query = Property::query();

        if ($request->has('location')) {
            $query->where('location', $request->location);
        }

        if ($request->has('property_type')) {
            $query->where('property_type', $request->property_type);
        }

        $limit = $request->get('limit', 20);
        $properties = $query->limit($limit)->get();

        return response()->json($properties);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'title' => 'required|string',
            'description' => 'required|string',
            'location' => 'required|string',
            'price' => 'required|numeric',
            'property_type' => 'required|string',
            'bedrooms' => 'required|integer',
            'bathrooms' => 'required|integer',
        ]);

        $property = Property::create(array_merge($validated, [
            'user_id' => auth()->id(),
            'status' => 'active',
            'created_at' => now()
        ]));

        return response()->json($property, 201);
    }

    public function show($id)
    {
        $property = Property::findOrFail($id);
        return response()->json($property);
    }

    public function update(Request $request, $id)
    {
        $property = Property::findOrFail($id);

        // Check ownership
        if ($property->user_id !== auth()->id()) {
            return response()->json(['error' => 'Unauthorized'], 403);
        }

        $property->update($request->all());
        return response()->json($property);
    }

    public function destroy($id)
    {
        $property = Property::findOrFail($id);

        if ($property->user_id !== auth()->id()) {
            return response()->json(['error' => 'Unauthorized'], 403);
        }

        $property->delete();
        return response()->json(['success' => true]);
    }
}
```

### 4.5 Image Upload & Processing

**Python (routes/images.py):**
```python
from PIL import Image, ImageDraw, ImageFont

@router.post("/upload")
async def upload_image(file: UploadFile):
    # Save file
    filepath = f"uploads/properties/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
    # Add watermark
    img = Image.open(filepath)
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Habitere.com", fill="white")
    img.save(filepath)
    
    return {"filename": file.filename}
```

**PHP (app/Services/ImageService.php):**
```php
<?php
namespace App\Services;

use Intervention\Image\Facades\Image;
use Illuminate\Support\Str;

class ImageService
{
    public function uploadAndWatermark($file, $directory = 'properties')
    {
        $filename = Str::uuid() . '.' . $file->getClientOriginalExtension();
        $path = storage_path("app/public/{$directory}");
        
        if (!file_exists($path)) {
            mkdir($path, 0755, true);
        }

        $fullPath = "{$path}/{$filename}";

        // Process and watermark
        $img = Image::make($file);
        
        // Add watermark
        $img->text('Habitere.com', 10, 10, function($font) {
            $font->file(public_path('fonts/arial.ttf'));
            $font->size(24);
            $font->color('#ffffff');
            $font->align('left');
            $font->valign('top');
        });

        $img->save($fullPath);

        return "{$directory}/{$filename}";
    }

    public function deleteImage($path)
    {
        $fullPath = storage_path("app/public/{$path}");
        if (file_exists($fullPath)) {
            unlink($fullPath);
        }
    }
}
```

### 4.6 House Plan Generation

**Python (routes/house_plans.py) - Floor Plan Generation:**
```python
from PIL import Image, ImageDraw
import uuid

def generate_proper_floor_plan(floor, floor_number):
    img = Image.new('RGB', (1200, 800), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw building perimeter
    draw.rectangle([(100, 100), (1100, 700)], outline='black', width=8)
    
    # Draw rooms with proper layout...
    # (complex logic here)
    
    filepath = f"/uploads/floor_plans/floor_{floor_number}_{uuid.uuid4().hex[:8]}.png"
    img.save(filepath)
    return filepath
```

**PHP (app/Services/HousePlanService.php):**
```php
<?php
namespace App\Services;

use Intervention\Image\Facades\Image;
use Illuminate\Support\Str;

class HousePlanService
{
    public function generateFloorPlan($floor, $floorNumber)
    {
        // Create blank canvas
        $width = 1200;
        $height = 800;
        $img = Image::canvas($width, $height, '#ffffff');

        // Draw building perimeter (thick black lines)
        $img->rectangle(100, 100, 1100, 700, function ($draw) {
            $draw->border(8, '#000000');
        });

        // Draw rooms, hallways, doors, windows
        foreach ($floor['rooms'] as $room) {
            // Calculate room position and size
            $roomX = $this->calculateRoomX($room);
            $roomY = $this->calculateRoomY($room);
            $roomW = $room['length'] * 50; // scale
            $roomH = $room['width'] * 50;

            // Draw room
            $img->rectangle($roomX, $roomY, $roomX + $roomW, $roomY + $roomH, function ($draw) {
                $draw->background('#ffffff');
                $draw->border(3, '#333333');
            });

            // Add room label
            $img->text($room['name'], $roomX + $roomW/2, $roomY + $roomH/2, function($font) {
                $font->file(public_path('fonts/arial.ttf'));
                $font->size(14);
                $font->color('#000000');
                $font->align('center');
                $font->valign('middle');
            });
        }

        // Save image
        $filename = "floor_{$floorNumber}_" . Str::random(8) . ".png";
        $path = storage_path("app/public/floor_plans/{$filename}");
        
        if (!file_exists(dirname($path))) {
            mkdir(dirname($path), 0755, true);
        }

        $img->save($path);

        return "floor_plans/{$filename}";
    }

    private function calculateRoomX($room)
    {
        // Room layout algorithm
        return 150; // Simplified
    }

    private function calculateRoomY($room)
    {
        return 150; // Simplified
    }
}
```

### 4.7 PDF Generation

**Python (ReportLab):**
```python
from reportlab.pdfgen import canvas

def generate_pdf(plan):
    filename = f"house_plan_{plan['id'][:8]}.pdf"
    c = canvas.Canvas(filename)
    c.drawString(100, 750, plan['name'])
    c.save()
    return filename
```

**PHP (TCPDF):**
```php
<?php
namespace App\Services;

use TCPDF;

class PDFService
{
    public function generateHousePlanPDF($plan)
    {
        $pdf = new TCPDF(PDF_PAGE_ORIENTATION, PDF_UNIT, PDF_PAGE_FORMAT, true, 'UTF-8', false);

        // Set document information
        $pdf->SetCreator('Habitere Platform');
        $pdf->SetAuthor('Habitere');
        $pdf->SetTitle($plan['name']);

        // Remove default header/footer
        $pdf->setPrintHeader(false);
        $pdf->setPrintFooter(false);

        // Add a page
        $pdf->AddPage();

        // Set font
        $pdf->SetFont('helvetica', 'B', 20);

        // Title
        $pdf->Cell(0, 10, $plan['name'], 0, 1, 'C');

        // Content
        $pdf->SetFont('helvetica', '', 12);
        $pdf->Ln(10);
        $pdf->Write(0, $plan['description'], '', 0, 'L', true);

        // Add floor plan images
        foreach ($plan['floors'] as $floor) {
            $pdf->AddPage();
            $pdf->SetFont('helvetica', 'B', 16);
            $pdf->Cell(0, 10, $floor['floor_name'], 0, 1, 'C');
            
            if (isset($floor['image_path'])) {
                $imagePath = storage_path("app/public/{$floor['image_path']}");
                if (file_exists($imagePath)) {
                    $pdf->Image($imagePath, 15, 40, 180, 0, 'PNG');
                }
            }
        }

        // Material costs table
        $pdf->AddPage();
        $pdf->SetFont('helvetica', 'B', 14);
        $pdf->Cell(0, 10, 'Bill of Quantities (BOQ)', 0, 1, 'L');
        
        // Table header
        $pdf->SetFont('helvetica', 'B', 10);
        $pdf->Cell(60, 7, 'Material', 1, 0, 'L');
        $pdf->Cell(30, 7, 'Quantity', 1, 0, 'C');
        $pdf->Cell(40, 7, 'Unit Price', 1, 0, 'R');
        $pdf->Cell(40, 7, 'Total', 1, 1, 'R');

        // Table content
        $pdf->SetFont('helvetica', '', 9);
        foreach ($plan['materials'] as $material) {
            $pdf->Cell(60, 6, $material['name'], 1, 0, 'L');
            $pdf->Cell(30, 6, $material['quantity'] . ' ' . $material['unit'], 1, 0, 'C');
            $pdf->Cell(40, 6, number_format($material['unit_price']) . ' FCFA', 1, 0, 'R');
            $pdf->Cell(40, 6, number_format($material['total_price']) . ' FCFA', 1, 1, 'R');
        }

        // Save PDF
        $filename = "house_plan_" . substr($plan['_id'], 0, 8) . ".pdf";
        $path = storage_path("app/public/pdf_plans/{$filename}");
        
        if (!file_exists(dirname($path))) {
            mkdir(dirname($path), 0755, true);
        }

        $pdf->Output($path, 'F');

        return "pdf_plans/{$filename}";
    }
}
```

---

## 5. FRONTEND CONVERSION (React → PHP)

### Option A: Keep React + PHP Backend (Recommended)

**Pros:**
- Less conversion work
- Keep existing UI/UX
- Modern frontend experience
- Easier to maintain

**Changes Needed:**
- Update API endpoints to PHP backend
- Adjust authentication flow
- Update environment variables

**Example:**

```javascript
// OLD (FastAPI)
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// NEW (PHP Laravel)
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL; // Same, but points to PHP

// API calls remain the same
axios.get(`${BACKEND_URL}/api/properties`)
```

### Option B: Convert to PHP Blade Templates

**Pros:**
- Everything in PHP
- Server-side rendering
- Simpler deployment

**Cons:**
- Complete rewrite needed
- Loss of React interactivity
- More development time

**Example Conversion:**

**React (Properties.js):**
```jsx
function Properties() {
  const [properties, setProperties] = useState([]);

  useEffect(() => {
    axios.get(`${BACKEND_URL}/api/properties`)
      .then(res => setProperties(res.data));
  }, []);

  return (
    <div>
      {properties.map(prop => (
        <PropertyCard key={prop.id} property={prop} />
      ))}
    </div>
  );
}
```

**PHP Blade (properties.blade.php):**
```php
@extends('layouts.app')

@section('content')
<div class="container">
    <h1>Properties</h1>
    
    <div class="row">
        @foreach($properties as $property)
            <div class="col-md-4">
                <div class="card">
                    <img src="{{ asset('storage/' . $property->images[0]) }}" class="card-img-top">
                    <div class="card-body">
                        <h5 class="card-title">{{ $property->title }}</h5>
                        <p class="card-text">{{ $property->location }}</p>
                        <p class="text-primary">{{ number_format($property->price) }} FCFA</p>
                        <a href="{{ route('properties.show', $property->_id) }}" class="btn btn-primary">
                            View Details
                        </a>
                    </div>
                </div>
            </div>
        @endforeach
    </div>
</div>
@endsection
```

**Controller (PropertyController.php):**
```php
<?php
namespace App\Http\Controllers;

use App\Models\Property;

class PropertyController extends Controller
{
    public function index()
    {
        $properties = Property::where('status', 'active')
            ->latest()
            ->paginate(20);

        return view('properties.index', compact('properties'));
    }

    public function show($id)
    {
        $property = Property::findOrFail($id);
        return view('properties.show', compact('property'));
    }
}
```

---

## 6. DATABASE MIGRATION

### MongoDB with PHP

**Install MongoDB PHP Extension:**
```bash
# Ubuntu/Debian
sudo apt-get install php8.2-mongodb

# Via composer
composer require mongodb/laravel-mongodb
```

**Configure (config/database.php):**
```php
'connections' => [
    'mongodb' => [
        'driver' => 'mongodb',
        'host' => env('DB_HOST', '127.0.0.1'),
        'port' => env('DB_PORT', 27017),
        'database' => env('DB_DATABASE', 'habitere'),
        'username' => env('DB_USERNAME'),
        'password' => env('DB_PASSWORD'),
        'options' => [
            'database' => env('DB_AUTH_DATABASE', 'admin'),
        ],
    ],
]
```

**Model Example (app/Models/Property.php):**
```php
<?php
namespace App\Models;

use MongoDB\Laravel\Eloquent\Model;

class Property extends Model
{
    protected $connection = 'mongodb';
    protected $collection = 'properties';

    protected $fillable = [
        'title',
        'description',
        'location',
        'price',
        'property_type',
        'bedrooms',
        'bathrooms',
        'area',
        'images',
        'user_id',
        'status',
    ];

    protected $casts = [
        'price' => 'float',
        'bedrooms' => 'integer',
        'bathrooms' => 'integer',
        'area' => 'float',
        'images' => 'array',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function bookings()
    {
        return $this->hasMany(Booking::class);
    }
}
```

### No Schema Migration Needed
MongoDB is schemaless, so existing data works as-is. Just ensure:
1. Collection names match
2. Field names match
3. Data types are compatible

---

## 7. FILE STRUCTURE

### Files to Convert

#### Backend Routes (Priority Order)
1. ✅ **auth.py** → AuthController.php (HIGH)
2. ✅ **properties.py** → PropertyController.php (HIGH)
3. ✅ **services.py** → ServiceController.php (HIGH)
4. ✅ **bookings.py** → BookingController.php (MEDIUM)
5. ✅ **messages.py** → MessageController.php (MEDIUM)
6. ✅ **users.py** → UserController.php (HIGH)
7. ✅ **subscriptions.py** → SubscriptionController.php (MEDIUM)
8. ✅ **security.py** → SecurityController.php (LOW)
9. ✅ **images.py** → ImageService.php (HIGH)
10. ✅ **house_plans.py** → HousePlanController.php + HousePlanService.php (MEDIUM)
11. ✅ **assets.py** → AssetController.php (LOW)
12. ✅ **reviews.py** → ReviewController.php (MEDIUM)

#### Frontend Pages (If converting to PHP)
Convert all 50+ React pages to Blade templates or keep React with API updates.

#### Utility Files
- **utils/auth.py** → Middleware/Authenticate.php
- **utils/database.py** → config/database.php

---

## 8. STEP-BY-STEP CONVERSION PLAN

### Phase 1: Setup (Week 1)
1. ✅ Install PHP 8.2+
2. ✅ Install Composer
3. ✅ Create new Laravel project: `composer create-project laravel/laravel habitere-php`
4. ✅ Install MongoDB driver: `composer require mongodb/laravel-mongodb`
5. ✅ Install other dependencies (Intervention Image, TCPDF, JWT)
6. ✅ Configure .env file with MongoDB connection
7. ✅ Test MongoDB connection

### Phase 2: Core Backend (Week 2-3)
1. ✅ Convert authentication system (auth.py → AuthController.php)
2. ✅ Implement JWT/Session authentication
3. ✅ Create User model
4. ✅ Test login/register/logout flows
5. ✅ Convert users.py → UserController.php
6. ✅ Test user CRUD operations

### Phase 3: Main Features (Week 4-6)
1. ✅ Convert properties.py → PropertyController.php
2. ✅ Create Property model
3. ✅ Implement image upload service (ImageService.php)
4. ✅ Test property CRUD with images
5. ✅ Convert services.py → ServiceController.php
6. ✅ Create Service model
7. ✅ Test service provider registration and booking

### Phase 4: Supporting Features (Week 7-8)
1. ✅ Convert bookings.py → BookingController.php
2. ✅ Convert messages.py → MessageController.php
3. ✅ Convert reviews.py → ReviewController.php
4. ✅ Convert subscriptions.py → SubscriptionController.php
5. ✅ Test all supporting features

### Phase 5: Advanced Features (Week 9-10)
1. ✅ Convert house_plans.py → HousePlanService.php
2. ✅ Implement floor plan generation (Intervention Image)
3. ✅ Implement PDF generation (TCPDF)
4. ✅ Test house plan creation with materials calculation
5. ✅ Convert security.py → SecurityController.php
6. ✅ Convert assets.py → AssetController.php

### Phase 6: Frontend Integration (Week 11-12)
**Option A (Keep React):**
1. ✅ Update API endpoints in React app
2. ✅ Test all frontend pages with new PHP backend
3. ✅ Fix any breaking changes

**Option B (Convert to Blade):**
1. ✅ Convert Home.js → home.blade.php
2. ✅ Convert Properties.js → properties/index.blade.php
3. ✅ Convert PropertyDetails.js → properties/show.blade.php
4. ✅ Continue converting all 50+ pages
5. ✅ Implement Tailwind CSS with Laravel Mix
6. ✅ Add JavaScript for interactivity

### Phase 7: Testing & Deployment (Week 13-14)
1. ✅ Comprehensive API testing
2. ✅ Frontend testing (manual or automated)
3. ✅ Performance optimization
4. ✅ Security audit
5. ✅ Deploy to production server
6. ✅ Monitor and fix issues

---

## 9. CODE EXAMPLES

### Complete Authentication Flow

**routes/api.php:**
```php
<?php
use App\Http\Controllers\AuthController;
use App\Http\Controllers\PropertyController;
use Illuminate\Support\Facades\Route;

// Public routes
Route::post('/auth/register', [AuthController::class, 'register']);
Route::post('/auth/login', [AuthController::class, 'login']);

// Protected routes
Route::middleware('auth:api')->group(function () {
    Route::get('/auth/me', [AuthController::class, 'me']);
    Route::post('/auth/logout', [AuthController::class, 'logout']);
    
    // Properties
    Route::apiResource('properties', PropertyController::class);
    
    // File uploads
    Route::post('/images/upload', [ImageController::class, 'upload']);
});
```

### Middleware for JWT Authentication

**app/Http/Middleware/AuthenticateWithJWT.php:**
```php
<?php
namespace App\Http\Middleware;

use Closure;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use App\Models\User;

class AuthenticateWithJWT
{
    public function handle($request, Closure $next)
    {
        $token = $request->cookie('session');

        if (!$token) {
            return response()->json(['error' => 'Not authenticated'], 401);
        }

        try {
            $decoded = JWT::decode($token, new Key(env('JWT_SECRET'), 'HS256'));
            $user = User::find($decoded->user_id);

            if (!$user) {
                return response()->json(['error' => 'User not found'], 401);
            }

            $request->merge(['auth_user' => $user]);
            auth()->setUser($user);

        } catch (\Exception $e) {
            return response()->json(['error' => 'Invalid token'], 401);
        }

        return $next($request);
    }
}
```

### File Upload with Watermarking

**app/Http/Controllers/ImageController.php:**
```php
<?php
namespace App\Http\Controllers;

use App\Services\ImageService;
use Illuminate\Http\Request;

class ImageController extends Controller
{
    protected $imageService;

    public function __construct(ImageService $imageService)
    {
        $this->imageService = $imageService;
    }

    public function upload(Request $request)
    {
        $request->validate([
            'image' => 'required|image|max:10240', // 10MB max
            'type' => 'required|in:property,service,profile'
        ]);

        $directory = $request->type . 's';
        $path = $this->imageService->uploadAndWatermark(
            $request->file('image'),
            $directory
        );

        return response()->json([
            'success' => true,
            'path' => $path,
            'url' => asset("storage/{$path}")
        ]);
    }

    public function serve($type, $filename)
    {
        $path = storage_path("app/public/{$type}s/{$filename}");

        if (!file_exists($path)) {
            abort(404);
        }

        return response()->file($path);
    }
}
```

---

## 10. TESTING STRATEGY

### Backend API Testing

**tests/Feature/PropertyTest.php:**
```php
<?php
namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use App\Models\Property;
use Illuminate\Foundation\Testing\RefreshDatabase;

class PropertyTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_list_properties()
    {
        Property::factory()->count(5)->create();

        $response = $this->getJson('/api/properties');

        $response->assertStatus(200)
                 ->assertJsonCount(5);
    }

    public function test_can_create_property()
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)
                         ->postJson('/api/properties', [
                             'title' => 'Beautiful Villa',
                             'description' => 'Spacious villa in Douala',
                             'location' => 'Douala',
                             'price' => 50000000,
                             'property_type' => 'villa',
                             'bedrooms' => 4,
                             'bathrooms' => 3,
                         ]);

        $response->assertStatus(201)
                 ->assertJsonPath('title', 'Beautiful Villa');

        $this->assertDatabaseHas('properties', [
            'title' => 'Beautiful Villa',
            'user_id' => $user->_id
        ]);
    }

    public function test_cannot_create_property_without_auth()
    {
        $response = $this->postJson('/api/properties', [
            'title' => 'Test Property'
        ]);

        $response->assertStatus(401);
    }
}
```

### Frontend Testing (If using Blade)

**tests/Feature/PropertyPageTest.php:**
```php
<?php
namespace Tests\Feature;

use Tests\TestCase;
use App\Models\Property;

class PropertyPageTest extends TestCase
{
    public function test_properties_page_displays_properties()
    {
        $property = Property::factory()->create([
            'title' => 'Test Villa'
        ]);

        $response = $this->get('/properties');

        $response->assertStatus(200)
                 ->assertSee('Test Villa');
    }
}
```

---

## 11. ENVIRONMENT CONFIGURATION

### .env File

```env
APP_NAME=Habitere
APP_ENV=production
APP_KEY=base64:GENERATE_WITH_php_artisan_key:generate
APP_DEBUG=false
APP_URL=https://habitere.com

# Database
DB_CONNECTION=mongodb
DB_HOST=127.0.0.1
DB_PORT=27017
DB_DATABASE=habitere
DB_USERNAME=
DB_PASSWORD=

# JWT
JWT_SECRET=GENERATE_RANDOM_SECRET_KEY

# File Storage
FILESYSTEM_DISK=local

# Mail (optional)
MAIL_MAILER=smtp
MAIL_HOST=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=
MAIL_PASSWORD=

# CORS
CORS_ALLOWED_ORIGINS=https://habitere.com
```

---

## 12. DEPLOYMENT

### Server Requirements
- **PHP:** 8.2+
- **MongoDB:** 4.4+
- **Composer:** Latest
- **Web Server:** Nginx or Apache
- **SSL Certificate:** Let's Encrypt

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name habitere.com;
    root /var/www/habitere/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    index index.php;

    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

### Deployment Commands

```bash
# Install dependencies
composer install --optimize-autoloader --no-dev

# Generate app key
php artisan key:generate

# Cache config
php artisan config:cache
php artisan route:cache
php artisan view:cache

# Set permissions
chmod -R 755 storage
chmod -R 755 bootstrap/cache

# Create symbolic link for storage
php artisan storage:link

# Restart services
sudo systemctl restart php8.2-fpm
sudo systemctl restart nginx
```

---

## 13. ESTIMATED TIMELINE & EFFORT

| Phase | Duration | Complexity | Priority |
|-------|----------|------------|----------|
| Setup & Planning | 1 week | Low | Critical |
| Authentication System | 1 week | Medium | Critical |
| User Management | 3 days | Low | Critical |
| Property Module | 2 weeks | Medium | Critical |
| Services Module | 1 week | Medium | High |
| Bookings & Messages | 1 week | Medium | High |
| House Plans Module | 2 weeks | High | Medium |
| Subscription System | 1 week | Medium | Medium |
| Image Processing | 3 days | Low | Critical |
| PDF Generation | 3 days | Medium | Medium |
| Frontend Conversion | 4 weeks | High | Critical |
| Testing | 2 weeks | High | Critical |
| **TOTAL** | **14-16 weeks** | | |

---

## 14. RECOMMENDATIONS

### ✅ Recommended Approach
1. **Keep React frontend** with PHP backend API
   - Less work (30% of full conversion)
   - Better UX
   - Modern architecture

2. **Use Laravel framework**
   - Best PHP framework
   - Great documentation
   - MongoDB support
   - Built-in authentication

3. **Gradual migration**
   - Start with authentication
   - Then core features (properties, services)
   - Finally advanced features

### ⚠️ Challenges
1. **Floor plan generation** - Image processing in PHP is less powerful than Python/Pillow
2. **PDF generation** - TCPDF has less features than ReportLab
3. **Async operations** - PHP doesn't have native async like Python
4. **Type safety** - Python with Pydantic is stricter than PHP

### 💡 Alternatives
- Consider keeping Python backend and converting only frontend
- Use PHP for simple CRUD, keep Python microservice for complex operations (house plans)

---

## 15. SUPPORT & RESOURCES

### Documentation
- Laravel: https://laravel.com/docs
- MongoDB PHP: https://www.mongodb.com/docs/php-library/
- Intervention Image: https://image.intervention.io/
- TCPDF: https://tcpdf.org/
- JWT PHP: https://github.com/firebase/php-jwt

### Tools
- **PHPStorm:** Best PHP IDE
- **Postman:** API testing
- **MongoDB Compass:** Database GUI
- **Git:** Version control

---

## CONCLUSION

This guide provides a complete roadmap for converting the Habitere platform from FastAPI (Python) + React to PHP. The recommended approach is to:

1. ✅ Keep React frontend (update API endpoints only)
2. ✅ Convert backend to Laravel (PHP)
3. ✅ Use MongoDB with PHP driver
4. ✅ Start with authentication and core modules
5. ✅ Test thoroughly at each phase

**Estimated Total Time:** 14-16 weeks with 2 developers

**Complexity:** Medium-High (Due to image processing and PDF generation)

**Success Rate:** High (Laravel + MongoDB is well-documented and battle-tested)

---

**Document Version:** 1.0  
**Last Updated:** November 26, 2024  
**Author:** Antigravity Development Team
