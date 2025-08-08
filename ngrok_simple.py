#!/usr/bin/env python3
"""
Simple Ngrok Setup - Just Works!
One command setup for ngrok tunnel.
"""

import subprocess
import time
import requests
import json
import os

def start_ngrok():
    """Start ngrok tunnel with simple approach."""
    print("🌐 Starting Ngrok Tunnel (Simple Mode)")
    print("=" * 40)
    
    # Check API server
    try:
        response = requests.get("http://localhost:5000/health", timeout=3)
        if not response.ok:
            raise Exception("API server not responding")
        print("✅ API server is running")
    except:
        print("❌ API server is not running!")
        print("💡 Start it first: python start_server.py")
        return
    
    # Kill any existing ngrok
    try:
        subprocess.run(['pkill', '-f', 'ngrok'], timeout=5)
        time.sleep(1)
    except:
        pass
    
    # Start ngrok in background
    print("🚀 Starting ngrok tunnel...")
    
    process = subprocess.Popen(
        ['ngrok', 'http', '5000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for startup
    print("⏳ Waiting for tunnel to establish...")
    time.sleep(5)
    
    # Get tunnel info
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        if response.ok:
            data = response.json()
            tunnels = data.get('tunnels', [])
            
            if tunnels:
                # Find HTTPS tunnel
                for tunnel in tunnels:
                    public_url = tunnel.get('public_url', '')
                    if public_url.startswith('https://'):
                        print("✅ Tunnel established!")
                        print(f"🌐 Public URL: {public_url}")
                        
                        # Save URL
                        with open('.ngrok_url', 'w') as f:
                            f.write(public_url)
                        
                        # Test the tunnel
                        print("\n🧪 Testing tunnel...")
                        try:
                            test_response = requests.get(f"{public_url}/health", 
                                                       timeout=10,
                                                       headers={'ngrok-skip-browser-warning': 'true'})
                            if test_response.ok:
                                print("✅ Tunnel test successful!")
                                health_data = test_response.json()
                                print(f"   Printer: {health_data.get('printer', 'N/A')}")
                            else:
                                print("⚠️  Tunnel responds but API test failed")
                        except Exception as e:
                            print(f"⚠️  Tunnel test failed: {e}")
                        
                        print(f"\n🎉 Setup Complete!")
                        print(f"📋 Use this in Odoo: {public_url}")
                        print(f"🧪 Test command: curl -H 'ngrok-skip-browser-warning: true' {public_url}/health")
                        print(f"🛑 Stop: killall ngrok")
                        
                        return public_url
            
            print("❌ No tunnels found")
        else:
            print("❌ Cannot get tunnel info from ngrok")
    except Exception as e:
        print(f"❌ Error getting tunnel info: {e}")
    
    return None

def test_tunnel():
    """Test existing tunnel."""
    if not os.path.exists('.ngrok_url'):
        print("❌ No tunnel URL found")
        print("💡 Start tunnel first: python ngrok_simple.py")
        return
    
    with open('.ngrok_url', 'r') as f:
        tunnel_url = f.read().strip()
    
    print(f"🧪 Testing tunnel: {tunnel_url}")
    
    try:
        # Test health
        response = requests.get(f"{tunnel_url}/health", 
                              timeout=10,
                              headers={'ngrok-skip-browser-warning': 'true'})
        
        if response.ok:
            print("✅ Health check passed")
            
            # Test print
            test_data = {
                "labels": [
                    {
                        "title": "W-CPN/OUT/TEST",
                        "date": "08/08/25",
                        "qr_code": "NGROK123"
                    }
                ]
            }
            
            print("🖨️  Testing print...")
            response = requests.post(f"{tunnel_url}/print",
                                   json=test_data,
                                   headers={
                                       'Content-Type': 'application/json',
                                       'ngrok-skip-browser-warning': 'true'
                                   },
                                   timeout=30)
            
            if response.ok:
                result = response.json()
                print("✅ Print test successful!")
                print(f"   Job ID: {result.get('job_info', 'N/A')}")
            else:
                print(f"❌ Print test failed: {response.text}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_tunnel()
    else:
        start_ngrok()

if __name__ == "__main__":
    main()