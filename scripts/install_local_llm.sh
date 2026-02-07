#!/bin/bash
# Install Ollama for Local LLM Lyrics Generation
# This script downloads and installs Ollama, then pulls a model for lyrics generation

set -e

echo "============================================"
echo " Installing Local LLM for Lyrics Generation"
echo "============================================"
echo ""

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "[OK] Ollama is already installed!"
else
    echo "[1/3] Installing Ollama..."
    echo ""
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "Detected macOS"
        echo "Downloading Ollama for macOS..."
        curl -fsSL https://ollama.com/install.sh | sh
    else
        # Linux
        echo "Detected Linux"
        echo "Downloading Ollama for Linux..."
        curl -fsSL https://ollama.com/install.sh | sh
    fi
    
    echo ""
    echo "Starting Ollama service..."
    
    # Start Ollama service in background
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - Ollama runs as a service after installation
        sleep 3
    else
        # Linux - start as background process if not running
        if ! pgrep -x "ollama" > /dev/null; then
            nohup ollama serve > /dev/null 2>&1 &
            sleep 3
        fi
    fi
fi

echo ""
echo "[2/3] Ensuring Ollama service is running..."
sleep 2

echo ""
echo "[3/3] Downloading Llama 3.2 model for lyrics generation..."
echo "This may take several minutes depending on your internet speed."
echo "Model size: ~2GB"
echo ""

# Pull the Llama 3.2 3B model (good balance of quality and speed for lyrics)
ollama pull llama3.2:3b

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Failed to download model. Please ensure Ollama is running."
    echo "You can manually pull the model later with: ollama pull llama3.2:3b"
    exit 1
fi

echo ""
echo "============================================"
echo " Local LLM Installation Complete!"
echo "============================================"
echo ""
echo "Model installed: Llama 3.2 3B"
echo ""
echo "Next steps:"
echo "1. The Ollama service is now running in the background"
echo "2. In the app settings, select \"Local LLM\" as your provider"
echo "3. The model \"llama3.2:3b\" will be used automatically"
echo ""
echo "Alternative models you can install:"
echo "  - ollama pull mistral           (7B, creative writing)"
echo "  - ollama pull llama3.2          (3B, default version)"
echo "  - ollama pull phi3              (3.8B, fast and efficient)"
echo ""
echo "To see all installed models: ollama list"
echo "To remove a model: ollama rm model-name"
echo ""
echo "To ensure Ollama starts on system boot:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  macOS: Already configured as a service"
else
    echo "  Linux: sudo systemctl enable ollama"
fi
echo ""
