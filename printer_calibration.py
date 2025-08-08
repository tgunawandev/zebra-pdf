#!/usr/bin/env python3
"""
Zebra Printer Calibration Script

This script helps calibrate the printer for proper label positioning.
Run this before printing labels to ensure alignment.
"""

import subprocess
import time

def calibrate_printer(printer_name: str = "ZTC-ZD230-203dpi-ZPL") -> bool:
    """
    Calibrate the Zebra printer for proper label detection and positioning.
    """
    print(f"🔧 Calibrating printer: {printer_name}")
    
    # Calibration ZPL commands
    calibration_zpl = """^XA
^JUS
^MMT
^MNY
^MTT
^PON
^PMN
^LRN
^CI0
^XZ

~JC
^XA
^JUS
^XZ"""
    
    try:
        # Send calibration commands
        process = subprocess.Popen(
            ['lp', '-d', printer_name, '-o', 'raw'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(input=calibration_zpl.encode('utf-8'), timeout=30)
        
        if process.returncode == 0:
            print("✅ Printer calibration sent successfully")
            print("⏳ Please wait for printer to complete calibration (may take 10-15 seconds)")
            time.sleep(15)  # Wait for calibration to complete
            return True
        else:
            print(f"❌ Calibration failed: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Calibration error: {e}")
        return False

def print_test_label(printer_name: str = "ZTC-ZD230-203dpi-ZPL") -> bool:
    """
    Print a test label to verify positioning and text sizing.
    """
    print(f"🖨️  Printing test label to {printer_name}")
    
    # Test label with consistent text sizing
    test_zpl = """^XA
^LL236
^PW394
^LH0,0
^LT0
^PR2
^MD5
^JMA

^FO30,30^BQN,2,5^FDLA,TEST123456^FS

^FO145,35^A0N,16,16^FDW-CPN/OUT/TEST^FS
^FO145,60^A0N,16,16^FD01/01/25^FS
^FO145,85^A0N,16,16^FDTEST123456^FS

^XZ"""
    
    try:
        process = subprocess.Popen(
            ['lp', '-d', printer_name, '-o', 'raw'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(input=test_zpl.encode('utf-8'), timeout=30)
        
        if process.returncode == 0:
            print("✅ Test label printed successfully")
            return True
        else:
            print(f"❌ Test print failed: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Test print error: {e}")
        return False

def main():
    """Main calibration routine."""
    print("🏷️  Zebra Printer Calibration Tool")
    print("=" * 40)
    
    # Step 1: Calibrate printer
    if calibrate_printer():
        print("\n📋 Step 1: Calibration completed")
    else:
        print("\n❌ Step 1: Calibration failed")
        return
    
    # Step 2: Print test label
    print("\n📋 Step 2: Printing test label...")
    if print_test_label():
        print("✅ Calibration complete! Check the test label for proper positioning.")
        print("📝 All text should be the same size (16x16)")
        print("📝 QR code should be positioned correctly")
        print("📝 Label should be properly aligned on the media")
    else:
        print("❌ Test print failed")

if __name__ == "__main__":
    main()