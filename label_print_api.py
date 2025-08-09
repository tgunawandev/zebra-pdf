#!/usr/bin/env python3
"""
Label Printing API Server
Local HTTP server that receives print requests from Odoo (cloud) and prints to local Zebra printer.
Secured with Bearer token authentication.
"""

from flask import Flask, request, jsonify, g
import logging
import subprocess
from datetime import datetime
import os
import sys

# Add the zebra_print module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zebra_print.auth.token_manager import TokenManager
from zebra_print.auth.middleware import AuthMiddleware

app = Flask(__name__)

# Initialize authentication
token_manager = TokenManager()
auth_middleware = AuthMiddleware(token_manager)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('print_api.log'),
        logging.StreamHandler()
    ]
)

PRINTER_NAME = "ZDesigner ZD230-203dpi ZPL"

def json_to_zpl(label_data):
    """
    Convert JSON label data directly to ZPL commands.
    Using simple format that matches working direct test.
    """
    logging.info(f"[PROCESS] Converting {len(label_data['labels'])} labels to ZPL")
    
    zpl_commands = []
    
    # Generate ZPL for each label using SIMPLE format like direct test
    for i, label in enumerate(label_data['labels']):
        zpl_commands.extend([
            "^XA",           # Start format
            "^PR2",          # Print speed
            "^MD5",          # Media darkness 
            "^JMA",          # Media type auto
            "^LH0,0",        # Label home position
            
            # Simple text layout (no QR code for now to test)
            f"^FO50,50^A0,16,16^FD{label.get('do_number', 'TEST-LABEL')}^FS",
            f"^FO50,80^A0,16,16^FD{label.get('customer', 'API Test')}^FS", 
            f"^FO50,110^A0,16,16^FD{label.get('date', '09/08/25')}^FS",
            f"^FO50,140^A0,16,16^FDQty: {label.get('qty', '1')} {label.get('uom', 'PCS')}^FS",
            
            "^XZ"            # End format
        ])
        
        # Add spacing between labels
        if i < len(label_data['labels']) - 1:
            zpl_commands.append("")
    
    zpl_string = "\n".join(zpl_commands)
    logging.info(f"[OK] Generated simple ZPL with {len(label_data['labels'])} labels")
    return zpl_string

