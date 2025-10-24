"""
LoveBite Backend Configuration
Configure your backend settings here
"""

import os

# Environment mode: 'development' or 'production'
# Change this to switch between local and live URLs
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # Change to 'development' for local testing
# Environment mode: 'development' or 'production'
# ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')  # Change to 'development' for local testing

# Database Configuration
# MongoDB Atlas Connection String
MONGODB_URI = "mongodb+srv://hussnainrajpoot5415:123456...@blogsdb.9xfkjee.mongodb.net/?retryWrites=true&w=majority&appName=blogsdb"
DATABASE_NAME = "lovebite"
COLLECTION_NAME = "apk_installations"

# Server Configuration
class DevelopmentConfig:
    """Local development configuration"""
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5055
    API_BASE_URL = 'http://localhost:5055'
    WS_BASE_URL = 'http://localhost:5055'
    CORS_ORIGINS = "*"  # Allow all origins in development

class ProductionConfig:
    """Production configuration for Render deployment"""
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.getenv('PORT', 5055))  # Render provides PORT env variable
    API_BASE_URL = 'https://lovebite-backend-j8vr.onrender.com'
    WS_BASE_URL = 'https://lovebite-backend-j8vr.onrender.com'
    CORS_ORIGINS = "*"  # Configure specific origins in production

# Select configuration based on environment
if ENVIRONMENT == 'production':
    Config = ProductionConfig
else:
    Config = DevelopmentConfig

# Print current configuration
def print_config():
    print(f"\n{'='*50}")
    print(f"🚀 LoveBite Backend Configuration")
    print(f"{'='*50}")
    print(f"Environment: {ENVIRONMENT.upper()}")
    print(f"Debug Mode: {Config.DEBUG}")
    print(f"Host: {Config.HOST}")
    print(f"Port: {Config.PORT}")
    print(f"API Base URL: {Config.API_BASE_URL}")
    print(f"WebSocket Base URL: {Config.WS_BASE_URL}")
    print(f"Database: {DATABASE_NAME}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"{'='*50}\n")

