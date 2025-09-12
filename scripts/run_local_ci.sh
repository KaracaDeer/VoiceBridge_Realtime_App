#!/bin/bash
# VoiceBridge Local CI/CD Pipeline Runner for Unix/Linux/macOS
# This script runs the same checks as GitHub Actions

set -e  # Exit on any error

echo ""
echo "============================================================"
echo "                VoiceBridge Local CI/CD Pipeline"
echo "============================================================"
echo "This script runs the same checks as GitHub Actions"
echo "Run this before pushing to catch issues early!"
echo "============================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed or not in PATH"
    echo "Please install Python3 and try again"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing CI dependencies..."
pip install --upgrade pip
pip install -r requirements-ci.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Run the local CI script
echo ""
echo "Running local CI pipeline..."
python scripts/local_ci.py

# Check the result
if [ $? -ne 0 ]; then
    echo ""
    echo "============================================================"
    echo "                    CI PIPELINE FAILED"
    echo "============================================================"
    echo "Some checks failed. Please fix them before pushing."
    echo ""
    echo "Common fixes:"
    echo "- Run: black src tests"
    echo "- Run: isort src tests"
    echo "- Fix flake8 errors"
    echo "- Fix mypy type errors"
    echo "============================================================"
    exit 1
else
    echo ""
    echo "============================================================"
    echo "                    CI PIPELINE PASSED"
    echo "============================================================"
    echo "All checks passed! Ready to push to GitHub."
    echo "============================================================"
    exit 0
fi