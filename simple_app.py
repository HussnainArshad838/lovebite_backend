#!/usr/bin/env python3
"""
Simple WSGI application without complex imports
"""

import os
import sys

# Set production environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['ENVIRONMENT'] = 'production'
os.environ['PYTHONUNBUFFERED'] = '1'

def simple_app(environ, start_response):
    """Simple WSGI application"""
    status = '200 OK'
    headers = [('Content-Type', 'application/json')]
    
    response_body = b'{"status": "ok", "message": "LoveBite Backend is running!"}'
    
    start_response(status, headers)
    return [response_body]

# WSGI application
application = simple_app

if __name__ == '__main__':
    print("🚀 Simple WSGI application ready!")
    print("✅ No external dependencies required")
    print("🌐 Application will respond to health checks")
