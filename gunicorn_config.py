# Gunicorn configuration for LoveBite backend
import os
import multiprocessing

# Server socket
bind = "0.0.0.0:8080"  # Changed to match your deployment port
backlog = 2048

# Worker processes - Use fewer workers for Railway's memory constraints
workers = min(2, multiprocessing.cpu_count() + 1)  # Reduced from 4 to 2
worker_class = "eventlet"  # Use eventlet for WebSocket support
worker_connections = 1000

# Timeout settings - Increased for WebSocket operations
timeout = 120  # Increased from 30 to 120 seconds
keepalive = 5  # Increased from 2 to 5 seconds
graceful_timeout = 30

# Memory management
max_requests = 500  # Reduced from 1000 to prevent memory buildup
max_requests_jitter = 50
preload_app = False  # Disable preloading to save memory

# Memory limits
worker_tmp_dir = "/dev/shm"  # Use shared memory for temporary files

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
    'PYTHONUNBUFFERED=1',  # Ensure output is sent to terminal
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
