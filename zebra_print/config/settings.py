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
    api_script_path: str = ""  # Will be set dynamically
    
    # Printer Settings
    printer_name: str = "ZDesigner ZD230-203dpi ZPL"
    
    # Tunnel Settings
    tunnel_name: str = "zebra-printer"
    ngrok_region: str = "us"
    
    # Timeouts
    http_timeout: int = 30
    
    # Paths
    base_dir: str = ""  # Will be set dynamically
    
    def __post_init__(self):
        """Set default paths dynamically after initialization."""
        if not self.base_dir:
            # Get the directory where this script is located and go up to project root
            current_file = os.path.abspath(__file__)
            # From zebra_print/config/settings.py go up 2 levels to project root
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        
        if not self.api_script_path:
            self.api_script_path = os.path.join(self.base_dir, "label_print_api.py")
    
    @classmethod
    def from_env(cls) -> 'AppSettings':
        """Create settings from environment variables."""
        # Create instance with defaults first
        instance = cls()
        
        # Override with environment variables if provided
        instance.api_host = os.getenv('ZEBRA_API_HOST', instance.api_host)
        instance.api_port = int(os.getenv('ZEBRA_API_PORT', str(instance.api_port)))
        instance.printer_name = os.getenv('ZEBRA_PRINTER_NAME', instance.printer_name)
        instance.tunnel_name = os.getenv('ZEBRA_TUNNEL_NAME', instance.tunnel_name)
        instance.ngrok_region = os.getenv('ZEBRA_NGROK_REGION', instance.ngrok_region)
        instance.http_timeout = int(os.getenv('ZEBRA_HTTP_TIMEOUT', str(instance.http_timeout)))
        
        # Allow environment override for paths
        if os.getenv('ZEBRA_BASE_DIR'):
            instance.base_dir = os.getenv('ZEBRA_BASE_DIR')
        if os.getenv('ZEBRA_API_SCRIPT_PATH'):
            instance.api_script_path = os.getenv('ZEBRA_API_SCRIPT_PATH')
        
        return instance
    
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