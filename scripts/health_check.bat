@echo off
REM VoiceBridge Health Check Script
REM Checks the status of all VoiceBridge services
REM Usage: scripts\health_check.bat

echo VoiceBridge Health Check
echo =======================

echo.
echo Checking Redis...
redis-cli ping >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo ✓ Redis is running
) else (
    echo ✗ Redis is not running
)

echo.
echo Checking MLflow...
curl -s http://localhost:5000/health >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo ✓ MLflow is running
) else (
    echo ✗ MLflow is not running
)

echo.
echo Checking VoiceBridge API...
curl -s http://localhost:8000/health >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo ✓ VoiceBridge API is running
) else (
    echo ✗ VoiceBridge API is not running
)

echo.
echo Checking Kafka (if available)...
netstat -an | findstr :9092 >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo ✓ Kafka is running
) else (
    echo ✗ Kafka is not running (optional)
)

echo.
echo Health check complete!
echo.
echo To start all services, run: scripts\start_all_services.bat
