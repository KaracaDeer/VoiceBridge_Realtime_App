#!/bin/bash

echo "🪝 Setting up Pre-commit Hooks"
echo "==============================="

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Install pre-commit
echo "📦 Installing pre-commit..."
pip install pre-commit
if [ $? -ne 0 ]; then
    echo "❌ Failed to install pre-commit"
    exit 1
fi

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install pre-commit hooks"
    exit 1
fi

# Test pre-commit on all files
echo "🧪 Testing pre-commit hooks..."
pre-commit run --all-files
if [ $? -ne 0 ]; then
    echo "⚠️  Pre-commit hooks found issues, but setup is complete"
    echo "💡 Fix the issues and commit again"
else
    echo "✅ Pre-commit hooks working correctly"
fi

echo ""
echo "🎉 Pre-commit setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Make a test commit to verify hooks work"
echo "2. Run './scripts/run_local_ci.sh' to test full pipeline"
echo "3. Push to GitHub to test Actions"
echo ""
