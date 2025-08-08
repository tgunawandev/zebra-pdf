#!/usr/bin/env python3
"""
REST API Server for PDF to Zebra Printer

Provides a simple REST API to upload and print PDF files to Zebra printer.
"""

import os
import tempfile
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pdf_printer import PDFZebraPrinter


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Initialize printer
printer = PDFZebraPrinter()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/status', methods=['GET'])
def get_printer_status():
    """Get printer status."""
    status = printer.get_printer_status()
    return jsonify({
        'success': True,
        'data': status
    })


@app.route('/api/print', methods=['POST'])
def print_pdf():
    """
    Upload and print a PDF file.
    
    Form data:
    - file: PDF file to upload and print
    - copies: Number of copies (optional, default: 1)
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Only PDF files are allowed'
            }), 400
        
        # Get number of copies
        copies = int(request.form.get('copies', 1))
        if copies < 1 or copies > 10:
            return jsonify({
                'success': False,
                'error': 'Copies must be between 1 and 10'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        try:
            # Print the PDF
            success = printer.print_pdf(file_path, copies)
            
            # Clean up uploaded file
            os.unlink(file_path)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'PDF printed successfully ({copies} copies)',
                    'filename': filename,
                    'copies': copies
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to print PDF to Zebra printer'
                }), 500
                
        except Exception as e:
            # Clean up uploaded file on error
            if os.path.exists(file_path):
                os.unlink(file_path)
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/print-file', methods=['POST'])
def print_existing_file():
    """
    Print an existing PDF file on the server.
    
    JSON data:
    - file_path: Path to PDF file on server
    - copies: Number of copies (optional, default: 1)
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify({
                'success': False,
                'error': 'file_path is required'
            }), 400
        
        file_path = data['file_path']
        copies = int(data.get('copies', 1))
        
        if copies < 1 or copies > 10:
            return jsonify({
                'success': False,
                'error': 'Copies must be between 1 and 10'
            }), 400
        
        # Print the PDF
        success = printer.print_pdf(file_path, copies)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'PDF printed successfully ({copies} copies)',
                'file_path': file_path,
                'copies': copies
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to print PDF to Zebra printer'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'message': 'PDF Zebra Printer API is running',
        'printer_available': printer.get_printer_status()['printer_available']
    })


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB.'
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


def main():
    """Run the API server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='PDF to Zebra Printer REST API')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"🖨️  PDF Zebra Printer API Server")
    print(f"   Host: {args.host}:{args.port}")
    print(f"   Printer: {printer.cups_printer or 'Not found'}")
    print(f"   Debug: {args.debug}")
    print("\n📋 API Endpoints:")
    print("   GET  /api/health     - Health check")
    print("   GET  /api/status     - Printer status")
    print("   POST /api/print      - Upload and print PDF")
    print("   POST /api/print-file - Print existing file")
    print("\n🚀 Starting server...")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()