#!/usr/bin/env python3
"""
Minimal WSGI application for testing
"""

import os
import sys

# Set production environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['ENVIRONMENT'] = 'production'
os.environ['PYTHONUNBUFFERED'] = '1'

print("🚀 Starting minimal WSGI application...")

try:
    from flask import Flask
    
    # Create a simple Flask app
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return {"status": "ok", "message": "LoveBite Backend is running!"}
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "timestamp": "2025-01-06T02:56:00Z"}
    
    print("✅ Minimal Flask app created successfully")
    
    # WSGI application
    application = app
    
    print("🎉 Minimal WSGI application ready!")
    
except Exception as e:
    print(f"❌ Error creating minimal app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
