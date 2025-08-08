#!/usr/bin/env python3
"""
Ngrok Tunnel Status
Check the current status of ngrok tunnel.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from ngrok_setup import NgrokManager

def main():
    ngrok = NgrokManager()
    
    print("🌐 Ngrok Tunnel Status")
    print("=" * 30)
    
    # Get status
    is_active = ngrok.get_status()
    
    # Show quick commands
    print("\n🛠️  Commands:")
    if is_active:
        print("   🛑 Stop tunnel: python ngrok_stop.py")
        print("   🧪 Test tunnel: python ngrok_test.py")
    else:
        print("   ▶️  Start tunnel: python ngrok_start.py")
        print("   🔧 Auto setup: python ngrok_setup.py")
    
    # Show API server status
    print(f"\n📊 API Server: {'✅ Running' if ngrok.check_api_server() else '❌ Stopped'}")

if __name__ == "__main__":
    main()