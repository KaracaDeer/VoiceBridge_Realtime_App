# VoiceBridge API Makefile
# Provides convenient commands for development, testing, and deployment

.PHONY: help install dev build test lint format clean docker-up docker-down health monitor quick-start

# Default target
help: ## Show this help message
	@echo "VoiceBridge API - Available Commands:"
	@echo "====================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install all dependencies (Python + Node.js)
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing Node.js dependencies..."
	cd frontend && npm install
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Installation completed!"

install-python: ## Install Python dependencies only
	pip install -r requirements.txt

install-frontend: ## Install frontend dependencies only
	cd frontend && npm install

# Development
dev: ## Start development servers (backend + frontend)
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Press Ctrl+C to stop"
	@trap 'kill %1; kill %2' INT; \
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload & \
	cd frontend && npm start & \
	wait

backend: ## Start backend server only
	@echo "Starting backend server..."
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

frontend: ## Start frontend server only
	@echo "Starting frontend server..."
	@echo "Frontend: http://localhost:3000"
	cd frontend && npm start

# Building
build: ## Build production version
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "Build completed!"

build-frontend: ## Build frontend only
	cd frontend && npm run build

# Testing
test: ## Run all tests
	@echo "Running Python tests..."
	pytest tests/ -v --tb=short
	@echo "Running frontend tests..."
	cd frontend && npm test -- --coverage --watchAll=false

test-python: ## Run Python tests only
	pytest tests/ -v --tb=short

test-frontend: ## Run frontend tests only
	cd frontend && npm test -- --coverage --watchAll=false

test-integration: ## Run integration tests
	pytest tests/test_integration.py -v --tb=short

test-websocket: ## Run WebSocket tests
	pytest tests/test_websocket_stream.py -v --tb=short

test-ml: ## Run ML model tests
	pytest tests/test_ml_models.py -v --tb=short

# Code Quality
lint: ## Run linting for all code
	@echo "Linting Python code..."
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503,E501
	@echo "Linting frontend code..."
	cd frontend && npm run lint

lint-python: ## Run Python linting only
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503,E501

lint-frontend: ## Run frontend linting only
	cd frontend && npm run lint

lint-fix: ## Fix linting issues automatically
	@echo "Fixing Python code formatting..."
	black src/ tests/ --line-length=88
	isort src/ tests/ --profile=black --line-length=88
	@echo "Fixing frontend code formatting..."
	cd frontend && npm run lint:fix

format: ## Format all code
	@echo "Formatting Python code..."
	black src/ tests/ --line-length=88
	isort src/ tests/ --profile=black --line-length=88
	@echo "Formatting frontend code..."
	cd frontend && npm run format

format-python: ## Format Python code only
	black src/ tests/ --line-length=88
	isort src/ tests/ --profile=black --line-length=88

format-frontend: ## Format frontend code only
	cd frontend && npm run format

# Type Checking
type-check: ## Run type checking
	@echo "Type checking Python code..."
	mypy src/ --ignore-missing-imports
	@echo "Type checking frontend code..."
	cd frontend && npm run type-check

type-check-python: ## Run Python type checking only
	mypy src/ --ignore-missing-imports

type-check-frontend: ## Run frontend type checking only
	cd frontend && npm run type-check

# Security
security: ## Run security checks
	@echo "Running security checks..."
	bandit -r src/ -f json -o bandit-report.json
	safety check --json --output safety-report.json
	@echo "Security reports generated: bandit-report.json, safety-report.json"

# Pre-commit
pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

# Docker
docker-up: ## Start Docker services
	@echo "Starting Docker services..."
	docker-compose up -d
	@echo "Services started! Check status with: make docker-status"

docker-down: ## Stop Docker services
	@echo "Stopping Docker services..."
	docker-compose down

docker-build: ## Build Docker images
	@echo "Building Docker images..."
	docker-compose build

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-status: ## Show Docker service status
	docker-compose ps

docker-prod: ## Start production Docker services
	@echo "Starting production Docker services..."
	docker-compose -f docker-compose.production.yml up -d

docker-monitoring: ## Start monitoring Docker services
	@echo "Starting monitoring services..."
	docker-compose -f docker-compose.monitoring.yml up -d

# Monitoring
health: ## Check service health
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "Backend not running"
	@curl -s http://localhost:3000 | head -1 || echo "Frontend not running"

monitor: ## Start performance monitoring
	@echo "Starting performance monitoring..."
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001"
	@echo "MLflow: http://localhost:5000"
	@echo "Flower (Celery): http://localhost:5555"
	docker-compose -f docker-compose.monitoring.yml up -d

# Database
db-setup: ## Setup databases
	@echo "Setting up databases..."
	python scripts/setup_mysql.py
	python scripts/setup_redis.py

# Services
start-kafka: ## Start Kafka services
	@echo "Starting Kafka..."
	python scripts/setup_kafka.py

start-mlflow: ## Start MLflow tracking
	@echo "Starting MLflow..."
	python scripts/start_mlflow.py

# CI/CD
ci: ## Run CI/CD pipeline locally
	@echo "Running CI/CD pipeline..."
	python scripts/local_ci.py

ci-test: ## Run CI tests
	@echo "Running CI tests..."
	python scripts/test_ci_setup.py

# Cleanup
clean: ## Clean cache and build files
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf build/ node_modules/.cache/ 2>/dev/null || true
	@echo "Cleanup completed!"

clean-docker: ## Clean Docker containers and images
	@echo "Cleaning Docker..."
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

# Quick Start
quick-start: install ## Complete setup and start development
	@echo "Quick start: Setting up VoiceBridge API..."
	@echo "1. Installing dependencies..."
	@echo "2. Starting services..."
	@echo "3. Opening application..."
	@echo ""
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Press Ctrl+C to stop all services"
	@trap 'kill %1; kill %2' INT; \
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload & \
	cd frontend && npm start & \
	wait

# Documentation
docs: ## Generate documentation
	@echo "Generating documentation..."
	@echo "API documentation available at: http://localhost:8000/docs"
	@echo "OpenAPI schema available at: http://localhost:8000/openapi.json"

# Release
release: ## Create a new release
	@echo "Creating release..."
	python scripts/create_release.py

# Development helpers
logs: ## Show application logs
	@echo "Showing application logs..."
	@tail -f logs/*.log 2>/dev/null || echo "No log files found"

check-deps: ## Check for outdated dependencies
	@echo "Checking Python dependencies..."
	pip list --outdated
	@echo "Checking frontend dependencies..."
	cd frontend && npm outdated

update-deps: ## Update dependencies
	@echo "Updating Python dependencies..."
	pip install --upgrade -r requirements.txt
	@echo "Updating frontend dependencies..."
	cd frontend && npm update

# Environment setup
env-setup: ## Setup environment variables
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from template..."; \
		cp .env.example .env 2>/dev/null || echo "No .env.example found"; \
		echo "Please edit .env file with your configuration"; \
	else \
		echo ".env file already exists"; \
	fi

# Performance testing
perf-test: ## Run performance tests
	@echo "Running performance tests..."
	python scripts/performance_monitor.py

# Backup
backup: ## Backup important data
	@echo "Creating backup..."
	@mkdir -p backups
	@tar -czf backups/voicebridge-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz \
		--exclude=node_modules \
		--exclude=__pycache__ \
		--exclude=.git \
		--exclude=logs \
		--exclude=backups \
		.
	@echo "Backup created in backups/ directory"