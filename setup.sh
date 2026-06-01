#!/bin/bash
# Local AI Security Lab Setup Script
# For authorized security research only

set -e

echo "=== Local AI Security Lab Setup ==="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script should be run as root or with sudo"
   exit 1
fi

# Detect OS
if [[ -f /etc/debian_version ]]; then
    OS="debian"
elif [[ -f /etc/redhat-release ]]; then
    OS="redhat"
elif [[ -f /etc/arch-release ]]; then
    OS="arch"
else
    OS="unknown"
fi

echo "Detected OS: $OS"

# Update system
echo ""
echo "=== Updating system ==="
if [[ "$OS" == "debian" ]]; then
    apt update && apt upgrade -y
elif [[ "$OS" == "redhat" ]]; then
    yum update -y
fi

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo ""
    echo "=== Installing Docker ==="
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
fi

# Install Ollama
if ! command -v ollama &> /dev/null; then
    echo ""
    echo "=== Installing Ollama ==="
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Start Ollama service
echo ""
echo "=== Starting Ollama ==="
systemctl enable --now ollama 2>/dev/null || echo "Ollama service not available, starting manually..."

# Pull recommended models
echo ""
echo "=== Pulling AI Models ==="
echo "This may take several minutes depending on your connection..."

ollama pull llama3.2 2>/dev/null || echo "Failed to pull llama3.2"
ollama pull codellama 2>/dev/null || echo "Failed to pull codellama"

# Setup OpenWebUI with Docker
echo ""
echo "=== Setting up OpenWebUI ==="

docker pull ghcr.io/open-webui/open-webui:main

docker stop open-webui 2>/dev/null || true
docker rm open-webui 2>/dev/null || true

docker run -d \
    --name open-webui \
    --network host \
    -v open-webui:/app/backend/data \
    -e OLLAMA_BASE_URL=http://127.0.0.1:11434 \
    -e WEBUI_SECRET_KEY="" \
    ghcr.io/open-webui/open-webui:main

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Services:"
echo "  OpenWebUI: http://localhost:8080"
echo "  Ollama API: http://localhost:11434"
echo ""
echo "Available models:"
ollama list
echo ""
echo "To use: Open http://localhost:8080 in your browser"