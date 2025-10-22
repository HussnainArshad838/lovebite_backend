# Vercel Deployment Guide

## Overview
This Flask application has been configured to work with Vercel's serverless environment. Note that WebSocket features (Flask-SocketIO) are disabled on Vercel as they're not supported in serverless functions.

## Files Created/Modified

### 1. `vercel.json`
- Main Vercel configuration file
- Routes all requests to `app.py`
- Sets environment variables
- Configures Python runtime

### 2. `requirements-vercel.txt`
- Lightweight requirements file for Vercel
- Excludes WebSocket dependencies (Flask-SocketIO, eventlet)
- Only includes essential packages

### 3. `app.py` (Modified)
- Added Vercel detection (`IS_VERCEL` environment variable)
- Conditionally imports SocketIO only when not on Vercel
- WebSocket handlers are wrapped in `if socketio:` blocks
- Added Vercel handler function

## Deployment Steps

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from project directory**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project or create new one
   - Choose your team/account
   - Confirm settings

5. **Set Environment Variables** (if needed):
   ```bash
   vercel env add MONGODB_URI
   vercel env add FLASK_ENV
   ```

## Features Available on Vercel

✅ **Working Features:**
- All REST API endpoints
- MongoDB integration
- Device tracking
- Installation statistics
- Admin dashboard (HTML pages)
- Camera control endpoints (without real-time streaming)

❌ **Disabled Features:**
- WebSocket connections
- Real-time camera streaming
- Live WebRTC communication

## Environment Variables

Make sure to set these in your Vercel dashboard:
- `MONGODB_URI`: Your MongoDB connection string
- `FLASK_ENV`: Set to "production"
- `VERCEL`: Automatically set to "1" by Vercel

## Testing

After deployment, test these endpoints:
- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /api/track-installation` - Track device installation
- `GET /api/installations` - Get installation data
- `GET /api/stats` - Get statistics
- `GET /admin_dashboard.html` - Admin dashboard

## Limitations

1. **No WebSockets**: Real-time features are disabled
2. **Cold Starts**: Serverless functions may have cold start delays
3. **Execution Time**: Limited to 30 seconds per request
4. **Memory**: Limited to 1GB per function

## Alternative for Full Features

For full WebSocket support, consider deploying to:
- Railway (current setup)
- Heroku
- DigitalOcean App Platform
- AWS Elastic Beanstalk

## Troubleshooting

1. **Import Errors**: Check that `requirements-vercel.txt` has all needed packages
2. **MongoDB Connection**: Verify your MongoDB URI is correct
3. **Timeout Issues**: Check function timeout settings in Vercel dashboard
4. **CORS Issues**: Verify CORS settings in your frontend

## Local Testing

To test Vercel behavior locally:
```bash
vercel dev
```

This will simulate the Vercel environment locally.
