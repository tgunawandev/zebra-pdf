#!/usr/bin/env python3
"""
Standalone Label Printing API Server (without UI dependencies)
"""

from flask import Flask, request, jsonify, g
import logging
import subprocess
from datetime import datetime
import os
import sys
import sqlite3
import secrets
import hashlib
from typing import Dict, List, Optional, Tuple
import json
from functools import wraps

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/print_api.log'),
        logging.StreamHandler()
    ]
)

PRINTER_NAME = "ZTC-ZD230-203dpi-ZPL"

class TokenManager:
    def __init__(self, db_path: str = "/app/data/zebra_print.db"):
        self.db_path = db_path
        self.TOKEN_PREFIX = "zpt_"
        self.TOKEN_LENGTH = 32
        self._ensure_tables()
    
    def _get_connection(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return sqlite3.connect(self.db_path)
    
    def _ensure_tables(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    token_hash TEXT NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP
                )
            """)
            conn.commit()
    
    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
    
    def generate_token(self, name: str = "default", description: str = None) -> str:
        random_part = secrets.token_hex(self.TOKEN_LENGTH)
        token = f"{self.TOKEN_PREFIX}{random_part}"
        token_hash = self._hash_token(token)
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO api_tokens (name, token_hash, description)
                VALUES (?, ?, ?)
            """, (name, token_hash, description))
            conn.commit()
        
        return token
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[str]]:
        if not token or not token.startswith(self.TOKEN_PREFIX):
            return False, None
        
        token_hash = self._hash_token(token)
        
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM api_tokens 
                WHERE token_hash = ? AND is_active = 1
            """, (token_hash,))
            
            result = cursor.fetchone()
            if result:
                # Update last_used
                conn.execute("""
                    UPDATE api_tokens 
                    SET last_used = CURRENT_TIMESTAMP 
                    WHERE token_hash = ?
                """, (token_hash,))
                conn.commit()
                return True, result[0]
        
        return False, None
    
    def get_all_tokens(self) -> List[Dict]:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT name, description, is_active, created_at, last_used
                FROM api_tokens ORDER BY created_at DESC
            """)
            
            tokens = []
            for row in cursor.fetchall():
                tokens.append({
                    'name': row[0],
                    'description': row[1],
                    'is_active': bool(row[2]),
                    'created_at': row[3],
                    'last_used': row[4]
                })
            
            return tokens

