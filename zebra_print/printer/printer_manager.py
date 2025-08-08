"""
Printer management system for multiple printer support.
"""

import subprocess
from typing import Dict, List, Optional

class PrinterManager:
    """Manages multiple printers and provides discovery capabilities."""
    
    def __init__(self):
        pass
    
    def get_all_printers(self) -> Dict[str, Dict]:
        """Get all available printers with their status."""
        printers = {}
        
        try:
            # Get printer list from CUPS
            result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('printer '):
                        # Parse: "printer ZTC-ZD230-203dpi-ZPL is idle.  enabled since ..."
                        parts = line.split()
                        if len(parts) >= 4:
                            printer_name = parts[1]
                            status = parts[3]  # idle, printing, etc.
                            
                            printers[printer_name] = {
                                'name': printer_name,
                                'status': status,
                                'type': self._detect_printer_type(printer_name),
                                'connection': self._get_printer_connection(printer_name),
                                'queue_jobs': self._get_queue_count(printer_name)
                            }
            
            return printers
            
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_printer_type(self, printer_name: str) -> str:
        """Detect printer type from name."""
        name_lower = printer_name.lower()
        if 'zebra' in name_lower or 'ztc' in name_lower or 'zd' in name_lower:
            return 'zebra'
        elif 'hp' in name_lower:
            return 'hp'
        elif 'canon' in name_lower:
            return 'canon'
        elif 'brother' in name_lower:
            return 'brother'
        else:
            return 'unknown'
    
    def _get_printer_connection(self, printer_name: str) -> str:
        """Get printer connection type."""
        try:
            result = subprocess.run(['lpstat', '-v', printer_name], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                if 'usb://' in result.stdout:
                    return 'USB'
                elif 'network' in result.stdout or 'socket://' in result.stdout:
                    return 'Network'
                elif 'ipp://' in result.stdout:
                    return 'IPP'
                else:
                    return 'Other'
            return 'Unknown'
        except:
            return 'Unknown'
    
    def _get_queue_count(self, printer_name: str) -> int:
        """Get number of jobs in printer queue."""
        try:
            result = subprocess.run(['lpstat', '-o', printer_name], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Count non-empty lines
                return len([line for line in result.stdout.split('\n') if line.strip()])
            return 0
        except:
            return 0
    
    def get_zebra_printers(self) -> Dict[str, Dict]:
        """Get only Zebra printers."""
        all_printers = self.get_all_printers()
        return {name: info for name, info in all_printers.items() 
                if info.get('type') == 'zebra'}
    
    def is_printer_available(self, printer_name: str) -> bool:
        """Check if a specific printer is available."""
        printers = self.get_all_printers()
        return printer_name in printers and printers[printer_name]['status'] in ['idle', 'processing']
    
    def get_default_printer(self) -> Optional[str]:
        """Get the default printer (first available Zebra printer)."""
        zebra_printers = self.get_zebra_printers()
        if zebra_printers:
            return list(zebra_printers.keys())[0]
        
        all_printers = self.get_all_printers()
        if all_printers:
            return list(all_printers.keys())[0]
        
        return None
    
    def test_printer(self, printer_name: str) -> Tuple[bool, str]:
        """Test printer connectivity."""
        try:
            result = subprocess.run(['lpstat', '-p', printer_name], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                if 'idle' in result.stdout:
                    return True, f"Printer {printer_name} is ready"
                else:
                    return True, f"Printer {printer_name} status: {result.stdout.strip()}"
            else:
                return False, f"Printer {printer_name} not found or unavailable"
                
        except Exception as e:
            return False, f"Printer test failed: {str(e)}"