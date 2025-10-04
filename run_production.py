#!/usr/bin/env python3
"""
Production server runner for LoveBite backend.
Uses eventlet for proper WebSocket support in production.
"""

import os
import sys
import eventlet
from app import app, socketio

# Set production environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['ENVIRONMENT'] = 'production'

# Monkey patch for eventlet compatibility
eventlet.monkey_patch()

def run_production_server():
    """Run the production server with eventlet."""
    print("Starting LoveBite APK Tracking API in production mode...")
    print("Using eventlet for WebSocket support")
    
    # Use eventlet as the server
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5055, 
        debug=False,
        use_reloader=False,
        log_output=True
    )

if __name__ == '__main__':
    run_production_server()
