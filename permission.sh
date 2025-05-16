#!/bin/bash

# permission.sh

# Make script executable if not already
SCRIPT_PATH="$(realpath "$0")"

if [ ! -x "$SCRIPT_PATH" ]; then
  echo "Making the script itself executable..."
  chmod +x "$SCRIPT_PATH"
  exec "$SCRIPT_PATH"  # Re-run the script now that it's executable
  exit
fi

# Load environment variables from .env file
if [ -f .env ]; then
  echo "🔄 Loading environment variables from .env..."
  set -a
  source .env
  set +a
else
  echo "❌ .env file not found!"
  exit 1
fi

# Check if PASSWORD is loaded
if [ -z "$PASSWORD" ]; then
  echo "❌ PASSWORD is not set in .env"
  exit 1
fi

# Set PYTHONPATH to current directory
export PYTHONPATH="$(pwd)"
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Change permissions using sudo
echo "$PASSWORD" | sudo -S chmod -R 755 /home/$USER/Videos/tg-inventory-management-system/redis_data/
echo "$PASSWORD" | sudo -S chmod -R 755 /home/$USER/Videos/tg-inventory-management-system/redis_data/redis_data/
echo "$PASSWORD" | sudo -S chmod -R 755 /home/$USER/Videos/tg-inventory-management-system/postgres_data/
echo "$PASSWORD" | sudo -S chmod +x /home/$USER/Videos/tg-inventory-management-system/redis_data/redis-entrypoint.sh
echo "$PASSWORD" | sudo -S chmod 777 /home/$USER/Videos/tg-inventory-management-system/run-frontend.sh
echo "$PASSWORD" | sudo -S chmod 777 /home/$USER/Videos/tg-inventory-management-system/start-frontend.sh
echo "$PASSWORD" | sudo -S chmod 777 /home/$USER/Videos/tg-inventory-management-system/run-frontend.sh
echo "$PASSWORD" | sudo -S chmod 777 /home/$USER/Videos/tg-inventory-management-system/install_docker_setup.sh
echo "$PASSWORD" | sudo -S chmod 755 /home/$USER/Videos/tg-inventory-management-system/static/qrcodes/*
echo "$PASSWORD" | sudo -S chmod 755 /home/$USER/Videos/tg-inventory-management-system/static/barcodes/*

echo "✅ Permissions set successfully."
