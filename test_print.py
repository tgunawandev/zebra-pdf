#!/usr/bin/env python3
"""
Test Print Labels
Simple script to test the label printing functionality.
"""

import requests
import json
from datetime import datetime

def test_print():
    """Test the label printing API with sample data."""
    print("🧪 Label Printing Test")
    print("=" * 30)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=3)
        if not response.ok:
            print("❌ API server is not responding")
            print("💡 Start server with: python start_server.py")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Start server with: python start_server.py")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    print("✅ API server is running")
    
    # Prepare test data
    test_labels = {
        "labels": [
            {
                "title": "W-CPN/OUT/TEST",
                "date": datetime.now().strftime("%d/%m/%y"),
                "qr_code": "TEST12345"
            }
        ]
    }
    
    print(f"📋 Sending {len(test_labels['labels'])} test labels...")
    print("📄 Test data:")
    for i, label in enumerate(test_labels['labels'], 1):
        print(f"   {i}. {label['title']} | {label['date']} | {label['qr_code']}")
    
    # Send print request
    try:
        response = requests.post(
            "http://localhost:5000/print",
            json=test_labels,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.ok:
            result = response.json()
            print("\n✅ Test print successful!")
            print(f"📊 Labels sent: {result.get('labels_count', 0)}")
            print(f"🆔 Job ID: {result.get('job_info', 'N/A')}")
            print(f"⏰ Timestamp: {result.get('timestamp', 'N/A')}")
            print("\n🏷️  Check your printer - test labels should be printing!")
            return True
        else:
            print(f"\n❌ Test print failed!")
            print(f"HTTP Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Print request timed out")
        print("💡 Check if printer is connected and ready")
        return False
    except Exception as e:
        print(f"❌ Print request error: {e}")
        return False

if __name__ == "__main__":
    test_print()