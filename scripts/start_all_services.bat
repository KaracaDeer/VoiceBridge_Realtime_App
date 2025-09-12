@echo off
REM VoiceBridge Start All Services Script
REM Starts all required services for VoiceBridge development
REM Usage: scripts\start_all_services.bat

echo Starting all VoiceBridge services...

REM Check if .env exists
if not exist ".env" (
    echo .env file not found. Running production setup...
    call scripts\setup_production.bat
    echo.
    echo Please update .env with your API keys before continuing.
    pause
)

echo Starting Redis...
start "Redis" cmd /k "redis-server --port 6379"

REM Wait for Redis to start
timeout /t 5 /nobreak

echo Starting MLflow...
start "MLflow" cmd /k "mlflow server --backend-store-uri sqlite:///mlflow_data/mlflow.db --default-artifact-root mlflow_data/artifacts --host 0.0.0.0 --port 5000"

REM Wait for MLflow to start
timeout /t 5 /nobreak

echo Starting Kafka (if available)...
if exist "kafka_data\kafka_2.13-2.8.1" (
    start "Zookeeper" cmd /k "cd kafka_data\kafka_2.13-2.8.1\bin\windows && zookeeper-server-start.bat ..\..\config\zookeeper.properties"
    timeout /t 10 /nobreak
    start "Kafka" cmd /k "cd kafka_data\kafka_2.13-2.8.1\bin\windows && kafka-server-start.bat ..\..\config\server.properties"
) else (
    echo Kafka not found. Run scripts\setup_kafka.bat first.
)

echo.
echo All services started!
echo.
echo Service URLs:
echo - Redis: localhost:6379
echo - MLflow UI: http://localhost:5000
echo - VoiceBridge API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo.
echo Starting VoiceBridge API...
python main.py
