@echo off
echo Starting VoiceBridge Frontend...
echo.

cd frontend

echo Checking if Node.js is available...
node --version
if errorlevel 1 (
    echo Node.js is not installed or not in PATH!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Installing dependencies...
call npm install
if errorlevel 1 (
    echo Error installing dependencies!
    pause
    exit /b 1
)

echo.
echo Starting development server...
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop the server
echo.

call npm start

pause
