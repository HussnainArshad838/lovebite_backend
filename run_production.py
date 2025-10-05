#!/usr/bin/env python3
"""
Production startup script for LoveBite backend
Optimized for Railway deployment with WebSocket support
"""

import os
import sys
import logging
from app import app, socketio

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main production entry point"""
    try:
        # Set production environment variables
        os.environ['FLASK_ENV'] = 'production'
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['PYTHONUNBUFFERED'] = '1'
        
        logger.info("🚀 Starting LoveBite Backend in Production Mode")
        logger.info("🌐 WebSocket support enabled")
        logger.info("📊 MongoDB connection configured")
        logger.info("🔧 Eventlet worker configured")
        
        # Import and configure eventlet
        try:
            import eventlet  # type: ignore
            eventlet.monkey_patch()
            logger.info("✅ Eventlet monkey patching applied")
        except ImportError as e:
            logger.warning(f"⚠️ Eventlet not available: {e}")
            logger.warning("   WebSocket performance may be reduced")
        
        # Start the server
        socketio.run(
            app,
            host='0.0.0.0',
            port=8080,  # Railway's port
            debug=False,
            log_output=True,
            use_reloader=False,
            allow_unsafe_werkzeug=True  # Fallback for WebSocket
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()