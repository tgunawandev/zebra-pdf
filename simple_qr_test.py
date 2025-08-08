#!/usr/bin/env python3
"""
Simple QR test - try different approaches to get QR working on ZD230
"""

import subprocess
import qrcode
from PIL import Image
import io

def test_simple_text_qr():
    """Test 1: Replace QR with simple text representation"""
    print("🧪 Test 1: Text-based QR representation")
    
    zpl = """^XA
^FO30,30^A0N,15,15^FD[QR:01010101160]^FS
^FO220,50^A0N,28,28^FDW-CPN/OUT/00002^FS
^FO220,90^A0N,25,25^FD12/04/22^FS
^FO220,130^A0N,22,22^FD01010101160^FS
^XZ"""
    
    send_zpl(zpl, "Text QR")

def test_barcode_128():
    """Test 2: Use Code 128 barcode instead of QR"""
    print("\n🧪 Test 2: Code 128 barcode (should work)")
    
    zpl = """^XA
^FO30,30^BCN,50,Y,N,N^FD01010101160^FS
^FO220,50^A0N,28,28^FDW-CPN/OUT/00002^FS
^FO220,90^A0N,25,25^FD12/04/22^FS
^FO220,130^A0N,22,22^FD01010101160^FS
^XZ"""
    
    send_zpl(zpl, "Code 128")

def test_manual_qr_box():
    """Test 3: Draw a simple QR-like box pattern"""
    print("\n🧪 Test 3: Manual QR-like pattern using boxes")
    
    zpl = """^XA
^FO30,30^GB100,100,10^FS
^FO40,40^GB80,80,2^FS
^FO50,50^GB60,60,5^FS
^FO220,50^A0N,28,28^FDW-CPN/OUT/00002^FS
^FO220,90^A0N,25,25^FD12/04/22^FS
^FO220,130^A0N,22,22^FD01010101160^FS
^XZ"""
    
    send_zpl(zpl, "Box Pattern")

def send_zpl(zpl_command, test_name):
    """Send ZPL to printer"""
    try:
        process = subprocess.Popen(
            ['lp', '-d', 'ZTC-ZD230-203dpi-ZPL-2', '-o', 'raw'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(input=zpl_command.encode('utf-8'), timeout=30)
        
        if process.returncode == 0:
            job_info = stdout.decode().strip()
            print(f"   ✅ {test_name} sent successfully")
        else:
            print(f"   ❌ {test_name} failed: {stderr.decode()}")
            
    except Exception as e:
        print(f"   ❌ {test_name} error: {e}")

if __name__ == "__main__":
    print("🔧 SIMPLE QR ALTERNATIVES TEST")
    print("Testing different approaches for ZD230...")
    
    test_simple_text_qr()
    test_barcode_128() 
    test_manual_qr_box()
    
    print("\n📋 Check your printer:")
    print("   1. Text representation of QR")
    print("   2. Code 128 barcode (linear)")
    print("   3. Box pattern (QR-like visual)")
    print("\nWe'll use whichever approach works best!")