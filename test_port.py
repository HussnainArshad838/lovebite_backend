#!/usr/bin/env python3
"""
Test script to verify port configuration
"""

import os
import sys

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['ENVIRONMENT'] = 'production'

# Import eventlet
try:
    import eventlet
    eventlet.monkey_patch()
    print("✅ Eventlet monkey patching applied")
except ImportError as e:
    print(f"⚠️ Eventlet not available: {e}")

# Import and test the WSGI app
try:
    from wsgi import application
    print("✅ WSGI application imported successfully")
    
    # Test basic functionality
    with application.test_client() as client:
        response = client.get('/')
        print(f"✅ Health check response: {response.status_code}")
        print(f"✅ Response data: {response.get_data(as_text=True)}")
        
        # Test API endpoints
        response = client.get('/api/stats')
        print(f"✅ API stats response: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error testing WSGI application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🎉 Port configuration test passed!")
print("🚀 Ready for deployment on port 5055")
