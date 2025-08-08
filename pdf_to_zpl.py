#!/usr/bin/env python3
"""
PDF to ZPL Converter

Converts PDF files containing QR labels to ZPL commands for Zebra printers.
"""

import subprocess
import tempfile
import os
from PIL import Image
import qrcode
from io import BytesIO
from qr_image_printer import qr_to_zpl_image

def pdf_to_zpl(pdf_path: str) -> str:
    """
    Convert PDF to ZPL commands.
    
    For QR label PDFs, this extracts the text and recreates ZPL commands.
    """
    print("🔄 Converting PDF to ZPL commands...")
    
    try:
        # Method 1: Try to extract text from PDF and recreate as ZPL
        text_content = extract_pdf_text(pdf_path)
        if text_content:
            zpl_commands = convert_text_to_zpl(text_content)
            if zpl_commands:
                return zpl_commands
        
        # Method 2: Convert PDF to image and create ZPL
        return convert_pdf_image_to_zpl(pdf_path)
        
    except Exception as e:
        print(f"❌ PDF to ZPL conversion failed: {e}")
        return None

def extract_pdf_text(pdf_path: str) -> list:
    """Extract text content from PDF."""
    try:
        # Use pdftotext to extract text
        result = subprocess.run(
            ['pdftotext', '-layout', pdf_path, '-'], 
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # Filter out empty lines
            text_lines = [line.strip() for line in lines if line.strip()]
            print(f"📄 Extracted {len(text_lines)} text lines from PDF")
            return text_lines
        else:
            print(f"⚠️  pdftotext failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"⚠️  Text extraction failed: {e}")
        return None

def convert_text_to_zpl(text_lines: list) -> str:
    """Convert extracted text to ZPL commands."""
    print("🔄 Converting text to ZPL...")
    
    if not text_lines:
        return None
    
    # Parse the text lines into groups of 3 (each represents one label/page)
    labels = []
    for i in range(0, len(text_lines), 3):
        if i + 2 < len(text_lines):  # Make sure we have all 3 lines
            label_data = {
                'title': text_lines[i],      # W-CPN/OUT/00002
                'date': text_lines[i + 1],   # 12/04/22
                'qr_code': text_lines[i + 2] # 01010101160, etc.
            }
            labels.append(label_data)
    
    print(f"📋 Parsed {len(labels)} labels from PDF")
    
    # Create ZPL for each label with printer setup
    zpl_commands = []
    
    # Add printer initialization commands ONCE at the beginning
    if labels:  # Only if we have labels to print
        zpl_commands.append("^XA")
        zpl_commands.append("^JUS")      # Auto-detect label length
        zpl_commands.append("^MMT")      # Set media type to thermal transfer
        zpl_commands.append("^MNY")      # Set continuous media
        zpl_commands.append("^MTT")      # Set media type to thermal transfer
        zpl_commands.append("^PON")      # Print orientation normal
        zpl_commands.append("^PMN")      # Print mode normal
        zpl_commands.append("^LRN")      # Label reverse normal
        zpl_commands.append("^CI0")      # Change international font/encoding
        zpl_commands.append("^XZ")
        zpl_commands.append("")  # Blank line separator
    
    for i, label in enumerate(labels):
        zpl_commands.append("^XA")  # Start format
        
        # CALIBRATION AND POSITIONING COMMANDS FOR CONSISTENT LABEL PLACEMENT
        zpl_commands.append("^LL236")     # Set label length to 236 dots (30mm)
        zpl_commands.append("^PW394")     # Set print width to 394 dots (50mm) 
        zpl_commands.append("^LH0,0")     # Set label home position (top-left)
        zpl_commands.append("^LT0")       # Set label top margin to 0
        zpl_commands.append("^PR2")       # Set print speed to 2 inches/second (slower for accuracy)
        zpl_commands.append("^MD5")       # Set media darkness to 5 (medium)
        zpl_commands.append("^JMA")       # Set media type to auto-detect
        
        # QR code with working format and consistent size
        zpl_commands.append(f"^FO30,30^BQN,2,5^FDLA,{label['qr_code']}^FS")
        
        # ALL TEXT WITH SAME SIZE (16x16) FOR CONSISTENCY
        # Text positioned after QR code with proper spacing
        # QR size 5 = 100 dots width, so text starts at 30 + 100 + 15 = 145
        
        # Title - using consistent 16x16 font size
        zpl_commands.append(f"^FO145,35^A0N,16,16^FD{label['title']}^FS")
        
        # Date - using consistent 16x16 font size
        zpl_commands.append(f"^FO145,60^A0N,16,16^FD{label['date']}^FS")
        
        # QR code number - using consistent 16x16 font size
        zpl_commands.append(f"^FO145,85^A0N,16,16^FD{label['qr_code']}^FS")
        
        zpl_commands.append("^XZ")  # End format
        
        # Add spacing between labels if multiple
        if i < len(labels) - 1:
            zpl_commands.append("")
    
    if zpl_commands:
        full_zpl = "\n".join(zpl_commands)
        print(f"✅ Generated ZPL with {len(labels)} labels")
        return full_zpl
    
    return None

def convert_pdf_image_to_zpl(pdf_path: str) -> str:
    """Convert PDF to image and then to simple ZPL."""
    print("🔄 Converting PDF via image method...")
    
    try:
        # Convert PDF to image
        with tempfile.TemporaryDirectory() as temp_dir:
            img_prefix = os.path.join(temp_dir, "page")
            
            # Use pdftoppm to convert
            result = subprocess.run([
                'pdftoppm', '-f', '1', '-l', '1', '-r', '150', 
                '-png', pdf_path, img_prefix
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"⚠️  PDF to image conversion failed: {result.stderr}")
                return create_fallback_zpl(pdf_path)
            
            # Find generated image
            import glob
            img_files = glob.glob(f"{img_prefix}*.png")
            
            if not img_files:
                return create_fallback_zpl(pdf_path)
            
            # For now, create a simple ZPL with PDF filename as QR code
            return create_fallback_zpl(pdf_path)
            
    except Exception as e:
        print(f"⚠️  Image conversion failed: {e}")
        return create_fallback_zpl(pdf_path)

def create_fallback_zpl(pdf_path: str) -> str:
    """Create a fallback ZPL with PDF filename and timestamp."""
    import datetime
    
    filename = os.path.basename(pdf_path)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    zpl = f"""^XA
^FO50,50^BQN,2,5^FDLA,PDF:{filename}^FS
^FO200,100^A0N,25,25^FDPDF Label^FS
^FO200,140^A0N,20,20^FD{filename[:25]}^FS
^FO200,170^A0N,15,15^FD{timestamp}^FS
^XZ"""
    
    print(f"✅ Created fallback ZPL for {filename}")
    return zpl

def print_zpl_to_zebra(zpl_commands: str, printer_name: str = "ZTC-ZD230-203dpi-ZPL") -> bool:
    """Print ZPL commands directly to Zebra printer."""
    try:
        print(f"🖨️  Sending ZPL to {printer_name}...")
        
        process = subprocess.Popen(
            ['lp', '-d', printer_name, '-o', 'raw'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(input=zpl_commands.encode('utf-8'), timeout=30)
        
        if process.returncode == 0:
            job_info = stdout.decode().strip()
            print(f"✅ ZPL printed successfully: {job_info}")
            return True
        else:
            print(f"❌ ZPL printing failed: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ ZPL printing error: {e}")
        return False