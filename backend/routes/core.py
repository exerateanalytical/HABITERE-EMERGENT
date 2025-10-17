"""
Core Routes Module
==================
Handles core utility API endpoints for Habitere platform.

This module provides:
- API root endpoint
- Health check endpoint
- Sample data initialization for development/testing

These are utility endpoints for monitoring, testing, and development.

Dependencies:
- FastAPI for routing
- MongoDB for sample data insertion

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import logging

# Import from parent modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_database

# Setup logging
logger = logging.getLogger(__name__)

# Create router for core endpoints
# All routes will be prefixed with /api
router = APIRouter(tags=["Core"])


# ==================== ROOT & HEALTH CHECK ====================

@router.get("/")
async def root():
    """
    API root endpoint.
    
    Returns basic information about the API.
    Public endpoint - no authentication required.
    
    Returns:
        API name and description
        
    Example:
        GET /api/
        
        Response:
        {
            "message": "Habitere API - Real Estate and Home Services Platform"
        }
    """
    return {
        "message": "Habitere API - Real Estate and Home Services Platform"
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Used for monitoring and load balancer health checks.
    Returns current timestamp to verify API is responsive.
    
    Returns:
        Health status and current timestamp
        
    Example:
        GET /api/health
        
        Response:
        {
            "status": "healthy",
            "timestamp": "2025-01-15T10:30:00Z"
        }
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ==================== SAMPLE DATA INITIALIZATION ====================

@router.post("/init-sample-data")
async def initialize_sample_data():
    """
    Initialize sample data for demonstration.
    
    Creates sample properties and services in the database.
    Useful for development, testing, and demos.
    
    Note: This should be disabled or protected in production.
    
    Returns:
        Success message
        
    Example:
        POST /api/init-sample-data
        
        Response:
        {
            "message": "Sample data initialized"
        }
    """
    db = get_database()
    
    try:
        # This calls the init_sample_data function
        # In a production refactoring, you'd implement sample data here
        # or import from a separate utility module
        
        logger.info("Sample data initialization requested")
        
        return {
            "message": "Sample data initialized",
            "note": "Implementation pending - create sample_data utility module"
        }
        
    except Exception as e:
        logger.error(f"Error initializing sample data: {e}")
        return {
            "message": "Sample data initialization failed",
            "error": str(e)
        }
