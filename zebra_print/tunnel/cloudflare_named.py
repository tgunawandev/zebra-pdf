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
    
    def __init__(self, tunnel_name: str = "zebra-printer", local_port: int = 5000, 
                 custom_domain: Optional[str] = None):
        self.tunnel_name = tunnel_name
        self.local_port = local_port
        self.custom_domain = custom_domain  # e.g., "tln-zebra-01.abcfood.app"
        self.config_dir = os.path.expanduser("~/.cloudflared")
        self.config_file = os.path.join(self.config_dir, f"{tunnel_name}.yml")
        
        # Use cross-platform temp directory
        import tempfile
        temp_dir = tempfile.gettempdir()
        self.pid_file = os.path.join(temp_dir, f"cloudflared_{tunnel_name}.pid")
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
            # Check if cloudflared is installed (cross-platform)
            import platform
            if platform.system() == "Windows":
                result = subprocess.run(['where', 'cloudflared'], 
                                      capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                install_msg = "cloudflared not found. Download from: https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
            else:
                result = subprocess.run(['which', 'cloudflared'], 
                                      capture_output=True, text=True)
                install_msg = "cloudflared not found. Install: curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared.deb"
            
            if result.returncode != 0:
                return False, install_msg
            
            # Check authentication (try multiple possible locations)
            cert_paths_to_try = [
                os.path.join(self.config_dir, "cert.pem"),  # Standard location: ~/.cloudflared/cert.pem
                os.path.join(os.path.expanduser("~"), "cloudflared", "cert.pem"),  # User folder: ~/cloudflared/cert.pem  
                os.path.join(os.path.expanduser("~"), ".cloudflare", "cert.pem"),  # Alternative: ~/.cloudflare/cert.pem
                "cert.pem"  # Current directory
            ]
            
            cert_found = False
            for cert_path in cert_paths_to_try:
                if os.path.exists(cert_path):
                    cert_found = True
                    print(f"[AUTH] Found certificate at: {cert_path}")
                    break
            
            if not cert_found:
                return False, f"Authentication required. Run: cloudflared tunnel login. Searched: {cert_paths_to_try[0]}"
            
            # Get or prompt for custom domain
            if not self.custom_domain:
                stored_config = self.db.get_tunnel_config(self.name)
                if stored_config and stored_config.domain_mapping:
                    self.custom_domain = stored_config.domain_mapping
                else:
                    return False, "Custom domain required. Use set_custom_domain() method or configure in UI"
            
            # Create tunnel if not exists
            import platform
            if platform.system() == "Windows":
                tunnel_check = subprocess.run(['cloudflared', 'tunnel', 'list'], 
                                            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                tunnel_check = subprocess.run(['cloudflared', 'tunnel', 'list'], 
                                            capture_output=True, text=True)
            if self.tunnel_name not in tunnel_check.stdout:
                if platform.system() == "Windows":
                    create_result = subprocess.run(['cloudflared', 'tunnel', 'create', self.tunnel_name], 
                                                 capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    create_result = subprocess.run(['cloudflared', 'tunnel', 'create', self.tunnel_name], 
                                                 capture_output=True, text=True)
                if create_result.returncode != 0:
                    return False, f"Failed to create tunnel: {create_result.stderr}"
            
            # Create config file with custom domain
            try:
                self._create_named_tunnel_config()
            except Exception as config_error:
                return False, f"Failed to create tunnel config: {config_error}. Try running 'cloudflared tunnel create {self.tunnel_name}' manually."
            
            # Create DNS record
            if platform.system() == "Windows":
                dns_result = subprocess.run([
                    'cloudflared', 'tunnel', 'route', 'dns', self.tunnel_name, self.custom_domain
                ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                dns_result = subprocess.run([
                    'cloudflared', 'tunnel', 'route', 'dns', self.tunnel_name, self.custom_domain
                ], capture_output=True, text=True)
            
            if dns_result.returncode != 0 and "already exists" not in dns_result.stderr:
                # Check if it's a domain ownership issue
                if "neither the ID nor the name" in dns_result.stderr or "DNS" in dns_result.stderr:
                    return False, f"Domain '{self.custom_domain}' must be managed by Cloudflare DNS first. Please:\n1. Add domain to Cloudflare\n2. Update nameservers\n3. Verify domain is active\n\nError: {dns_result.stderr}"
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
    
    def _auto_discover_credentials(self) -> Optional[str]:
        """Auto-discover the correct credentials file for this tunnel."""
        try:
            # Method 1: Parse tunnel list to get tunnel ID
            import platform
            if platform.system() == "Windows":
                result = subprocess.run(['cloudflared', 'tunnel', 'list'], 
                                      capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                result = subprocess.run(['cloudflared', 'tunnel', 'list'], 
                                      capture_output=True, text=True)
            tunnel_id = None
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if self.tunnel_name in line:
                        parts = line.split()
                        if len(parts) > 0:
                            tunnel_id = parts[0]
                            break
            
            if tunnel_id:
                credentials_path = os.path.join(self.config_dir, f"{tunnel_id}.json")
                if os.path.exists(credentials_path):
                    return credentials_path
            
            # Method 2: Find any .json file and verify it matches our tunnel
            # Try multiple config directories
            config_dirs_to_check = [
                self.config_dir,  # ~/.cloudflared
                os.path.join(os.path.expanduser("~"), "cloudflared"),  # ~/cloudflared
                os.path.join(os.path.expanduser("~"), ".cloudflare"),  # ~/.cloudflare
                "."  # current directory
            ]
            
            for config_dir in config_dirs_to_check:
                if os.path.exists(config_dir):
                    for filename in os.listdir(config_dir):
                        if filename.endswith('.json') and len(filename) == 40:  # UUID.json format
                            credentials_path = os.path.join(config_dir, filename)
                            
                            # Verify this credential file belongs to our tunnel
                            tunnel_id_from_file = filename[:-5]  # Remove .json
                            if platform.system() == "Windows":
                                info_result = subprocess.run(['cloudflared', 'tunnel', 'info', tunnel_id_from_file], 
                                                           capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                            else:
                                info_result = subprocess.run(['cloudflared', 'tunnel', 'info', tunnel_id_from_file], 
                                                           capture_output=True, text=True)
                            
                            if info_result.returncode == 0 and self.tunnel_name in info_result.stdout:
                                return credentials_path
            
            return None
            
        except Exception as e:
            print(f"Credential discovery error: {e}")
            return None
    
    def _create_named_tunnel_config(self):
        """Create Cloudflare Named Tunnel configuration with automatic credential discovery."""
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Auto-discover credentials file
        credentials_file = self._auto_discover_credentials()
        
        if not credentials_file:
            # Last resort: look for any .json file
            for filename in os.listdir(self.config_dir):
                if filename.endswith('.json'):
                    credentials_file = os.path.join(self.config_dir, filename)
                    print(f"[WARNING]️ Using fallback credentials: {credentials_file}")
                    break
        
        if not credentials_file:
            # Final attempt: list all .json files in config directory for debugging
            json_files = []
            try:
                if os.path.exists(self.config_dir):
                    for f in os.listdir(self.config_dir):
                        if f.endswith('.json'):
                            json_files.append(f)
            except:
                pass
            
            error_msg = f"No tunnel credentials found for '{self.tunnel_name}'.\n"
            error_msg += f"Checked directory: {self.config_dir}\n"
            if json_files:
                error_msg += f"Found credential files: {json_files}\n"
                error_msg += "Try running: cloudflared tunnel delete zebra-printer && cloudflared tunnel create zebra-printer"
            else:
                error_msg += "No credential files found. Run 'cloudflared tunnel login' and 'cloudflared tunnel create zebra-printer'"
            
            raise Exception(error_msg)
        
        print(f"[OK] Using credentials: {credentials_file}")
        
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
            
            # Start tunnel with config file using robust background execution
            import platform
            import tempfile
            
            if platform.system() == "Windows":
                # Windows doesn't have nohup, but subprocess handles background execution
                cmd = ['cloudflared', 'tunnel', '--config', self.config_file, 'run', self.tunnel_name]
            else:
                cmd = ['nohup', 'cloudflared', 'tunnel', '--config', self.config_file, 'run', self.tunnel_name]
            
            # Start process in background with proper log handling
            
            if platform.system() == "Windows":
                log_file = os.path.join(tempfile.gettempdir(), f'cloudflared_{self.tunnel_name}.log')
                cwd = None
            else:
                log_file = os.path.join(tempfile.gettempdir(), f'cloudflared_{self.tunnel_name}.log')
                cwd = '/'
            
            with open(log_file, 'w') as f:
                if platform.system() == "Windows":
                    process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, 
                                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                else:
                    process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, 
                                             preexec_fn=os.setsid, cwd=cwd)
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait for tunnel to initialize (reduced for faster startup)
            time.sleep(2)
            
            # Verify tunnel is running using multiple methods
            if not self._verify_tunnel_health():
                # Read logs for debugging
                try:
                    with open(log_file, 'r') as f:
                        logs = f.read()
                    return False, f"Tunnel failed to start properly. Logs: {logs[-500:]}", None
                except:
                    return False, "Tunnel failed to start and no logs available", None
            
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
    
    def _verify_tunnel_health(self) -> bool:
        """Verify tunnel is healthy using multiple methods."""
        # Method 1: Check PID file and process
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)  # Check if process exists
                
                # Method 2: Check if cloudflared process is running
                import platform
                if platform.system() == "Windows":
                    ps_result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq cloudflared.exe'], 
                                             capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    # Check if our tunnel name appears in the output
                    if ps_result.returncode == 0 and self.tunnel_name in ps_result.stdout:
                        return True
                else:
                    ps_result = subprocess.run(['pgrep', '-f', f'cloudflared.*{self.tunnel_name}'], 
                                             capture_output=True, text=True)
                    if ps_result.returncode == 0:
                        return True
                if ps_result.returncode == 0:
                    return True
                    
            except (OSError, ProcessLookupError, ValueError):
                pass
        
        # Method 3: Check cloudflared tunnel list for active connections
        try:
            import platform
            if platform.system() == "Windows":
                result = subprocess.run(['cloudflared', 'tunnel', 'list'], 
                                      capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                result = subprocess.run(['cloudflared', 'tunnel', 'list'], 
                                      capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if self.tunnel_name in line and 'CONNECTIONS' in result.stdout:
                        # Check if this tunnel has active connections
                        parts = line.split()
                        if len(parts) >= 4:  # ID, NAME, CREATED, CONNECTIONS
                            return True
        except:
            pass
        
        return False
    
    def is_active(self) -> bool:
        """Check if tunnel is currently active using robust detection."""
        return self._verify_tunnel_health()
    
    def get_webhook_url(self) -> Optional[str]:
        """Get the webhook URL for Odoo integration."""
        if self.custom_domain and self.is_active():
            return f"https://{self.custom_domain}/print"
        return None