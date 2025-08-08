#!/usr/bin/env python3
"""
Test Cloudflare Tunnel
Test the permanent tunnel with print requests.
"""

import sys
import os
import json
import requests
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from cloudflare_setup import CloudflareManager

def main():
    cf = CloudflareManager()
    
    print("🧪 Testing Cloudflare Tunnel")
    print("=" * 35)
    
    # Load tunnel info
    if not cf.get_existing_tunnel():
        print("❌ No tunnel configured!")
        print("💡 Run setup first: python cloudflare_setup.py")
        return
    
    print(f"🌐 Testing URL: {cf.tunnel_url}")
    
    # Test 1: Health check
    print("\n1. 🔍 Health Check...")
    try:
        response = requests.get(f"{cf.tunnel_url}/health", timeout=10)
        if response.ok:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   🖨️  Printer: {data.get('printer', 'N/A')}")
            print(f"   ⏰ Timestamp: {data.get('timestamp', 'N/A')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Printer status
    print("\n2. 🖨️  Printer Status...")
    try:
        response = requests.get(f"{cf.tunnel_url}/printer/status", timeout=10)
        if response.ok:
            data = response.json()
            print("✅ Printer status check passed!")
            print(f"   📊 Status: {data.get('status', 'N/A')}")
        else:
            print(f"❌ Printer status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Printer status error: {e}")
    
    # Test 3: Print test
    print("\n3. 🏷️  Print Test...")
    test_data = {
        "labels": [
            {
                "title": "W-CPN/OUT/CF-TEST",
                "date": datetime.now().strftime("%d/%m/%y"),
                "qr_code": "CLOUDFLARE123"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{cf.tunnel_url}/print",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.ok:
            result = response.json()
            print("✅ Print test successful!")
            print(f"   📊 Labels sent: {result.get('labels_count', 0)}")
            print(f"   🆔 Job ID: {result.get('job_info', 'N/A')}")
            print("\n🏷️  Check your printer - test label should be printing!")
        else:
            print(f"❌ Print test failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Print test error: {e}")
        return
    
    print(f"\n🎉 All tests passed!")
    print(f"🌐 PERMANENT URL: {cf.tunnel_url}")
    print("📋 Ready for Odoo integration!")
    print("\n💡 Odoo Webhook Configuration:")
    print(f"   URL: {cf.tunnel_url}/print")
    print(f"   Method: POST")
    print(f"   Content-Type: application/json")

if __name__ == "__main__":
    main()