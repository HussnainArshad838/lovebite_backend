# Port Configuration Fix

## Problem
Railway was configured to use port 5055, but our backend was configured to run on port 8080. This caused the health check to fail because Railway couldn't reach the application.

## Solution
Updated all port references from 8080 to 5055 to match Railway's configuration.

## Files Updated

### 1. `gunicorn_config.py`
```python
# Before
bind = "0.0.0.0:8080"

# After  
bind = "0.0.0.0:5055"
```

### 2. `wsgi.py`
```python
# Before
socketio.run(app, host='0.0.0.0', port=8080, debug=False)

# After
socketio.run(app, host='0.0.0.0', port=5055, debug=False)
```

### 3. `run_production.py`
```python
# Before
port=8080,  # Railway's port

# After
port=5055,  # Railway's port
```

### 4. `app.py`
```python
# Before
port=8080,  # Use Railway's port

# After
port=5055,  # Use Railway's port
```

### 5. `railway.json`
```json
{
  "deploy": {
    "startCommand": "gunicorn --config gunicorn_config.py wsgi:application"
  }
}
```

## Railway Configuration
- **Public Domain**: `lovebitebackend-production-1f4e.up.railway.app`
- **Port**: 5055
- **Health Check Path**: `/`
- **Health Check Timeout**: 100 seconds

## Expected Results
After deployment:
- ✅ Health check should pass
- ✅ Application accessible at `https://lovebitebackend-production-1f4e.up.railway.app/`
- ✅ WebSocket connections working
- ✅ Admin dashboard functional
- ✅ Camera control working

## Deploy Command
```bash
cd lovebite_backend
./redeploy.sh
```

Or manually:
```bash
railway up
```
