#!/bin/bash

# Start the Frontend

# Set the password (⚠️ NOT SECURE in production)
PASSWORD="$PASSWORD"

# Get the absolute path of the script
SCRIPT_PATH="$(realpath "$BASH_SOURCE")"

# Check if the script is executable; if not, make it so
if [ ! -x "$SCRIPT_PATH" ]; then
  echo "$PASSWORD" | sudo -S chmod +x "$SCRIPT_PATH"
  exec "$SCRIPT_PATH"  # Re-run this script after making it executable
  exit
fi

# Allow Docker to access the X11 display
xhost +local:docker

# Run the Docker container
docker run -it --rm \
  --network host \
  -e DISPLAY=$DISPLAY \
  -e PYTHONPATH=/app \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  ims-frontend python app/entry_inventory.py

  # -v $(pwd):/app \
