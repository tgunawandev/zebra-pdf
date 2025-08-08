#!/usr/bin/env python3
"""
Stop Label Printing API Server
Simple script to stop the background server.
"""

import os
import signal
import requests
import time

def is_server_running():
    """Check if server is running."""
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        return response.ok
    except:
        return False

def stop_server():
    """Stop the API server."""
    if not is_server_running():
        print("⚠️  API server is not running")
        # Clean up PID file if it exists
        if os.path.exists('.server.pid'):
            os.remove('.server.pid')
            print("🧹 Cleaned up stale PID file")
        return True
    
    print("🛑 Stopping API server...")
    
    try:
        if os.path.exists('.server.pid'):
            with open('.server.pid', 'r') as f:
                pid = int(f.read().strip())
            
            # Send terminate signal
            os.kill(pid, signal.SIGTERM)
            
            # Wait for shutdown
            for i in range(10):
                if not is_server_running():
                    break
                time.sleep(0.5)
            
            if not is_server_running():
                print(f"✅ Server stopped successfully (PID: {pid})")
                os.remove('.server.pid')
                return True
            else:
                # Force kill if still running
                print("⚡ Force stopping server...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
                os.remove('.server.pid')
                print("✅ Server force stopped")
                return True
                
        else:
            print("⚠️  No PID file found, but server is running")
            print("💡 Use 'pkill -f label_print_api.py' to stop manually")
            return False
            
    except ProcessLookupError:
        print("⚠️  Server process not found (already stopped)")
        if os.path.exists('.server.pid'):
            os.remove('.server.pid')
        return True
    except Exception as e:
        print(f"❌ Error stopping server: {e}")
        return False

if __name__ == "__main__":
    stop_server()