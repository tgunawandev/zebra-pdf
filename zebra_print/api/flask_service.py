"""
Flask-based API service implementation.
Manages the Flask server for handling label print requests.
"""

import os
import signal
import subprocess
import time
import requests
import tempfile
from typing import Dict, Tuple
from zebra_print.api.base import APIService

class FlaskAPIService(APIService):
    """Flask-based API service implementation."""
    
    def __init__(self, port: int = 5000, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        
        # Use cross-platform temp directory
        temp_dir = tempfile.gettempdir()
        self.pid_file = os.path.join(temp_dir, f"flask_api_{port}.pid")
        
        # Set script path dynamically
        current_file = os.path.abspath(__file__)
        # From zebra_print/api/flask_service.py go up 3 levels to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        self.script_path = os.path.join(project_root, "label_print_api.py")
    
    def is_running(self) -> bool:
        """Check if API service is running (PID file or HTTP response)."""
        # Method 1: Check PID file (for manually started instances)
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Check if process is still running
                os.kill(pid, 0)
                return True
                
            except (OSError, ProcessLookupError, ValueError):
                # Clean up stale PID file
                os.remove(self.pid_file)
        
        # Method 2: Check if API is responding (for supervisor/Docker instances)
        return self._health_check()
    
    def start(self) -> Tuple[bool, str]:
        """Start the API service."""
        try:
            if self.is_running():
                return True, "API server already running"
            
            if not os.path.exists(self.script_path):
                return False, f"API script not found: {self.script_path}"
            
            # Start Flask server in background
            import platform
            if platform.system() == "Windows":
                # Use python instead of python3 on Windows
                cmd = ['python', self.script_path]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, 
                                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                # Unix/Linux
                cmd = ['python3', self.script_path]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, preexec_fn=os.setsid)
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait for server to start
            time.sleep(2)
            
            # Verify server is responding
            if self._health_check():
                return True, f"API server started on {self.host}:{self.port}"
            else:
                # Check if process is still running
                if self.is_running():
                    return False, "API server started but not responding to health check"
                else:
                    # Process died, check stderr for error
                    try:
                        stderr_output = process.stderr.read().decode().strip() if process.stderr else ""
                        if "Port" in stderr_output and "in use" in stderr_output:
                            return False, f"Port {self.port} is already in use by another process"
                        else:
                            return False, f"API server process died: {stderr_output}"
                    except:
                        return False, "API server process died unexpectedly"
                
        except Exception as e:
            return False, f"Failed to start API server: {str(e)}"
    
    def stop(self) -> Tuple[bool, str]:
        """Stop the API service."""
        try:
            if not os.path.exists(self.pid_file):
                return True, "API server not running"
            
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Cross-platform process termination
            import platform
            if platform.system() == "Windows":
                # Windows process termination
                try:
                    import psutil
                    process = psutil.Process(pid)
                    process.terminate()
                    time.sleep(2)
                    if process.is_running():
                        process.kill()
                except ImportError:
                    # Fallback if psutil not available
                    subprocess.run(['taskkill', '/pid', str(pid), '/f'], check=False)
                except Exception:
                    # Final fallback
                    subprocess.run(['taskkill', '/pid', str(pid), '/f'], check=False)
            else:
                # Unix/Linux process termination
                try:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    time.sleep(2)
                    # Force kill if still running
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGKILL)
                    except:
                        pass
                except:
                    # Fallback to simple kill
                    try:
                        os.kill(pid, signal.SIGTERM)
                        time.sleep(2)
                        os.kill(pid, signal.SIGKILL)
                    except:
                        pass
            
            # Remove PID file
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            
            return True, "API server stopped"
            
        except Exception as e:
            return False, f"Failed to stop API server: {str(e)}"
    
    def get_status(self) -> Dict[str, any]:
        """Get API service status."""
        # Use localhost for client connections when server binds to 0.0.0.0
        client_host = "localhost" if self.host == "0.0.0.0" else self.host
        
        status = {
            'running': self.is_running(),
            'host': client_host,
            'port': self.port,
            'pid': None,
            'health': False,
            'url': f"http://{client_host}:{self.port}"
        }
        
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    status['pid'] = int(f.read().strip())
            except:
                pass
        
        if status['running']:
            status['health'] = self._health_check()
        
        return status
    
    def _health_check(self) -> bool:
        """Perform internal health check."""
        try:
            response = requests.get(f"http://{self.host}:{self.port}/health", timeout=3)
            return response.status_code == 200
        except:
            return False