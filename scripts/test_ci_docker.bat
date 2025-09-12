@echo off
echo 🐳 Testing CI/CD with Docker
echo =============================

REM Check if Docker is running
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not running
    echo Please install Docker Desktop and start it
    pause
    exit /b 1
)

echo ✅ Docker is available

REM Build Docker image
echo 🔨 Building Docker image...
docker build -t voicebridge:ci-test .
if errorlevel 1 (
    echo ❌ Docker build failed
    pause
    exit /b 1
)

echo ✅ Docker image built successfully

REM Run CI tests in Docker container
echo 🧪 Running CI tests in Docker container...
docker run --rm -v "%cd%":/app -w /app voicebridge:ci-test python scripts/local_ci.py
if errorlevel 1 (
    echo ❌ CI tests failed in Docker
    pause
    exit /b 1
)

echo ✅ All CI tests passed in Docker environment
echo 🎉 Your code is ready for GitHub Actions!
pause
