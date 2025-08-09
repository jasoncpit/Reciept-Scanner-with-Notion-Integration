#!/bin/bash

# FastAPI Production Startup Script
# This script starts the FastAPI application using gunicorn for production

set -e

# Configuration
APP_DIR="/Users/admin/JR_Reciept_Scanner_AI"
VENV_DIR="$APP_DIR/.venv"
APP_MODULE="app.main:app"
HOST="0.0.0.0"
DEFAULT_PORT="8000"
PORT="${FASTAPI_PORT:-$DEFAULT_PORT}"  # Allow environment variable override
WORKERS="4"
WORKER_CLASS="uvicorn.workers.UvicornWorker"
MAX_REQUESTS="1000"
MAX_REQUESTS_JITTER="50"
TIMEOUT="30"

# Load environment variables if .env file exists
if [ -f "$APP_DIR/.env" ]; then
    echo "Loading environment variables from .env file..."
    set -a
    source "$APP_DIR/.env"
    set +a
fi

# Change to app directory
cd "$APP_DIR"

# Activate virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
else
    echo "Virtual environment not found at $VENV_DIR"
    echo "Please create a virtual environment first."
    exit 1
fi

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "gunicorn not found. Installing dependencies..."
    pip install -r requirements.txt
fi

echo "Starting FastAPI application in production mode..."
echo "App Module: $APP_MODULE"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Worker Class: $WORKER_CLASS"

# Start the application
exec gunicorn "$APP_MODULE" \
    --bind "$HOST:$PORT" \
    --workers "$WORKERS" \
    --worker-class "$WORKER_CLASS" \
    --max-requests "$MAX_REQUESTS" \
    --max-requests-jitter "$MAX_REQUESTS_JITTER" \
    --timeout "$TIMEOUT" \
    --keep-alive 2 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
