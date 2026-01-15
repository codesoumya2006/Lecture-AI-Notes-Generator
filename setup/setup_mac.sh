#!/bin/bash

# Lecture Voice-to-Notes Generator - macOS Setup
# Auto-setup for macOS (Intel & Apple Silicon)

set -e

echo "======================================"
echo "Lecture Voice-to-Notes Generator"
echo "macOS Auto-Setup"
echo "======================================"
echo ""

# Check if Homebrew is installed
echo "[1/9] Checking Homebrew installation..."
if ! command -v brew &> /dev/null; then
    echo "⚠ Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
echo "✓ Homebrew ready"

# Install system dependencies
echo "[2/9] Installing system dependencies with Homebrew..."
brew install ffmpeg portaudio python@3.10 > /dev/null 2>&1 || true
echo "✓ System dependencies installed"

# Check Python
echo "[3/9] Checking Python installation..."
python3 --version
echo "✓ Python found"

# Upgrade pip
echo "[4/9] Upgrading pip..."
python3 -m pip install --upgrade pip --quiet --disable-pip-version-check
echo "✓ Pip upgraded"

# Create virtual environment
echo "[5/9] Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "[6/9] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install Python dependencies
echo "[7/9] Installing Python dependencies..."
pip install -r requirements.txt --quiet --disable-pip-version-check
echo "✓ Python dependencies installed"

# Check/Install Ollama
echo "[8/9] Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    ollamaVersion=$(ollama --version)
    echo "✓ Ollama found: $ollamaVersion"
else
    echo "⚠ Ollama not found. Installing with Homebrew..."
    brew install ollama > /dev/null 2>&1 || {
        echo "⚠ Homebrew install failed. Downloading Ollama directly..."
        curl -fsSL https://ollama.ai/install.sh | sh
    }
    echo "✓ Ollama installed"
fi

# Pull Ollama models
echo "[9/9] Pulling Ollama model (mistral)..."
if command -v ollama &> /dev/null; then
    ollama pull mistral > /dev/null 2>&1 &
    echo "✓ Mistral pull started (background)"
else
    echo "⚠ Ollama not available, skipping model pull"
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
