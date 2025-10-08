import os

# Server socket
port = os.getenv('PORT', '8080')
bind = f"0.0.0.0:{port}"

print(f"🚀 Gunicorn starting on port: {port}")

# Worker settings - MINIMAL for Railway
workers = 1
worker_class = "eventlet"
worker_connections = 500
threads = 1
worker_tmp_dir = "/tmp"

# Timeout settings
timeout = 120
keepalive = 5
graceful_timeout = 30

# Memory management - AGGRESSIVE
max_requests = 50
max_requests_jitter = 10
preload_app = False

# Logging - MUST BE ENABLED
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True

# Process naming
proc_name = "lovebite_backend"
daemon = False

# Environment
raw_env = [
    'FLASK_ENV=production',
    'ENVIRONMENT=production',
    'PYTHONUNBUFFERED=1',
]

# Hooks for debugging
def when_ready(server):
    server.log.info("✅ Server is ready!")

def pre_fork(server, worker):
    server.log.info(f"🔄 Worker spawning (pid: {worker.pid})")

def post_fork(server, worker):
    server.log.info(f"✅ Worker spawned (pid: {worker.pid})")

def worker_abort(worker):
    worker.log.error(f"❌ Worker aborted (pid: {worker.pid})")