#!/usr/bin/env python3
"""
QR Code Image-Based Printer - generates QR as image then converts to ZPL
"""

import qrcode
from PIL import Image
import io
import subprocess

def qr_to_zpl_image(qr_data, size_pixels=150):
    """Convert QR code data to ZPL image commands."""
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size_pixels, size_pixels), Image.NEAREST)
    
    # Convert to 1-bit (black/white)
    img = img.convert('1')
    
    # Convert to ZPL graphic field format
    width, height = img.size
    
    # Convert image to ZPL hex data
    zpl_data = []
    for y in range(height):
        row_data = 0
        bit_count = 0
        row_hex = ""
        
        for x in range(width):
            pixel = img.getpixel((x, y))
            # 0 = black, 255 = white in PIL
            # In ZPL: 0 = white, 1 = black
            bit = 0 if pixel == 255 else 1
            
            row_data = (row_data << 1) | bit
            bit_count += 1
            
            if bit_count == 8:
                row_hex += f"{row_data:02X}"
                row_data = 0
                bit_count = 0
        
        # Pad remaining bits if needed
        if bit_count > 0:
            row_data = row_data << (8 - bit_count)
            row_hex += f"{row_data:02X}"
        
        zpl_data.append(row_hex)
    
    # Calculate bytes per row
    bytes_per_row = (width + 7) // 8
    total_bytes = len("".join(zpl_data)) // 2
    
    # Generate ZPL graphic field command
    zpl_graphic = f"^GFA,{total_bytes},{total_bytes},{bytes_per_row},{''.join(zpl_data)}"
    
    return zpl_graphic, width, height

def create_qr_label_with_image(qr_data, title, date, code):
    """Create ZPL with QR code as image."""
    
    # Generate QR code as ZPL image
    qr_graphic, qr_width, qr_height = qr_to_zpl_image(qr_data, 120)
    
    # Create complete ZPL
    zpl = f"""^XA
^FO30,30{qr_graphic}^FS
^FO220,50^A0N,28,28^FD{title}^FS
^FO220,90^A0N,25,25^FD{date}^FS
^FO220,130^A0N,22,22^FD{code}^FS
^XZ"""
    
    return zpl

def print_qr_image_label(qr_data, title, date, code):
    """Print QR label using image-based approach."""
    
    print(f"🖨️ Creating QR label with image approach...")
    print(f"   QR: {qr_data}")
    print(f"   Title: {title}")
    print(f"   Date: {date}")
    print(f"   Code: {code}")
    
    try:
        zpl = create_qr_label_with_image(qr_data, title, date, code)
        
        # Print the ZPL
        process = subprocess.Popen(
            ['lp', '-d', 'ZTC-ZD230-203dpi-ZPL', '-o', 'raw'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(input=zpl.encode('utf-8'), timeout=30)
        
        if process.returncode == 0:
            job_info = stdout.decode().strip()
            print(f"✅ QR image label printed: {job_info}")
            return True
        else:
            print(f"❌ Printing failed: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Test with your data
    success = print_qr_image_label(
        qr_data="http://local-odoo16.abcfood.app/QR-QR00000049",
        title="W-CPN/OUT/00002",
        date="12/04/22",
        code="01010101160"
    )
    
    if success:
        print("\n🎉 QR code should now appear as an image!")
    else:
        print("\n❌ Image approach failed too")