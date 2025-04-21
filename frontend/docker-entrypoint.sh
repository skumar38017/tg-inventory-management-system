#!/bin/bash

# Set up X11 forwarding based on OS
if [ -e /tmp/.X11-unix ]; then
    # Linux configuration
    export DISPLAY=${DISPLAY_LINUX:-:0}
    xhost +local:docker &> /dev/null
    echo "Running in Linux mode with X11 forwarding (DISPLAY: $DISPLAY)"
else
    # Windows/Mac configuration
    export DISPLAY=${DISPLAY:-host.docker.internal:0}
    echo "Running in Windows/Mac mode with X11 forwarding (DISPLAY: $DISPLAY)"
fi

# Verify X11 connection
if ! xhost >& /dev/null; then
    echo "ERROR: X11 server connection failed!"
    echo "Possible fixes:"
    echo "1. Windows/Mac: Ensure XServer (VcXsrv/XQuartz) is running with:"
    echo "   - Disable access control (-ac option)"
    echo "   - Allow network clients"
    echo "2. Linux: Run 'xhost +local:docker' first"
    echo "3. Check DISPLAY environment variable (Current: $DISPLAY)"
    exit 1
fi

# Wait for backend services with timeout
echo "Waiting for backend services..."
timeout=30
while ! nc -z postgres 5432; do
    sleep 1
    ((timeout--))
    if [ $timeout -le 0 ]; then
        echo "ERROR: PostgreSQL service not available!"
        exit 1
    fi
done

timeout=30
while ! nc -z redis 6379; do
    sleep 1
    ((timeout--))
    if [ $timeout -le 0 ]; then
        echo "ERROR: Redis service not available!"
        exit 1
    fi
done

echo "All required services are available. Starting application..."

# Run the application with exec to replace shell process
exec python app/entry_inventory.py "$@"