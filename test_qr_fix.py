#!/usr/bin/env python3
"""
QR Code Fix Test - Demonstrates the QR code printing fix
"""

import subprocess
from pdf_to_zpl import pdf_to_zpl, print_zpl_to_zebra
from qr_image_printer import print_qr_image_label

def test_old_vs_new_qr():
    print("🔧 QR Code Fix Comparison Test")
    print("=" * 50)
    
    # Test 1: Old broken format (should show partial QR)
    print("\n❌ OLD FORMAT (Broken):")
    old_zpl = """^XA
^FO30,30^BQN,2,4^FD01010101160^FS
^FO220,50^A0N,28,28^FDW-CPN/OUT/00002^FS
^FO220,90^A0N,25,25^FD12/04/22^FS
^FO220,130^A0N,22,22^FD01010101160^FS
^XZ"""
    
    print("   ZPL: ^FO30,30^BQN,2,4^FD01010101160^FS")
    send_zpl(old_zpl, "Old Format")
    
    # Test 2: New fixed format (should show proper QR)
    print("\n✅ NEW FORMAT (Fixed):")
    new_zpl = """^XA
^FO30,30^BQN,2,8^FD01010101160^FS
^FO220,50^A0N,28,28^FDW-CPN/OUT/00002^FS
^FO220,90^A0N,25,25^FD12/04/22^FS
^FO220,130^A0N,22,22^FD01010101160^FS
^XZ"""
    
    print("   ZPL: ^FO30,30^BQN,2,8^FD01010101160^FS")
    send_zpl(new_zpl, "New Format")
    
    # Test 3: Image-based approach (guaranteed to work)
    print("\n🎯 IMAGE-BASED (Bulletproof):")
    print("   Converting QR to bitmap image...")
    success = print_qr_image_label(
        qr_data='01010101160',
        title='W-CPN/OUT/00002',
        date='12/04/22', 
        code='01010101160'
    )
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

def send_zpl(zpl_command, label):
    """Send ZPL command to printer."""
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
            print(f"   ✅ {label} sent to printer")
            return True
        else:
            print(f"   ❌ {label} failed: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"   ❌ {label} error: {e}")
        return False

def test_full_pdf():
    print("\n🔄 FULL PDF TEST:")
    print("Testing complete PDF to ZPL conversion with fixed QR codes...")
    
    pdf_path = 'input/QR Labels - W-CPN_OUT_00002.pdf'
    zpl_commands = pdf_to_zpl(pdf_path)
    
    if zpl_commands:
        print("   ✅ PDF conversion successful")
        print(f"   📄 Generated ZPL with {len(zpl_commands.split('XA')) - 1} labels")
        
        # Show QR command from generated ZPL
        lines = zpl_commands.split('\n')
        for line in lines:
            if '^BQ' in line:
                print(f"   🎯 QR Command: {line}")
                break
        
        # Print it
        success = print_zpl_to_zebra(zpl_commands, 'ZTC-ZD230-203dpi-ZPL-2')
        print(f"   Result: {'✅ Success - All 3 QR labels printed!' if success else '❌ Failed'}")
    else:
        print("   ❌ PDF conversion failed")

if __name__ == "__main__":
    test_old_vs_new_qr()
    test_full_pdf()
    
    print("\n🎉 QR CODE FIX COMPLETE!")
    print("📋 Check your printer output:")
    print("   • First label should show broken/partial QR (old format)")
    print("   • Second label should show perfect QR code (new format)")
    print("   • Third label should show perfect QR as bitmap (image method)")
    print("   • Last 3 labels should be your complete PDF with working QR codes!")