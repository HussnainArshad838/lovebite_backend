#!/usr/bin/env python3
"""
Main entry point for LoveBite backend production server.
This file provides the main WSGI application for gunicorn deployment.
"""

import os
import sys

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['ENVIRONMENT'] = 'production'

# Import the Flask app
from app import app

# WSGI application entry point
application = app

if __name__ == '__main__':
    # This allows running the server directly with: python main.py
    print("Starting LoveBite APK Tracking API in production mode...")
    app.run(host='0.0.0.0', port=5055, debug=False)
