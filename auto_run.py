#!/usr/bin/env python3
"""
Auto-run script for Lecture Voice-to-Notes Generator.
Handles platform detection and setup automation.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def print_header():
    print("\n" + "=" * 60)
    print("Lecture Voice-to-Notes Generator - Auto Setup")
    print("=" * 60 + "\n")

def detect_platform():
    """Detect operating system."""
    system = platform.system()
    return system

def run_setup_windows():
    """Run Windows PowerShell setup."""
    print("🪟 Detected Windows")
    print("Running PowerShell setup script...\n")
    
    setup_script = Path(__file__).parent / "setup" / "setup_windows.ps1"
    
    if not setup_script.exists():
        print(f"❌ Setup script not found: {setup_script}")
        return False
    
    try:
        # Run PowerShell script
        cmd = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", str(setup_script)
        ]
        
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Error running setup: {e}")
        return False

def run_setup_linux():
    """Run Linux Bash setup."""
    print("🐧 Detected Linux")
    print("Running Bash setup script...\n")
    
    setup_script = Path(__file__).parent / "setup" / "setup_linux.sh"
    
    if not setup_script.exists():
        print(f"❌ Setup script not found: {setup_script}")
        return False
    
    try:
        # Make script executable
        os.chmod(setup_script, 0o755)
        
        # Run bash script
        result = subprocess.run(
            ["bash", str(setup_script)],
            cwd=Path(__file__).parent
        )
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Error running setup: {e}")
        return False

def run_setup_mac():
    """Run macOS setup."""
    print("🍎 Detected macOS")
    print("Running Bash setup script...\n")
    
    setup_script = Path(__file__).parent / "setup" / "setup_mac.sh"
    
    if not setup_script.exists():
        print(f"❌ Setup script not found: {setup_script}")
        return False
    
    try:
        # Make script executable
        os.chmod(setup_script, 0o755)
        
        # Run bash script
        result = subprocess.run(
            ["bash", str(setup_script)],
            cwd=Path(__file__).parent
        )
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Error running setup: {e}")
        return False

def main():
    print_header()
    
    # Detect platform
    system = detect_platform()
    
    # Run appropriate setup
    if system == "Windows":
        success = run_setup_windows()
    elif system == "Linux":
        success = run_setup_linux()
    elif system == "Darwin":  # macOS
        success = run_setup_mac()
    else:
        print(f"❌ Unsupported platform: {system}")
        return 1
    
    if success:
        print("\n✓ Setup completed successfully!")
        return 0
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
