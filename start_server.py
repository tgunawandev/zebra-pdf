#!/usr/bin/env python3
"""
Start Label Printing API Server
Simple script to start the server in background.
"""

import subprocess
import sys
import time
import os
import requests

def is_server_running():
    """Check if server is already running."""
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        return response.ok
    except:
        return False

def start_server():
    """Start the API server in background."""
    if is_server_running():
        print("✅ API server is already running on http://localhost:5000")
        return True
    
    print("🚀 Starting Label Printing API Server...")
    
    try:
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, 'label_print_api.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Save PID for management
        with open('.server.pid', 'w') as f:
            f.write(str(process.pid))
        
        # Wait and verify
        time.sleep(3)
        if is_server_running():
            print("✅ Server started successfully!")
            print(f"   📍 URL: http://localhost:5000")
            print(f"   🆔 PID: {process.pid}")
            print("   🛑 Stop: python stop_server.py")
            print("   📋 Test: python test_print.py")
            return True
        else:
            print("❌ Server failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    start_server()