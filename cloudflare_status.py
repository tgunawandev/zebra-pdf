#!/usr/bin/env python3
"""
Cloudflare Tunnel Status
Check the status of the permanent tunnel.
"""

import sys
import os
import json
import requests
sys.path.append(os.path.dirname(__file__))

from cloudflare_setup import CloudflareManager

def main():
    cf = CloudflareManager()
    
    print("🌐 Cloudflare Tunnel Status")
    print("=" * 35)
    
    # Check if tunnel is configured
    if cf.get_existing_tunnel():
        print("✅ Tunnel Configuration: FOUND")
        print(f"   🆔 Tunnel ID: {cf.tunnel_id}")
        print(f"   📛 Tunnel Name: {cf.tunnel_name}")
        print(f"   🌐 PERMANENT URL: {cf.tunnel_url}")
        
        # Test tunnel
        print(f"\n🧪 Testing tunnel...")
        if cf.test_tunnel():
            print("✅ Tunnel Status: ACTIVE")
            
            # Test API endpoints
            try:
                response = requests.get(f"{cf.tunnel_url}/health", timeout=5)
                if response.ok:
                    data = response.json()
                    print(f"   🖨️  Printer: {data.get('printer', 'N/A')}")
                else:
                    print(f"   ⚠️  API responded with: {response.status_code}")
            except Exception as e:
                print(f"   ❌ API test failed: {e}")
        else:
            print("❌ Tunnel Status: INACTIVE")
    else:
        print("❌ Tunnel Configuration: NOT FOUND")
        print("💡 Run setup: python cloudflare_setup.py")
    
    # Show API server status
    print(f"\n📊 Local API Server: {'✅ Running' if cf.check_api_server() else '❌ Stopped'}")
    
    # Show commands
    print(f"\n🛠️  Commands:")
    if cf.get_existing_tunnel():
        if cf.test_tunnel():
            print("   🛑 Stop tunnel: python cloudflare_stop.py")
            print("   🧪 Test tunnel: python cloudflare_test.py")
        else:
            print("   ▶️  Start tunnel: python cloudflare_start.py")
    else:
        print("   🔧 Setup tunnel: python cloudflare_setup.py")

if __name__ == "__main__":
    main()