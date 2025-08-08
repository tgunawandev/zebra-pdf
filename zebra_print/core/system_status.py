"""
System status coordinator.
Manages the overall system state and coordinates between components.
"""

from typing import Dict, Optional
from zebra_print.api.base import APIService
from zebra_print.printer.base import PrinterService
from zebra_print.tunnel.base import TunnelProvider
from zebra_print.database.db_manager import DatabaseManager

class SystemStatus:
    """Coordinates system status across all components."""
    
    def __init__(self, 
                 api_service: APIService,
                 printer_service: PrinterService,
                 tunnel_providers: Dict[str, TunnelProvider]):
        self.api_service = api_service
        self.printer_service = printer_service
        self.tunnel_providers = tunnel_providers
        self._active_tunnel: Optional[TunnelProvider] = None
        self.db = DatabaseManager()
    
    def get_overall_status(self) -> Dict[str, any]:
        """Get comprehensive system status."""
        # API status
        api_running = self.api_service.is_running()
        api_status = self.api_service.get_status() if api_running else {}
        
        # Printer status
        printer_ready = self.printer_service.is_ready()
        printer_status = self.printer_service.get_status()
        
        # Tunnel status (check database first)
        active_tunnel = self.get_active_tunnel()
        tunnel_info = None
        
        # Check for configured tunnels in database
        tunnel_configs = self.db.get_all_tunnel_configs()
        configured_tunnels = [tc for tc in tunnel_configs if tc.is_configured]
        
        if active_tunnel and active_tunnel.is_active():
            tunnel_info = {
                'name': active_tunnel.name,
                'is_permanent': active_tunnel.is_permanent,
                'status': active_tunnel.get_status(),
                'configured': True
            }
        elif configured_tunnels:
            # Show configured but not active tunnel
            config = configured_tunnels[0]  # Get first configured
            tunnel_info = {
                'name': config.name,
                'is_permanent': config.name == 'cloudflare_named',
                'status': {'configured': True, 'active': False, 'url': config.current_url},
                'configured': True
            }
        
        # Integration readiness
        integration_ready = api_running and printer_ready and active_tunnel is not None
        
        return {
            'api': {
                'running': api_running,
                'details': api_status
            },
            'printer': {
                'ready': printer_ready,
                'details': printer_status
            },
            'tunnel': tunnel_info,
            'integration_ready': integration_ready,
            'webhook_url': tunnel_info['status'].get('url') + '/print' if tunnel_info and tunnel_info['status'].get('url') else None
        }
    
    def get_active_tunnel(self) -> Optional[TunnelProvider]:
        """Get the currently active tunnel provider."""
        if self._active_tunnel and self._active_tunnel.is_active():
            return self._active_tunnel
        
        # Check all tunnel providers to find active one
        for tunnel in self.tunnel_providers.values():
            if tunnel.is_active():
                self._active_tunnel = tunnel
                return tunnel
        
        self._active_tunnel = None
        return None
    
    def is_system_ready(self) -> bool:
        """Check if the entire system is ready for operation."""
        status = self.get_overall_status()
        return status['integration_ready']
    
    def get_recommended_actions(self) -> list:
        """Get list of recommended actions to make system ready."""
        actions = []
        status = self.get_overall_status()
        
        if not status['api']['running']:
            actions.append("Start API server")
        
        if not status['printer']['ready']:
            actions.append("Check printer connection and status")
        
        if not status['tunnel']:
            actions.append("Set up and start tunnel (Cloudflare recommended)")
        
        return actions