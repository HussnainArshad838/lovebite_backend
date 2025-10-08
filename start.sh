#!/bin/bash

echo "=================================="
echo "Starting LoveBite Backend"
echo "=================================="
echo "PORT: ${PORT:-8080}"
echo "RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-local}"
echo "=================================="

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    source /opt/venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Start gunicorn with explicit configuration
exec gunicorn \
    --bind "0.0.0.0:${PORT:-8080}" \
    --worker-class eventlet \
    --workers 1 \
    --timeout 120 \
    --keepalive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    app:app
