#!/bin/bash

# FastAPI + Ngrok Quick Start Script
# This script starts your FastAPI app and exposes it via ngrok

set -e

echo "🚀 Starting FastAPI with Ngrok..."

# Configuration
APP_DIR="/Users/admin/JR_Reciept_Scanner_AI"
DEFAULT_PORT="8000"
PORT="${FASTAPI_PORT:-$DEFAULT_PORT}"  # Allow environment variable override

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on a specific port
kill_port_processes() {
    local port=$1
    print_warning "Port $port is in use. Attempting to free it..."
    
    # Get PIDs using the port
    local pids=$(lsof -ti :$port 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        print_info "Found processes using port $port: $pids"
        
        # Try graceful shutdown first
        for pid in $pids; do
            if kill -0 $pid 2>/dev/null; then
                print_info "Sending SIGTERM to PID $pid..."
                kill $pid
            fi
        done
        
        # Wait a moment for graceful shutdown
        sleep 3
        
        # Check if processes are still running and force kill if necessary
        pids=$(lsof -ti :$port 2>/dev/null)
        if [ ! -z "$pids" ]; then
            print_warning "Processes still running, force killing..."
            for pid in $pids; do
                if kill -0 $pid 2>/dev/null; then
                    print_info "Force killing PID $pid..."
                    kill -9 $pid
                fi
            done
            sleep 1
        fi
        
        # Verify port is now free
        if check_port $port; then
            print_error "Failed to free port $port"
            return 1
        else
            print_status "Port $port is now free"
        fi
    fi
}

# Function to cleanup on exit
cleanup() {
    print_info "Stopping services..."
    
    # Stop FastAPI using PID file
    if [ -f "$APP_DIR/logs/fastapi.pid" ]; then
        local pid=$(cat "$APP_DIR/logs/fastapi.pid")
        if kill -0 $pid 2>/dev/null; then
            print_info "Stopping FastAPI (PID: $pid)..."
            kill $pid
            rm -f "$APP_DIR/logs/fastapi.pid"
        fi
    fi
    
    # Also try to stop any processes we started
    if [ ! -z "$FASTAPI_PID" ]; then
        if kill -0 $FASTAPI_PID 2>/dev/null; then
            kill $FASTAPI_PID 2>/dev/null || true
        fi
    fi
    
    print_status "Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Change to app directory
cd "$APP_DIR"

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    print_warning "Ngrok not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ngrok
    else
        print_error "Please install ngrok manually: https://ngrok.com/download"
        exit 1
    fi
fi

# Check if ngrok is authenticated
if ! ngrok config check &> /dev/null; then
    print_warning "Ngrok not authenticated. Please run:"
    echo "   ngrok config add-authtoken YOUR_AUTH_TOKEN"
    echo ""
    print_info "Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

# Check and free port if needed
if check_port $PORT; then
    print_warning "Port $PORT is already in use"
    if ! kill_port_processes $PORT; then
        print_error "Could not free port $PORT. Please manually stop the process using this port."
        print_info "You can check what's using the port with: lsof -i :$PORT"
        print_info "Or use a different port by setting FASTAPI_PORT environment variable"
        exit 1
    fi
fi

# Clean up any stale PID files
if [ -f "$APP_DIR/logs/fastapi.pid" ]; then
    local pid=$(cat "$APP_DIR/logs/fastapi.pid")
    if ! kill -0 $pid 2>/dev/null; then
        print_info "Removing stale PID file..."
        rm -f "$APP_DIR/logs/fastapi.pid"
    fi
fi

print_info "Using port: $PORT"
print_info "You can change the port by setting FASTAPI_PORT environment variable"

# Start FastAPI in background
print_status "Starting FastAPI application..."
./deploy_network.sh deploy &
FASTAPI_PID=$!

# Wait for FastAPI to start
print_info "Waiting for FastAPI to start..."
sleep 5

# Test if FastAPI is running
if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    print_status "FastAPI is running on port $PORT"
else
    print_warning "FastAPI health check failed. Check logs:"
    echo "   tail -f logs/fastapi.log"
    cleanup
fi

# Start ngrok
print_status "Starting ngrok tunnel..."
echo ""
print_info "Your API will be available at the ngrok URL below:"
echo "   • Health: https://[ngrok-url]/health"
echo "   • Scan: https://[ngrok-url]/scan"
echo ""
print_warning "Press Ctrl+C to stop both services"
echo ""

# Start ngrok
ngrok http $PORT

# Cleanup when ngrok stops
cleanup 