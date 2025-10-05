#!/bin/bash

echo "🚀 Deploying LoveBite Backend with Simple WSGI App"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "simple_app.py" ]; then
    echo "❌ Error: simple_app.py not found. Please run this script from the backend directory."
    exit 1
fi

echo "✅ Simple WSGI app found"

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment initiated successfully!"
    echo ""
    echo "🔍 Checking deployment status..."
    echo "   This may take a few minutes..."
    echo ""
    
    # Wait a bit for deployment to start
    sleep 10
    
    echo "📊 Checking logs..."
    railway logs --tail 50
    
    echo ""
    echo "🌐 Your backend should be available at:"
    echo "   https://lovebitebackend-production-1f4e.up.railway.app/"
    echo ""
    echo "🧪 Test the health check:"
    echo "   curl https://lovebitebackend-production-1f4e.up.railway.app/"
    echo ""
    echo "📱 If this works, we can then switch back to the full Flask app"
    
else
    echo "❌ Railway deployment failed!"
    echo "Check the output above for errors."
    exit 1
fi
