#!/bin/bash
set -e

# Use Railway's PORT environment variable, default to 8000
PORT=${PORT:-8000}

echo "=== Railway Deployment Debug Info ==="
echo "PORT: $PORT"
echo "SECRET_KEY: ${SECRET_KEY:+SET}"
echo "POSTGRES_HOST: ${POSTGRES_HOST:-NOT_SET}"
echo "POSTGRES_USER: ${POSTGRES_USER:+SET}"
echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:+SET}"
echo "REDIS_HOST: ${REDIS_HOST:-NOT_SET}"
echo "====================================="

echo "Starting uvicorn on 0.0.0.0:$PORT"

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info