#!/bin/bash

# Description: Start all components of the tg-inventory-management-system
# Author: You
# Date: 2025-04-26
# ------------------------------------------
PASSWORD="12345six"

# Set script to exit on any error
set -e

# Define the project path
PROJECT_DIR="/home/$USER/Documents/tg-inventory-management-system"
LOG_FILE="$PROJECT_DIR/startup.log"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to run commands with sudo and password
run_with_sudo() {
    echo "$PASSWORD" | sudo -S "$@"
}

# Change to the project directory
log "Changing to project directory: $PROJECT_DIR"
cd "$PROJECT_DIR" || { log "Failed to change directory"; exit 1; }
sleep 1

# Delete/clean all previous log
log "Cleaning previous log..."
> "$LOG_FILE"

# Run permission.sh
log "Running permission.sh"
bash permission.sh || { log "Failed to run permission.sh"; exit 1; }
sleep 1

# Deactivate Virtual env if already activated
log "Deactivating Virtual env if already activated"
deactivate || true
sleep 1

# Activate Virtual env
log "Activating Virtual env"
source .venv/bin/activate || { log "Failed to activate virtual environment"; exit 1; }
sleep 2

# Run permission.sh again
log "Running permission.sh again"
bash permission.sh || { log "Failed to run permission.sh"; exit 1; }
sleep 1

# Stop running Docker containers if any
log "Stopping any running Docker containers..."
docker compose down || log "No containers were running."
sleep 5

# Reset permissions
log "Reapplying permissions..."
bash permission.sh || { log "Failed to reapply permissions"; exit 1; }
sleep 1

# Start Docker containers
log "Starting Docker containers..."
docker compose up -d || { log "Failed to start Docker containers"; exit 1; }
sleep 6

# Check if port 8000 is in use
log "Checking if port 8000 is in use..."
if lsof -i :8000 &> /dev/null; then
    log "Port 8000 is in use. Attempting to free it..."
    PIDS=$(lsof -t -i :8000)
    for PID in $PIDS; do
        echo "$PASSWORD" | sudo -S kill -9 "$PID"
        log "Killed process using port 8000 (PID: $PID)"
    done
else
    log "Port 8000 is free."
fi
sleep 2

# Reapply permissions
log "Reapplying permissions again..."
bash permission.sh || { log "Failed to reapply permissions"; exit 1; }
sleep 1

# Start backend using uvicorn in background
log "Starting FastAPI backend with uvicorn..."
nohup uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload >> "$PROJECT_DIR/backend.log" 2>&1 &
sleep 10

# Final permission check
log "Running final permission check..."
bash permission.sh || { log "Failed to reapply permissions"; exit 1; }
sleep 1

# Start frontend
log "Starting frontend..."
bash run-frontend.sh || { log "Failed to start frontend"; exit 1; }

log "All services started successfully."
