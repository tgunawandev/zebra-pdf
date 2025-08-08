#!/usr/bin/env python3
"""
Create QR labels from text data for Zebra printer.
"""

import subprocess
import sys

def create_qr_label(qr_data, title, date, code):
    """Create ZPL for a single QR label with your format."""
    zpl = f"""^XA
^FO30,30^BQN,2,4^FD{qr_data}^FS
^FO220,50^A0N,28,28^FD{title}^FS
^FO220,90^A0N,25,25^FD{date}^FS
^FO220,130^A0N,22,22^FD{code}^FS
^XZ"""
    return zpl

def print_label(zpl_commands, printer_name="ZTC-ZD230-203dpi-ZPL"):
    """Print ZPL commands to Zebra printer."""
    try:
        process = subprocess.Popen(
            ['lp', '-d', printer_name, '-o', 'raw'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(input=zpl_commands.encode('utf-8'), timeout=30)
        
        if process.returncode == 0:
            job_info = stdout.decode().strip()
            print(f"✅ Label printed successfully: {job_info}")
            return True
        else:
            print(f"❌ Printing failed: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function with examples."""
    if len(sys.argv) > 1 and sys.argv[1] == "example":
        # Example usage
        print("🏷️ Creating example label...")
        
        qr_data = "http://local-odoo16.abcfood.app/QR-QR00000049"
        title = "W-CPN/OUT/00002"
        date = "12/04/22"
        code = "01010101160"
        
        zpl = create_qr_label(qr_data, title, date, code)
        print("Generated ZPL:")
        print(zpl)
        print()
        
        print("Printing...")
        print_label(zpl)
        
    else:
        print("🏷️ QR Label Creator")
        print("==================")
        
        # Interactive mode
        qr_data = input("QR Data (URL): ").strip() or "http://local-odoo16.abcfood.app/QR-QR00000049"
        title = input("Title: ").strip() or "W-CPN/OUT/00002"
        date = input("Date: ").strip() or "12/04/22"
        code = input("Code: ").strip() or "01010101160"
        
        print(f"\nCreating label:")
        print(f"  QR: {qr_data}")
        print(f"  Title: {title}")
        print(f"  Date: {date}")
        print(f"  Code: {code}")
        
        zpl = create_qr_label(qr_data, title, date, code)
        print_label(zpl)

if __name__ == "__main__":
    main()