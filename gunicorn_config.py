# Gunicorn configuration for LoveBite backend
import os
import multiprocessing

# Server socket - Use Railway's dynamic PORT
# Server socket - Use Railway's PORT environment variable or default to 8080
port = os.getenv('PORT', '8080')
bind = f"0.0.0.0:{port}"
print(f"🚀 Starting Gunicorn on port: {port}")
print(f"🔍 Environment PORT: {os.getenv('PORT')}")
print(f"🔍 Binding to: {bind}")
print(f"🔍 Railway environment: {os.getenv('RAILWAY_ENVIRONMENT', 'NOT SET')}")
print(f"🔍 Railway project: {os.getenv('RAILWAY_PROJECT_ID', 'NOT SET')}")

# Force Railway to use port 8080
if os.getenv('RAILWAY_ENVIRONMENT'):
    print(f"🔧 Railway detected - using port 8080")
    port = '8080'
    bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes - Use only 1 worker for Railway's memory constraints
workers = 1  # Reduced to 1 worker to prevent memory issues
worker_class = "eventlet"  # Use eventlet for WebSocket support
worker_connections = 1000

# Timeout settings - Optimized for Railway
timeout = 30  # Reduced back to 30 seconds
keepalive = 2  # Reduced keepalive
graceful_timeout = 30

# Memory management - Aggressive settings for Railway
max_requests = 100  # Very low to prevent memory buildup
max_requests_jitter = 10
preload_app = False  # Disable preloading to save memory

# Memory limits
worker_tmp_dir = "/tmp"  # Use /tmp for temporary files

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "lovebite_backend"

# Server mechanics
daemon = False
pidfile = "/tmp/lovebite_backend.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = None
# certfile = None

# Environment variables
raw_env = [
    'FLASK_ENV=production',
    'ENVIRONMENT=production',
    'PYTHONUNBUFFERED=1',
    'PYTHONDONTWRITEBYTECODE=1',  # Prevent .pyc files
]

# Eventlet specific settings
def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")
