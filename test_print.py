#!/usr/bin/env python3
"""
Simple test script to verify if the Zebra printer is actually printing.
"""

import subprocess
import tempfile
import os

def test_simple_print():
    """Test printing a simple text document to verify printer works."""
    print("🧪 Testing simple text printing...")
    
    # Create a simple text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("TEST PRINT\n")
        f.write("This is a test from the PDF printer app.\n")
        f.write("If you see this, the printer is working!\n")
        f.write("=" * 40 + "\n")
        text_file = f.name
    
    try:
        # Print the text file
        cmd = ['lp', '-d', 'ZTC-ZD230-203dpi-ZPL', text_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            job_info = result.stdout.strip()
            print(f"✅ Text file sent to printer: {job_info}")
            return True
        else:
            print(f"❌ Text printing failed: {result.stderr}")
            return False
            
    finally:
        # Clean up
        os.unlink(text_file)

def test_zpl_print():
    """Test printing raw ZPL commands to verify Zebra printer works."""
    print("🧪 Testing ZPL command printing...")
    
    # Simple ZPL command to print a label
    zpl_command = """^XA
^FO50,50^A0N,50,50^FDTest Label^FS
^FO50,120^A0N,30,30^FDPDF Printer Test^FS
^FO50,170^BQN,2,4^FDLA,Hello World^FS
^XZ"""
    
    try:
        # Send ZPL directly to printer
        process = subprocess.Popen(
            ['lp', '-d', 'ZTC-ZD230-203dpi-ZPL', '-o', 'raw'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(input=zpl_command.encode('utf-8'), timeout=30)
        
        if process.returncode == 0:
            job_info = stdout.decode().strip()
            print(f"✅ ZPL commands sent to printer: {job_info}")
            return True
        else:
            print(f"❌ ZPL printing failed: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ ZPL test error: {e}")
        return False

def test_pdf_to_image_print(pdf_path):
    """Test converting PDF to image and then printing."""
    print("🧪 Testing PDF to image conversion and printing...")
    
    try:
        # Convert PDF to PPM image
        with tempfile.NamedTemporaryFile(suffix='.ppm', delete=False) as img_file:
            img_path = img_file.name
        
        # Use pdftoppm to convert first page
        convert_cmd = ['pdftoppm', '-f', '1', '-l', '1', '-r', '150', pdf_path, img_path.replace('.ppm', '')]
        convert_result = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=30)
        
        if convert_result.returncode != 0:
            print(f"❌ PDF conversion failed: {convert_result.stderr}")
            return False
        
        # Find the generated image file
        import glob
        img_files = glob.glob(f"{img_path.replace('.ppm', '')}*.ppm")
        
        if not img_files:
            print("❌ No image file generated")
            return False
        
        actual_img = img_files[0]
        print(f"📷 Generated image: {actual_img}")
        
        # Print the image
        print_cmd = ['lp', '-d', 'ZTC-ZD230-203dpi-ZPL', actual_img]
        print_result = subprocess.run(print_cmd, capture_output=True, text=True, timeout=30)
        
        # Clean up
        for f in img_files:
            os.unlink(f)
        
        if print_result.returncode == 0:
            job_info = print_result.stdout.strip()
            print(f"✅ Image printed: {job_info}")
            return True
        else:
            print(f"❌ Image printing failed: {print_result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ PDF to image test error: {e}")
        return False

if __name__ == "__main__":
    print("🖨️  Zebra Printer Test Suite")
    print("=" * 40)
    
    # Test 1: Simple text printing
    test1 = test_simple_print()
    print()
    
    # Test 2: ZPL command printing
    test2 = test_zpl_print()
    print()
    
    # Test 3: PDF to image printing
    pdf_file = "/home/tgunawan/Downloads/QR Labels - W-CPN_OUT_00002.pdf"
    if os.path.exists(pdf_file):
        test3 = test_pdf_to_image_print(pdf_file)
    else:
        print("⚠️  PDF file not found, skipping image test")
        test3 = False
    
    print()
    print("📋 Test Results:")
    print(f"   Text printing: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"   ZPL printing:  {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"   PDF printing:  {'✅ PASS' if test3 else '❌ FAIL'}")
    
    if test2:
        print("\n🎉 ZPL printing works! Your Zebra printer should have printed a test label.")
    else:
        print("\n⚠️  Zebra printer may not be properly configured for raw ZPL commands.")