"""
Authentication middleware for Flask API endpoints.
Provides decorators and utilities for token-based authentication.
"""

import os
from functools import wraps
from flask import request, jsonify, g
from typing import Optional, Tuple


class AuthMiddleware:
    """Flask authentication middleware for API token validation."""
    
    def __init__(self, token_manager):
        """Initialize with token manager instance."""
        self.token_manager = token_manager
        # Get system token from environment for persistent access
        self.system_token = os.getenv('ZEBRA_API_TOKEN')
    
    def _validate_token(self, token: str) -> Tuple[bool, str]:
        """Validate token - checks system token first, then database tokens."""
        if not token:
            return False, None
            
        # Check system token from environment first
        if self.system_token and token == self.system_token:
            return True, "system"
        
        # Fall back to database tokens
        is_valid, token_name = self.token_manager.validate_token(token)
        return is_valid, token_name or "unknown"
    
    def require_auth(self, f):
        """Decorator to require authentication for Flask routes."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self._extract_token_from_request()
            
            if not token:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'API token required. Provide via Authorization header, query param, or request body.'
                }), 401
            
            is_valid, token_name = self._validate_token(token)
            
            if not is_valid:
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'Invalid, expired, or revoked API token'
                }), 401
            
            # Store token info in Flask's g object for use in the route
            g.current_token = token_name
            g.authenticated = True
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def _extract_token_from_request(self) -> Optional[str]:
        """Extract token from Authorization header, query params, or request body."""
        # 1. Check Authorization header (Bearer token)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        # 2. Check query parameter
        token = request.args.get('token')
        if token:
            return token
        
        # 3. Check request body (JSON)
        if request.is_json:
            data = request.get_json()
            if data and 'token' in data:
                return data['token']
        
        return None
    
    def get_current_token_name(self) -> Optional[str]:
        """Get the name of the current authenticated token."""
        return getattr(g, 'current_token', None)
    
    def is_authenticated(self) -> bool:
        """Check if current request is authenticated."""
        return getattr(g, 'authenticated', False)