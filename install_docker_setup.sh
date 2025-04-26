#!/bin/bash

# 🔐 Your sudo password (use with caution)
password="12345six"

# Exit immediately if any command fails
set -e

echo "🔧 Installing base packages..."
echo "$password" | sudo -S apt update
echo "$password" | sudo -S apt install -y git tree ca-certificates curl python3.12-venv -y

echo "🧹 Removing conflicting Docker-related packages..."
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do 
  echo "$password" | sudo -S apt-get remove -y $pkg || true
done

echo "🔐 Adding Docker’s official GPG key..."
echo "$password" | sudo -S install -m 0755 -d /etc/apt/keyrings
echo "$password" | sudo -S curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
echo "$password" | sudo -S chmod a+r /etc/apt/keyrings/docker.asc

echo "📦 Setting up Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  echo "$password" | sudo -S tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "🔄 Updating package lists and installing Docker + Compose plugin..."
echo "$password" | sudo -S apt-get update
echo "$password" | sudo -S apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

echo "👤 Adding current user to Docker group..."
echo "$password" | sudo -S usermod -aG docker $USER

echo "✅ Setup complete!"
echo "🚨 Please log out and log back in for Docker group permissions to apply."

echo "$password" | sudo -S apt install python-is-python3 -y
echo "$password" | sudo -S apt update
echo "$password" | sudo -S apt install python3-tk -y
echo "$password" | sudo -S  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
echo "$password" | sudo -S  unzip awscliv2.zip
echo "$password" | sudo -S ./aws/install -y
echo "$password" | sudo -S apt-get update -y
echo "$password" | sudo -S apt-get upgrade -y
