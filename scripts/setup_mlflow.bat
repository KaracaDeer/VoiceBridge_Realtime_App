@echo off
echo Setting up MLflow server for VoiceBridge...

REM Create MLflow directory
if not exist "mlflow_data" mkdir mlflow_data

REM Start MLflow server
echo Starting MLflow server on port 5000...
mlflow server --backend-store-uri sqlite:///mlflow_data/mlflow.db --default-artifact-root mlflow_data/artifacts --host 0.0.0.0 --port 5000

echo MLflow server started at http://localhost:5000
echo You can access the MLflow UI in your browser
