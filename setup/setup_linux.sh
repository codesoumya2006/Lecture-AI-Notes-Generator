#!/bin/bash

# Lecture Voice-to-Notes Generator - Linux Setup
# Auto-setup for Linux (Debian/Ubuntu/Fedora)

set -e

echo "======================================"
echo "Lecture Voice-to-Notes Generator"
echo "Linux Auto-Setup"
echo "======================================"
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect Linux distribution"
    exit 1
fi

# Install system dependencies based on OS
echo "[1/9] Installing system dependencies..." 
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq ffmpeg portaudio19-dev python3-dev python3-pip python3-venv > /dev/null 2>&1
elif [ "$OS" = "fedora" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    sudo dnf install -y -q ffmpeg portaudio-devel python3-devel python3-pip > /dev/null 2>&1
else
    echo "⚠ Unsupported Linux distribution: $OS"
    echo "Please install ffmpeg, python3-dev, python3-pip, and portaudio19-dev manually"
fi
echo "✓ System dependencies installed"

# Check Python
echo "[2/9] Checking Python installation..."
python3 --version
echo "✓ Python found"

# Upgrade pip
echo "[3/9] Upgrading pip..."
python3 -m pip install --upgrade pip --quiet --disable-pip-version-check
echo "✓ Pip upgraded"

# Create virtual environment
echo "[4/9] Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "[5/9] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install Python dependencies
echo "[6/9] Installing Python dependencies..."
pip install -r requirements.txt --quiet --disable-pip-version-check
echo "✓ Python dependencies installed"

# Check/Install Ollama
echo "[7/9] Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    ollamaVersion=$(ollama --version)
    echo "✓ Ollama found: $ollamaVersion"
else
    echo "⚠ Ollama not found. Installing..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "✓ Ollama installed"
fi

# Pull Ollama models
echo "[8/9] Pulling Ollama model (mistral)..."
if command -v ollama &> /dev/null; then
    ollama pull mistral > /dev/null 2>&1 &
    echo "✓ Mistral pull started (background)"
else
    echo "⚠ Ollama not available, skipping model pull"
fi

# Verification
echo "[9/9] Verifying setup..."
if python3 --version > /dev/null 2>&1; then
    echo "✓ Python verified"
else
    echo "✗ Python verification failed"
    exit 1
fi

echo ""
echo "======================================"
echo "✓ Setup completed successfully!"
echo "======================================"
echo ""
echo "Starting Streamlit application..."
echo ""

# Launch Streamlit
streamlit run app.py
