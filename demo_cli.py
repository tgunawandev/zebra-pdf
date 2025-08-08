#!/usr/bin/env python3
"""
Demo CLI for Zebra PDF Printer
Demonstrates all the key functionality.
"""

import os
import sys
from pdf_printer import PDFZebraPrinter
from pdf_to_zpl import pdf_to_zpl, print_zpl_to_zebra

def main():
    print("🖨️  Zebra PDF Printer Demo")
    print("=" * 50)
    
    # Initialize printer
    printer = PDFZebraPrinter()
    
    # Check printer status
    status = printer.get_printer_status()
    print("\n📋 Printer Status:")
    print(f"   CUPS Printer: {status['cups_printer'] or 'Not found'}")
    print(f"   Available: {'✅ Yes' if status['printer_available'] else '❌ No'}")
    print(f"   Can Print: {'✅ Yes' if status['can_print'] else '❌ No'}")
    
    if not status['can_print']:
        print("\n❌ No printer available. Please check your Zebra printer connection.")
        return
    
    # Test PDF file
    pdf_file = "input/QR Labels - W-CPN_OUT_00002.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"\n❌ PDF file not found: {pdf_file}")
        return
    
    print(f"\n📄 Testing with PDF: {pdf_file}")
    
    # Method 1: Direct CLI printing
    print("\n🔄 Method 1: Direct PDF printing via CLI")
    success1 = printer.print_pdf(pdf_file, 1)
    print(f"   Result: {'✅ Success' if success1 else '❌ Failed'}")
    
    # Method 2: PDF to ZPL conversion
    print("\n🔄 Method 2: PDF to ZPL conversion")
    zpl_commands = pdf_to_zpl(pdf_file)
    if zpl_commands:
        print("   ✅ ZPL conversion successful")
        
        # Show sample ZPL
        lines = zpl_commands.split('\n')
        print(f"   📝 Generated {len(lines)} lines of ZPL")
        print("   📋 Sample ZPL commands:")
        for i, line in enumerate(lines[:5]):
            print(f"      {i+1}: {line}")
        if len(lines) > 5:
            print(f"      ... and {len(lines)-5} more lines")
        
        # Print ZPL
        print("   🖨️  Printing ZPL commands...")
        success2 = print_zpl_to_zebra(zpl_commands, printer.cups_printer)
        print(f"   Result: {'✅ Success' if success2 else '❌ Failed'}")
    else:
        print("   ❌ ZPL conversion failed")
        success2 = False
    
    # Summary
    print("\n📊 Demo Results:")
    print(f"   Direct PDF printing: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   PDF to ZPL printing: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 or success2:
        print("\n🎉 Your Zebra printer should now have printed QR labels!")
        print("💡 The system automatically:")
        print("   • Detects Zebra printers in CUPS")
        print("   • Extracts QR codes and text from PDF") 
        print("   • Converts to native ZPL commands")
        print("   • Handles multiple printing methods as fallback")
    else:
        print("\n⚠️  Both methods failed. Check:")
        print("   • Printer is powered on and connected")
        print("   • Printer is configured in CUPS")
        print("   • No paper jams or errors")

if __name__ == "__main__":
    main()