# Contributing to VoiceBridge

Thank you for your interest in contributing to VoiceBridge! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- OpenAI API Key (for AI features)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/KaracaDeer/VoiceBridge_Realtime_App.git
   cd VoiceBridge_Realtime_App
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-ci.txt  # CI/CD tools
   
   # Create .env file
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Start Services**
   ```bash
   # Start backend
   python main.py
   
   # Start frontend (in another terminal)
   cd frontend
   npm run dev
   ```

5. **Setup Pre-commit Hooks**
   ```bash
   # Windows
   scripts\setup_precommit.bat
   
   # Linux/Mac
   ./scripts/setup_precommit.sh
   ```

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Write descriptive docstrings
- Keep functions small and focused

### Commit Messages
Use conventional commit format:
```
feat: add new feature
fix: fix bug
docs: update documentation
style: formatting changes
refactor: code refactoring
test: add tests
chore: maintenance tasks
```

### Testing
```bash
# Run local CI/CD pipeline
python scripts/local_ci.py

# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_api.py tests/test_simple_startup.py

# Run with coverage
python -m pytest tests/ --cov=src

# Test with Docker
scripts\test_ci_docker.bat  # Windows
./scripts/test_ci_docker.sh  # Linux/Mac
```

## 🐛 Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

## ✨ Feature Requests

For new features:
- Check existing issues first
- Describe the use case
- Explain the expected behavior
- Consider backward compatibility

## 🔧 Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   # Run local CI/CD pipeline
   python scripts/local_ci.py
   
   # Run specific tests
   python -m pytest tests/test_api.py tests/test_simple_startup.py
   
   # Test manually
   python main.py
   ```

4. **Submit Pull Request**
   - Clear description of changes
   - Reference related issues
   - Include screenshots for UI changes

## 📁 Project Structure

```
VoiceBridge_Realtime_App/
├── .github/           # GitHub Actions, templates
├── docs/              # Documentation
├── src/               # Source code
│   ├── services/      # Business logic services
│   ├── database/      # Database models
│   ├── models/        # Data models
│   ├── routes/        # API routes
│   ├── middleware/    # Custom middleware
│   └── tasks/         # Celery tasks
├── tests/             # Test files
├── scripts/           # Utility scripts (including CI/CD)
├── docker/            # Docker configuration
├── frontend/          # React frontend
├── monitoring/        # Prometheus & Grafana configs
├── postman/           # API testing collections
├── proto/             # gRPC protocol buffers
├── requirements.txt   # Python dependencies
└── requirements-ci.txt # CI/CD dependencies
```

## 🧪 Testing

### Backend Tests
```bash
# Unit tests
python -m pytest tests/test_api.py

# Startup tests
python -m pytest tests/test_simple_startup.py

# Real-time tests
python -m pytest tests/test_realtime.py

# Security tests
python -m pytest tests/test_security.py

# ML model tests (if available)
python -m pytest tests/test_ml_models.py
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🐳 Docker Development

```bash
# Build and start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

## 📊 Performance Testing

```bash
# Run performance monitoring
python scripts/performance_monitor.py

# Load testing
python -m pytest tests/test_performance.py
```

## 🔒 Security

- Never commit API keys or secrets
- Use environment variables for configuration
- Follow security best practices
- Report security issues privately

## 📚 Documentation

- Update README.md for major changes
- Add docstrings to new functions/classes
- Update API documentation in docs/
- Include examples in code comments

## 🎯 Areas for Contribution

- **Audio Processing**: Improve speech recognition accuracy
- **Real-time Features**: WebSocket and streaming optimizations
- **ML Models**: Integration of new models (Whisper, Wav2Vec2, OpenAI, TensorFlow, PyTorch)
- **Frontend**: UI/UX improvements and React components
- **Testing**: Increase test coverage and CI/CD improvements
- **Documentation**: Improve guides and examples
- **Performance**: Optimization and monitoring with Prometheus/Grafana
- **Security**: Enhanced authentication and encryption
- **CI/CD**: Local testing pipeline improvements
- **Monitoring**: System health and metrics enhancements
- **Docker**: Containerization and deployment improvements
- **gRPC**: High-performance service communication

## 💬 Communication

- **Issues**: [GitHub Issues](https://github.com/KaracaDeer/VoiceBridge_Realtime_App/issues) for bugs and feature requests
- **Discussions**: [GitHub Discussions](https://github.com/KaracaDeer/VoiceBridge_Realtime_App/discussions) for questions
- **LinkedIn**: [Fatma Karaca Erdogan](https://www.linkedin.com/in/fatma-karaca-erdogan-32201a378/) for professional networking
- **Code Review**: All PRs require review before merging
- **Email**: fatmakaracaerdogan@gmail.com for direct contact

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to VoiceBridge! 🎉
