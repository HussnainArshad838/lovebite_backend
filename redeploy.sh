#!/bin/bash

echo "🚀 Redeploying LoveBite Backend with Python 3.12 compatibility fixes"
echo "=================================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the backend directory."
    exit 1
fi

echo "✅ Backend files found"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "⚠️  Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    echo "   or visit: https://docs.railway.app/develop/cli"
    exit 1
fi

echo "✅ Railway CLI found"

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway first:"
    echo "   railway login"
    exit 1
fi

echo "✅ Railway authentication confirmed"

echo ""
echo "🔧 Key fixes applied:"
echo "   • Updated greenlet to version 3.1.1 (Python 3.12 compatible)"
echo "   • Optimized Gunicorn configuration for Railway"
echo "   • Enhanced WebSocket handling"
echo "   • Improved error handling and logging"
echo ""

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Your backend is now available at:"
    echo "   https://lovebitebackend-production-1f4e.up.railway.app/"
    echo ""
    echo "📊 Admin Dashboard:"
    echo "   https://lovebitebackend-production-1f4e.up.railway.app/admin_dashboard.html"
    echo ""
    echo "🔧 To check logs:"
    echo "   railway logs"
    echo ""
    echo "🔄 To restart the service:"
    echo "   railway restart"
    echo ""
    echo "📱 Test your mobile app now - the backend should work properly!"
else
    echo "❌ Deployment failed!"
    echo "Check the logs above for errors."
    exit 1
fi
