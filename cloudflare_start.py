#!/usr/bin/env python3
"""
Start Cloudflare Tunnel
Simple command to start the permanent tunnel.
"""

import sys
import os
import json
import subprocess
import time
import requests

sys.path.append(os.path.dirname(__file__))
from cloudflare_setup import CloudflareManager

def main():
    cf = CloudflareManager()
    
    print("🌐 Starting Cloudflare Tunnel...")
    
    # Load existing tunnel info
    if not cf.get_existing_tunnel():
        print("❌ No tunnel configured!")
        print("💡 Run setup first: python cloudflare_setup.py")
        return
    
    # Check API server
    if not cf.check_api_server():
        print("❌ API server is not running!")
        print("💡 Start it first: python start_server.py")
        return
    
    # Start tunnel
    if cf.start_tunnel():
        print(f"✅ Tunnel started!")
        print(f"🌐 PERMANENT URL: {cf.tunnel_url}")
    else:
        print("❌ Failed to start tunnel")

if __name__ == "__main__":
    main()