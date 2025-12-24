#!/bin/bash
set -e

# Use Railway's PORT environment variable, default to 8000
PORT=${PORT:-8000}

echo "Starting uvicorn on 0.0.0.0:$PORT"

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT