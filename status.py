#!/usr/bin/env python3
"""
Check Label Printing API Server Status
Shows detailed status information.
"""

import os
import requests
import subprocess

def check_server_status():
    """Check comprehensive server status."""
    print("🏷️  Label Printing API - Status Check")
    print("=" * 45)
    
    # Check if server is responding
    server_running = False
    try:
        response = requests.get("http://localhost:5000/health", timeout=3)
        if response.ok:
            server_running = True
            data = response.json()
            print("✅ API Server: RUNNING")
            print(f"   📍 URL: http://localhost:5000")
            print(f"   🖨️  Printer: {data.get('printer', 'N/A')}")
            print(f"   ⏰ Timestamp: {data.get('timestamp', 'N/A')}")
        else:
            print("❌ API Server: ERROR")
            print(f"   HTTP Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ API Server: STOPPED")
        print("   📍 Expected URL: http://localhost:5000")
    except Exception as e:
        print("❌ API Server: ERROR")
        print(f"   Error: {e}")
    
    # Check PID file
    print("\n📄 Process Information:")
    if os.path.exists('.server.pid'):
        with open('.server.pid', 'r') as f:
            pid = f.read().strip()
        print(f"   🆔 PID File: {pid}")
        
        # Check if process is actually running
        try:
            result = subprocess.run(['ps', '-p', pid], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ Process: RUNNING")
            else:
                print("   ❌ Process: NOT FOUND (stale PID)")
        except:
            print("   ❓ Process: UNKNOWN")
    else:
        print("   📄 No PID file found")
    
    # Check printer status
    print("\n🖨️  Printer Status:")
    try:
        if server_running:
            response = requests.get("http://localhost:5000/printer/status", timeout=3)
            if response.ok:
                printer_data = response.json()
                print(f"   ✅ {printer_data.get('printer', 'N/A')}: {printer_data.get('status', 'N/A')}")
            else:
                print("   ❌ Printer status check failed")
        else:
            # Direct check using lpstat
            result = subprocess.run(['lpstat', '-p', 'ZTC-ZD230-203dpi-ZPL'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ ZTC-ZD230-203dpi-ZPL: Available")
            else:
                print("   ❌ ZTC-ZD230-203dpi-ZPL: Not found")
    except Exception as e:
        print(f"   ❌ Printer check error: {e}")
    
    # Check log file
    print("\n📋 Log Information:")
    log_file = 'print_api.log'
    if os.path.exists(log_file):
        try:
            stat = os.stat(log_file)
            size = stat.st_size
            print(f"   📄 {log_file}: {size} bytes")
            
            # Show last log entry
            with open(log_file, 'r') as f:
                lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                print(f"   📝 Last entry: {last_line[:60]}...")
        except Exception as e:
            print(f"   ❌ Log file error: {e}")
    else:
        print(f"   📄 No log file: {log_file}")
    
    # Show quick commands
    print("\n🛠️  Quick Commands:")
    if server_running:
        print("   🛑 Stop server: python stop_server.py")
        print("   🧪 Test print: python test_print.py")
    else:
        print("   ▶️  Start server: python start_server.py")
    print("   📄 View logs: tail -f print_api.log")
    print("   🎛️  Control panel: python quick_start.py")

if __name__ == "__main__":
    check_server_status()