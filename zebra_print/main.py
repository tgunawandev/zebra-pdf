"""
Main entry point for the Zebra Print Control System.
Implements dependency injection and coordinates all components.
"""

import sys
from typing import Dict
from zebra_print.config.settings import AppSettings
from zebra_print.api.flask_service import FlaskAPIService
from zebra_print.api.http_client import HTTPAPIClient
from zebra_print.printer import get_zebra_printer
from zebra_print.tunnel.cloudflare import CloudflareTunnel
from zebra_print.tunnel.cloudflare_named import CloudflareNamedTunnel
from zebra_print.tunnel.cloudflare_quick import CloudflareQuickTunnel
from zebra_print.tunnel.ngrok import NgrokTunnel
from zebra_print.tunnel.base import TunnelProvider
from zebra_print.core.system_status import SystemStatus
from zebra_print.core.label_service import LabelService
from zebra_print.ui.menu_controller import MenuController

class ZebraPrintApplication:
    """Main application class with dependency injection."""
    
    def __init__(self, settings: AppSettings = None):
        self.settings = settings or AppSettings.from_env()
        self._setup_dependencies()
    
    def _setup_dependencies(self):
        """Setup all application dependencies."""
        
        # Core services
        self.api_service = FlaskAPIService(
            port=self.settings.api_port,
            host=self.settings.api_host
        )
        
        self.api_client = HTTPAPIClient(
            timeout=self.settings.http_timeout
        )
        
        self.printer_service = get_zebra_printer(
            printer_name=self.settings.printer_name
        )
        
        # Tunnel providers
        self.tunnel_providers: Dict[str, TunnelProvider] = {
            'cloudflare': CloudflareTunnel(
                tunnel_name="zebra-quick",  # Use different name to avoid conflicts
                local_port=self.settings.api_port
            ),
            'cloudflare_named': CloudflareNamedTunnel(
                tunnel_name=self.settings.tunnel_name,
                local_port=self.settings.api_port
            ),
            'cloudflare_quick': CloudflareQuickTunnel(
                local_port=self.settings.api_port
            ),
            'ngrok': NgrokTunnel(
                local_port=self.settings.api_port,
                region=self.settings.ngrok_region
            )
        }
        
        # Coordinator services
        self.system_status = SystemStatus(
            api_service=self.api_service,
            printer_service=self.printer_service,
            tunnel_providers=self.tunnel_providers
        )
        
        self.label_service = LabelService(
            api_client=self.api_client
        )
        
        # UI Controller
        self.menu_controller = MenuController(
            system_status=self.system_status,
            label_service=self.label_service
        )
    
    def run(self):
        """Run the application."""
        try:
            print("[*] Starting Zebra Print Control System...")
            print(f"[*] Base directory: {self.settings.base_dir}")
            print(f"[*] Printer: {self.settings.printer_name}")
            print(f"[*] API: {self.settings.api_host}:{self.settings.api_port}")
            print(f"[*] Tunnel: {self.settings.tunnel_name}")
            
            # Run the main menu
            self.menu_controller.run()
            
        except KeyboardInterrupt:
            print("\n[!] Application interrupted by user")
            self._cleanup()
        except Exception as e:
            print(f"\n[ERROR] Application error: {e}")
            self._cleanup()
            sys.exit(1)
    
    def _cleanup(self):
        """Cleanup resources before exit."""
        print("\n[*] Cleaning up...")
        
        try:
            # Stop API service if running
            if self.api_service.is_running():
                print("[*] Stopping API service...")
                self.api_service.stop()
            
            # Stop any active tunnels
            for tunnel in self.tunnel_providers.values():
                if tunnel.is_active():
                    print(f"[*] Stopping {tunnel.name} tunnel...")
                    tunnel.stop()
            
            # Close API client session
            if hasattr(self.api_client, 'close'):
                self.api_client.close()
                
        except Exception as e:
            print(f"[WARNING] Cleanup warning: {e}")
        
        print("[*] Cleanup completed")

def main():
    """Application entry point."""
    app = ZebraPrintApplication()
    app.run()

if __name__ == "__main__":
    main()