@echo off
echo 🚀 Setting up CI/CD Environment for Windows
echo ================================================

echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo 🔧 Installing pre-commit...
pip install pre-commit
if %errorlevel% neq 0 (
    echo ❌ Failed to install pre-commit
    pause
    exit /b 1
)

echo.
echo 🪝 Installing pre-commit hooks...
pre-commit install
if %errorlevel% neq 0 (
    echo ❌ Failed to install pre-commit hooks
    pause
    exit /b 1
)

echo.
echo 🧪 Testing pre-commit hooks...
pre-commit run --all-files
if %errorlevel% neq 0 (
    echo ⚠️  Pre-commit hooks found issues, but setup is complete
)

echo.
echo 🎉 CI/CD setup completed!
echo.
echo 📋 Next steps:
echo 1. Run 'python scripts/local_ci.py' to test the full pipeline
echo 2. Make a test commit to verify pre-commit hooks work
echo 3. Push to GitHub to test Actions
echo.
pause
