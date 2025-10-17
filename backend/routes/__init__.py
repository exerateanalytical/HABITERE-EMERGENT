"""
Routes Package
===============
Modular route handlers for Habitere API.

This package contains all API route modules organized by feature:
- auth.py: Authentication (login, register, OAuth, password reset)
- properties.py: Property management (CRUD, filtering, cleanup)
- services.py: Professional services management
- users.py: User profile management
- bookings.py: Booking system (property viewings, service bookings)
- messages.py: Real-time messaging system
- reviews.py: Reviews and ratings system
- core.py: Core utilities (health checks, root endpoint)
- images.py: Image upload and management
- payments.py: Payment processing (MTN MoMo)

Each module exports a FastAPI APIRouter that can be included in the main app.

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

# Import all route modules for easy access
from . import (
    auth,
    properties,
    services,
    users,
    bookings,
    messages,
    reviews,
    core,
    images,
    payments
)

__all__ = [
    "auth",
    "properties",
    "services",
    "users",
    "bookings",
    "messages",
    "reviews",
    "core",
    "images",
    "payments"
]
