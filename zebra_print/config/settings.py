"""
Application settings and configuration.
Centralizes all configuration options.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AppSettings:
    """Application configuration settings."""
    
    # API Server Settings
    api_host: str = "0.0.0.0"
    api_port: int = 5000
    api_script_path: str = "/home/tgunawan/project/01-web/zebra-pdf/label_print_api.py"
    
    # Printer Settings
    printer_name: str = "ZTC-ZD230-203dpi-ZPL"
    
    # Tunnel Settings
    tunnel_name: str = "zebra-print"
    ngrok_region: str = "us"
    
    # Timeouts
    http_timeout: int = 30
    
    # Paths
    base_dir: str = "/home/tgunawan/project/01-web/zebra-pdf"
    
    @classmethod
    def from_env(cls) -> 'AppSettings':
        """Create settings from environment variables."""
        return cls(
            api_host=os.getenv('ZEBRA_API_HOST', cls.api_host),
            api_port=int(os.getenv('ZEBRA_API_PORT', str(cls.api_port))),
            api_script_path=os.getenv('ZEBRA_API_SCRIPT_PATH', cls.api_script_path),
            printer_name=os.getenv('ZEBRA_PRINTER_NAME', cls.printer_name),
            tunnel_name=os.getenv('ZEBRA_TUNNEL_NAME', cls.tunnel_name),
            ngrok_region=os.getenv('ZEBRA_NGROK_REGION', cls.ngrok_region),
            http_timeout=int(os.getenv('ZEBRA_HTTP_TIMEOUT', str(cls.http_timeout))),
            base_dir=os.getenv('ZEBRA_BASE_DIR', cls.base_dir)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            'api_host': self.api_host,
            'api_port': self.api_port,
            'api_script_path': self.api_script_path,
            'printer_name': self.printer_name,
            'tunnel_name': self.tunnel_name,
            'ngrok_region': self.ngrok_region,
            'http_timeout': self.http_timeout,
            'base_dir': self.base_dir
        }