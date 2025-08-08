#!/usr/bin/env python3
"""Test different QR code ZPL formats."""

import subprocess

def test_qr_format(zpl_command, description):
    """Test a specific QR ZPL format."""
    print(f"\n🧪 Testing: {description}")
    print(f"ZPL: {zpl_command}")
    
    try:
        process = subprocess.Popen(
            ['lp', '-d', 'ZTC-ZD230-203dpi-ZPL', '-o', 'raw'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(input=zpl_command.encode('utf-8'), timeout=30)
        
        if process.returncode == 0:
            job_info = stdout.decode().strip()
            print(f"✅ Sent to printer: {job_info}")
            return True
        else:
            print(f"❌ Failed: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔬 QR Code ZPL Format Testing")
    print("=" * 40)
    
    test_number = "01010101160"
    
    # Test different QR code formats
    formats = [
        (f"^XA^FO50,50^BQN,2,3^FDQA,{test_number}^FS^FO200,50^A0N,25,25^FDFormat 1^FS^XZ", 
         "Standard QR (QA format, size 3)"),
        
        (f"^XA^FO50,50^BQN,2,4^FDLA,{test_number}^FS^FO200,50^A0N,25,25^FDFormat 2^FS^XZ", 
         "LA format, size 4"),
        
        (f"^XA^FO50,50^BQN,2,5^FD{test_number}^FS^FO200,50^A0N,25,25^FDFormat 3^FS^XZ", 
         "Direct data, size 5"),
        
        (f"^XA^FO50,50^BQN,2,6^FDHA,{test_number}^FS^FO200,50^A0N,25,25^FDFormat 4^FS^XZ", 
         "HA format, size 6"),
        
        (f"^XA^FO50,50^BQN,2,4,Q^FD{test_number}^FS^FO200,50^A0N,25,25^FDFormat 5^FS^XZ", 
         "With error correction Q"),
    ]
    
    for zpl, desc in formats:
        test_qr_format(zpl, desc)
        print("   Waiting 2 seconds...")
        import time
        time.sleep(2)