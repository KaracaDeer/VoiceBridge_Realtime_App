# VoiceBridge Makefile
# Easy commands for local development and CI

.PHONY: help install test lint format clean ci docker-build docker-test

# Default target
help:
	@echo "VoiceBridge Development Commands"
	@echo "================================"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install all dependencies"
	@echo "  install-ci  Install CI dependencies only"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black and isort"
	@echo "  type-check  Run type checking with mypy"
	@echo "  security    Run security checks"
	@echo ""
	@echo "Testing:"
	@echo "  test        Run all tests"
	@echo "  test-fast   Run tests with minimal output"
	@echo "  test-ci     Run tests as in CI"
	@echo ""
	@echo "CI/CD:"
	@echo "  ci          Run full local CI pipeline"
	@echo "  ci-quick    Run quick CI checks"
	@echo "  pre-commit  Install pre-commit hooks"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build Build Docker image"
	@echo "  docker-test  Test Docker image"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       Clean up temporary files"
	@echo "  setup       Complete project setup"

# Setup commands
install:
	pip install -r requirements.txt

install-ci:
	pip install -r requirements-ci.txt

setup: install-ci
	python scripts/test_ci_setup.py
	@echo "✅ Setup complete! Run 'make ci' to test everything."

# Code quality commands
lint:
	flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black src tests
	isort src tests

format-check:
	black --check src tests
	isort --check-only src tests

type-check:
	mypy src --ignore-missing-imports --no-strict-optional

security:
	bandit -r src/ -f json || true
	safety check --json || true

# Testing commands
test:
	pytest tests/ -v

test-fast:
	pytest tests/ --maxfail=1 --disable-warnings -q

test-ci:
	pytest tests/test_api.py tests/test_simple_startup.py --maxfail=1 --disable-warnings -v --tb=short

# CI/CD commands
ci: install-ci
	python scripts/local_ci.py

ci-quick: format-check lint type-check test-fast

pre-commit:
	pip install pre-commit
	pre-commit install
	pre-commit run --all-files

# Docker commands
docker-build:
	docker build -t voicebridge:test -f docker/Dockerfile .

docker-test: docker-build
	docker run --rm voicebridge:test python --version

# Utility commands
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/

# Development workflow
dev-setup: install-ci pre-commit
	@echo "✅ Development environment ready!"
	@echo "💡 Run 'make ci' before pushing to GitHub"

# Quick development cycle
dev: format lint test-fast
	@echo "✅ Quick development checks passed!"

# Full development cycle
dev-full: format lint type-check test security
	@echo "✅ Full development checks passed!"