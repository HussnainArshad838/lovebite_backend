# Gunicorn configuration for LoveBite backend
import os

# Server socket
bind = "0.0.0.0:5055"
backlog = 2048

# Worker processes
workers = 4
worker_class = "eventlet"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

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
]
