@echo off
echo 🪝 Setting up Pre-commit Hooks
echo ===============================

REM Check virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install pre-commit
echo 📦 Installing pre-commit...
pip install pre-commit
if errorlevel 1 (
    echo ❌ Failed to install pre-commit
    pause
    exit /b 1
)

REM Install pre-commit hooks
echo 🪝 Installing pre-commit hooks...
pre-commit install
if errorlevel 1 (
    echo ❌ Failed to install pre-commit hooks
    pause
    exit /b 1
)

REM Test pre-commit on all files
echo 🧪 Testing pre-commit hooks...
pre-commit run --all-files
if errorlevel 1 (
    echo ⚠️  Pre-commit hooks found issues, but setup is complete
    echo 💡 Fix the issues and commit again
) else (
    echo ✅ Pre-commit hooks working correctly
)

echo.
echo 🎉 Pre-commit setup completed!
echo.
echo 📋 Next steps:
echo 1. Make a test commit to verify hooks work
echo 2. Run 'scripts\run_local_ci.bat' to test full pipeline
echo 3. Push to GitHub to test Actions
echo.
pause
