#!/usr/bin/env python3
"""
Network diagnostic utility for Windows API connection testing.
"""

import socket
import requests
import subprocess
import sys

def test_port_availability(host, port):
    """Test if a port is available for binding."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0  # True if port is available
    except Exception as e:
        print(f"[ERROR] Port test failed: {e}")
        return False

def test_localhost_connection():
    """Test basic localhost connectivity."""
    try:
        response = requests.get("http://127.0.0.1:80", timeout=1)
        print("[OK] Basic localhost connectivity works")
        return True
    except requests.exceptions.ConnectionError:
        print("[INFO] Port 80 not responding (normal)")
        return True
    except Exception as e:
        print(f"[ERROR] Localhost test failed: {e}")
        return False

def check_firewall_status():
    """Check Windows Firewall status."""
    try:
        result = subprocess.run([
            "netsh", "advfirewall", "show", "allprofiles", "state"
        ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            if "ON" in result.stdout:
                print("[WARNING] Windows Firewall is enabled")
                print("[INFO] This might block localhost connections")
                return True
            else:
                print("[OK] Windows Firewall appears to be disabled")
                return False
        else:
            print("[INFO] Could not check firewall status")
            return None
    except Exception as e:
        print(f"[ERROR] Firewall check failed: {e}")
        return None

def test_api_port(port=5000):
    """Test if the API port is accessible."""
    print(f"\n[TEST] Testing API port {port}...")
    
    # Test if port is available for binding
    if test_port_availability("127.0.0.1", port):
        print(f"[OK] Port {port} is available")
    else:
        print(f"[WARNING] Port {port} is already in use")
        
    # Test if something is listening on the port
    try:
        response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
        print(f"[OK] API is responding on port {port}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"[INFO] Nothing listening on port {port}")
        return False
    except requests.exceptions.Timeout:
        print(f"[WARNING] Connection to port {port} timed out")
        return False
    except Exception as e:
        print(f"[ERROR] API test failed: {e}")
        return False

def main():
    """Run network diagnostics."""
    print("=== ZEBRA PRINT NETWORK DIAGNOSTICS ===")
    print("Testing Windows network connectivity...\n")
    
    # Test basic localhost
    print("[TEST] Basic localhost connectivity...")
    test_localhost_connection()
    
    # Check firewall
    print("\n[TEST] Windows Firewall status...")
    check_firewall_status()
    
    # Test API port
    test_api_port(5000)
    
    # Show recommendations
    print("\n=== RECOMMENDATIONS ===")
    print("If API connection fails:")
    print("1. Try disabling Windows Firewall temporarily")
    print("2. Check if antivirus is blocking Python")
    print("3. Try running as Administrator")
    print("4. Use a different port (like 8000 or 3000)")
    print("5. Check Windows Defender settings")
    
    print("\n[INFO] Run this script again after starting the API server")

if __name__ == "__main__":
    main()