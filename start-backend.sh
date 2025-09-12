#!/bin/bash

echo "Starting VoiceBridge Backend..."
echo

echo "Checking Python dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error installing dependencies!"
        exit 1
    fi
fi

echo
echo "Starting FastAPI server..."
echo "Backend will be available at: http://localhost:8000"
echo

python main.py
