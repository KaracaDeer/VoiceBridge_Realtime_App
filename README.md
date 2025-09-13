# VoiceBridge - Real-Time Speech-to-Text for Accessibility

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/KaracaDeer/VoiceBridge_Realtime_App)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Fatma%20Karaca%20Erdogan-blue.svg)](https://www.linkedin.com/in/fatma-karaca-erdogan-32201a378/)


**VoiceBridge enables hearing-impaired users to follow real-time conversations in meetings, classrooms, or social environments with sub-second transcription latency.** Built with modern microservices architecture, it combines AI/ML models, WebSocket streaming, and accessibility-first design to deliver accurate, scalable speech-to-text services.

🇹🇷 [Turkish README](README_TR.md)

## 🚀 Live Demo

https://voicebridge-realtime-app.onrender.com

## 🎯 Demo

<img src="docs/images/demo.gif" alt="VoiceBridge Demo" width="300" height="533">

## 🚀 Quick Start

```bash
# 1. Clone and install
git clone https://github.com/KaracaDeer/VoiceBridge_Realtime_App.git
cd VoiceBridge_Realtime_App
make install

# 2. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 3. Start development
make dev
```

**Access**: Frontend (http://localhost:3000) | Backend (http://localhost:8000) | API Docs (http://localhost:8000/docs)

### Docker Quick Start
```bash
docker-compose up -d
```

## 🏗️ Architecture

📖 [VoiceBridge Architecture](docs/architecture.md)

```
User → Frontend → WebSocket → Backend → ML Models → Text Output
  ↓       ↓          ↓         ↓         ↓          ↓
React   Audio    Real-time  FastAPI   Whisper   Display
UI     Capture   Stream     Server    Wav2Vec2  Results
```

📖 [Detailed Architecture](docs/images/architecture.md)

## ✨ Key Features

- 🎤 **Voice Processing** - Real-time speech recognition with sub-second latency
- 🤖 **AI/ML Integration** - OpenAI Whisper, Wav2Vec2, custom models with TensorFlow & PyTorch
- 🔄 **Real-time Streaming** - WebSocket-based live audio processing
- 🚀 **Microservices & Scaling** - Docker, Kubernetes, distributed architecture
- 🔐 **Security & Auth** - JWT, OAuth2, AES-256 encryption
- 📊 **Monitoring & Analytics** - Prometheus, Grafana, comprehensive logging

## 🤖 AI/ML Performance

### Model Performance

| Model | Accuracy | Latency | Confidence | Languages |
|-------|----------|---------|------------|-----------|
| **OpenAI Whisper** | 95.2% | 0.8s | 0.89 | 50+ |
| **Wav2Vec2** | 87.5% | 1.2s | 0.82 | English |

### Sample Transcriptions

**High Quality Audio:**
- Input: "Hello, this is a test of the VoiceBridge system."
- Output: "Hello, this is a test of the VoiceBridge system."
- Confidence: 0.96 | Processing Time: 0.7s

**Noisy Audio:**
- Input: [Audio with background noise]
- Output: "Hello, this is a test of the VoiceBridge system."
- Confidence: 0.78 | Processing Time: 1.1s

### MLflow Dashboard
- **Local**: http://localhost:5000
- **Features**: Model versioning, experiment tracking, performance metrics
- **TensorFlow and PyTorch model integration** for custom model deployment

📊 [Detailed ML Performance Report](docs/ml_performance.md)

## 🛠️ Tech Stack

### Frontend
- React 18, JavaScript, real-time UI

### Backend
- FastAPI, Python 3.11+, WebSocket streaming

### AI/ML
- OpenAI Whisper, Wav2Vec2 for real-time transcription
- Custom ML models trained with **TensorFlow** & **PyTorch**
- Data preprocessing & feature engineering using **scikit-learn**
- MLflow, Weights & Biases for experiment tracking

### Infrastructure
- Docker, Kubernetes, Kafka, Celery, Redis

## 📁 Project Structure

```
VoiceBridge_Realtime_App/
├── src/                    # Backend source code
│   ├── services/          # Business logic & ML services
│   ├── routes/            # API endpoints
│   ├── models/            # Data models
│   └── tasks/             # Background tasks
├── frontend/              # React application
├── tests/                 # Test suite
├── docs/                  # Documentation
├── deployment/            # Docker & K8s configs
└── scripts/               # Utility scripts
```

📖 [Detailed Project Structure](docs/architecture.md)

## 🧪 Testing & Development

```bash
make test          # Run all tests (85%+ coverage)
make lint          # Code linting
make format        # Code formatting
```

📋 [Test Documentation](tests/README.md)

## 📚 Documentation

- 📖 [Architecture Guide](docs/architecture.md)
- 🤖 [ML Performance Report](docs/ml_performance.md)
- 🧪 [Test Documentation](tests/README.md)
- 🚀 [Deployment Guide](docs/deployment.md)
- 📋 [API Documentation](http://localhost:8000/docs)

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
PORT=8000
HOST=127.0.0.1
DATABASE_URL=sqlite:///./voicebridge.db
REDIS_URL=redis://localhost:6379
MLFLOW_TRACKING_URI=http://localhost:5000
```

📝 [Full Configuration Guide](docs/configuration.md)

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies |
| `make dev` | Start development servers |
| `make test` | Run all tests |
| `make lint` | Code linting |
| `make format` | Code formatting |
| `make docker-up` | Start Docker services |
| `make health` | Check service health |

📋 [Full Command Reference](docs/commands.md)

## 🤝 Contributing & Support

### 🚀 Contributing
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `make test`
5. **Submit a pull request**

**For detailed guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)**

### 💬 Support
- **🐛 Issues**: [GitHub Issues](https://github.com/KaracaDeer/VoiceBridge_Realtime_App/issues)
- **💭 Discussions**: [GitHub Discussions](https://github.com/KaracaDeer/VoiceBridge_Realtime_App/discussions)
- **💼 LinkedIn**: [Fatma Karaca Erdogan](https://www.linkedin.com/in/fatma-karaca-erdogan-32201a378/)
- **📧 Email**: fatmakaracaerdogan@gmail.com

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

* **OpenAI** - For providing state-of-the-art AI models
* **FastAPI** - For the high-performance backend framework
* **React Team** - For the amazing frontend library
* **MLflow** - For model tracking and deployment
* **Prometheus & Grafana** - For monitoring and observability
* **Docker** - For containerization and deployment

