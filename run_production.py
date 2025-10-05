#!/usr/bin/env python3
"""
Production WSGI application for LoveBite backend
Optimized for Railway deployment with WebSocket support
"""

import os
import sys
import logging

# Set production environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['ENVIRONMENT'] = 'production'
os.environ['PYTHONUNBUFFERED'] = '1'

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import and configure eventlet
try:
    import eventlet  # type: ignore
    eventlet.monkey_patch()
    logger.info("✅ Eventlet monkey patching applied")
except ImportError as e:
    logger.warning(f"⚠️ Eventlet not available: {e}")
    logger.warning("   WebSocket performance may be reduced")

# Import the Flask app and SocketIO
from app import app, socketio

logger.info("🚀 LoveBite Backend WSGI Application Ready")
logger.info("🌐 WebSocket support enabled")
logger.info("📊 MongoDB connection configured")
logger.info("🔧 Eventlet worker configured")

# Create WSGI application
application = app

# For direct execution (not recommended in production)
if __name__ == '__main__':
    try:
        logger.info("🚀 Starting LoveBite Backend in Production Mode")
        
        # Start the server
        socketio.run(
            app,
            host='0.0.0.0',
            port=5055,  # Railway's port
            debug=False,
            log_output=True,
            use_reloader=False,
            allow_unsafe_werkzeug=True  # Fallback for WebSocket
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)