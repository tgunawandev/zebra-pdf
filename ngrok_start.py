#!/usr/bin/env python3
"""
Start Ngrok Tunnel
Simple command to start the ngrok tunnel.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from ngrok_setup import NgrokManager

def main():
    ngrok = NgrokManager()
    
    print("🌐 Starting Ngrok Tunnel...")
    
    # Check if API server is running
    if not ngrok.check_api_server():
        print("❌ API server is not running!")
        print("💡 Start it first: python start_server.py")
        return
    
    # Start tunnel
    tunnel_url = ngrok.start_tunnel()
    if tunnel_url:
        print("✅ Tunnel started successfully!")
        print(f"🌐 Public URL: {tunnel_url}")
        print("💡 Use this URL in your Odoo webhook configuration")
    else:
        print("❌ Failed to start tunnel")

if __name__ == "__main__":
    main()