def print_to_zebra(zpl_commands):
    """Send ZPL commands to Zebra printer using cross-platform approach."""
    try:
        logging.info(f"[PRINTER] Sending ZPL to {PRINTER_NAME}")
        
        # Import and use the cross-platform printer system
        try:
            from zebra_print.printer import get_zebra_printer
        except ImportError as import_error:
            logging.error(f"[ERROR] Failed to import zebra_print.printer: {import_error}")
            return False, f"Printer module import failed: {import_error}. Check Python path and zebra_print installation."
        
        printer_service = get_zebra_printer(PRINTER_NAME)
        success, message = printer_service.print_zpl(zpl_commands)
        
        if success:
            logging.info(f"[OK] ZPL printed successfully: {message}")
            return True, message
        else:
            logging.error(f"[ERROR] ZPL printing failed: {message}")
            return False, message
            
    except Exception as e:
        logging.error(f"[ERROR] Print error: {e}")
        return False, f"Print system error: {e}"

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
    """
    Main endpoint to receive print requests from Odoo.
    
    POST /print
    Content-Type: application/json
    {
        "labels": [
            {
                "qr_code": "01010101160",
                "do_number": "W-CPN/OUT/00002", 
                "route": "Route A",
                "date": "12/04/22",
                "customer": "Customer Name",
                "so_number": "SO-67890",
                "mo_number": "MO-12345",
                "item": "Product Name",
                "qty": "100",
                "uom": "PCS"
            }
        ]
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        
        # Validate data structure
        if 'labels' not in data:
            return jsonify({"error": "Missing 'labels' field"}), 400
        
        if not isinstance(data['labels'], list) or len(data['labels']) == 0:
            return jsonify({"error": "'labels' must be a non-empty array"}), 400
        
        # Validate each label
        required_fields = ['qr_code', 'do_number', 'route', 'date', 'customer', 'so_number', 'mo_number', 'item', 'qty', 'uom']
        for i, label in enumerate(data['labels']):
            for field in required_fields:
                if field not in label:
                    return jsonify({"error": f"Label {i}: missing '{field}' field"}), 400
        
        logging.info(f"[POST] Received print request for {len(data['labels'])} labels")
        
        # Convert to ZPL
        zpl = json_to_zpl(data)
        
        # Print to Zebra
        success, message = print_to_zebra(zpl)
        
        if success:
            response = {
                "success": True,
                "message": "Labels printed successfully",
                "labels_count": len(data['labels']),
                "job_info": message,
                "timestamp": datetime.now().isoformat()
            }
            logging.info(f"[OK] Print request completed successfully")
            return jsonify(response)
        else:
            response = {
                "success": False,
                "error": "Printing failed",
                "details": message,
                "timestamp": datetime.now().isoformat()
            }
            logging.error(f"[ERROR] Print request failed: {message}")
            return jsonify(response), 500
            
    except Exception as e:
        logging.error(f"[ERROR] Print request error: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/printer/status', methods=['GET'])
@auth_middleware.require_auth
def printer_status():
    """Check printer status using cross-platform approach."""
    try:
        try:
            from zebra_print.printer import get_zebra_printer
        except ImportError as import_error:
            logging.error(f"[ERROR] Failed to import zebra_print.printer: {import_error}")
            return jsonify({
                "printer": PRINTER_NAME,
                "status": "error",
                "details": f"Printer module import failed: {import_error}",
                "timestamp": datetime.now().isoformat()
            }), 500
        
        printer_service = get_zebra_printer(PRINTER_NAME)
        status = printer_service.get_status()
        
        # Map status to API response format
        if status.get('exists') and status.get('enabled'):
            api_status = "available"
            http_code = 200
        elif status.get('exists') and not status.get('enabled'):
            api_status = "disabled"
            http_code = 200
        elif not status.get('exists'):
            api_status = "not_found"
            http_code = 404
        else:
            api_status = "error"
            http_code = 500
            
        response_data = {
            "printer": PRINTER_NAME,
            "status": api_status,
            "details": {
                "exists": status.get('exists', False),
                "enabled": status.get('enabled', False),
                "accepting_jobs": status.get('accepting_jobs', False),
                "state": status.get('state', 'unknown'),
                "connection": status.get('connection', 'unknown'),
                "jobs_queued": status.get('jobs_queued', 0)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response_data), http_code
            
    except Exception as e:
        logging.error(f"[ERROR] Printer status check failed: {e}")
        return jsonify({
            "printer": PRINTER_NAME,
            "status": "error", 
            "details": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/auth/token', methods=['POST'])
def generate_token():
    """Generate a new API token. (Admin endpoint - no auth required for initial setup)"""
    try:
        data = request.get_json() if request.is_json else {}
        name = data.get('name', 'default')
        description = data.get('description')
        
        # For easier setup, allow token generation without auth initially
        # In production, you may want to enable this by changing False to True
        REQUIRE_AUTH_FOR_TOKEN_GENERATION = False
        
        if REQUIRE_AUTH_FOR_TOKEN_GENERATION:
            # If multiple tokens exist, require authentication
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
        try:
            new_token = token_manager.generate_token(name, description)
            
            return jsonify({
                'success': True,
                'token': new_token,
                'name': name,
                'message': 'Token generated successfully',
                'webhook_examples': {
                    'header': f'Authorization: Bearer {new_token}',
                    'query': f'/print?token={new_token}',
                    'body': f'{{"token": "{new_token}", "labels": [...]}}'
                }
            })
        except ValueError as e:
            return jsonify({
                'error': 'Token generation failed',
                'message': str(e)
            }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Token generation failed',
            'details': str(e)
        }), 500

@app.route('/auth/tokens', methods=['GET'])
@auth_middleware.require_auth  
def list_tokens():
    """List all API tokens (without revealing token values)."""
    try:
        tokens = token_manager.get_all_tokens()
        return jsonify({
            'success': True,
            'tokens': tokens,
            'current_token': g.current_token
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to list tokens',
            'details': str(e)
        }), 500

@app.route('/auth/token/<name>', methods=['DELETE'])
@auth_middleware.require_auth
def revoke_token(name):
    """Revoke a token by name."""
    try:
        success = token_manager.revoke_token(name)
        if success:
            return jsonify({
                'success': True,
                'message': f'Token "{name}" revoked successfully'
            })
        else:
            return jsonify({
                'error': 'Token not found',
                'message': f'No token named "{name}" found'
            }), 404
    except Exception as e:
        return jsonify({
            'error': 'Failed to revoke token',
            'details': str(e)
        }), 500

@app.route('/auth/info', methods=['GET'])
def auth_info():
    """Get authentication information and token count."""
    try:
        tokens = token_manager.get_all_tokens()
        active_tokens = [t for t in tokens if t['is_active']]
        
        return jsonify({
            'authentication_enabled': True,
            'total_tokens': len(tokens),
            'active_tokens': len(active_tokens),
            'tokens': tokens,
            'endpoints': {
                'protected': ['/print', '/printer/status', '/auth/tokens'],
                'public': ['/health', '/auth/info', '/auth/token'],
                'auth_methods': ['Authorization: Bearer token', 'Query: ?token=', 'Body: {"token": ""}']
            }
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to get auth info',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    logging.info("[START] Starting Label Printing API Server")
    logging.info(f"[BROWSER] Printer: {PRINTER_NAME}")
    logging.info("[URL] Endpoints:")
    logging.info("   POST /print - Print labels ([AUTH] AUTH REQUIRED)")
    logging.info("   GET /health - Health check (public)")
    logging.info("   GET /printer/status - Printer status ([AUTH] AUTH REQUIRED)")
    logging.info("   POST /auth/token - Generate API token")
    logging.info("   GET /auth/tokens - List tokens ([AUTH] AUTH REQUIRED)")
    logging.info("   DELETE /auth/token/<name> - Revoke token ([AUTH] AUTH REQUIRED)")
    
    # Ensure default token exists on startup
    tokens = token_manager.get_all_tokens()
    if not tokens:
        default_token = token_manager.generate_token("default", "Default API access token")
        logging.info(f"[TOKEN] Generated default API token: {default_token}")
        logging.info("[AUTH] SAVE THIS TOKEN - you'll need it for webhook authentication!")
    else:
        logging.info("[AUTH] API authentication enabled - tokens required for protected endpoints")
    
    app.run(host='0.0.0.0', port=5000, debug=False)