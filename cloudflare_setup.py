#!/usr/bin/env python3
"""
Cloudflare Tunnel Setup - PERMANENT URL!
Set up a permanent tunnel URL that never changes.
"""

import os
import subprocess
import json
import time
import requests
import uuid
from pathlib import Path

class CloudflareManager:
    def __init__(self):
        self.config_dir = Path.home() / ".cloudflared"
        self.config_file = self.config_dir / "config.yml"
        self.tunnel_name = "zebra-printer"
        self.local_port = 5000
        self.tunnel_id = None
        self.tunnel_url = None
        
    def check_cloudflared(self):
        """Check if cloudflared is installed."""
        try:
            result = subprocess.run(['which', 'cloudflared'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Cloudflared found:", result.stdout.strip())
                return True
            else:
                print("❌ Cloudflared not found")
                print("📥 Install: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
                return False
        except Exception as e:
            print(f"❌ Error checking cloudflared: {e}")
            return False
    
    def check_api_server(self):
        """Check if local API server is running."""
        try:
            response = requests.get(f"http://localhost:{self.local_port}/health", timeout=3)
            return response.ok
        except:
            return False
    
    def login_cloudflare(self):
        """Login to Cloudflare (one-time setup)."""
        print("🔐 Checking Cloudflare authentication...")
        
        # Check if already authenticated
        try:
            result = subprocess.run(['cloudflared', 'tunnel', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Already authenticated with Cloudflare")
                return True
        except:
            pass
        
        print("🔑 Need to authenticate with Cloudflare...")
        print("📱 A browser window will open for authentication")
        input("⏎ Press Enter when ready...")
        
        try:
            result = subprocess.run(['cloudflared', 'tunnel', 'login'], 
                                  timeout=120)
            if result.returncode == 0:
                print("✅ Successfully authenticated!")
                return True
            else:
                print("❌ Authentication failed")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Authentication timed out")
            return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def create_tunnel(self):
        """Create a new tunnel with permanent subdomain."""
        print(f"🔧 Creating tunnel: {self.tunnel_name}")
        
        try:
            # Create tunnel
            result = subprocess.run(['cloudflared', 'tunnel', 'create', self.tunnel_name],
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Extract tunnel ID from output
                lines = result.stderr.split('\n')
                for line in lines:
                    if 'Created tunnel' in line and '.json' in line:
                        # Extract tunnel ID (UUID format)
                        parts = line.split()
                        for part in parts:
                            if len(part) == 36 and part.count('-') == 4:  # UUID format
                                self.tunnel_id = part
                                break
                        break
                
                if self.tunnel_id:
                    print(f"✅ Tunnel created with ID: {self.tunnel_id}")
                    
                    # Generate permanent subdomain
                    subdomain = f"zebra-printer-{self.tunnel_id[:8]}"
                    self.tunnel_url = f"https://{subdomain}.trycloudflare.com"
                    
                    print(f"🌐 Permanent URL: {self.tunnel_url}")
                    
                    # Save tunnel info
                    tunnel_info = {
                        'tunnel_id': self.tunnel_id,
                        'tunnel_name': self.tunnel_name,
                        'tunnel_url': self.tunnel_url,
                        'subdomain': subdomain
                    }
                    
                    with open('.cloudflare_tunnel', 'w') as f:
                        json.dump(tunnel_info, f, indent=2)
                    
                    return True
                else:
                    print("❌ Could not extract tunnel ID")
                    return False
            else:
                print(f"❌ Failed to create tunnel: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating tunnel: {e}")
            return False
    
    def get_existing_tunnel(self):
        """Get existing tunnel info."""
        if os.path.exists('.cloudflare_tunnel'):
            with open('.cloudflare_tunnel', 'r') as f:
                tunnel_info = json.load(f)
                self.tunnel_id = tunnel_info.get('tunnel_id')
                self.tunnel_name = tunnel_info.get('tunnel_name')
                self.tunnel_url = tunnel_info.get('tunnel_url')
                return True
        return False
    
    def create_config(self):
        """Create tunnel configuration."""
        print("📝 Creating tunnel configuration...")
        
        if not self.tunnel_id:
            print("❌ No tunnel ID available")
            return False
        
        # Create config directory
        self.config_dir.mkdir(exist_ok=True)
        
        # Create config content
        config_content = f"""tunnel: {self.tunnel_id}
credentials-file: {self.config_dir}/{self.tunnel_id}.json

ingress:
  - hostname: {self.tunnel_url.replace('https://', '')}
    service: http://localhost:{self.local_port}
  - service: http_status:404
"""
        
        try:
            with open(self.config_file, 'w') as f:
                f.write(config_content)
            
            print(f"✅ Config created: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Error creating config: {e}")
            return False
    
    def start_tunnel(self):
        """Start the tunnel."""
        print("🚀 Starting Cloudflare tunnel...")
        
        if not self.check_api_server():
            print("❌ API server is not running!")
            print("💡 Start it first: python start_server.py")
            return False
        
        try:
            # Start tunnel in background
            process = subprocess.Popen(
                ['cloudflared', 'tunnel', 'run', self.tunnel_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Save process ID
            with open('.cloudflare_pid', 'w') as f:
                f.write(str(process.pid))
            
            print("⏳ Waiting for tunnel to establish...")
            time.sleep(5)
            
            # Test tunnel
            if self.test_tunnel():
                print("✅ Tunnel started successfully!")
                print(f"🌐 PERMANENT URL: {self.tunnel_url}")
                print("📋 Use this URL in Odoo - IT NEVER CHANGES!")
                return True
            else:
                print("❌ Tunnel test failed")
                return False
                
        except Exception as e:
            print(f"❌ Error starting tunnel: {e}")
            return False
    
    def stop_tunnel(self):
        """Stop the tunnel."""
        print("🛑 Stopping Cloudflare tunnel...")
        
        try:
            # Kill cloudflared process
            subprocess.run(['pkill', '-f', 'cloudflared'], timeout=10)
            
            # Clean up PID file
            if os.path.exists('.cloudflare_pid'):
                os.remove('.cloudflare_pid')
            
            print("✅ Tunnel stopped")
            return True
        except Exception as e:
            print(f"❌ Error stopping tunnel: {e}")
            return False
    
    def test_tunnel(self):
        """Test the tunnel."""
        if not self.tunnel_url:
            return False
        
        try:
            response = requests.get(f"{self.tunnel_url}/health", timeout=10)
            return response.ok
        except:
            return False
    
    def auto_setup(self):
        """Automated setup process."""
        print("🌐 Cloudflare Tunnel Setup - PERMANENT URL!")
        print("=" * 50)
        
        # Step 1: Check cloudflared
        if not self.check_cloudflared():
            return False
        
        # Step 2: Login to Cloudflare
        if not self.login_cloudflare():
            return False
        
        # Step 3: Check for existing tunnel
        if self.get_existing_tunnel():
            print(f"✅ Found existing tunnel: {self.tunnel_name}")
            print(f"🌐 Permanent URL: {self.tunnel_url}")
        else:
            # Step 4: Create new tunnel
            if not self.create_tunnel():
                return False
        
        # Step 5: Create config
        if not self.create_config():
            return False
        
        # Step 6: Check API server
        if not self.check_api_server():
            print("\n💡 Starting API server first...")
            result = subprocess.run(['python', 'start_server.py'], 
                                  capture_output=True, text=True)
            time.sleep(2)
            
            if not self.check_api_server():
                print("❌ Could not start API server")
                return False
        
        # Step 7: Start tunnel
        if self.start_tunnel():
            print(f"\n🎉 SETUP COMPLETE!")
            print(f"🌐 PERMANENT URL: {self.tunnel_url}")
            print(f"📋 Use in Odoo: {self.tunnel_url}/print")
            print(f"🔄 URL NEVER CHANGES - Set it once in Odoo!")
            print(f"🛑 Stop: python cloudflare_stop.py")
            
            return True
        else:
            return False

def main():
    cf = CloudflareManager()
    cf.auto_setup()

if __name__ == "__main__":
    main()