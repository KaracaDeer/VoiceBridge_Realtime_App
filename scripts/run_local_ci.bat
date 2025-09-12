@echo off
REM VoiceBridge Local CI/CD Pipeline Runner for Windows
REM This script runs the same checks as GitHub Actions

echo.
echo ============================================================
echo                VoiceBridge Local CI/CD Pipeline
echo ============================================================
echo This script runs the same checks as GitHub Actions
echo Run this before pushing to catch issues early!
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing CI dependencies...
pip install --upgrade pip
pip install -r requirements-ci.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Run the local CI script
echo.
echo Running local CI pipeline...
python scripts/local_ci.py

REM Check the result
if errorlevel 1 (
    echo.
    echo ============================================================
    echo                    CI PIPELINE FAILED
    echo ============================================================
    echo Some checks failed. Please fix them before pushing.
    echo.
    echo Common fixes:
    echo - Run: black src tests
    echo - Run: isort src tests
    echo - Fix flake8 errors
    echo - Fix mypy type errors
    echo ============================================================
    pause
    exit /b 1
) else (
    echo.
    echo ============================================================
    echo                    CI PIPELINE PASSED
    echo ============================================================
    echo All checks passed! Ready to push to GitHub.
    echo ============================================================
    pause
    exit /b 0
)