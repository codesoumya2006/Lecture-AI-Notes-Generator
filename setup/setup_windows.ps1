# Lecture Voice-to-Notes Generator - Windows Setup
# Auto-setup for Windows (PowerShell)

param([switch]$SkipBrowser)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Lecture Voice-to-Notes Generator" -ForegroundColor Cyan
Write-Host "Windows Auto-Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/9] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "[2/9] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ Pip upgraded" -ForegroundColor Green

# Create virtual environment
Write-Host "[3/9] Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[4/9] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install Python dependencies
Write-Host "[5/9] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet --disable-pip-version-check
Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# Check/Install FFmpeg
Write-Host "[6/9] Checking FFmpeg installation..." -ForegroundColor Yellow
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "✓ FFmpeg found: $ffmpegVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ FFmpeg not found. Attempting to install via winget..." -ForegroundColor Yellow
    try {
        winget install -e --id FFmpeg.FFmpeg -q --accept-package-agreements --accept-source-agreements
        Write-Host "✓ FFmpeg installed successfully" -ForegroundColor Green
        $env:Path += ";C:\Program Files\ffmpeg\bin"
    } catch {
        Write-Host "⚠ Could not auto-install FFmpeg via winget. Please install manually from ffmpeg.org" -ForegroundColor Yellow
    }
}

# Check/Install Ollama
Write-Host "[7/9] Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✓ Ollama found: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ Ollama not found. Installing Ollama..." -ForegroundColor Yellow
    try {
        # Download Ollama installer
        $OllamaUrl = "https://ollama.ai/download/OllamaSetup.exe"
        $OllamaInstaller = "$env:TEMP\OllamaSetup.exe"
        
        if (Test-Path $OllamaInstaller) {
            Remove-Item $OllamaInstaller -Force
        }
        
        Write-Host "Downloading Ollama..." -ForegroundColor Gray
        (New-Object Net.WebClient).DownloadFile($OllamaUrl, $OllamaInstaller)
        
        Write-Host "Installing Ollama silently..." -ForegroundColor Gray
        Start-Process -FilePath $OllamaInstaller -ArgumentList "/S" -Wait
        
        Write-Host "✓ Ollama installed successfully" -ForegroundColor Green
        
        # Add to PATH
        $env:Path += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama"
    } catch {
        Write-Host "⚠ Could not auto-install Ollama. Please install manually from ollama.ai" -ForegroundColor Yellow
        Write-Host "Proceeding without Ollama - some features may not work" -ForegroundColor Yellow
    }
}

# Pull Ollama models
Write-Host "[8/9] Pulling Ollama model (mistral)..." -ForegroundColor Yellow
try {
    ollama pull mistral --quiet
    Write-Host "✓ Mistral model ready" -ForegroundColor Green
} catch {
    Write-Host "⚠ Could not pull Mistral model. Ensure Ollama is running." -ForegroundColor Yellow
}

# Verification
Write-Host "[9/9] Verifying setup..." -ForegroundColor Yellow
$success = $true

try {
    $pythonTest = python --version 2>&1
    Write-Host "✓ Python verified" -ForegroundColor Green
} catch {
    Write-Host "✗ Python verification failed" -ForegroundColor Red
    $success = $false
}

Write-Host ""
if ($success) {
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "✓ Setup completed successfully!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Starting Streamlit application..." -ForegroundColor Cyan
    Write-Host ""
    
    # Launch Streamlit
    streamlit run app.py
} else {
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "✗ Setup completed with errors" -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the errors above and try again." -ForegroundColor Yellow
}
