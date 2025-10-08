import os
import multiprocessing

# Server socket
port = os.getenv('PORT', '8080')
bind = f"0.0.0.0:{port}"

print(f"🚀 Gunicorn starting on port: {port}")

# Worker settings - OPTIMIZED for Railway
workers = 1
worker_class = "eventlet"
worker_connections = 1000
threads = 1

# Timeout settings - INCREASED
timeout = 300  # Increased from 120
keepalive = 10
graceful_timeout = 60

# Memory management
max_requests = 100
max_requests_jitter = 20
preload_app = True  # Preload to avoid repeated imports

# Logging - ENABLED
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

# Hooks
def on_starting(server):
    server.log.info("="*50)
    server.log.info("🚀 LoveBite Backend Starting...")
    server.log.info(f"📍 Port: {port}")
    server.log.info(f"👷 Workers: {workers}")
    server.log.info(f"⏱️  Timeout: {timeout}s")
    server.log.info("="*50)

def when_ready(server):
    server.log.info("✅ Server is ready and accepting connections!")

def pre_fork(server, worker):
    server.log.info(f"🔄 Worker spawning (pid: {worker.pid})")

def post_fork(server, worker):
    server.log.info(f"✅ Worker spawned (pid: {worker.pid})")

def worker_int(worker):
    worker.log.info(f"⚠️  Worker received INT or QUIT signal (pid: {worker.pid})")

def worker_abort(worker):
    worker.log.error(f"❌ Worker aborted (pid: {worker.pid})")

def post_worker_init(worker):
    worker.log.info(f"🎯 Worker initialized (pid: {worker.pid})")