"""
Configuration file for LoveBite Backend
Contains all environment-specific settings and URLs
"""

import os

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://hussnainrajpoot5415:123456...@blogsdb.9xfkjee.mongodb.net/?retryWrites=true&w=majority&appName=blogsdb"

# Base URLs
LOCAL_BASE_URL = "http://127.0.0.1:8080/"
LIVE_BASE_URL = "https://lovebite-backend-4y9z.onrender.com"

# Environment Detection
IS_VERCEL = os.getenv('VERCEL') == '1'
IS_RENDER = os.getenv('RENDER') == 'true'
IS_PRODUCTION = IS_VERCEL or IS_RENDER

# Automatically select base URL based on environment
if IS_PRODUCTION:
    BASE_URL = LIVE_BASE_URL
else:
    BASE_URL = LOCAL_BASE_URL

# CORS Configuration
CORS_ORIGINS = "*"  # Allow all origins for development
CORS_SUPPORTS_CREDENTIALS = True

# Database Configuration
DB_NAME = "lovebite"
COLLECTION_NAME = "apk_installations"

# Server Configuration
DEFAULT_PORT = 8080
HOST = "0.0.0.0"

# Logging Configuration
LOG_LEVEL = "INFO"

# WebSocket Configuration (only for non-Vercel environments)
SOCKETIO_CORS_ORIGINS = "*"
SOCKETIO_PING_TIMEOUT = 60
SOCKETIO_PING_INTERVAL = 25
SOCKETIO_MAX_HTTP_BUFFER_SIZE = 1000000  # 1MB