class AuthMiddleware:
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager
    
    def require_auth(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Try Authorization header first
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
                is_valid, token_name = self.token_manager.validate_token(token)
                if is_valid:
                    g.current_token = token_name
                    return f(*args, **kwargs)
            
            # Try query parameter
            token = request.args.get('token')
            if token:
                is_valid, token_name = self.token_manager.validate_token(token)
                if is_valid:
                    g.current_token = token_name
                    return f(*args, **kwargs)
            
            # Try request body
            if request.is_json:
                data = request.get_json()
                token = data.get('token') if data else None
                if token:
                    is_valid, token_name = self.token_manager.validate_token(token)
                    if is_valid:
                        g.current_token = token_name
                        return f(*args, **kwargs)
            
            return jsonify({'error': 'Authentication required', 'message': 'Valid API token required'}), 401
        
        return decorated_function

# Initialize services
token_manager = TokenManager()
auth_middleware = AuthMiddleware(token_manager)

def json_to_zpl(label_data):
    """Convert JSON label data to ZPL commands."""
    logging.info(f"🔄 Converting {len(label_data['labels'])} labels to ZPL")
    
    zpl_commands = []
    
    # Printer initialization
    zpl_commands.extend([
        "^XA", "^JUS", "^MMT", "^MNY", "^MTT", "^PON", "^PMN", "^LRN", "^CI0", "^XZ", ""
    ])
    
    # Generate ZPL for each label
    for i, label in enumerate(label_data['labels']):
        zpl_commands.extend([
            "^XA",
            "^LL236", "^PW394", "^LH0,0", "^LT0", "^PR2", "^MD5", "^JMA",
            f"^FO30,30^BQN,2,5^FDLA,{label['qr_code']}^FS",
            f"^FO145,35^A0N,16,16^FD{label['title']}^FS",
            f"^FO145,60^A0N,16,16^FD{label['date']}^FS",
            f"^FO145,85^A0N,16,16^FD{label['qr_code']}^FS",
            "^XZ"
        ])
        
        if i < len(label_data['labels']) - 1:
            zpl_commands.append("")
    
    return "\n".join(zpl_commands)

def print_to_zebra(zpl_commands, printer_name=None):
    """Send ZPL commands to Zebra printer."""
    target_printer = printer_name or PRINTER_NAME
    
    try:
        logging.info(f"🖨️ Sending ZPL to {target_printer}")
        
        process = subprocess.Popen(
            ['lp', '-d', target_printer, '-o', 'raw'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(input=zpl_commands.encode('utf-8'), timeout=30)
        
        if process.returncode == 0:
            job_info = stdout.decode().strip()
            logging.info(f"✅ ZPL printed successfully: {job_info}")
            return True, job_info
        else:
            error_msg = stderr.decode()
            logging.error(f"❌ ZPL printing failed: {error_msg}")
            return False, error_msg
            
    except Exception as e:
        logging.error(f"❌ ZPL printing error: {e}")
        return False, str(e)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "printer": PRINTER_NAME
    })

@app.route('/print', methods=['POST'])
@auth_middleware.require_auth
def print_labels():
    """Print labels endpoint."""
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        
        if 'labels' not in data:
            return jsonify({"error": "Missing 'labels' field"}), 400
        
        if not isinstance(data['labels'], list) or len(data['labels']) == 0:
            return jsonify({"error": "'labels' must be a non-empty array"}), 400
        
        required_fields = ['title', 'date', 'qr_code']
        for i, label in enumerate(data['labels']):
            for field in required_fields:
                if field not in label:
                    return jsonify({"error": f"Label {i}: missing '{field}' field"}), 400
        
        logging.info(f"📨 Received print request for {len(data['labels'])} labels")
        
        # Convert to ZPL
        zpl = json_to_zpl(data)
        
        # Print to Zebra
        success, message = print_to_zebra(zpl)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Labels printed successfully",
                "labels_count": len(data['labels']),
                "job_info": message,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Printing failed",
                "details": message,
                "timestamp": datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logging.error(f"❌ Print request error: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/auth/token', methods=['POST'])
def generate_token():
    """Generate a new API token."""
    try:
        data = request.get_json() if request.is_json else {}
        name = data.get('name', 'default')
        description = data.get('description')
        
        # Check if authentication is needed (if multiple tokens exist)
        existing_tokens = token_manager.get_all_tokens()
        needs_auth = len(existing_tokens) > 1
        
        if needs_auth:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'Token generation requires valid API token for security'
                }), 401
            
            token = auth_header[7:]
            is_valid, _ = token_manager.validate_token(token)
            if not is_valid:
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'Invalid or revoked API token'
                }), 401
        
        # Generate new token
        new_token = token_manager.generate_token(name, description)
        
        return jsonify({
            'success': True,
            'token': new_token,
            'name': name,
            'message': 'Token generated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Token generation failed',
            'details': str(e)
        }), 500

@app.route('/templates', methods=['GET'])
def list_templates():
    """List available templates."""
    return jsonify({
        'success': True,
        'templates': [
            {
                'name': 'standard',
                'description': 'Standard QR code label with title, date, and QR code',
                'required_fields': ['title', 'date', 'qr_code'],
                'label_size': '30x50mm'
            }
        ]
    })

@app.route('/printers', methods=['GET'])
def list_printers():
    """List available printers."""
    try:
        result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True, timeout=10)
        printers = []
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('printer '):
                    parts = line.split()
                    if len(parts) >= 4:
                        printers.append({
                            'name': parts[1],
                            'status': parts[3],
                            'type': 'zebra' if 'zebra' in parts[1].lower() or 'ztc' in parts[1].lower() else 'other'
                        })
        
        return jsonify({
            'success': True,
            'printers': printers,
            'default_printer': PRINTER_NAME
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to list printers',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    logging.info("🚀 Starting Standalone Label Printing API Server")
    
    # Ensure default token exists
    tokens = token_manager.get_all_tokens()
    if not tokens:
        default_token = token_manager.generate_token("default", "Default API access token")
        logging.info(f"🔑 Generated default API token: {default_token}")
    
    app.run(host='0.0.0.0', port=5001, debug=False)