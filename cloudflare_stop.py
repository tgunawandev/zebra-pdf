#!/usr/bin/env python3
"""
Stop Cloudflare Tunnel
Simple command to stop the tunnel.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from cloudflare_setup import CloudflareManager

def main():
    cf = CloudflareManager()
    
    print("🛑 Stopping Cloudflare Tunnel...")
    
    if cf.stop_tunnel():
        print("✅ Tunnel stopped!")
    else:
        print("❌ Failed to stop tunnel")

if __name__ == "__main__":
    main()