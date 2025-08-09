"""
Cloudflare Quick Tunnel implementation.
Provides instant URLs without domain ownership requirements.
"""

import os
import subprocess
import time
import re
from typing import Dict, Optional, Tuple
from zebra_print.tunnel.base import TunnelProvider
from zebra_print.database.db_manager import DatabaseManager
from zebra_print.database.models import TunnelConfig

class CloudflareQuickTunnel(TunnelProvider):
    """Cloudflare Quick Tunnel - no domain ownership required."""
    
    def __init__(self, local_port: int = 5000):
        self.local_port = local_port
        self.pid_file = f"/tmp/cloudflared_quick_{local_port}.pid"
        self.log_file = f"/tmp/cloudflared_quick_{local_port}.log"
        self.db = DatabaseManager()
        self._tunnel_url: Optional[str] = None
    
    @property
    def name(self) -> str:
        return "cloudflare_quick"
    
    @property
    def is_permanent(self) -> bool:
        return False  # Quick tunnels are temporary
    
    def setup(self) -> Tuple[bool, str]:
        """Setup Quick Tunnel (no configuration needed)."""
        # Quick tunnels require no setup - just authentication
        try:
            # Check if cloudflared is available (cross-platform)
            import platform
            if platform.system() == "Windows":
                result = subprocess.run(['where', 'cloudflared'], 
                                      capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                result = subprocess.run(['which', 'cloudflared'], 
                                      capture_output=True, text=True)
            if result.returncode != 0:
                return False, "cloudflared not found"
            
            # Save configuration (minimal for quick tunnel)
            config = TunnelConfig(
                name=self.name,
                is_configured=True,
                domain_mapping=None,  # Quick tunnels get random domains
                config_data={"local_port": self.local_port}
            )
            self.db.save_tunnel_config(config)
            
            return True, "Quick tunnel ready (no domain setup required)"
            
        except Exception as e:
            return False, f"Setup failed: {str(e)}"
    
    def start(self) -> Tuple[bool, str, Optional[str]]:
        """Start Quick Tunnel."""
        try:
            # Check if already running
            if self.is_active():
                stored_config = self.db.get_tunnel_config(self.name)
                if stored_config and stored_config.current_url:
                    return True, "Quick tunnel already running", stored_config.current_url
            
            # Start cloudflared quick tunnel
            cmd = ['cloudflared', 'tunnel', '--url', f'http://localhost:{self.local_port}']
            
            # Start process and capture output
            import platform
            with open(self.log_file, 'w') as log:
                if platform.system() == "Windows":
                    process = subprocess.Popen(cmd, stdout=log, stderr=log, 
                                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                else:
                    process = subprocess.Popen(cmd, stdout=log, stderr=log, preexec_fn=os.setsid)
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait for tunnel URL to appear in logs
            tunnel_url = None
            for attempt in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                
                if os.path.exists(self.log_file):
                    with open(self.log_file, 'r') as f:
                        log_content = f.read()
                    
                    # Look for trycloudflare.com URL
                    match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', log_content)
                    if match:
                        tunnel_url = match.group(0)
                        break
            
            if not tunnel_url:
                return False, "Failed to get tunnel URL (timeout after 30s)", None
            
            self._tunnel_url = tunnel_url
            
            # Update database with URL
            self.db.update_tunnel_status(self.name, True, tunnel_url)
            
            return True, f"Quick tunnel started", tunnel_url
            
        except Exception as e:
            return False, f"Failed to start tunnel: {str(e)}", None
    
    def stop(self) -> Tuple[bool, str]:
        """Stop Quick Tunnel."""
        try:
            if not os.path.exists(self.pid_file):
                return True, "Tunnel not running"
            
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Kill process (cross-platform)
            import platform
            if platform.system() == "Windows":
                # On Windows, use taskkill to terminate the process tree
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], 
                             capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # On Linux, kill process group
                os.killpg(os.getpgid(pid), 15)  # SIGTERM
            time.sleep(2)
            
            # Remove files
            for file_path in [self.pid_file, self.log_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            self._tunnel_url = None
            
            # Update database
            self.db.update_tunnel_status(self.name, False, None)
            
            return True, "Quick tunnel stopped"
            
        except Exception as e:
            return False, f"Failed to stop tunnel: {str(e)}"
    
    def get_status(self) -> Dict[str, any]:
        """Get current tunnel status."""
        stored_config = self.db.get_tunnel_config(self.name)
        
        status = {
            'active': self.is_active(),
            'configured': stored_config.is_configured if stored_config else False,
            'url': None,
            'pid': None,
            'temporary': True  # Quick tunnels are always temporary
        }
        
        if stored_config:
            status['url'] = stored_config.current_url
        
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    status['pid'] = int(f.read().strip())
            except:
                pass
        
        return status
    
    def is_active(self) -> bool:
        """Check if tunnel is currently active."""
        if not os.path.exists(self.pid_file):
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            os.kill(pid, 0)
            return True
            
        except (OSError, ProcessLookupError, ValueError):
            # Clean up stale files
            for file_path in [self.pid_file, self.log_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)
            return False
    
    def get_webhook_url(self) -> Optional[str]:
        """Get the webhook URL for Odoo integration."""
        if self._tunnel_url and self.is_active():
            return f"{self._tunnel_url}/print"
        
        # Check database for stored URL
        stored_config = self.db.get_tunnel_config(self.name)
        if stored_config and stored_config.current_url and self.is_active():
            return f"{stored_config.current_url}/print"
        
        return None