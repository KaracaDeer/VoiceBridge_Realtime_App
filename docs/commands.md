# Command Reference

## Development Commands

### Installation & Setup
```bash
# Install all dependencies (Python + Node.js)
make install

# Install Python dependencies only
make install-python

# Install frontend dependencies only
make install-frontend

# Setup pre-commit hooks
make pre-commit-install
```

### Development Servers
```bash
# Start both backend and frontend
make dev

# Start backend only
make backend

# Start frontend only
make frontend

# Quick start (install + start)
make quick-start
```

### Building
```bash
# Build production version
make build

# Build frontend only
make build-frontend
```

## Testing Commands

### Test Execution
```bash
# Run all tests (Python + frontend)
make test

# Run Python tests only
make test-python

# Run frontend tests only
make test-frontend

# Run integration tests
make test-integration

# Run WebSocket tests
make test-websocket

# Run ML model tests
make test-ml
```

### Test Coverage
```bash
# Run tests with coverage
make test-coverage

# Generate coverage report
make coverage-report
```

## Code Quality Commands

### Linting
```bash
# Run linting for all code
make lint

# Run Python linting only
make lint-python

# Run frontend linting only
make lint-frontend

# Fix linting issues automatically
make lint-fix
```

### Formatting
```bash
# Format all code
make format

# Format Python code only
make format-python

# Format frontend code only
make format-frontend
```

### Type Checking
```bash
# Run type checking
make type-check

# Run Python type checking only
make type-check-python

# Run frontend type checking only
make type-check-frontend
```

### Security
```bash
# Run security checks
make security

# Run bandit security scan
make bandit

# Run safety dependency check
make safety
```

## Docker Commands

### Docker Services
```bash
# Start Docker services
make docker-up

# Stop Docker services
make docker-down

# Build Docker images
make docker-build

# View Docker logs
make docker-logs

# Check Docker service status
make docker-status
```

### Docker Deployment
```bash
# Start production Docker stack
make docker-prod

# Start monitoring services
make docker-monitoring

# Clean Docker containers and images
make clean-docker
```

## Monitoring Commands

### Health & Status
```bash
# Check service health
make health

# Start performance monitoring
make monitor

# View application logs
make logs
```

### Database
```bash
# Setup databases
make db-setup

# Database migrations
make db-migrate

# Database backup
make db-backup
```

## Service Management

### Kafka Services
```bash
# Start Kafka services
make start-kafka

# Stop Kafka services
make stop-kafka
```

### MLflow Services
```bash
# Start MLflow tracking
make start-mlflow

# Stop MLflow tracking
make stop-mlflow
```

## CI/CD Commands

### Local CI/CD
```bash
# Run CI/CD pipeline locally
make ci

# Run CI tests
make ci-test

# Test CI Docker setup
make test-ci-docker
```

### Pre-commit
```bash
# Run pre-commit hooks on all files
make pre-commit

# Install pre-commit hooks
make pre-commit-install
```

## Utility Commands

### Cleanup
```bash
# Clean cache and build files
make clean

# Clean Python cache
make clean-python

# Clean frontend build
make clean-frontend
```

### Dependencies
```bash
# Check for outdated dependencies
make check-deps

# Update dependencies
make update-deps

# Update Python dependencies
make update-python-deps

# Update frontend dependencies
make update-frontend-deps
```

### Environment
```bash
# Setup environment variables
make env-setup

# Validate environment
make env-validate
```

### Backup
```bash
# Create backup
make backup

# Restore from backup
make restore
```

## Performance Commands

### Performance Testing
```bash
# Run performance tests
make perf-test

# Load testing
make load-test

# Benchmark tests
make benchmark
```

### Monitoring
```bash
# Start monitoring stack
make monitor

# View metrics
make metrics

# Generate performance report
make perf-report
```

## Release Commands

### Release Management
```bash
# Create a new release
make release

# Build release package
make release-build

# Deploy release
make release-deploy
```

## Help Commands

### Documentation
```bash
# Show help
make help

# Generate documentation
make docs

# Serve documentation locally
make docs-serve
```

## NPM Commands (Frontend)

### Development
```bash
# Start development server
npm start

# Start with backend
npm run dev

# Build for production
npm run build
```

### Testing
```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in CI mode
npm run test:ci
```

### Code Quality
```bash
# Run linting
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Check formatting
npm run format:check

# Type checking
npm run type-check
```

## Python Commands

### Development
```bash
# Run main application
python main.py

# Run with uvicorn
uvicorn main:app --reload

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Testing
```bash
# Run pytest
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### Code Quality
```bash
# Run black formatter
black src/ tests/

# Run isort
isort src/ tests/

# Run flake8
flake8 src/ tests/

# Run mypy
mypy src/
```

## Scripts

### Setup Scripts
```bash
# Run setup script
python scripts/setup_ci.py

# Setup pre-commit
python scripts/setup_precommit.py

# Setup production
python scripts/setup_production.py
```

### Utility Scripts
```bash
# Health check
python scripts/health_check.py

# Performance monitor
python scripts/performance_monitor.py

# Quick test
python scripts/quick_test.py
```

### CI Scripts
```bash
# Local CI
python scripts/local_ci.py

# Test CI setup
python scripts/test_ci_setup.py

# Test production
python scripts/test_production.py
```
