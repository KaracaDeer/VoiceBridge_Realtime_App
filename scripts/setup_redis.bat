@echo off
echo Setting up Redis for VoiceBridge...

REM Check if Redis is already installed
where redis-server >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo Redis is already installed
    goto :start_redis
)

echo Redis not found. Installing Redis...

REM Download Redis for Windows
echo Downloading Redis for Windows...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.msi' -OutFile 'redis-installer.msi'"

REM Install Redis
echo Installing Redis...
msiexec /i redis-installer.msi /quiet

REM Wait for installation
timeout /t 10 /nobreak

REM Clean up installer
del redis-installer.msi

:start_redis
echo Starting Redis server...
redis-server --port 6379 --daemonize yes

echo Redis server started on port 6379
echo You can test it with: redis-cli ping
