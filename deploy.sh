#!/bin/bash

# LoveBite Backend Deployment Script
# This script helps deploy the backend to Railway with proper configuration

echo "🚀 LoveBite Backend Deployment Script"
echo "====================================="

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

# Create a backup of current files
echo "📦 Creating backup..."
mkdir -p backups
cp -r . backups/backup_$(date +%Y%m%d_%H%M%S)/
echo "✅ Backup created"

# Set production environment variables
echo "🔧 Setting production environment variables..."
export FLASK_ENV=production
export ENVIRONMENT=production
export PYTHONUNBUFFERED=1

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

if [ $? -eq 0 ]; then
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
else
    echo "❌ Deployment failed!"
    echo "Check the logs above for errors."
    exit 1
fi
