@echo off
echo VoiceBridge Quick Start
echo ========================
echo.

echo 1. Starting backend...
cd /d "%~dp0"
start "VoiceBridge Backend" cmd /k "python simple_main.py"

echo 2. Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo 3. Starting frontend...
cd frontend
start "VoiceBridge Frontend" cmd /k "npm start"

echo.
echo ✅ Both services are starting!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo To stop services, close the terminal windows.
echo.
pause
