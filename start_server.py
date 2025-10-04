#!/usr/bin/env python3
"""
Unified server startup script for LoveBite backend.
Handles both development and production modes.
"""

import os
import sys
import argparse
import subprocess

def run_development():
    """Run the server in development mode."""
    print("Starting LoveBite backend in DEVELOPMENT mode...")
    os.environ['FLASK_ENV'] = 'development'
    os.environ['ENVIRONMENT'] = 'development'
    
    # Import and run the app directly
    from app import app, socketio
    socketio.run(app, host='0.0.0.0', port=5055, debug=True)

def run_production_eventlet():
    """Run the server in production mode using eventlet."""
    print("Starting LoveBite backend in PRODUCTION mode (eventlet)...")
    os.environ['FLASK_ENV'] = 'production'
    os.environ['ENVIRONMENT'] = 'production'
    
    try:
        # Import and run with eventlet
        import eventlet
        eventlet.monkey_patch()
        print("✅ Using eventlet for WebSocket support")
    except ImportError:
        print("⚠️  Warning: eventlet not available, falling back to standard server")
        print("   Install eventlet with: pip install eventlet")
    
    from app import app, socketio
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5055, 
        debug=False,
        use_reloader=False,
        log_output=True
    )

def run_production_gunicorn():
    """Run the server in production mode using gunicorn."""
    print("Starting LoveBite backend in PRODUCTION mode (gunicorn)...")
    
    # Set environment variables
    env = os.environ.copy()
    env['FLASK_ENV'] = 'production'
    env['ENVIRONMENT'] = 'production'
    
    # Run gunicorn with sync worker (better for Flask-SocketIO)
    cmd = [
        'gunicorn',
        '--config', 'gunicorn_config.py',
        '--worker-class', 'sync',
        '--workers', '4',
        '--bind', '0.0.0.0:8080',
        'main:application'  # Use main.py with application variable
    ]
    
    subprocess.run(cmd, env=env)

def main():
    parser = argparse.ArgumentParser(description='Start LoveBite backend server')
    parser.add_argument(
        '--mode', 
        choices=['dev', 'prod-eventlet', 'prod-gunicorn'], 
        default='dev',
        help='Server mode: dev (development), prod-eventlet (production with eventlet), prod-gunicorn (production with gunicorn)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'dev':
        run_development()
    elif args.mode == 'prod-eventlet':
        run_production_eventlet()
    elif args.mode == 'prod-gunicorn':
        run_production_gunicorn()

if __name__ == '__main__':
    main()