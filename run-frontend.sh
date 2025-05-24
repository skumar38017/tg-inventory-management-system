#!/bin/bash

echo "🧠 Detecting OS..."

OS="$(uname -s)"

# Load environment variables from .env
if [ -f .env ]; then
  set -a
  source .env
  set +a
else
  echo "❌ .env file not found!"
  exit 1
fi

# ========== WINDOWS (Git Bash / WSL) ==========
if [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS_NT"* || "$OS" == "Windows_NT" ]]; then
  echo "🪟 Detected Windows"

  # Extract host IP from ipconfig (fallback if BACKEND_URL not set)
  if [ -z "$BACKEND_URL" ]; then
    HOST_IP=$(ipconfig | grep "IPv4 Address" | awk -F: '{print $2}' | tr -d ' \r')
    BACKEND_URL="http://$HOST_IP:8000"
  fi

  echo "✅ BACKEND_URL: $BACKEND_URL"

  echo "🚀 Running container..."
  docker run -it --rm \
    --network host \
    -e DISPLAY=$DISPLAY \
    -e PYTHONPATH=/app \
    -e USER_ID=$(id -u) \
    -e GROUP_ID=$(id -g) \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /home/$USER:/host/home/$USER \
    -v /tmp:/host/tmp \
    891377266155.dkr.ecr.ap-south-1.amazonaws.com/tg/inventory:latest \
    python app/entry_inventory.py

# ========== LINUX / macOS ==========
else
    #!/bin/bash
    echo "🐧 Detected Linux / macOS"
    # Start the Frontend

    # Load environment variables from .env file
    if [ -f .env ]; then
    # Export only non-comment, non-empty lines from .env
    set -a  # Automatically export all variables
    source .env
    set +a
    else
    echo "❌ .env file not found!"
    exit 1
    fi

    # Set the password from the loaded environment variable
    PASSWORD="$PASSWORD"

    # Get the absolute path of the script
    SCRIPT_PATH="$(realpath "$BASH_SOURCE")"

    # Check if the script is executable; if not, make it so
    if [ ! -x "$SCRIPT_PATH" ]; then
    echo "$PASSWORD" | sudo -S chmod +x "$SCRIPT_PATH"
    exec "$SCRIPT_PATH"  # Re-run this script after making it executable
    exit
    fi

    # Automatically detect and set the DISPLAY variable

    # If running on a local machine, use :0 as the display
    if [ -z "$DISPLAY" ]; then
    # Check if the script is running on a local machine with a GUI
    if tty -s; then
        # It's running on a local machine, set DISPLAY to :0
        export DISPLAY=:0
    else
        # Running remotely, set DISPLAY to the default forwarded X11 display
        export DISPLAY=:0.0  # This might need adjustment depending on your setup
    fi
    fi

    # Ensure DISPLAY is set and not empty
    if [ -z "$DISPLAY" ]; then
    echo "❌ DISPLAY variable is not set! Ensure X11 forwarding is enabled."
    exit 1
    fi

    # Allow Docker to access the X11 display
    xhost +local:docker

    # Run the Docker container and pass DISPLAY from the host to the container
  docker run -it --rm \
    --network host \
    -e DISPLAY=$DISPLAY \
    -e PYTHONPATH=/app \
    -e USER_ID=$(id -u) \
    -e GROUP_ID=$(id -g) \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /home/$USER:/host/home/$USER \
    -v /tmp:/host/tmp \
    891377266155.dkr.ecr.ap-south-1.amazonaws.com/tg/inventory:frontend-latest \
    python app/entry_inventory.py
fi