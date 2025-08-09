#!/bin/bash

# Port Manager Utility for FastAPI Receipt Scanner
# This script helps manage ports and processes

set -e

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

# Function to show what's using a port
show_port_usage() {
    local port=$1
    echo "🔍 Checking port $port..."
    
    if check_port $port; then
        print_warning "Port $port is in use by:"
        lsof -i :$port
    else
        print_status "Port $port is free"
    fi
}

# Function to kill processes on a specific port
kill_port_processes() {
    local port=$1
    local force=$2
    
    if ! check_port $port; then
        print_info "Port $port is already free"
        return 0
    fi
    
    print_warning "Port $port is in use. Attempting to free it..."
    
    # Get PIDs using the port
    local pids=$(lsof -ti :$port 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        print_info "Found processes using port $port: $pids"
        
        if [ "$force" = "true" ]; then
            # Force kill immediately
            for pid in $pids; do
                if kill -0 $pid 2>/dev/null; then
                    print_info "Force killing PID $pid..."
                    kill -9 $pid
                fi
            done
        else
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

# Function to find available ports
find_available_ports() {
    local start_port=$1
    local count=${2:-5}
    
    echo "🔍 Looking for available ports starting from $start_port..."
    
    local found_ports=()
    local current_port=$start_port
    
    while [ ${#found_ports[@]} -lt $count ] && [ $current_port -lt 65535 ]; do
        if ! check_port $current_port; then
            found_ports+=($current_port)
            print_status "Port $current_port is available"
        fi
        ((current_port++))
    done
    
    if [ ${#found_ports[@]} -eq 0 ]; then
        print_error "No available ports found starting from $start_port"
        return 1
    fi
    
    echo ""
    print_info "Available ports: ${found_ports[*]}"
    echo ""
    print_info "To use one of these ports:"
    echo "   export FASTAPI_PORT=${found_ports[0]} && ./deploy_network.sh deploy"
}

# Function to show all Python processes
show_python_processes() {
    echo "🐍 Python processes currently running:"
    
    local python_pids=$(pgrep -f python 2>/dev/null || true)
    
    if [ -z "$python_pids" ]; then
        print_info "No Python processes found"
        return
    fi
    
    for pid in $python_pids; do
        local cmd=$(ps -p $pid -o command= 2>/dev/null || echo "Unknown")
        local port_info=""
        
        # Check if this process is using any ports
        local ports=$(lsof -p $pid -i -P 2>/dev/null | grep LISTEN | awk '{print $9}' | cut -d: -f2 | sort -u)
        if [ ! -z "$ports" ]; then
            port_info=" (using ports: $ports)"
        fi
        
        echo "   PID $pid: $cmd$port_info"
    done
}

# Function to clean up stale PID files
cleanup_pid_files() {
    local app_dir="/Users/admin/JR_Reciept_Scanner_AI"
    
    echo "🧹 Cleaning up stale PID files..."
    
    if [ -f "$app_dir/logs/fastapi.pid" ]; then
        local pid=$(cat "$app_dir/logs/fastapi.pid")
        if ! kill -0 $pid 2>/dev/null; then
            print_info "Removing stale FastAPI PID file (PID: $pid)"
            rm -f "$app_dir/logs/fastapi.pid"
        else
            print_info "FastAPI PID file is valid (PID: $pid)"
        fi
    fi
    
    print_status "PID file cleanup completed"
}

# Main script logic
case "${1:-help}" in
    "check")
        port=${2:-8000}
        show_port_usage $port
        ;;
    "kill")
        port=${2:-8000}
        force=${3:-false}
        kill_port_processes $port $force
        ;;
    "find")
        start_port=${2:-8000}
        count=${3:-5}
        find_available_ports $start_port $count
        ;;
    "python")
        show_python_processes
        ;;
    "cleanup")
        cleanup_pid_files
        ;;
    "status")
        echo "📊 Current Status:"
        echo ""
        show_port_usage 8000
        echo ""
        show_port_usage 8001
        echo ""
        show_port_usage 8002
        echo ""
        show_python_processes
        echo ""
        cleanup_pid_files
        ;;
    "help"|*)
        echo "🔧 Port Manager Utility"
        echo ""
        echo "Usage: $0 {check|kill|find|python|cleanup|status|help}"
        echo ""
        echo "Commands:"
        echo "   check [port]     - Check if a port is in use (default: 8000)"
        echo "   kill [port] [force] - Kill processes using a port (default: 8000, force: false)"
        echo "   find [start] [count] - Find available ports starting from port (default: 8000, 5)"
        echo "   python          - Show all Python processes"
        echo "   cleanup         - Clean up stale PID files"
        echo "   status          - Show comprehensive status"
        echo "   help            - Show this help message"
        echo ""
        echo "Examples:"
        echo "   $0 check 8000           # Check if port 8000 is in use"
        echo "   $0 kill 8000            # Gracefully kill processes on port 8000"
        echo "   $0 kill 8000 true       # Force kill processes on port 8000"
        echo "   $0 find 8000 10         # Find 10 available ports starting from 8000"
        echo "   $0 status               # Show comprehensive status"
        echo ""
        echo "Environment Variables:"
        echo "   FASTAPI_PORT - Set custom port for FastAPI deployment"
        ;;
esac 