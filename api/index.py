"""
Vercel serverless entry point - Keep it simple!
"""
import os
import sys

# Set Vercel environment flag BEFORE importing anything
os.environ['VERCEL'] = '1'
os.environ['FLASK_ENV'] = 'production'

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app - it will auto-detect VERCEL=1 and skip SocketIO
from app import app

# Export the app directly - Vercel will handle the WSGI wrapping
# No need for custom handler function
app
