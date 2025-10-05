#!/usr/bin/env python3
"""
WSGI entry point for LoveBite backend
Compatible with Gunicorn eventlet worker
"""

import os
import sys

# Set production environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['ENVIRONMENT'] = 'production'
os.environ['PYTHONUNBUFFERED'] = '1'

# Import and configure eventlet
try:
    import eventlet  # type: ignore
    eventlet.monkey_patch()
    print("✅ Eventlet monkey patching applied")
except ImportError as e:
    print(f"⚠️ Eventlet not available: {e}")

# Import the Flask app
from app import app

print("🚀 LoveBite Backend WSGI Application Ready")
print("🌐 WebSocket support enabled")
print("📊 MongoDB connection configured")

# WSGI application
application = app

if __name__ == '__main__':
    # For direct execution
    from app import socketio
    socketio.run(app, host='0.0.0.0', port=5055, debug=False)