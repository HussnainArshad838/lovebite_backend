#!/bin/bash

echo "💕 LoveBite APK Tracking System - PRODUCTION MODE"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the lovebite_backend directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created!"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements if needed
echo "📦 Installing production requirements..."
pip install -r requirements.txt --quiet

# Set production environment variables
export FLASK_ENV=production
export ENVIRONMENT=production

# Start the server in production mode
echo "🚀 Starting LoveBite APK Tracking Server in PRODUCTION mode..."
echo "🌐 Server will be available at: http://localhost:5055"
echo "📊 Admin Dashboard: http://localhost:5055/admin_dashboard.html"
echo ""
echo "Using eventlet for WebSocket support in production"
echo "Press Ctrl+C to stop the server"
echo ""

# Use the production startup script
python start_server.py --mode prod-eventlet
