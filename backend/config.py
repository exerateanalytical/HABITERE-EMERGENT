"""
Configuration Module
====================
Centralized configuration management for Habitere platform.

This module handles:
- Environment variable loading
- Application settings
- Database configuration
- External service configuration (SendGrid, Google OAuth, etc.)

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Application Settings
    
    Loads and validates all configuration from environment variables.
    Provides type-safe access to configuration values.
    """
    
    # ==================== DATABASE CONFIGURATION ====================
    MONGO_URL: str = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME: str = os.environ.get('DB_NAME', 'test_database')
    
    # ==================== SECURITY & AUTH ====================
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_SECRET: str = os.environ.get('JWT_SECRET', SECRET_KEY)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # ==================== GOOGLE OAUTH CONFIGURATION ====================
    GOOGLE_CLIENT_ID: Optional[str] = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET: Optional[str] = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI: Optional[str] = os.environ.get('GOOGLE_REDIRECT_URI')
    
    # ==================== SENDGRID EMAIL CONFIGURATION ====================
    SENDGRID_API_KEY: Optional[str] = os.environ.get('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL: str = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@habitere.com')
    SENDGRID_FROM_NAME: str = os.environ.get('SENDGRID_FROM_NAME', 'Habitere')
    
    # ==================== APPLICATION SETTINGS ====================
    FRONTEND_URL: str = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    ENVIRONMENT: str = os.environ.get('ENVIRONMENT', 'development')
    
    # Cookie settings - environment aware
    SECURE_COOKIES: bool = ENVIRONMENT == 'production'
    SAMESITE_COOKIES: str = 'None' if ENVIRONMENT == 'production' else 'lax'
    
    # ==================== FILE UPLOAD SETTINGS ====================
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: set = {
        'image/jpeg',
        'image/jpg', 
        'image/png',
        'image/gif',
        'image/webp'
    }
    
    # ==================== MTN MOMO CONFIGURATION ====================
    MTN_MOMO_SUBSCRIPTION_KEY: Optional[str] = os.environ.get('MTN_MOMO_SUBSCRIPTION_KEY')
    MTN_MOMO_API_USER: Optional[str] = os.environ.get('MTN_MOMO_API_USER')
    MTN_MOMO_API_KEY: Optional[str] = os.environ.get('MTN_MOMO_API_KEY')
    MTN_MOMO_ENVIRONMENT: str = os.environ.get('MTN_MOMO_ENVIRONMENT', 'sandbox')
    MTN_MOMO_BASE_URL: str = "https://sandbox.momodeveloper.mtn.com" if MTN_MOMO_ENVIRONMENT == 'sandbox' else "https://momodeveloper.mtn.com"
    
    # ==================== LOGGING CONFIGURATION ====================
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')


# Singleton instance
settings = Settings()


# ==================== HELPER FUNCTIONS ====================

def get_database_url() -> str:
    """
    Get the complete MongoDB connection URL.
    
    Returns:
        str: Full MongoDB connection string
    """
    return settings.MONGO_URL


def is_production() -> bool:
    """
    Check if running in production environment.
    
    Returns:
        bool: True if production, False otherwise
    """
    return settings.ENVIRONMENT == 'production'


def is_development() -> bool:
    """
    Check if running in development environment.
    
    Returns:
        bool: True if development, False otherwise
    """
    return settings.ENVIRONMENT == 'development'
