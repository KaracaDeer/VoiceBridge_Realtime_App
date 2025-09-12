@echo off
REM VoiceBridge API Postman Setup Script
REM This script helps set up the Postman collection and environments

echo ========================================
echo VoiceBridge API Postman Setup
echo ========================================
echo.

REM Check if Postman is installed
echo Checking for Postman installation...
where postman >nul 2>nul
if %errorlevel% neq 0 (
    echo Postman is not installed or not in PATH.
    echo Please install Postman from: https://www.postman.com/downloads/
    echo.
    pause
    exit /b 1
)

echo Postman found!
echo.

REM Check if Newman is installed
echo Checking for Newman (Postman CLI)...
where newman >nul 2>nul
if %errorlevel% neq 0 (
    echo Newman is not installed. Installing Newman...
    npm install -g newman
    if %errorlevel% neq 0 (
        echo Failed to install Newman. Please install manually: npm install -g newman
        pause
        exit /b 1
    )
    echo Newman installed successfully!
) else (
    echo Newman found!
)
echo.

REM Create test reports directory
echo Creating test reports directory...
if not exist "test_reports" mkdir test_reports
echo Test reports directory created!
echo.

REM Display available commands
echo ========================================
echo Available Commands:
echo ========================================
echo.
echo 1. Import Collection and Environment:
echo    - Open Postman
echo    - Click Import
echo    - Select: VoiceBridge_API_Collection.json
echo    - Select environment file (Development/Production/Testing)
echo.
echo 2. Run Tests with Newman:
echo    newman run VoiceBridge_API_Collection.json -e VoiceBridge_Development_Environment.json
echo.
echo 3. Generate HTML Report:
echo    newman run VoiceBridge_API_Collection.json -e VoiceBridge_Development_Environment.json --reporters html --reporter-html-export test_reports/report.html
echo.
echo 4. Run Tests with Custom Script:
echo    node test_scripts/run_tests.js
echo.

REM Ask user what they want to do
echo ========================================
echo What would you like to do?
echo ========================================
echo.
echo 1. Run basic API tests
echo 2. Generate test report
echo 3. Open Postman
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Running basic API tests...
    newman run VoiceBridge_API_Collection.json -e VoiceBridge_Development_Environment.json
    echo.
    echo Tests completed!
    pause
) else if "%choice%"=="2" (
    echo.
    echo Generating test report...
    newman run VoiceBridge_API_Collection.json -e VoiceBridge_Development_Environment.json --reporters html --reporter-html-export test_reports/report.html
    echo.
    echo Report generated: test_reports/report.html
    pause
) else if "%choice%"=="3" (
    echo.
    echo Opening Postman...
    start postman
    echo.
    echo Please import the collection and environment files manually.
    pause
) else if "%choice%"=="4" (
    echo.
    echo Goodbye!
    exit /b 0
) else (
    echo.
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
pause
