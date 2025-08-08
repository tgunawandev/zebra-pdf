#!/usr/bin/env python3
"""
Automated Ngrok Setup for Label Printing API
Seamless and easy setup for cloud-to-local connectivity.
"""

import os
import subprocess
import json
import time
import requests
import yaml
from pathlib import Path

class NgrokManager:
    def __init__(self):
        self.config_dir = Path.home() / ".ngrok2"
        self.config_file = self.config_dir / "ngrok.yml"
        self.tunnel_name = "label-printer"
        self.local_port = 5000
        self.ngrok_process = None
        
    def check_ngrok_installed(self):
        """Check if ngrok is installed."""
        try:
            result = subprocess.run(['which', 'ngrok'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Ngrok found:", result.stdout.strip())
                return True
            else:
                print("❌ Ngrok not found")
                return False
        except Exception as e:
            print(f"❌ Error checking ngrok: {e}")
            return False
    
    def check_api_server(self):
        """Check if local API server is running."""
        try:
            response = requests.get(f"http://localhost:{self.local_port}/health", timeout=3)
            return response.ok
        except:
            return False
    
    def create_ngrok_config(self):
        """Create ngrok configuration file."""
        print("🔧 Creating ngrok configuration...")
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Create ngrok config
        config = {
            'version': '2',
            'tunnels': {
                self.tunnel_name: {
                    'addr': self.local_port,
                    'proto': 'http',
                    'bind_tls': True,
                    'inspect': False,
                    'metadata': 'Zebra Label Printing API'
                }
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            print(f"✅ Config created: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Error creating config: {e}")
            return False
    
    def get_auth_token(self):
        """Check if ngrok auth token is configured."""
        try:
            result = subprocess.run(['ngrok', 'config', 'check'], 
                                  capture_output=True, text=True, timeout=10)
            
            if "valid" in result.stdout.lower():
                print("✅ Ngrok auth token is configured")
                return True
            else:
                print("⚠️  Ngrok auth token not configured")
                print("📝 Get your free auth token from: https://dashboard.ngrok.com/get-started/your-authtoken")
                
                token = input("🔑 Enter your ngrok auth token (or press Enter to skip): ").strip()
                if token:
                    result = subprocess.run(['ngrok', 'config', 'add-authtoken', token],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✅ Auth token configured successfully")
                        return True
                    else:
                        print(f"❌ Error configuring auth token: {result.stderr}")
                        return False
                else:
                    print("⚠️  Skipping auth token setup - limited to 1 tunnel")
                    return True
        except Exception as e:
            print(f"❌ Error checking auth token: {e}")
            return False
    
    def start_tunnel(self):
        """Start ngrok tunnel."""
        if not self.check_api_server():
            print("❌ API server is not running!")
            print("💡 Start it first: python start_server.py")
            return False
        
        print("🌐 Starting ngrok tunnel...")
        
        try:
            # Start ngrok tunnel
            self.ngrok_process = subprocess.Popen(
                ['ngrok', 'start', self.tunnel_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            print("⏳ Waiting for tunnel to establish...")
            time.sleep(3)
            
            # Get tunnel URL
            tunnel_url = self.get_tunnel_url()
            if tunnel_url:
                print("✅ Tunnel established successfully!")
                print(f"🌐 Public URL: {tunnel_url}")
                print(f"🔗 Use this URL in Odoo: {tunnel_url}")
                
                # Save URL to file for easy access
                with open('.ngrok_url', 'w') as f:
                    f.write(tunnel_url)
                
                return tunnel_url
            else:
                print("❌ Failed to get tunnel URL")
                return None
                
        except Exception as e:
            print(f"❌ Error starting tunnel: {e}")
            return None
    
    def get_tunnel_url(self):
        """Get the public tunnel URL from ngrok API."""
        try:
            # Try to get tunnels from ngrok local API
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.ok:
                data = response.json()
                tunnels = data.get('tunnels', [])
                
                for tunnel in tunnels:
                    if tunnel.get('name') == self.tunnel_name:
                        return tunnel.get('public_url')
                
                # If named tunnel not found, get first HTTPS tunnel
                for tunnel in tunnels:
                    public_url = tunnel.get('public_url', '')
                    if public_url.startswith('https://'):
                        return public_url
            
            return None
        except Exception:
            return None
    
    def stop_tunnel(self):
        """Stop ngrok tunnel."""
        print("🛑 Stopping ngrok tunnel...")
        
        try:
            # Kill ngrok process
            subprocess.run(['pkill', '-f', 'ngrok'], timeout=10)
            
            # Clean up URL file
            if os.path.exists('.ngrok_url'):
                os.remove('.ngrok_url')
            
            print("✅ Tunnel stopped")
            return True
        except Exception as e:
            print(f"❌ Error stopping tunnel: {e}")
            return False
    
    def get_status(self):
        """Get ngrok tunnel status."""
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=2)
            if response.ok:
                data = response.json()
                tunnels = data.get('tunnels', [])
                
                if tunnels:
                    print("✅ Ngrok Status: ACTIVE")
                    for tunnel in tunnels:
                        name = tunnel.get('name', 'unnamed')
                        public_url = tunnel.get('public_url', 'N/A')
                        proto = tunnel.get('proto', 'N/A')
                        print(f"   🌐 {name}: {public_url} ({proto})")
                    
                    # Show saved URL if exists
                    if os.path.exists('.ngrok_url'):
                        with open('.ngrok_url', 'r') as f:
                            saved_url = f.read().strip()
                        print(f"   📄 Saved URL: {saved_url}")
                    
                    return True
                else:
                    print("❌ Ngrok Status: NO TUNNELS")
                    return False
            else:
                print("❌ Ngrok Status: NOT RUNNING")
                return False
        except:
            print("❌ Ngrok Status: NOT RUNNING")
            return False
    
    def auto_setup(self):
        """Automated setup process."""
        print("🚀 Automated Ngrok Setup for Label Printing")
        print("=" * 50)
        
        # Step 1: Check ngrok
        if not self.check_ngrok_installed():
            print("💡 Install ngrok from: https://ngrok.com/download")
            return False
        
        # Step 2: Create config
        if not self.create_ngrok_config():
            return False
        
        # Step 3: Check/setup auth token
        if not self.get_auth_token():
            return False
        
        # Step 4: Check API server
        if not self.check_api_server():
            print("\n💡 Starting API server first...")
            result = subprocess.run(['python', 'start_server.py'], 
                                  capture_output=True, text=True)
            time.sleep(2)
            
            if not self.check_api_server():
                print("❌ Could not start API server")
                return False
        
        # Step 5: Start tunnel
        tunnel_url = self.start_tunnel()
        if tunnel_url:
            print(f"\n🎉 Setup Complete!")
            print(f"📍 Local API: http://localhost:{self.local_port}")
            print(f"🌐 Public URL: {tunnel_url}")
            print(f"📋 Test: curl {tunnel_url}/health")
            print(f"🛑 Stop: python ngrok_stop.py")
            
            return True
        else:
            return False

def main():
    ngrok = NgrokManager()
    ngrok.auto_setup()

if __name__ == "__main__":
    main()