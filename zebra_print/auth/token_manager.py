"""
Token Manager for Zebra Print API authentication.
Handles token generation, validation, storage, and management.
"""

import json
import secrets
import string
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os


class TokenManager:
    """Manages API tokens for authentication."""
    
    def __init__(self, storage_file: str = '/app/data/api_tokens.json'):
        """Initialize token manager with storage file."""
        self.storage_file = storage_file
        self._ensure_storage_dir()
        self._load_tokens()
    
    def _ensure_storage_dir(self):
        """Ensure the storage directory exists."""
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
    
    def _load_tokens(self):
        """Load tokens from storage file."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    self.tokens = json.load(f)
            else:
                self.tokens = {}
        except Exception:
            self.tokens = {}
    
    def _save_tokens(self):
        """Save tokens to storage file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.tokens, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save tokens: {e}")
    
    def _generate_token_value(self) -> str:
        """Generate a secure random token."""
        alphabet = string.ascii_letters + string.digits
        token_part = ''.join(secrets.choice(alphabet) for _ in range(32))
        return f"zp_{token_part}"
    
    def generate_token(self, name: str, description: str = None) -> str:
        """Generate a new API token."""
        if name in self.tokens:
            raise ValueError(f"Token with name '{name}' already exists")
        
        token_value = self._generate_token_value()
        token_data = {
            'name': name,
            'token_hash': self._hash_token(token_value),
            'description': description,
            'created_at': datetime.now().isoformat(),
            'last_used': None,
            'is_active': True
        }
        
        self.tokens[name] = token_data
        self._save_tokens()
        
        return token_value
    
    def _hash_token(self, token: str) -> str:
        """Hash token for secure storage."""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """Validate a token and return (is_valid, token_name)."""
        if not token or not token.startswith('zp_'):
            return False, None
        
        token_hash = self._hash_token(token)
        
        for name, token_data in self.tokens.items():
            if (token_data['token_hash'] == token_hash and 
                token_data['is_active']):
                
                # Update last used timestamp
                token_data['last_used'] = datetime.now().isoformat()
                self._save_tokens()
                
                return True, name
        
        return False, None
    
    def revoke_token(self, name: str) -> bool:
        """Revoke a token by name."""
        if name not in self.tokens:
            return False
        
        self.tokens[name]['is_active'] = False
        self._save_tokens()
        return True
    
    def get_all_tokens(self) -> List[Dict]:
        """Get information about all tokens (without revealing token values)."""
        result = []
        for name, token_data in self.tokens.items():
            result.append({
                'name': name,
                'description': token_data.get('description'),
                'created_at': token_data['created_at'],
                'last_used': token_data['last_used'],
                'is_active': token_data['is_active']
            })
        return result
    
    def get_token_info(self, name: str) -> Optional[Dict]:
        """Get information about a specific token."""
        if name not in self.tokens:
            return None
        
        token_data = self.tokens[name]
        return {
            'name': name,
            'description': token_data.get('description'),
            'created_at': token_data['created_at'],
            'last_used': token_data['last_used'],
            'is_active': token_data['is_active']
        }