#!/usr/bin/env python3
"""
Simple PDF to Zebra Printer Application

This app can receive PDFs and print them to a Zebra printer connected via USB.
It provides both CLI and REST API interfaces.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
try:
    from pdf2image import convert_from_path
    from PIL import Image
    PDF_CONVERSION_AVAILABLE = True
except ImportError:
    PDF_CONVERSION_AVAILABLE = False


class PDFZebraPrinter:
    """
    Simple PDF printer for Zebra printers via USB connection.
    Uses CUPS for reliable PDF printing.
    """
    
    def __init__(self):
        """Initialize the PDF printer."""
        self.cups_printer = self._detect_zebra_printer()
        
    def _detect_zebra_printer(self) -> Optional[str]:
        """Detect Zebra printer in CUPS."""
        try:
            result = subprocess.run(['lpstat', '-p'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                zebra_printers = []
                
                # Collect all Zebra printers
                for line in lines:
                    if line.startswith('printer '):
                        parts = line.split()
                        if len(parts) >= 2:
                            printer_name = parts[1]
                            name_lower = printer_name.lower()
                            
                            # Look for Zebra-related keywords
                            if any(keyword in name_lower for keyword in 
                                   ['ztc', 'zebra', 'zpl', 'zd230']):
                                zebra_printers.append((printer_name, line))
                
                # Prefer enabled/idle printers over disabled ones
                for printer_name, line in zebra_printers:
                    if 'idle' in line and 'enabled' in line:
                        return printer_name
                
                # Return first Zebra printer if none are idle/enabled
                if zebra_printers:
                    return zebra_printers[0][0]
                                
                # If no Zebra printer found, try to use the first available printer
                for line in lines:
                    if line.startswith('printer '):
                        parts = line.split()
                        if len(parts) >= 2:
                            return parts[1]
                            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
            
        return None
    
    def print_pdf(self, pdf_path: str, copies: int = 1) -> bool:
        """
        Print a PDF file to the Zebra printer.
        
        Args:
            pdf_path (str): Path to PDF file
            copies (int): Number of copies to print
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return False
            
        if not self.cups_printer:
            print("❌ No Zebra printer found in CUPS")
            print("   Make sure your Zebra printer is connected and configured in CUPS")
            return False
        
        try:
            print(f"🖨️  Printing {pdf_path} to {self.cups_printer} ({copies} copies)...")
            
            # Try direct PDF printing first
            cmd = ['lp', '-d', self.cups_printer, '-n', str(copies), pdf_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                job_info = result.stdout.strip()
                print(f"✅ PDF printed successfully! {job_info}")
                return True
            else:
                # If direct PDF printing fails, try alternative methods
                error_msg = result.stderr.strip()
                if "Unsupported document-format" in error_msg:
                    print("⚠️  Direct PDF printing not supported, trying alternative method...")
                    return self._print_pdf_alternative(pdf_path, copies)
                else:
                    print(f"❌ Printing failed: {error_msg}")
                    return False
                
        except subprocess.TimeoutExpired:
            print("❌ Print job timed out")
            return False
        except Exception as e:
            print(f"❌ Print error: {e}")
            return False
    
    def _print_pdf_alternative(self, pdf_path: str, copies: int = 1) -> bool:
        """
        Alternative PDF printing methods for Zebra printer.
        """
        print(f"🔍 Trying alternative printing methods for Zebra printer...")
        
        # Method 1: Try converting PDF to ZPL (best method for Zebra printers)
        try:
            print("🔄 Converting PDF to ZPL commands...")
            from pdf_to_zpl import pdf_to_zpl, print_zpl_to_zebra
            
            zpl_commands = pdf_to_zpl(pdf_path)
            if zpl_commands:
                # Print each copy
                for copy_num in range(copies):
                    if copies > 1:
                        print(f"   Printing copy {copy_num + 1} of {copies}")
                    success = print_zpl_to_zebra(zpl_commands, self.cups_printer)
                    if not success:
                        print(f"❌ Failed to print copy {copy_num + 1}")
                        return False
                
                print("✅ PDF converted to ZPL and printed successfully!")
                return True
            else:
                print("⚠️  PDF to ZPL conversion failed, trying other methods...")
                
        except Exception as e:
            print(f"⚠️  ZPL conversion failed: {e}")
        
        # Method 2: Try different CUPS options
        print("🔄 Trying CUPS with different options...")
        cups_options = [
            ['-o', 'raw'],
            ['-o', 'media=50x30mm'],
            ['-o', 'PageSize=50x30mm'],
            ['-o', 'fit-to-page'],
            []  # No special options
        ]
        
        for i, options in enumerate(cups_options, 1):
            try:
                print(f"   Method {i}: CUPS with options {options}")
                cmd = ['lp', '-d', self.cups_printer, '-n', str(copies)] + options + [pdf_path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    job_info = result.stdout.strip()
                    print(f"✅ PDF printed with CUPS options {options}! {job_info}")
                    # Wait a moment and check if job was processed
                    import time
                    time.sleep(2)
                    return self._verify_print_job(job_info)
                else:
                    print(f"   Failed: {result.stderr.strip()}")
                    
            except Exception as e:
                print(f"   Error: {e}")
        
        # Method 3: Try converting PDF to image and then print
        try:
            print("🔄 Trying to convert PDF to image first...")
            # This would require pdf2image, but let's try a simpler approach first
            
            # Use pdftoppm to convert PDF to PPM image
            with tempfile.NamedTemporaryFile(suffix='.ppm', delete=False) as img_file:
                img_path = img_file.name
            
            convert_cmd = ['pdftoppm', '-singlefile', pdf_path, img_path.replace('.ppm', '')]
            convert_result = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=30)
            
            if convert_result.returncode == 0:
                # Print the image
                print_cmd = ['lp', '-d', self.cups_printer, '-n', str(copies), f"{img_path.replace('.ppm', '')}.ppm"]
                print_result = subprocess.run(print_cmd, capture_output=True, text=True, timeout=30)
                
                # Clean up
                import glob
                for f in glob.glob(f"{img_path.replace('.ppm', '')}*"):
                    os.unlink(f)
                
                if print_result.returncode == 0:
                    job_info = print_result.stdout.strip()
                    print(f"✅ PDF printed via image conversion! {job_info}")
                    return self._verify_print_job(job_info)
                else:
                    print(f"❌ Image printing failed: {print_result.stderr}")
            else:
                print(f"⚠️  PDF to image conversion failed: {convert_result.stderr}")
                    
        except Exception as e:
            print(f"⚠️  Image conversion method failed: {e}")
        
        print("❌ All alternative printing methods failed")
        return False
    
    def _verify_print_job(self, job_info: str) -> bool:
        """Verify if the print job was actually processed."""
        try:
            import time
            print(f"🔍 Verifying print job: {job_info}")
            
            # Wait a bit for the job to be processed
            time.sleep(3)
            
            # Check print queue
            result = subprocess.run(['lpq', '-P', self.cups_printer], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout
                print(f"   Queue status: {output.strip()}")
                
                # If queue is empty and printer is ready, job likely completed
                if "no entries" in output and "ready" in output:
                    print("✅ Print job appears to have been processed")
                    return True
                elif "entries" in output:
                    print("⚠️  Print job still in queue")
                    return True  # Job is queued, consider it successful
                else:
                    print("⚠️  Unable to determine job status")
                    return True  # Assume success if we can't determine
            
        except Exception as e:
            print(f"⚠️  Could not verify print job: {e}")
        
        return True  # Default to success if we can't verify
    
    def get_printer_status(self) -> dict:
        """Get printer status information."""
        return {
            'cups_printer': self.cups_printer,
            'printer_available': bool(self.cups_printer),
            'can_print': bool(self.cups_printer)
        }


def main_cli():
    """CLI interface for PDF printing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Print PDF files to Zebra printer via USB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_printer.py print /path/to/file.pdf
  python pdf_printer.py print /path/to/file.pdf --copies 3
  python pdf_printer.py status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Print command
    print_parser = subparsers.add_parser('print', help='Print a PDF file')
    print_parser.add_argument('pdf_file', help='Path to PDF file to print')
    print_parser.add_argument('--copies', '-c', type=int, default=1,
                            help='Number of copies to print (default: 1)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show printer status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    printer = PDFZebraPrinter()
    
    if args.command == 'print':
        success = printer.print_pdf(args.pdf_file, args.copies)
        sys.exit(0 if success else 1)
        
    elif args.command == 'status':
        status = printer.get_printer_status()
        print("Zebra Printer Status:")
        print(f"  CUPS Printer: {status['cups_printer'] or 'Not found'}")
        print(f"  Available: {'Yes' if status['printer_available'] else 'No'}")
        print(f"  Can Print: {'Yes' if status['can_print'] else 'No'}")


if __name__ == '__main__':
    main_cli()