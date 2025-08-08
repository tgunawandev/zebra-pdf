#!/usr/bin/env python3
"""
Label Printing API Server
Local HTTP server that receives print requests from Odoo (cloud) and prints to local Zebra printer.
"""

from flask import Flask, request, jsonify
import logging
import subprocess
from datetime import datetime
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('print_api.log'),
        logging.StreamHandler()
    ]
)

PRINTER_NAME = "ZTC-ZD230-203dpi-ZPL"

def json_to_zpl(label_data):
    """
    Convert JSON label data directly to ZPL commands.
    No PDF processing needed!
    
    Expected JSON format:
    {
        "labels": [
            {"title": "W-CPN/OUT/00002", "date": "12/04/22", "qr_code": "01010101160"},
            {"title": "W-CPN/OUT/00003", "date": "12/04/22", "qr_code": "01010101161"}
        ]
    }
    """
    logging.info(f"🔄 Converting {len(label_data['labels'])} labels to ZPL")
    
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
            "^LT0",          # Set label top margin to 0
            "^PR2",          # Set print speed to 2 inches/second (slower for accuracy)
            "^MD5",          # Set media darkness to 5 (medium)
            "^JMA",          # Set media type to auto-detect
            
            # QR code
            f"^FO30,30^BQN,2,5^FDLA,{label['qr_code']}^FS",
            
            # ALL TEXT WITH CONSISTENT 16x16 SIZE
            f"^FO145,35^A0N,16,16^FD{label['title']}^FS",      # Title
            f"^FO145,60^A0N,16,16^FD{label['date']}^FS",       # Date
            f"^FO145,85^A0N,16,16^FD{label['qr_code']}^FS",    # QR code number
            
            "^XZ"            # End format
        ])
        
        # Add spacing between labels
        if i < len(label_data['labels']) - 1:
            zpl_commands.append("")
    
    zpl_string = "\n".join(zpl_commands)
    logging.info(f"✅ Generated ZPL with {len(label_data['labels'])} labels")
    return zpl_string

def print_to_zebra(zpl_commands):
    """Send ZPL commands to Zebra printer."""
    try:
        logging.info(f"🖨️  Sending ZPL to {PRINTER_NAME}")
        
        process = subprocess.Popen(
            ['lp', '-d', PRINTER_NAME, '-o', 'raw'],
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
def print_labels():
    """
    Main endpoint to receive print requests from Odoo.
    
    POST /print
    Content-Type: application/json
    {
        "labels": [
            {"title": "W-CPN/OUT/00002", "date": "12/04/22", "qr_code": "01010101160"},
            {"title": "W-CPN/OUT/00003", "date": "12/04/22", "qr_code": "01010101161"}
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
            response = {
                "success": True,
                "message": "Labels printed successfully",
                "labels_count": len(data['labels']),
                "job_info": message,
                "timestamp": datetime.now().isoformat()
            }
            logging.info(f"✅ Print request completed successfully")
            return jsonify(response)
        else:
            response = {
                "success": False,
                "error": "Printing failed",
                "details": message,
                "timestamp": datetime.now().isoformat()
            }
            logging.error(f"❌ Print request failed: {message}")
            return jsonify(response), 500
            
    except Exception as e:
        logging.error(f"❌ Print request error: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/printer/status', methods=['GET'])
def printer_status():
    """Check printer status."""
    try:
        result = subprocess.run(['lpstat', '-p', PRINTER_NAME], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return jsonify({
                "printer": PRINTER_NAME,
                "status": "available",
                "details": result.stdout.strip()
            })
        else:
            return jsonify({
                "printer": PRINTER_NAME,
                "status": "error",
                "details": result.stderr.strip()
            }), 500
            
    except Exception as e:
        return jsonify({
            "printer": PRINTER_NAME,
            "status": "error", 
            "details": str(e)
        }), 500

if __name__ == '__main__':
    logging.info("🚀 Starting Label Printing API Server")
    logging.info(f"📱 Printer: {PRINTER_NAME}")
    logging.info("🔗 Endpoints:")
    logging.info("   POST /print - Print labels")
    logging.info("   GET /health - Health check")
    logging.info("   GET /printer/status - Printer status")
    
    app.run(host='0.0.0.0', port=5000, debug=False)