"""
Windows-based Zebra printer service implementation.
Manages Zebra printer connection and status via Windows printing system.
"""

import subprocess
import platform
import tempfile
import os
import re
from typing import Dict, Tuple, List
from zebra_print.printer.base import PrinterService

class ZebraWindowsPrinter(PrinterService):
    """Windows-based Zebra printer service implementation."""
    
    def __init__(self, printer_name: str = "ZTC-ZD230-203dpi-ZPL"):
        self._printer_name = printer_name
        if platform.system() != "Windows":
            raise RuntimeError("ZebraWindowsPrinter only works on Windows")
    
    @property
    def name(self) -> str:
        return self._printer_name
    
    def is_ready(self) -> bool:
        """Check if printer is ready to print."""
        try:
            # Use PowerShell to check printer status
            cmd = [
                "powershell", "-Command",
                f"Get-Printer -Name '{self._printer_name}' | Select-Object PrinterStatus"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode != 0:
                return False
            
            # Check if printer status indicates it's ready
            output = result.stdout.lower()
            return 'normal' in output or 'idle' in output
            
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
            # Get printer info using PowerShell
            cmd = [
                "powershell", "-Command",
                f"Get-Printer -Name '{self._printer_name}' | ConvertTo-Json"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                import json
                try:
                    printer_info = json.loads(result.stdout)
                    status['exists'] = True
                    
                    # Map Windows printer status to our status
                    printer_status = printer_info.get('PrinterStatus', 'Unknown')
                    if printer_status == 'Normal':
                        status['enabled'] = True
                        status['state'] = 'idle'
                        status['accepting_jobs'] = True
                    elif 'Error' in str(printer_status):
                        status['state'] = 'error'
                    else:
                        status['state'] = str(printer_status).lower()
                    
                    # Get connection type
                    port_name = printer_info.get('PortName', '')
                    if 'USB' in port_name.upper():
                        status['connection'] = 'USB'
                    elif any(x in port_name.upper() for x in ['TCP', 'IP', 'NET']):
                        status['connection'] = 'Network'
                    else:
                        status['connection'] = 'Other'
                        
                except json.JSONDecodeError:
                    # Fallback to basic parsing
                    if "Normal" in result.stdout:
                        status['exists'] = True
                        status['enabled'] = True
                        status['state'] = 'idle'
                        status['accepting_jobs'] = True
            
            # Get job queue info
            queue_cmd = [
                "powershell", "-Command",
                f"Get-PrintJob -PrinterName '{self._printer_name}' | Measure-Object | Select-Object Count"
            ]
            queue_result = subprocess.run(queue_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if queue_result.returncode == 0:
                try:
                    count_match = re.search(r'Count\s*:\s*(\d+)', queue_result.stdout)
                    if count_match:
                        status['jobs_queued'] = int(count_match.group(1))
                except:
                    pass
            
        except Exception as e:
            status['error'] = str(e)
        
        return status
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test printer connection."""
        try:
            # Simple test - check if printer exists and is accessible
            status = self.get_status()
            if status['exists']:
                return True, "Printer connection test successful"
            else:
                return False, "Printer not found or not accessible"
                
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
^FO50,110^A0,16,16^FDTime: Windows^FS
^XZ"""
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.zpl', delete=False) as temp_file:
                temp_file.write(test_zpl)
                temp_file_path = temp_file.name
            
            try:
                # Send to printer using copy command (raw printing)
                cmd = f'copy "{temp_file_path}" "\\\\localhost\\{self._printer_name}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True, "Test label sent to printer successfully"
                else:
                    return False, f"Failed to print test label: {result.stderr}"
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                
        except Exception as e:
            return False, f"Test print error: {str(e)}"
    
    def get_printer_list(self) -> Dict[str, str]:
        """Get list of available printers."""
        printers = {}
        
        try:
            cmd = [
                "powershell", "-Command",
                "Get-Printer | Select-Object Name, PrinterStatus | ConvertTo-Json"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                import json
                try:
                    printer_list = json.loads(result.stdout)
                    if isinstance(printer_list, list):
                        for printer in printer_list:
                            name = printer.get('Name', '')
                            status = printer.get('PrinterStatus', 'Unknown')
                            printers[name] = str(status)
                    elif isinstance(printer_list, dict):
                        # Single printer case
                        name = printer_list.get('Name', '')
                        status = printer_list.get('PrinterStatus', 'Unknown')
                        if name:
                            printers[name] = str(status)
                except json.JSONDecodeError:
                    # Fallback parsing
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Name' in line and ':' in line:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                name = parts[1].strip()
                                printers[name] = 'Unknown'
        except Exception:
            pass
        
        return printers
    
    def setup_printer(self, device_uri: str = None) -> Tuple[bool, str]:
        """Setup/configure the printer in Windows."""
        try:
            # Check if printer already exists
            status = self.get_status()
            if status['exists']:
                return True, f"Printer {self._printer_name} already configured"
            
            # For Windows, we typically can't auto-setup printers programmatically
            # without admin privileges. Instead, provide instructions.
            available_printers = self.get_printer_list()
            
            if not available_printers:
                return False, "No printers found. Please install the Zebra printer driver and add the printer through Windows Settings."
            
            # Look for similar Zebra printers
            zebra_printers = []
            for printer_name in available_printers.keys():
                if any(keyword in printer_name.upper() for keyword in ['ZEBRA', 'ZTC', 'ZD', 'ZPL']):
                    zebra_printers.append(printer_name)
            
            if zebra_printers:
                suggested_printer = zebra_printers[0]
                return False, f"Zebra printer found but with different name: '{suggested_printer}'. Please update the printer name in configuration or rename the printer to '{self._printer_name}' in Windows Settings."
            else:
                printer_list = ', '.join(list(available_printers.keys())[:5])
                return False, f"No Zebra printers found. Available printers: {printer_list}. Please install Zebra printer driver and add printer."
            
        except Exception as e:
            return False, f"Setup failed: {str(e)}"
    
    def print_zpl(self, zpl_content: str) -> Tuple[bool, str]:
        """Print ZPL content directly to the printer."""
        try:
            # Create temporary file with ZPL content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.zpl', delete=False) as temp_file:
                temp_file.write(zpl_content)
                temp_file_path = temp_file.name
            
            try:
                # Send to printer using copy command (raw printing)
                cmd = f'copy "{temp_file_path}" "\\\\localhost\\{self._printer_name}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True, "ZPL sent to printer successfully"
                else:
                    return False, f"Failed to send ZPL to printer: {result.stderr}"
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            return False, f"Print error: {str(e)}"