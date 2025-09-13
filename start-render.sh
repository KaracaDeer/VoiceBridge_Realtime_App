#!/bin/bash

# VoiceBridge Render Startup Script
echo "Starting VoiceBridge on Render..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p storage
mkdir -p mlflow_data

# Set environment variables for production
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export API_DEBUG=false
export DATABASE_DEMO_MODE=true

# Start the application
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
