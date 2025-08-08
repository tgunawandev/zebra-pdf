#!/usr/bin/env python3
"""
Quick Start Guide for Odoo-to-Zebra Label Printing
Complete setup and testing guide.
"""

import subprocess
import sys
import json
import time
import os

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = ['flask', 'requests']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n📥 Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def start_api_server():
    """Start the label printing API server in background."""
    import signal
    
    # Check if server is already running
    if is_server_running():
        print("✅ API server is already running on http://localhost:5000")
        return True
    
    print("🚀 Starting Label Printing API Server in background...")
    
    try:
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, 'label_print_api.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Save PID for later management
        with open('.server.pid', 'w') as f:
            f.write(str(process.pid))
        
        # Wait a moment and check if it started successfully
        time.sleep(2)
        if is_server_running():
            print("✅ API server started successfully!")
            print("   📍 Running on: http://localhost:5000")
            print("   🆔 Process ID:", process.pid)
            print("   📄 Logs: print_api.log")
            print("   🛑 Stop with: python stop_server.py")
            return True
        else:
            print("❌ Failed to start API server")
            return False
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def stop_api_server():
    """Stop the API server if running."""
    import signal
    
    try:
        # Try to read PID file
        if os.path.exists('.server.pid'):
            with open('.server.pid', 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists and kill it
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                print(f"✅ API server stopped (PID: {pid})")
                os.remove('.server.pid')
                return True
            except ProcessLookupError:
                print("⚠️  Server process not found (already stopped)")
                os.remove('.server.pid')
                return True
            except Exception as e:
                print(f"❌ Error stopping server: {e}")
                return False
        else:
            print("⚠️  No server PID file found")
            return True
            
    except Exception as e:
        print(f"❌ Error stopping server: {e}")
        return False

def is_server_running():
    """Check if the API server is running."""
    import requests
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        return response.ok
    except:
        return False

def get_server_status():
    """Get detailed server status."""
    if is_server_running():
        try:
            import requests
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.ok:
                data = response.json()
                print("✅ API Server Status: RUNNING")
                print(f"   📍 URL: http://localhost:5000")
                print(f"   🖨️  Printer: {data.get('printer', 'N/A')}")
                print(f"   ⏰ Started: {data.get('timestamp', 'N/A')}")
                
                # Check PID if available
                if os.path.exists('.server.pid'):
                    with open('.server.pid', 'r') as f:
                        pid = f.read().strip()
                    print(f"   🆔 Process ID: {pid}")
                
                return True
        except Exception as e:
            print(f"✅ Server running but status check failed: {e}")
            return True
    else:
        print("❌ API Server Status: STOPPED")
        print("   💡 Start with option 2 or: python label_print_api.py &")
        return False

def view_server_logs():
    """View the server logs."""
    log_file = 'print_api.log'
    
    if not os.path.exists(log_file):
        print(f"📄 No log file found: {log_file}")
        print("💡 Start the server first to generate logs")
        return
    
    print(f"📄 Server Logs ({log_file}):")
    print("=" * 50)
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Show last 20 lines
        recent_lines = lines[-20:] if len(lines) > 20 else lines
        
        for line in recent_lines:
            print(line.rstrip())
        
        print("=" * 50)
        print(f"📊 Total log entries: {len(lines)}")
        print("💡 Live logs: tail -f print_api.log")
        
    except Exception as e:
        print(f"❌ Error reading logs: {e}")

def run_test():
    """Run a quick test of the system."""
    import requests
    
    print("🧪 Running system test...")
    
    # Sample data that Odoo would send
    test_labels = {
        "labels": [
            {
                "title": "W-CPN/OUT/TEST",
                "date": "08/08/25", 
                "qr_code": "TEST12345"
            }
        ]
    }
    
    try:
        print("   Testing API connection...")
        response = requests.get("http://localhost:5000/health", timeout=5)
        if not response.ok:
            print("❌ API server not responding. Start it first with option 2.")
            return
        
        print("   ✅ API server is running")
        
        print("   Testing label printing...")
        response = requests.post(
            "http://localhost:5000/print",
            json=test_labels,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.ok:
            result = response.json()
            print("   ✅ Test label sent to printer!")
            print(f"   📄 Job info: {result.get('job_info', 'N/A')}")
            print("\n🏷️  Check your printer - a test label should be printing!")
        else:
            print(f"   ❌ Printing failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Start it first with option 2.")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def show_integration_summary():
    """Show complete integration summary."""
    print("📋 Complete Odoo Integration Summary")
    print("=" * 50)
    
    print("🎯 SOLUTION OVERVIEW:")
    print("   Odoo (cloud) → JSON API call → Local Python server → Zebra printer")
    print("   ✅ No PDF generation needed!")
    print("   ✅ Direct JSON to ZPL conversion")
    print("   ✅ Consistent text sizing (16x16)")
    print("   ✅ Proper label positioning")
    
    print("\n🔧 SETUP STEPS:")
    print("   1. Install dependencies: pip install flask requests")
    print("   2. Start API server: python label_print_api.py")
    print("   3. Setup connectivity: python setup_connectivity.py")
    print("   4. Add Odoo integration: python odoo_integration.py")
    
    print("\n🌐 CONNECTIVITY OPTIONS:")
    print("   • Ngrok tunnel (development): Fastest setup")
    print("   • VPN connection (production): Most secure") 
    print("   • Polling/queue system (enterprise): No exposed ports")
    
    print("\n📨 ODOO SENDS JSON LIKE THIS:")
    sample_json = {
        "labels": [
            {"title": "W-CPN/OUT/00002", "date": "12/04/22", "qr_code": "01010101160"},
            {"title": "W-CPN/OUT/00003", "date": "12/04/22", "qr_code": "01010101161"}
        ]
    }
    print(json.dumps(sample_json, indent=2))
    
    print("\n✅ BENEFITS:")
    print("   • 10x faster (no PDF processing)")
    print("   • Consistent text sizing")
    print("   • Better error handling")
    print("   • Real-time printing status")
    print("   • Easy debugging")

def main():
    """Main quick start menu."""
    print("🏷️  Zebra Label Printing - Quick Start")
    print("=" * 45)
    print("Connect Odoo (cloud) → Local Zebra Printer")
    print("No PDF needed - Direct JSON to printing!")
    print("=" * 45)
    
    while True:
        print("\n🚀 Zebra Label Printing - Control Panel")
        print("=" * 45)
        
        # Show current server status
        print("📊 Current Status:")
        get_server_status()
        
        print("\n🎯 Available Actions:")
        print("1. 🔍 Check Dependencies")
        print("2. ▶️  Start API Server (Background)")
        print("3. ⏹️  Stop API Server") 
        print("4. 🧪 Run Test Print")
        print("5. 🌐 Setup Connectivity") 
        print("6. 📁 Generate Odoo Code")
        print("7. 📋 Show Complete Guide")
        print("8. 📄 View Server Logs")
        print("0. ❌ Exit")
        
        choice = input("\nChoose option (0-8): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            check_dependencies()
        elif choice == '2':
            start_api_server()
        elif choice == '3':
            stop_api_server()
        elif choice == '4':
            run_test()
        elif choice == '5':
            subprocess.run([sys.executable, 'setup_connectivity.py'])
        elif choice == '6':
            subprocess.run([sys.executable, 'odoo_integration.py'])
        elif choice == '7':
            show_integration_summary()
        elif choice == '8':
            view_server_logs()
        else:
            print("❌ Invalid choice. Please try again.")
            
        # Pause before showing menu again
        input("\n⏎ Press Enter to continue...")

if __name__ == "__main__":
    main()