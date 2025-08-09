"""
Ngrok tunnel implementation.
Provides temporary URL solution using ngrok tunnels.
"""

import os
import json
import subprocess
import time
import requests
from typing import Dict, Optional, Tuple
from zebra_print.tunnel.base import TunnelProvider

class NgrokTunnel(TunnelProvider):
    """Ngrok tunnel provider implementation."""
    
    def __init__(self, local_port: int = 5000, region: str = "us"):
        self.local_port = local_port
        self.region = region
        self.pid_file = f"/tmp/ngrok_{local_port}.pid"
        self.api_url = "http://localhost:4040/api/tunnels"
        self._tunnel_url: Optional[str] = None
    
    @property
    def name(self) -> str:
        return "ngrok"
    
    @property
    def is_permanent(self) -> bool:
        return False
    
    def setup(self) -> Tuple[bool, str]:
        """Setup ngrok with authentication."""
        try:
            # Check if ngrok is installed
            result = subprocess.run(['which', 'ngrok'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return False, "ngrok not found. Please install: curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo \"deb https://ngrok-agent.s3.amazonaws.com buster main\" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok"
            
            # Check if authenticated
            config_result = subprocess.run(['ngrok', 'config', 'check'], 
                                         capture_output=True, text=True)
            if "valid" not in config_result.stdout.lower():
                return False, "Ngrok authentication required. Please run: ngrok config add-authtoken YOUR_TOKEN"
            
            return True, "Ngrok setup completed"
            
        except Exception as e:
            return False, f"Setup failed: {str(e)}"
    
    def start(self) -> Tuple[bool, str, Optional[str]]:
        """Start the ngrok tunnel."""
        try:
            # Check if already running
            if self.is_active():
                status = self.get_status()
                return True, "Tunnel already running", status.get('url')
            
            # Start ngrok in background
            cmd = ['ngrok', 'http', str(self.local_port), '--region', self.region, '--log', 'stdout']
            import platform
            if platform.system() == "Windows":
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, 
                                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, preexec_fn=os.setsid)
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait for ngrok to establish connection
            time.sleep(3)
            
            # Get tunnel URL from API
            tunnel_url = self._get_tunnel_url_from_api()
            self._tunnel_url = tunnel_url
            
            if tunnel_url:
                return True, f"Ngrok tunnel started successfully", tunnel_url
            else:
                return False, "Tunnel started but URL not found", None
                
        except Exception as e:
            return False, f"Failed to start tunnel: {str(e)}", None
    
    def stop(self) -> Tuple[bool, str]:
        """Stop the ngrok tunnel."""
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
            
            return True, "Ngrok tunnel stopped"
            
        except Exception as e:
            return False, f"Failed to stop tunnel: {str(e)}"
    
    def get_status(self) -> Dict[str, any]:
        """Get current tunnel status."""
        status = {
            'active': self.is_active(),
            'url': self._tunnel_url,
            'pid': None,
            'api_available': self._is_api_available()
        }
        
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    status['pid'] = int(f.read().strip())
            except:
                pass
        
        if not status['url'] and status['active'] and status['api_available']:
            status['url'] = self._get_tunnel_url_from_api()
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
    
    def _is_api_available(self) -> bool:
        """Check if ngrok API is available."""
        try:
            response = requests.get(self.api_url, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _get_tunnel_url_from_api(self) -> Optional[str]:
        """Get tunnel URL from ngrok API."""
        try:
            if not self._is_api_available():
                return None
            
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                
                for tunnel in tunnels:
                    if (tunnel.get('config', {}).get('addr') == f"http://localhost:{self.local_port}" and 
                        tunnel.get('proto') == 'https'):
                        return tunnel.get('public_url')
                
                # Fallback: get first HTTPS tunnel
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        return tunnel.get('public_url')
            
            return None
            
        except Exception:
            return None
    
    def get_public_url(self) -> Optional[str]:
        """Get the current public URL (alias for compatibility)."""
        if self._tunnel_url:
            return self._tunnel_url
        
        if self.is_active():
            return self._get_tunnel_url_from_api()
        
        return None