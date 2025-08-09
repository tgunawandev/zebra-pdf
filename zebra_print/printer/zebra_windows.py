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
                # First check if this is a USB printer
                is_usb_printer = self._is_usb_printer()
                
                if is_usb_printer:
                    # For USB printers, skip copy command and use Windows print methods
                    return self._try_usb_printer_methods(zpl_content, temp_file_path)
                else:
                    # Method 1: Try copy command for network printers
                    cmd = f'copy "{temp_file_path}" "\\\\localhost\\{self._printer_name}"'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    if result.returncode == 0:
                        return True, "ZPL sent to printer successfully via copy command"
                    else:
                        # Fallback to other methods
                        return self._try_direct_printer_port(zpl_content, temp_file_path)
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            return False, f"Print error: {str(e)}"
    
    def _is_usb_printer(self) -> bool:
        """Check if the printer is connected via USB."""
        try:
            cmd = [
                "powershell", "-Command",
                f"Get-Printer -Name '{self._printer_name}' | Select-Object PortName"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                return "USB" in result.stdout.upper()
            return False
        except:
            return False
    
    def _try_usb_printer_methods(self, zpl_content: str, temp_file_path: str) -> Tuple[bool, str]:
        """Try USB printer-specific printing methods."""
        
        # Method 1: Windows print command (works better for USB)
        try:
            print_cmd = f'print /D:"{self._printer_name}" "{temp_file_path}"'
            result = subprocess.run(print_cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                return True, "ZPL sent to USB printer successfully via print command"
        except Exception as e:
            pass
        
        # Method 2: Try PowerShell with raw bytes
        try:
            # Write ZPL as binary to ensure raw printing
            binary_file = temp_file_path + ".bin"
            with open(binary_file, 'wb') as f:
                f.write(zpl_content.encode('utf-8'))
            
            ps_cmd = [
                "powershell", "-Command",
                f"$bytes = [System.IO.File]::ReadAllBytes('{binary_file}'); $bytes | Out-Printer -Name '{self._printer_name}'"
            ]
            ps_result = subprocess.run(ps_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Clean up binary file
            try:
                os.unlink(binary_file)
            except:
                pass
            
            if ps_result.returncode == 0:
                return True, "ZPL sent to USB printer successfully via PowerShell raw printing"
        except Exception as e:
            pass
        
        # Method 3: Try Python win32print if available
        try:
            import win32print
            import win32api
            
            # Get printer handle
            printer_handle = win32print.OpenPrinter(self._printer_name)
            
            try:
                # Start print job
                job_id = win32print.StartDocPrinter(printer_handle, 1, ("ZPL Label", None, "RAW"))
                win32print.StartPagePrinter(printer_handle)
                
                # Send raw ZPL data
                win32print.WritePrinter(printer_handle, zpl_content.encode('utf-8'))
                
                # End print job
                win32print.EndPagePrinter(printer_handle)
                win32print.EndDocPrinter(printer_handle)
                
                return True, "ZPL sent to USB printer successfully via win32print"
            finally:
                win32print.ClosePrinter(printer_handle)
                
        except ImportError:
            # win32print not available
            pass
        except Exception as e:
            pass
        
        # All methods failed
        return False, f"All USB printing methods failed. Printer may not support raw ZPL printing or needs driver reconfiguration."
    
    def _try_direct_printer_port(self, zpl_content: str, temp_file_path: str) -> Tuple[bool, str]:
        """Try alternative printing methods when copy command fails."""
        try:
            # Method 2a: Try using print command instead of copy
            print_cmd = f'print "{temp_file_path}"'
            result = subprocess.run(print_cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                return True, "ZPL sent to printer successfully via print command"
            
            # Method 2b: Try PowerShell Out-Printer
            ps_cmd = [
                "powershell", "-Command",
                f"Get-Content '{temp_file_path}' | Out-Printer -Name '{self._printer_name}'"
            ]
            ps_result = subprocess.run(ps_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if ps_result.returncode == 0:
                return True, "ZPL sent to printer successfully via PowerShell"
            
            # Method 2c: Try writing directly to printer port (if we can find it)
            return self._try_printer_port_write(zpl_content)
            
        except Exception as e:
            return False, f"Alternative printing methods failed: {str(e)}"
    
    def _try_printer_port_write(self, zpl_content: str) -> Tuple[bool, str]:
        """Try writing directly to printer port."""
        try:
            # Get printer port information
            cmd = [
                "powershell", "-Command",
                f"Get-Printer -Name '{self._printer_name}' | Select-Object PortName"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0 and "USB" in result.stdout:
                # For USB printers, we can't write directly to port easily
                return False, f"USB printer detected - copy command failed, may need different driver setup"
            elif result.returncode == 0:
                # Try to extract port name and write directly
                import re
                port_match = re.search(r'PortName\s*:\s*(\S+)', result.stdout)
                if port_match:
                    port_name = port_match.group(1)
                    if port_name.startswith("FILE:") or port_name.startswith("USB"):
                        return False, f"Printer on {port_name} - cannot write directly"
                    else:
                        # Try writing to network port
                        try:
                            with open(f"\\\\localhost\\{port_name}", "wb") as port:
                                port.write(zpl_content.encode('utf-8'))
                            return True, f"ZPL sent directly to printer port {port_name}"
                        except:
                            return False, f"Failed to write to printer port {port_name}"
                else:
                    return False, "Could not determine printer port"
            else:
                return False, f"Could not get printer port information: {result.stderr}"
                
        except Exception as e:
            return False, f"Direct port write failed: {str(e)}"