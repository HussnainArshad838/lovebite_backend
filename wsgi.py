#!/usr/bin/env python3
"""
WSGI entry point for LoveBite backend production server.
This file provides a proper WSGI application for production deployment.
"""

import os
import sys
from app import app, socketio

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['ENVIRONMENT'] = 'production'

def create_app():
    """Create and return the Flask-SocketIO application."""
    return app, socketio

if __name__ == '__main__':
    # This allows running the server directly with: python wsgi.py
    print("Starting LoveBite APK Tracking API in production mode...")
    socketio.run(app, host='0.0.0.0', port=5055, debug=False, allow_unsafe_werkzeug=True)
