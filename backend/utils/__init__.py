"""
Utilities Package
=================
Common utility modules for Habitere backend.

This package includes:
- auth.py: Authentication utilities and middleware
- helpers.py: Helper functions for serialization and data transformation

Author: Habitere Development Team
Last Modified: 2025-10-17
"""

from .auth import get_current_user, get_current_user_optional, require_admin, check_ownership
from .helpers import serialize_doc, prepare_for_mongo, parse_from_mongo, validate_uuid, paginate_results

__all__ = [
    # Authentication utilities
    "get_current_user",
    "get_current_user_optional",
    "require_admin",
    "check_ownership",
    
    # Helper utilities
    "serialize_doc",
    "prepare_for_mongo",
    "parse_from_mongo",
    "validate_uuid",
    "paginate_results",
]
