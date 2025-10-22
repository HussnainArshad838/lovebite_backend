# API Directory for Vercel

This directory contains the Vercel serverless entry point.

## Structure

- `index.py` - Main entry point for Vercel serverless functions
  - Sets up the environment for Vercel
  - Imports the Flask app from the parent directory
  - Exports the app as `handler` for Vercel

## How It Works

When deployed to Vercel:
1. Vercel detects `api/index.py` as a serverless function
2. The file sets `VERCEL=1` environment variable
3. It imports the main Flask app from `../app.py`
4. The app automatically disables WebSocket features when `VERCEL=1`
5. Vercel wraps the Flask app and handles all HTTP requests

## Local Development

For local development, you don't need to use this file. Just run:

```bash
python app.py
```

The main `app.py` will run with full features including WebSockets.

## Vercel Deployment

When you deploy to Vercel, it automatically uses this entry point:

```bash
vercel
```

No additional configuration needed!
