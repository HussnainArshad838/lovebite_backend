"""
Vercel serverless entry point
"""
import os
import sys

# Set environment before imports
os.environ['VERCEL'] = '1'
os.environ['FLASK_ENV'] = 'production'
os.environ['VERCEL_HANDLER_INSPECTION'] = '0'

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import Flask app
from app import app as application

# Vercel expects the WSGI app to be available at module level
# This is the entry point for serverless function
def handler(environ, start_response):
    """Vercel serverless handler"""
    return application(environ, start_response)
