#!/usr/bin/env python3
"""
Zebra Label Printing FastAPI Server
Modern API server with auto-documentation for Zebra printer integration.
Secured with Bearer token authentication.
"""

import logging
import subprocess
import sys
import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

# Add the zebra_print module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zebra_print.auth.token_manager import TokenManager
from zebra_print.api.models import (
    PrintRequest, PrintResponse, HealthResponse, PrinterStatusResponse,
    TokenRequest, TokenResponse, TokenListResponse, AuthInfoResponse,
    ErrorResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="Zebra Label Printing API",
    description="API for printing labels to Zebra printers with ZPL support",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()

# Initialize authentication
token_manager = TokenManager()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('print_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_zebra_printer_name():
    """Auto-detect Zebra printer from CUPS."""
    try:
        result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                # Look for printer lines that contain Zebra keywords
                if line.startswith('printer ') and any(keyword in line.lower() for keyword in ['zebra', 'ztc', 'zd230']):
                    # Extract printer name from "printer NAME ..."
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
            
            # If no Zebra printer found, return the first available printer
            for line in lines:
                if line.startswith('printer '):
                    parts = line.split()
                    if len(parts) >= 2:
                        logger.warning(f"No Zebra printer found, using: {parts[1]}")
                        return parts[1]
                        
    except Exception as e:
        logger.error(f"Failed to detect printer: {e}")
    
    # Fallback to default
    return "ZTC-ZD230-203dpi-ZPL"

PRINTER_NAME = get_zebra_printer_name()
logger.info(f"[INIT] Using printer: {PRINTER_NAME}")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Bearer token authentication."""
    token = credentials.credentials
    is_valid, token_name = token_manager.validate_token(token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"token": token, "name": token_name}

def json_to_zpl(label_data: dict) -> str:
    """
    Convert JSON label data directly to ZPL commands.
    No PDF processing needed!
    """
    logger.info(f"[PROCESS] Converting {len(label_data['labels'])} labels to ZPL")
    
    zpl_commands = []
    
    # Printer initialization (once at the beginning)
    zpl_commands.extend([
        "^XA",
        "^JUS",      # Auto-detect label length
        "^MMT",      # Set media type to thermal transfer
        "^MNY",      # Set continuous media
        "^MTT",      # Set media type to thermal transfer
        "^PON",      # Print orientation normal
        "^PMN",      # Print mode normal
        "^LRN",      # Label reverse normal
        "^CI0",      # Change international font/encoding
        "^XZ",
        ""           # Blank line separator
    ])
    
    # Generate ZPL for each label
    for i, label in enumerate(label_data['labels']):
        zpl_commands.extend([
            "^XA",           # Start format
            
            # CALIBRATION AND POSITIONING COMMANDS
            "^LL236",        # Set label length to 236 dots (30mm)
            "^PW394",        # Set print width to 394 dots (50mm) 
            "^LH0,0",        # Set label home position (top-left)
            "^LT8",          # Set label top margin to 8 dots (reduced from 20)
            "^PR2",          # Set print speed to 2 inches/second (slower for accuracy)
            "^MD5",          # Set media darkness to 5 (medium)
            "^JMA",          # Set media type to auto-detect
            
            # QR code only (no text) - repositioned to (25,40)
            f"^FO25,40^BQN,2,5^FDLA,{label['qr_code']}^FS",
            
            # TEXT FIELDS WITH NEW LAYOUT - 18x18 SIZE (9 fields, no qr_code text)
            f"^FO180,50^A0N,18,18^FD{label['do_number']}^FS",      # DO Number
            f"^FO180,75^A0N,18,18^FD{label['route']} {label['date']}^FS",        # Route + Date
            f"^FO180,100^A0N,18,18^FD{label['customer']}^FS",      # Customer
            f"^FO180,125^A0N,18,18^FD{label['so_number']} {label['mo_number']}^FS",  # SO + MO Number
            f"^FO180,150^A0N,18,18^FD{label['item']}^FS",          # Item
            f"^FO180,175^A0N,18,18^FD{label['qty']} {label['uom']}^FS",  # Qty + UOM
            
            "^XZ"            # End format
        ])
        
        # Add spacing between labels
        if i < len(label_data['labels']) - 1:
            zpl_commands.append("")
    
    zpl_string = "\n".join(zpl_commands)
    logger.info(f"[OK] Generated ZPL with {len(label_data['labels'])} labels")
    return zpl_string

def print_to_zebra(zpl_commands: str):
    """Send ZPL commands to Zebra printer using cross-platform approach."""
    try:
        logger.info(f"[PRINTER] Sending ZPL to {PRINTER_NAME}")
        
        # Import and use the cross-platform printer system
        try:
            from zebra_print.printer import get_zebra_printer
        except ImportError as import_error:
            logger.error(f"[ERROR] Failed to import zebra_print.printer: {import_error}")
            return False, f"Printer module import failed: {import_error}. Check Python path and zebra_print installation."
        
        # Re-detect printer in case it changed
        current_printer = get_zebra_printer_name()
        logger.info(f"[PRINTER] Using detected printer: {current_printer}")
        printer_service = get_zebra_printer(current_printer)
        success, message = printer_service.print_zpl(zpl_commands)
        
        if success:
            logger.info(f"[OK] ZPL printed successfully: {message}")
            return True, message
        else:
            logger.error(f"[ERROR] ZPL printing failed: {message}")
            return False, message
            
    except Exception as e:
        logger.error(f"[ERROR] Print error: {e}")
        return False, f"Print system error: {e}"

# API Endpoints

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint - redirects to API documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        printer=PRINTER_NAME
    )

@app.post("/print", 
         response_model=PrintResponse, 
         responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
         tags=["Printing"])
async def print_labels(
    request: PrintRequest,
    auth: dict = Depends(verify_token)
):
    """
    Print labels to Zebra printer.
    
    This endpoint receives label data and prints them directly to the configured Zebra printer
    using ZPL (Zebra Programming Language) commands.
    """
    try:
        logger.info(f"[POST] Received print request for {len(request.labels)} labels from token: {auth['name']}")
        
        # Convert to ZPL
        label_data = {"labels": [label.dict() for label in request.labels]}
        zpl = json_to_zpl(label_data)
        
        # Print to Zebra
        success, message = print_to_zebra(zpl)
        
        if success:
            logger.info(f"[OK] Print request completed successfully")
            return PrintResponse(
                success=True,
                message="Labels printed successfully",
                labels_count=len(request.labels),
                job_info=message,
                timestamp=datetime.now().isoformat()
            )
        else:
            logger.error(f"[ERROR] Print request failed: {message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Printing failed: {message}"
            )
            
    except Exception as e:
        logger.error(f"[ERROR] Print request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/printer/status", 
         response_model=PrinterStatusResponse, 
         responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
         tags=["Printer"])
async def printer_status(auth: dict = Depends(verify_token)):
    """Check printer status using cross-platform approach."""
    try:
        try:
            from zebra_print.printer import get_zebra_printer
        except ImportError as import_error:
            logger.error(f"[ERROR] Failed to import zebra_print.printer: {import_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Printer module import failed: {import_error}"
            )
        
        # Re-detect printer in case it changed
        current_printer = get_zebra_printer_name()
        logger.info(f"[PRINTER] Using detected printer: {current_printer}")
        printer_service = get_zebra_printer(current_printer)
        status_info = printer_service.get_status()
        
        # Map status to API response format
        if status_info.get('exists') and status_info.get('enabled'):
            api_status = "available"
        elif status_info.get('exists') and not status_info.get('enabled'):
            api_status = "disabled"
        elif not status_info.get('exists'):
            api_status = "not_found"
        else:
            api_status = "error"
            
        return PrinterStatusResponse(
            printer=PRINTER_NAME,
            status=api_status,
            details={
                "exists": status_info.get('exists', False),
                "enabled": status_info.get('enabled', False),
                "accepting_jobs": status_info.get('accepting_jobs', False),
                "state": status_info.get('state', 'unknown'),
                "connection": status_info.get('connection', 'unknown'),
                "jobs_queued": status_info.get('jobs_queued', 0)
            },
            timestamp=datetime.now().isoformat()
        )
            
    except Exception as e:
        logger.error(f"[ERROR] Printer status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Printer status check failed: {str(e)}"
        )

@app.post("/auth/token", response_model=TokenResponse, tags=["Authentication"])
async def generate_token(request: TokenRequest):
    """Generate a new API token. (Admin endpoint - no auth required for initial setup)"""
    try:
        # For easier setup, allow token generation without auth initially
        # In production, you may want to enable this by changing False to True
        REQUIRE_AUTH_FOR_TOKEN_GENERATION = False
        
        if REQUIRE_AUTH_FOR_TOKEN_GENERATION:
            # This would require authentication - implement if needed
            pass
        
        # Generate new token
        try:
            new_token = token_manager.generate_token(request.name, request.description)
            
            return TokenResponse(
                success=True,
                token=new_token,
                name=request.name,
                message="Token generated successfully",
                webhook_examples={
                    "header": f"Authorization: Bearer {new_token}",
                    "query": f"/print?token={new_token}",
                    "body": f'{{"token": "{new_token}", "labels": [...]}}'
                }
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token generation failed: {str(e)}"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token generation failed: {str(e)}"
        )

@app.get("/auth/tokens", response_model=TokenListResponse, tags=["Authentication"])
async def list_tokens(auth: dict = Depends(verify_token)):
    """List all API tokens (without revealing token values)."""
    try:
        tokens = token_manager.get_all_tokens()
        return TokenListResponse(
            success=True,
            tokens=tokens,
            current_token=auth['name']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tokens: {str(e)}"
        )

@app.delete("/auth/token/{name}", tags=["Authentication"])
async def revoke_token(name: str, auth: dict = Depends(verify_token)):
    """Revoke a token by name."""
    try:
        success = token_manager.revoke_token(name)
        if success:
            return {"success": True, "message": f'Token "{name}" revoked successfully'}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'No token named "{name}" found'
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke token: {str(e)}"
        )

@app.get("/auth/info", response_model=AuthInfoResponse, tags=["Authentication"])
async def auth_info():
    """Get authentication information and token count."""
    try:
        tokens = token_manager.get_all_tokens()
        active_tokens = [t for t in tokens if t['is_active']]
        
        return AuthInfoResponse(
            authentication_enabled=True,
            total_tokens=len(tokens),
            active_tokens=len(active_tokens),
            tokens=tokens,
            endpoints={
                "protected": ["/print", "/printer/status", "/auth/tokens"],
                "public": ["/health", "/auth/info", "/auth/token"],
                "auth_methods": ["Authorization: Bearer token", "Query: ?token=", "Body: {\"token\": \"\"}"]
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get auth info: {str(e)}"
        )

if __name__ == '__main__':
    import uvicorn
    
    logger.info("[START] Starting Zebra Label Printing FastAPI Server")
    logger.info(f"[PRINTER] Printer: {PRINTER_NAME}")
    logger.info("[URL] API Documentation:")
    logger.info("   📋 OpenAPI Docs: http://localhost:5000/docs")
    logger.info("   📖 ReDoc: http://localhost:5000/redoc")
    logger.info("   🔗 OpenAPI JSON: http://localhost:5000/openapi.json")
    logger.info("[URL] Endpoints:")
    logger.info("   POST /print - Print labels (🔒 AUTH REQUIRED)")
    logger.info("   GET /health - Health check (public)")
    logger.info("   GET /printer/status - Printer status (🔒 AUTH REQUIRED)")
    logger.info("   POST /auth/token - Generate API token")
    logger.info("   GET /auth/tokens - List tokens (🔒 AUTH REQUIRED)")
    logger.info("   DELETE /auth/token/<name> - Revoke token (🔒 AUTH REQUIRED)")
    
    # Ensure default token exists on startup
    tokens = token_manager.get_all_tokens()
    if not tokens:
        default_token = token_manager.generate_token("default", "Default API access token")
        logger.info(f"[TOKEN] Generated default API token: {default_token}")
        logger.info("[AUTH] SAVE THIS TOKEN - you'll need it for webhook authentication!")
    else:
        logger.info("[AUTH] API authentication enabled - tokens required for protected endpoints")
    
    uvicorn.run(app, host='0.0.0.0', port=5000, log_level="info")