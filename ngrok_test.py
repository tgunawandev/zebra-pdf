#!/usr/bin/env python3
"""
Test Ngrok Tunnel
Test the ngrok tunnel with a sample print request.
"""

import sys
import os
import requests
import json
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from ngrok_setup import NgrokManager

def main():
    ngrok = NgrokManager()
    
    print("🧪 Testing Ngrok Tunnel")
    print("=" * 30)
    
    # Get tunnel URL
    tunnel_url = None
    if os.path.exists('.ngrok_url'):
        with open('.ngrok_url', 'r') as f:
            tunnel_url = f.read().strip()
    
    if not tunnel_url:
        tunnel_url = ngrok.get_tunnel_url()
    
    if not tunnel_url:
        print("❌ No active tunnel found")
        print("💡 Start tunnel: python ngrok_start.py")
        return
    
    print(f"🌐 Testing URL: {tunnel_url}")
    
    # Test health endpoint
    try:
        print("\n1. Testing health check...")
        response = requests.get(f"{tunnel_url}/health", timeout=10)
        if response.ok:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Printer: {data.get('printer', 'N/A')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test print endpoint
    try:
        print("\n2. Testing print endpoint...")
        test_data = {
            "labels": [
                {
                    "title": "W-CPN/OUT/NGROK",
                    "date": datetime.now().strftime("%d/%m/%y"),
                    "qr_code": "NGROK123"
                }
            ]
        }
        
        response = requests.post(
            f"{tunnel_url}/print",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.ok:
            result = response.json()
            print("✅ Print test successful!")
            print(f"   Labels: {result.get('labels_count', 0)}")
            print(f"   Job ID: {result.get('job_info', 'N/A')}")
            print("\n🏷️  Check your printer - test label should be printing!")
        else:
            print(f"❌ Print test failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Print test error: {e}")
        return
    
    print("\n🎉 Ngrok tunnel is working correctly!")
    print(f"📋 Use this URL in Odoo: {tunnel_url}")
    print("📝 Example Odoo webhook URL:")
    print(f"   {tunnel_url}/print")

if __name__ == "__main__":
    main()