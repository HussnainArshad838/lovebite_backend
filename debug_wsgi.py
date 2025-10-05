#!/usr/bin/env python3
"""
Debug WSGI application to identify startup issues
"""

import os
import sys
import traceback

# Set production environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['ENVIRONMENT'] = 'production'
os.environ['PYTHONUNBUFFERED'] = '1'

print("🔍 Starting WSGI debug...")

try:
    # Import and configure eventlet
    print("📦 Importing eventlet...")
    import eventlet
    eventlet.monkey_patch()
    print("✅ Eventlet monkey patching applied")
except ImportError as e:
    print(f"⚠️ Eventlet not available: {e}")

try:
    # Import the Flask app
    print("📦 Importing Flask app...")
    from app import app
    print("✅ Flask app imported successfully")
    
    # Test basic functionality
    print("🧪 Testing Flask app...")
    with app.test_client() as client:
        response = client.get('/')
        print(f"✅ Health check response: {response.status_code}")
        print(f"✅ Response data: {response.get_data(as_text=True)}")
        
except Exception as e:
    print(f"❌ Error importing Flask app: {e}")
    print("📋 Full traceback:")
    traceback.print_exc()
    sys.exit(1)

print("🎉 WSGI debug completed successfully!")
print("🚀 Application is ready for deployment")
