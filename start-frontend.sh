#!/bin/bash

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
  -e BACKEND_URL=$BACKEND_URL \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /home/$USER:/host/home/$USER \
  -v /tmp:/host/tmp \
  891377266155.dkr.ecr.ap-south-1.amazonaws.com/tg/inventory:latest \
  python app/entry_inventory.py




#  secon script

# #!/bin/bash

# # Start the Frontend

# # Set the password (⚠️ NOT SECURE in production)
# PASSWORD="12345six"

# # Check if the script is executable; if not, make it so
# if [ ! -x "$0" ]; then
#   echo "$PASSWORD" | sudo -S chmod +x "$0"
#   exec "$0"  # Re-run this script after making it executable
#   exit
# fi

# # Allow Docker to access the X11 display
# xhost +local:docker

# # Run the Docker container
# docker run -it --rm \
#   --network host \
#   -e DISPLAY=$DISPLAY \
#   -e PYTHONPATH=/app \
#   -v /tmp/.X11-unix:/tmp/.X11-unix \
#   ims-frontend python app/entry_inventory.py

#   # -v $(pwd):/app \