#!/bin/bash

# Simple FastAPI Production Startup Script
set -e

# Configuration
APP_DIR="/Users/admin/JR_Reciept_Scanner_AI"
VENV_DIR="$APP_DIR/.venv"
APP_MODULE="app.main:app"
HOST="127.0.0.1"
PORT="8000"
WORKERS="1"
WORKER_CLASS="uvicorn.workers.UvicornWorker"

echo "Starting FastAPI Receipt Scanner..."

# Change to app directory
cd "$APP_DIR"

# Activate virtual environment (using miniconda)
echo "Activating virtual environment..."
source "/Users/admin/miniconda3/bin/activate"

# Activate local venv if exists
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
fi

echo "Starting application with gunicorn..."
echo "App Module: $APP_MODULE"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"

# Start with gunicorn
exec gunicorn "$APP_MODULE" \
    --bind "$HOST:$PORT" \
    --workers "$WORKERS" \
    --worker-class "$WORKER_CLASS" \
    --timeout 120 \
    --keep-alive 2 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
