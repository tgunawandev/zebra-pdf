"""
CUPS-based Zebra printer service implementation.
Manages Zebra printer connection and status via CUPS.
"""

import subprocess
import re
from typing import Dict, Tuple
from zebra_print.printer.base import PrinterService

class ZebraCUPSPrinter(PrinterService):
    """CUPS-based Zebra printer service implementation."""
    
    def __init__(self, printer_name: str = "ZTC-ZD230-203dpi-ZPL"):
        self._printer_name = printer_name
    
    @property
    def name(self) -> str:
        return self._printer_name
    
    def is_ready(self) -> bool:
        """Check if printer is ready to print."""
        try:
            # Check printer status via lpstat
            result = subprocess.run(['lpstat', '-p', self._printer_name], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                return False
            
            # Check if printer is enabled and accepting jobs
            output = result.stdout.lower()
            return 'enabled' in output and 'accepting' not in output or 'not accepting' not in output
            
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, any]:
        """Get printer status information."""
        status = {
            'name': self._printer_name,
            'exists': False,
            'enabled': False,
            'accepting_jobs': False,
            'state': 'unknown',
            'jobs_queued': 0,
            'connection': 'unknown'
        }
        
        try:
            # Get printer info
            result = subprocess.run(['lpstat', '-p', self._printer_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                status['exists'] = True
                output = result.stdout.lower()
                
                if 'enabled' in output:
                    status['enabled'] = True
                    status['state'] = 'idle'
                else:
                    status['state'] = 'disabled'
                
                if 'accepting' in output and 'not accepting' not in output:
                    status['accepting_jobs'] = True
            
            # Get job queue info
            queue_result = subprocess.run(['lpstat', '-o', self._printer_name], 
                                        capture_output=True, text=True)
            if queue_result.returncode == 0:
                jobs = queue_result.stdout.strip().split('\n')
                status['jobs_queued'] = len([j for j in jobs if j.strip()])
            
            # Check printer connection via lpstat -v
            conn_result = subprocess.run(['lpstat', '-v', self._printer_name], 
                                       capture_output=True, text=True)
            if conn_result.returncode == 0:
                output = conn_result.stdout
                if 'usb://' in output:
                    status['connection'] = 'USB'
                elif 'socket://' in output:
                    status['connection'] = 'Network'
                else:
                    status['connection'] = 'Other'
            
        except Exception as e:
            status['error'] = str(e)
        
        return status
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test printer connection."""
        try:
            # Send a simple test command to printer
            test_zpl = "^XA^HH^XZ"  # Simple ZPL command to test communication
            
            process = subprocess.run([
                'echo', '-e', test_zpl, '|', 'lp', '-d', self._printer_name, '-o', 'raw'
            ], shell=True, capture_output=True, text=True)
            
            if process.returncode == 0:
                return True, "Printer connection test successful"
            else:
                return False, f"Connection test failed: {process.stderr}"
                
        except Exception as e:
            return False, f"Connection test error: {str(e)}"
    
    def print_test_label(self) -> Tuple[bool, str]:
        """Print a test label to verify printer functionality."""
        try:
            # Create a simple test ZPL label
            test_zpl = """^XA
^PR2
^MD5
^JMA
^LH0,0
^FO50,50^A0,16,16^FDTest Label^FS
^FO50,80^A0,16,16^FDPrinter: """ + self._printer_name + """^FS
^FO50,110^A0,16,16^FDTime: $(time)^FS
^XZ"""
            
            # Send to printer
            process = subprocess.Popen(['lp', '-d', self._printer_name, '-o', 'raw'], 
                                     stdin=subprocess.PIPE, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     text=True)
            
            stdout, stderr = process.communicate(input=test_zpl)
            
            if process.returncode == 0:
                return True, "Test label sent to printer successfully"
            else:
                return False, f"Failed to print test label: {stderr}"
                
        except Exception as e:
            return False, f"Test print error: {str(e)}"
    
    def get_printer_list(self) -> Dict[str, str]:
        """Get list of available printers."""
        printers = {}
        
        try:
            result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    match = re.match(r'printer\s+(\S+)\s+(.*)', line)
                    if match:
                        name, status = match.groups()
                        printers[name] = status
                        
        except Exception:
            pass
        
        return printers
    
    def setup_printer(self, device_uri: str = None) -> Tuple[bool, str]:
        """Setup/configure the printer in CUPS."""
        try:
            if device_uri is None:
                # Try to auto-detect USB Zebra printer
                result = subprocess.run(['lpinfo', '-v'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'usb://' in line and ('zebra' in line.lower() or 'zd' in line.lower()):
                            device_uri = line.split()[1]
                            break
                
                if not device_uri:
                    return False, "No USB Zebra printer detected"
            
            # Add/configure printer
            cmd = [
                'lpadmin', '-p', self._printer_name,
                '-v', device_uri,
                '-P', '/dev/null',  # No PPD file for raw printing
                '-o', 'printer-is-accepting-jobs=true',
                '-o', 'printer-state=idle'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return False, f"Failed to configure printer: {result.stderr}"
            
            # Enable printer
            enable_result = subprocess.run(['cupsenable', self._printer_name], 
                                         capture_output=True, text=True)
            if enable_result.returncode != 0:
                return False, f"Failed to enable printer: {enable_result.stderr}"
            
            # Accept jobs
            accept_result = subprocess.run(['cupsaccept', self._printer_name], 
                                         capture_output=True, text=True)
            if accept_result.returncode != 0:
                return False, f"Failed to accept jobs: {accept_result.stderr}"
            
            return True, f"Printer {self._printer_name} configured successfully"
            
        except Exception as e:
            return False, f"Setup failed: {str(e)}"