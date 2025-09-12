@echo off
echo Starting VoiceBridge Backend...
echo.

echo Checking Python dependencies...
pip show fastapi > nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error installing dependencies!
        pause
        exit /b 1
    )
)

echo.
echo Starting FastAPI server...
echo Backend will be available at: http://localhost:8000
echo.

python main.py

pause
