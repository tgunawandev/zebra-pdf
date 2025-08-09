"""
Cloudflare Tunnel implementation.
Provides permanent URL solution using Cloudflare tunnels.
"""

import os
import json
import subprocess
import time
from typing import Dict, Optional, Tuple
from zebra_print.tunnel.base import TunnelProvider

class CloudflareTunnel(TunnelProvider):
    """Cloudflare tunnel provider implementation."""
    
    def __init__(self, tunnel_name: str = "zebra-quick", local_port: int = 5000):
        self.tunnel_name = tunnel_name
        self.local_port = local_port
        self.config_dir = os.path.expanduser("~/.cloudflared")
        self.config_file = os.path.join(self.config_dir, f"{tunnel_name}.yml")
        self.pid_file = f"/tmp/cloudflared_{tunnel_name}.pid"
        self._tunnel_url: Optional[str] = None
    
    @property
    def name(self) -> str:
        return "cloudflare"
    
    @property
    def is_permanent(self) -> bool:
        # Quick Tunnels are temporary, like ngrok
        # For permanent tunnels, you need a Cloudflare domain and authentication
        return False
    
    def setup(self) -> Tuple[bool, str]:
        """Setup Cloudflare tunnel (Quick Tunnel mode - no auth required)."""
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
                install_msg = "cloudflared not found. Please install: curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared.deb"
            
            if result.returncode != 0:
                return False, install_msg
            
            # Test cloudflared can run
            if platform.system() == "Windows":
                test_result = subprocess.run(['cloudflared', '--version'], 
                                           capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                test_result = subprocess.run(['cloudflared', '--version'], 
                                           capture_output=True, text=True)
            if test_result.returncode != 0:
                return False, "cloudflared installation appears to be broken"
            
            # Quick Tunnels don't require authentication or tunnel creation
            # They work like ngrok - just start and get a temporary URL
            
            return True, f"Cloudflare Quick Tunnel ready (no authentication required)"
            
        except Exception as e:
            return False, f"Setup failed: {str(e)}"
    
    def _create_config_file(self):
        """Create Cloudflare tunnel configuration file."""
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Use simple config without hostname for quick tunnels
        config = {
            'tunnel': self.tunnel_name,
            'credentials-file': os.path.join(self.config_dir, f"{self.tunnel_name}.json"),
            'ingress': [
                {
                    'service': f"http://localhost:{self.local_port}"
                }
            ]
        }
        
        with open(self.config_file, 'w') as f:
            import yaml
            yaml.safe_dump(config, f, default_flow_style=False)
    
    def start(self) -> Tuple[bool, str, Optional[str]]:
        """Start the Cloudflare tunnel."""
        try:
            # Check if already running
            if self.is_active():
                status = self.get_status()
                return True, "Tunnel already running", status.get('url')
            
            # Use Quick Tunnel instead of named tunnel for simplicity
            # This is like ngrok but uses Cloudflare infrastructure
            cmd = ['cloudflared', 'tunnel', '--url', f'http://localhost:{self.local_port}']
            
            import platform
            if platform.system() == "Windows":
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, 
                                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                                         text=True, bufsize=1, universal_newlines=True)
            else:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT, preexec_fn=os.setsid, 
                                         text=True, bufsize=1, universal_newlines=True)
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait and parse output for URL
            tunnel_url = None
            start_time = time.time()
            timeout = 30  # 30 second timeout
            
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    # Process died
                    break
                
                try:
                    # Read a line from stdout
                    line = process.stdout.readline()
                    if line:
                        # Look for the tunnel URL in the output
                        if 'https://' in line and 'trycloudflare.com' in line:
                            # Extract URL
                            import re
                            url_match = re.search(r'https://[^\s]+\.trycloudflare\.com', line)
                            if url_match:
                                tunnel_url = url_match.group(0)
                                break
                except:
                    pass
                
                time.sleep(0.5)
            
            self._tunnel_url = tunnel_url
            
            if tunnel_url:
                return True, f"Cloudflare Quick Tunnel started", tunnel_url
            else:
                return False, "Tunnel started but URL not found", None
                
        except Exception as e:
            return False, f"Failed to start tunnel: {str(e)}", None
    
    def stop(self) -> Tuple[bool, str]:
        """Stop the Cloudflare tunnel."""
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
            
            return True, "Cloudflare tunnel stopped"
            
        except Exception as e:
            return False, f"Failed to stop tunnel: {str(e)}"
    
    def get_status(self) -> Dict[str, any]:
        """Get current tunnel status."""
        status = {
            'active': self.is_active(),
            'url': self._tunnel_url,
            'pid': None,
            'config_file': self.config_file
        }
        
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    status['pid'] = int(f.read().strip())
            except:
                pass
        
        if not status['url'] and status['active']:
            status['url'] = self._get_tunnel_url()
            self._tunnel_url = status['url']
        
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
    
    def _get_tunnel_url(self) -> Optional[str]:
        """Extract tunnel URL from cloudflared logs or info."""
        try:
            # First try to get from tunnel info
            import platform
            if platform.system() == "Windows":
                result = subprocess.run(['cloudflared', 'tunnel', 'info', self.tunnel_name], 
                                      capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                result = subprocess.run(['cloudflared', 'tunnel', 'info', self.tunnel_name], 
                                      capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    # Look for any https URL
                    if 'https://' in line:
                        parts = line.split()
                        for part in parts:
                            if part.startswith('https://'):
                                return part.strip()
            
            # Try to get URL from running process logs
            # This requires checking the process output, which is more complex
            # For now, we'll use a simpler approach - check if tunnel is accessible
            
            # Try common Cloudflare tunnel patterns
            potential_urls = []
            
            # Quick tunnel format: https://random-words.trycloudflare.com
            # We can't predict this, so we'll need to parse logs or use API
            
            return None
            
        except Exception:
            return None