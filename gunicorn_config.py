import os
import multiprocessing

# Server socket
port = os.getenv('PORT', '8080')
bind = f"0.0.0.0:{port}"

print(f"🚀 Starting Gunicorn on port: {port}")

backlog = 512

# Worker processes
workers = 1
worker_class = "eventlet"
worker_connections = 500
threads = 1

# Timeout settings
timeout = 120
keepalive = 5
graceful_timeout = 30

# Memory management
max_requests = 100
max_requests_jitter = 10
preload_app = False

worker_tmp_dir = "/tmp"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "lovebite_backend"

daemon = False
pidfile = "/tmp/lovebite_backend.pid"

# Environment variables
raw_env = [
    'FLASK_ENV=production',
    'ENVIRONMENT=production',
    'PYTHONUNBUFFERED=1',
    'PYTHONDONTWRITEBYTECODE=1',
]

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)