"""
Vercel serverless entry point
This file imports the Flask app and exports it for Vercel
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Vercel environment
os.environ['VERCEL'] = '1'
os.environ['FLASK_ENV'] = 'production'

# Import the Flask app
from app import app

# Export for Vercel
handler = app
