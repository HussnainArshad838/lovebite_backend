#!/usr/bin/env python3
"""
Simple WSGI application for Railway deployment testing
This is a minimal app to verify the basic setup works
"""

import os
import sys
import json
from datetime import datetime

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['ENVIRONMENT'] = 'production'
os.environ['PYTHONUNBUFFERED'] = '1'

print("🚀 Starting Simple WSGI Application...")
print(f"Python version: {sys.version}")
print(f"Port: {os.getenv('PORT', '5055')}")

def application(environ, start_response):
    """
    Simple WSGI application that responds to health checks
    """
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # Log the request
    print(f"📝 Request: {method} {path}")
    
    # Handle health check endpoint
    if path == '/' or path == '/health':
        status = '200 OK'
        response_data = {
            "status": "ok",
            "message": "LoveBite Backend is running!",
            "timestamp": datetime.utcnow().isoformat(),
            "port": os.getenv('PORT', '5055'),
            "environment": "production"
        }
        
        response_body = json.dumps(response_data).encode('utf-8')
        response_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))
        ]
        
        start_response(status, response_headers)
        return [response_body]
    
    # Handle API info endpoint
    elif path == '/api/info':
        status = '200 OK'
        response_data = {
            "name": "LoveBite APK Tracking API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": [
                "/",
                "/health",
                "/api/info"
            ]
        }
        
        response_body = json.dumps(response_data).encode('utf-8')
        response_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))
        ]
        
        start_response(status, response_headers)
        return [response_body]
    
    # 404 for other paths
    else:
        status = '404 Not Found'
        response_data = {
            "error": "Not Found",
            "path": path
        }
        
        response_body = json.dumps(response_data).encode('utf-8')
        response_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body)))
        ]
        
        start_response(status, response_headers)
        return [response_body]

print("✅ Simple WSGI application initialized successfully!")
print("📍 Endpoints available:")
print("   - / (health check)")
print("   - /health (health check)")
print("   - /api/info (API info)")
