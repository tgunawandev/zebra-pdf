#!/usr/bin/env python3
"""
Stop Ngrok Tunnel
Simple command to stop the ngrok tunnel.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from ngrok_setup import NgrokManager

def main():
    ngrok = NgrokManager()
    
    print("🛑 Stopping Ngrok Tunnel...")
    
    if ngrok.stop_tunnel():
        print("✅ Tunnel stopped successfully!")
    else:
        print("❌ Failed to stop tunnel")

if __name__ == "__main__":
    main()