#!/bin/bash

# VoiceBridge API Postman Setup Script
# This script helps set up the Postman collection and environments

echo "========================================"
echo "VoiceBridge API Postman Setup"
echo "========================================"
echo

# Check if Postman is installed
echo "Checking for Postman installation..."
if ! command -v postman &> /dev/null; then
    echo "Postman is not installed or not in PATH."
    echo "Please install Postman from: https://www.postman.com/downloads/"
    echo
    read -p "Press Enter to continue..."
    exit 1
fi

echo "Postman found!"
echo

# Check if Newman is installed
echo "Checking for Newman (Postman CLI)..."
if ! command -v newman &> /dev/null; then
    echo "Newman is not installed. Installing Newman..."
    npm install -g newman
    if [ $? -ne 0 ]; then
        echo "Failed to install Newman. Please install manually: npm install -g newman"
        read -p "Press Enter to continue..."
        exit 1
    fi
    echo "Newman installed successfully!"
else
    echo "Newman found!"
fi
echo

# Create test reports directory
echo "Creating test reports directory..."
mkdir -p test_reports
echo "Test reports directory created!"
echo

# Display available commands
echo "========================================"
echo "Available Commands:"
echo "========================================"
echo
echo "1. Import Collection and Environment:"
echo "   - Open Postman"
echo "   - Click Import"
echo "   - Select: VoiceBridge_API_Collection.json"
echo "   - Select environment file (Development/Production/Testing)"
echo
echo "2. Run Tests with Newman:"
echo "   newman run VoiceBridge_API_Collection.json -e VoiceBridge_Development_Environment.json"
echo
echo "3. Generate HTML Report:"
echo "   newman run VoiceBridge_API_Collection.json -e VoiceBridge_Development_Environment.json --reporters html --reporter-html-export test_reports/report.html"
echo
echo "4. Run Tests with Custom Script:"
echo "   node test_scripts/run_tests.js"
echo

# Ask user what they want to do
echo "========================================"
echo "What would you like to do?"
echo "========================================"
echo
echo "1. Run basic API tests"
echo "2. Generate test report"
echo "3. Open Postman"
echo "4. Exit"
echo

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo
        echo "Running basic API tests..."
        newman run VoiceBridge_API_Collection.json -e VoiceBridge_Development_Environment.json
        echo
        echo "Tests completed!"
        read -p "Press Enter to continue..."
        ;;
    2)
        echo
        echo "Generating test report..."
        newman run VoiceBridge_API_Collection.json -e VoiceBridge_Development_Environment.json --reporters html --reporter-html-export test_reports/report.html
        echo
        echo "Report generated: test_reports/report.html"
        read -p "Press Enter to continue..."
        ;;
    3)
        echo
        echo "Opening Postman..."
        postman &
        echo
        echo "Please import the collection and environment files manually."
        read -p "Press Enter to continue..."
        ;;
    4)
        echo
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo
        echo "Invalid choice. Please run the script again."
        read -p "Press Enter to continue..."
        exit 1
        ;;
esac

echo
echo "Setup completed successfully!"
read -p "Press Enter to continue..."
