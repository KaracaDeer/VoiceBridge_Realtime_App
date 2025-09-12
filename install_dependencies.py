#!/usr/bin/env python3
"""
Dependency installation script for VoiceBridge API
"""

import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def install_package(package_name, description=None):
    """Install a Python package"""
    if description is None:
        description = f"Installing {package_name}"

    return run_command(f"pip install {package_name}", description)


def main():
    """Main installation function"""
    print("🚀 VoiceBridge API - Dependency Installation")
    print("=" * 50)

    # Check Python version
    print(f"Python version: {sys.version}")

    # Install missing packages
    packages = [
        ("aiokafka", "Installing aiokafka for Kafka streaming"),
        ("confluent-kafka", "Installing confluent-kafka for Kafka integration"),
        ("requests", "Installing requests for HTTP client"),
        ("websocket-client", "Installing websocket-client for WebSocket support"),
        ("grpcio-tools", "Installing grpcio-tools for gRPC support"),
    ]

    success_count = 0
    total_count = len(packages)

    for package, description in packages:
        if install_package(package, description):
            success_count += 1
        print()

    # Try to install from requirements.txt
    print("📦 Installing from requirements.txt...")
    if run_command("pip install -r requirements.txt", "Installing all requirements"):
        success_count += 1
    print()

    # Summary
    print("📊 Installation Summary")
    print("=" * 50)
    print(f"Successfully installed: {success_count}/{total_count + 1} packages")

    if success_count == total_count + 1:
        print("🎉 All dependencies installed successfully!")
        return True
    else:
        print("⚠️  Some dependencies failed to install. Check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
