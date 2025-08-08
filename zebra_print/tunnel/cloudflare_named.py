"""
Cloudflare Named Tunnel implementation with custom domain mapping.
Provides permanent URLs with custom subdomains like tln-zebra-01.abcfood.app
"""

import os
import json
import subprocess
import time
import yaml
from typing import Dict, Optional, Tuple
from zebra_print.tunnel.base import TunnelProvider
from zebra_print.database.db_manager import DatabaseManager
from zebra_print.database.models import TunnelConfig

class CloudflareNamedTunnel(TunnelProvider):
    """Cloudflare Named Tunnel with custom domain mapping."""
    
    def __init__(self, tunnel_name: str = "zebra-print", local_port: int = 5000, 
                 custom_domain: Optional[str] = None):
        self.tunnel_name = tunnel_name
        self.local_port = local_port
        self.custom_domain = custom_domain  # e.g., "tln-zebra-01.abcfood.app"
        self.config_dir = os.path.expanduser("~/.cloudflared")
        self.config_file = os.path.join(self.config_dir, f"{tunnel_name}.yml")
        self.pid_file = f"/tmp/cloudflared_{tunnel_name}.pid"
        self.db = DatabaseManager()
        self._tunnel_url: Optional[str] = None
    
    @property
    def name(self) -> str:
        return "cloudflare_named"
    
    @property
    def is_permanent(self) -> bool:
        return True  # Named tunnels with domains are permanent
    
    def set_custom_domain(self, domain: str) -> Tuple[bool, str]:
        """Set custom domain for this tunnel."""
        if not domain or '.' not in domain:
            return False, "Invalid domain format"
        
        self.custom_domain = domain
        
        # Save to database
        config = TunnelConfig(
            name=self.name,
            is_configured=True,
            domain_mapping=domain,
            config_data={"tunnel_name": self.tunnel_name, "local_port": self.local_port}
        )
        self.db.save_tunnel_config(config)
        
        return True, f"Custom domain set to: {domain}"
    
    def setup(self) -> Tuple[bool, str]:
        """Setup Cloudflare Named Tunnel with authentication and domain."""
        try:
            # Check if cloudflared is installed
            result = subprocess.run(['which', 'cloudflared'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return False, "cloudflared not found. Install: curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared.deb"
            
            # Check authentication
            cert_path = os.path.join(self.config_dir, "cert.pem")
            if not os.path.exists(cert_path):
                return False, "Authentication required. Run: cloudflared tunnel login"
            
            # Get or prompt for custom domain
            if not self.custom_domain:
                stored_config = self.db.get_tunnel_config(self.name)
                if stored_config and stored_config.domain_mapping:
                    self.custom_domain = stored_config.domain_mapping
                else:
                    return False, "Custom domain required. Use set_custom_domain() method or configure in UI"
            
            # Create tunnel if not exists
            tunnel_check = subprocess.run(['cloudflared', 'tunnel', 'list'], 
                                        capture_output=True, text=True)
            if self.tunnel_name not in tunnel_check.stdout:
                create_result = subprocess.run(['cloudflared', 'tunnel', 'create', self.tunnel_name], 
                                             capture_output=True, text=True)
                if create_result.returncode != 0:
                    return False, f"Failed to create tunnel: {create_result.stderr}"
            
            # Create config file with custom domain
            self._create_named_tunnel_config()
            
            # Create DNS record
            dns_result = subprocess.run([
                'cloudflared', 'tunnel', 'route', 'dns', self.tunnel_name, self.custom_domain
            ], capture_output=True, text=True)
            
            if dns_result.returncode != 0 and "already exists" not in dns_result.stderr:
                return False, f"Failed to create DNS record: {dns_result.stderr}"
            
            # Save configuration to database
            config = TunnelConfig(
                name=self.name,
                is_configured=True,
                domain_mapping=self.custom_domain,
                config_data={
                    "tunnel_name": self.tunnel_name,
                    "local_port": self.local_port,
                    "config_file": self.config_file
                }
            )
            self.db.save_tunnel_config(config)
            
            return True, f"Named tunnel '{self.tunnel_name}' configured with domain: {self.custom_domain}"
            
        except Exception as e:
            return False, f"Setup failed: {str(e)}"
    
    def _create_named_tunnel_config(self):
        """Create Cloudflare Named Tunnel configuration with custom domain."""
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Find tunnel credentials file
        credentials_file = None
        tunnel_id = None
        
        # Get tunnel ID from list
        result = subprocess.run(['cloudflared', 'tunnel', 'list'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\\n'):
                if self.tunnel_name in line:
                    parts = line.split()
                    if len(parts) > 0:
                        tunnel_id = parts[0]
                        break
        
        if tunnel_id:
            credentials_file = os.path.join(self.config_dir, f"{tunnel_id}.json")
        
        config = {
            'tunnel': self.tunnel_name,
            'credentials-file': credentials_file,
            'ingress': [
                {
                    'hostname': self.custom_domain,
                    'service': f"http://localhost:{self.local_port}"
                },
                {
                    'service': 'http_status:404'
                }
            ]
        }
        
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False)
    
    def start(self) -> Tuple[bool, str, Optional[str]]:
        """Start the Named Tunnel."""
        try:
            # Check if already running
            if self.is_active():
                return True, "Named tunnel already running", f"https://{self.custom_domain}"
            
            # Ensure we have configuration
            stored_config = self.db.get_tunnel_config(self.name)
            if not stored_config or not stored_config.is_configured:
                return False, "Tunnel not configured. Run setup first.", None
            
            if stored_config.domain_mapping:
                self.custom_domain = stored_config.domain_mapping
            
            # Start tunnel with config file
            cmd = ['cloudflared', 'tunnel', '--config', self.config_file, 'run', self.tunnel_name]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, preexec_fn=os.setsid)
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait for tunnel to start
            time.sleep(5)
            
            # The URL is our custom domain
            tunnel_url = f"https://{self.custom_domain}"
            self._tunnel_url = tunnel_url
            
            # Update database
            self.db.update_tunnel_status(self.name, True, tunnel_url)
            
            return True, f"Named tunnel started successfully", tunnel_url
            
        except Exception as e:
            return False, f"Failed to start tunnel: {str(e)}", None
    
    def stop(self) -> Tuple[bool, str]:
        """Stop the Named Tunnel."""
        try:
            if not os.path.exists(self.pid_file):
                return True, "Tunnel not running"
            
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Kill process group
            os.killpg(os.getpgid(pid), 15)  # SIGTERM
            time.sleep(2)
            
            # Remove PID file
            os.remove(self.pid_file)
            self._tunnel_url = None
            
            # Update database
            self.db.update_tunnel_status(self.name, False, None)
            
            return True, "Named tunnel stopped"
            
        except Exception as e:
            return False, f"Failed to stop tunnel: {str(e)}"
    
    def get_status(self) -> Dict[str, any]:
        """Get current tunnel status."""
        stored_config = self.db.get_tunnel_config(self.name)
        
        status = {
            'active': self.is_active(),
            'configured': stored_config.is_configured if stored_config else False,
            'url': None,
            'domain': self.custom_domain,
            'pid': None,
            'config_file': self.config_file
        }
        
        if stored_config:
            status['url'] = stored_config.current_url
            if stored_config.domain_mapping:
                status['domain'] = stored_config.domain_mapping
                if status['active']:
                    status['url'] = f"https://{stored_config.domain_mapping}"
        
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
            # Clean up stale PID file
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            return False
    
    def get_webhook_url(self) -> Optional[str]:
        """Get the webhook URL for Odoo integration."""
        if self.custom_domain and self.is_active():
            return f"https://{self.custom_domain}/print"
        return None