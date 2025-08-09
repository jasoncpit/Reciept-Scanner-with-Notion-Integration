#!/bin/bash

# FastAPI Application Startup Script
# This script starts the FastAPI application using uvicorn

set -e

# Configuration
APP_DIR="/Users/admin/JR_Reciept_Scanner_AI"
VENV_DIR="$APP_DIR/.venv"
APP_MODULE="app.main:app"
HOST="0.0.0.0"
PORT="8000"
WORKERS="4"

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

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "uvicorn not found. Installing dependencies..."
    pip install -r requirements.txt
fi

echo "Starting FastAPI application..."
echo "App Module: $APP_MODULE"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"

# Start the application
exec uvicorn "$APP_MODULE" \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level info \
    --access-log \
    --reload
