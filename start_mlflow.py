#!/usr/bin/env python3
"""
MLFlow Server Startup Script
"""
import os
import subprocess
import sys


def start_mlflow_server():
    """Start MLFlow server"""
    print("🚀 Starting MLFlow Server...")

    # Create mlruns directory if it doesn't exist
    os.makedirs("mlruns", exist_ok=True)

    try:
        # Start MLFlow server
        cmd = [
            sys.executable,
            "-m",
            "mlflow",
            "server",
            "--host",
            "0.0.0.0",
            "--port",
            "5000",
            "--backend-store-uri",
            "sqlite:///mlflow.db",
            "--default-artifact-root",
            "./mlruns",
        ]

        print(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting MLFlow server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 MLFlow server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    start_mlflow_server()
