#!/bin/bash

echo "🚀 LoveBite Backend - Quick Fix Deployment"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "simple_app.py" ]; then
    echo "❌ Error: simple_app.py not found. Please run this script from the backend directory."
    exit 1
fi

echo "✅ Simple WSGI app found"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Railway CLI. Please install manually:"
        echo "   npm install -g @railway/cli"
        exit 1
    fi
fi

echo "✅ Railway CLI found"

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway first:"
    echo "   railway login"
    echo ""
    echo "After logging in, run this script again."
    exit 1
fi

echo "✅ Railway authentication confirmed"

# Set environment variables
echo "🔧 Setting environment variables..."
railway variables set FLASK_ENV=production
railway variables set ENVIRONMENT=production
railway variables set PYTHONUNBUFFERED=1

echo "✅ Environment variables set"

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment initiated successfully!"
    echo ""
    echo "⏳ Waiting for deployment to complete..."
    sleep 15
    
    echo "📊 Checking deployment logs..."
    railway logs --tail 20
    
    echo ""
    echo "🧪 Testing health check..."
    echo "Testing: https://lovebitebackend-production-1f4e.up.railway.app/"
    
    # Test health check
    response=$(curl -s https://lovebitebackend-production-1f4e.up.railway.app/)
    if [ $? -eq 0 ]; then
        echo "✅ Health check response:"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo "❌ Health check failed. Check logs above."
    fi
    
    echo ""
    echo "🌐 Your backend is available at:"
    echo "   https://lovebitebackend-production-1f4e.up.railway.app/"
    echo ""
    echo "📋 Available endpoints:"
    echo "   - / (health check)"
    echo "   - /health (health check)"
    echo "   - /api/info (API info)"
    echo ""
    echo "🔍 Useful commands:"
    echo "   railway logs          # View logs"
    echo "   railway status        # Check status"
    echo "   railway variables     # View environment variables"
    echo ""
    echo "🎉 If this works, we can now switch to the full Flask app!"
    
else
    echo "❌ Railway deployment failed!"
    echo "Check the output above for errors."
    exit 1
fi
