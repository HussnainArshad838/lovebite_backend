# Gunicorn configuration for LoveBite backend
import os
import multiprocessing

# Server socket - Railway provides PORT environment variable
port = os.getenv('PORT', '8080')
bind = f"0.0.0.0:{port}"

print(f"🚀 Starting Gunicorn on port: {port}")
print(f"🔍 Environment PORT: {os.getenv('PORT')}")
print(f"🔍 Binding to: {bind}")

backlog = 512  # Reduced for memory efficiency

# Worker processes - Use only 1 worker for Railway's memory constraints
workers = 1  # Reduced to 1 worker to prevent memory issues
worker_class = "eventlet"  # Use eventlet for WebSocket support
worker_connections = 1000

# Timeout settings - Increased for MongoDB connection time
timeout = 120  # Increased to 120 seconds for MongoDB
keepalive = 5  # Increased keepalive
graceful_timeout = 30

# Memory management - Optimized for Railway
max_requests = 1000  # Balanced for stability
max_requests_jitter = 50
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
