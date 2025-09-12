# Scripts Directory

This directory contains various utility scripts for development, deployment, and maintenance.

## Script Categories

### 🚀 **Quick Start & Setup**
- `quick-start.bat` - Windows quick start script for backend + frontend
- `start-backend.bat/sh` - Start backend services
- `start-frontend.bat/sh` - Start frontend development server
- `setup_ci.bat/sh` - Setup CI/CD environment
- `setup_precommit.bat/sh` - Install pre-commit hooks

### 🔧 **Development & Testing**
- `local_ci.py` - Run local CI tests
- `run_local_ci.bat/sh` - Execute local CI pipeline
- `quick_test.py` - Quick API and functionality tests
- `test_ci_setup.py` - Test CI environment setup
- `test_ci_docker.bat` - Test CI with Docker

### 🗄️ **Database & Storage**
- `setup_mysql.py` - MySQL database setup
- `setup_redis.bat` - Redis setup
- `setup_kafka.bat` - Kafka setup
- `setup_mlflow.bat` - MLFlow setup

### 🚀 **Deployment & Production**
- `deploy.sh` - Production deployment script
- `setup_production.bat` - Production environment setup
- `create_release.py` - Create release packages

### 📊 **Monitoring & Maintenance**
- `performance_monitor.py` - Performance monitoring
- `health_check.bat` - Health check script
- `check_errors.py` - Error checking utility

### 🔧 **Utilities**
- `generate_proto.py` - Generate protobuf files
- `start_all_services.bat` - Start all services at once

## Usage

Most scripts are designed to be run from the project root directory. Check individual script headers for specific usage instructions.

## Requirements

- Python 3.8+
- Node.js 16+ (for frontend scripts)
- Docker (for containerized scripts)
- Required Python packages (see requirements.txt)

## Examples

```bash
# Quick start (Windows)
./scripts/quick-start.bat

# Setup CI environment
./scripts/setup_ci.bat

# Run local tests
python scripts/local_ci.py

# Generate protobuf files
python scripts/generate_proto.py
```
