#!/usr/bin/env python3
"""
Test script to verify database saving is working
"""

import requests
import json
from datetime import datetime

# Test data
test_device_data = {
    "device_id": f"test_device_{int(datetime.now().timestamp())}",
    "app_version": "1.0.0",
    "device_info": {
        "brand": "Test",
        "model": "Test Device",
        "systemName": "Android",
        "systemVersion": "13",
        "deviceId": f"test_device_{int(datetime.now().timestamp())}",
        "appVersion": "1.0.0",
        "buildNumber": "1",
        "bundleId": "com.lovebite",
        "isEmulator": False,
        "isTablet": False
    },
    "country": "Test Country",
    "city": "Test City",
    "timezone": "UTC"
}

# Test local backend
print("=" * 60)
print("🧪 Testing Database Save - Local Backend")
print("=" * 60)

try:
    response = requests.post(
        "http://localhost:5055/api/track-installation",
        json=test_device_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("\n✅ SUCCESS: Data saved to database!")
            print(f"   Message: {result.get('message')}")
            print(f"   Database: {result.get('database', 'Unknown')}")
        else:
            print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
    else:
        print(f"\n❌ HTTP Error: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "=" * 60)

# Test getting installations
print("\n📊 Testing Get Installations...")
try:
    response = requests.get("http://localhost:5055/api/installations?limit=5", timeout=10)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            count = result.get("pagination", {}).get("total_count", 0)
            print(f"✅ Found {count} installations in database")
            if count > 0:
                print(f"   Latest device: {result.get('data', [{}])[0].get('device_id', 'N/A')}")
        else:
            print(f"❌ Error: {result.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("=" * 60)

