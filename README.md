# VoiceBridge - Real-Time Speech-to-Text & Big Data Processing for Accessibility

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/KaracaDeer/VoiceBridge_Realtime_App)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/KaracaDeer/VoiceBridge_Realtime_App)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org)
[![React](https://img.shields.io/badge/react-18.2.0-blue.svg)](https://reactjs.org)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Fatma%20Karaca%20Erdogan-blue.svg)](https://www.linkedin.com/in/fatma-karaca-erdogan-32201a378/)

VoiceBridge is a real-time speech-to-text application designed to bridge communication gaps for people with hearing impairments.
It combines deep learning, distributed systems, and big data technologies to deliver accurate, scalable, and accessible transcription services.

🇹🇷 [Turkish README](README_TR.md)

## 🚀 Live Demo

https://voicebridge-realtime-app.onrender.com

## 🎯 Demo

<img src="docs/images/demo.gif" alt="VoiceBridge Demo" width="300" height="533">

## ✨ Features

- 🎤 **Real-time Voice Processing** - Advanced speech recognition and transcription
- 🤖 **AI-Powered Transcription** - Multiple ML models including Whisper, Wav2Vec2, and OpenAI
- 🧠 **Deep Learning Integration** - TensorFlow and PyTorch model support
- 📊 **Machine Learning Pipeline** - scikit-learn, NumPy, and Pandas integration
- 🔄 **Real-time Streaming** - WebSocket-based live audio streaming
- 📱 **Responsive Design** - Modern, minimalist interface that works on all devices
- 🚀 **Microservices Architecture** - Scalable distributed system design
- 📚 **ML Model Management** - MLflow integration for model tracking and deployment
- 🔬 **Experiment Tracking** - Weights & Biases for ML experiment visualization
- 🔐 **User Authentication** - Secure user management and session tracking
- 🔑 **JWT Authentication** - Secure token-based authentication system
- 🌐 **OAuth 2.0 Integration** - Social login with Google, GitHub, and Microsoft
- 📊 **Real-time Monitoring** - Prometheus metrics and Grafana dashboards
- 🔄 **Message Queues** - Kafka and Redis for high-performance messaging
- 🔍 **Advanced Analytics** - Spark-based data processing and analytics
- 🛡️ **Security Features** - AES-256 encryption, rate limiting, and secure storage
- ⚡ **Task Processing** - Celery workers for background job processing
- 🌐 **gRPC Services** - High-performance inter-service communication
- 📈 **Performance Monitoring** - Real-time system metrics and health checks
- 🔧 **CI/CD Pipeline** - Automated testing, linting, and deployment

## 🔍 Detailed Features

### Real-time Voice Processing
**Advanced Speech Recognition**
- Multiple ML models (Whisper, Wav2Vec2, OpenAI)
- Real-time audio streaming with WebSocket
- Low-latency transcription processing
- Multi-language support (Whisper model)

**Audio Preprocessing**
- Noise reduction and audio enhancement
- Format conversion and normalization
- Real-time audio quality monitoring

### ML Model Management
**MLflow Integration**
- Model versioning and tracking
- Experiment management
- Model deployment and serving

**Performance Monitoring**
- Real-time model performance metrics
- Accuracy tracking and reporting
- A/B testing for model comparison

### Microservices Architecture
**Service Communication**
- gRPC for high-performance inter-service communication
- RESTful APIs for external integrations
- Message queues for asynchronous processing

**Scalable Infrastructure**
- Docker containerization
- Kubernetes deployment ready
- Load balancing and auto-scaling

### Authentication and User Management
**Local Registration/Login**
- Create accounts with username, email, and password
- Secure password hashing with bcrypt
- JWT token-based authentication

**OAuth 2.0 Social Login**
- Google, GitHub, and Microsoft integration
- Secure OAuth flow with state validation
- Automatic account creation for OAuth users

**User Profile Management**
- View and update profile information
- Track login history and authentication provider
- Secure token refresh mechanism

## 🏗️ Technology Stack

### Frontend
- React 18 + JavaScript - Modern UI framework
- Vite - Lightning-fast build tool
- CSS3 - Modern styling and animations
- WebSocket Client - Real-time communication
- Audio Processing - Web Audio API integration

### Backend
- FastAPI - High-performance Python web framework
- SQLAlchemy - SQL toolkit and ORM
- MongoDB - NoSQL database for metadata
- MySQL - Relational database for user data
- ChromaDB - AI-native vector database
- LangChain - LLM application framework
- OpenAI Integration - GPT-4, Whisper, and Embeddings
- JWT & OAuth2 - Authentication and authorization services

### AI & ML
- **Multiple ML Models** - Whisper, Wav2Vec2, OpenAI
- **Deep Learning Frameworks** - TensorFlow, PyTorch
- **Machine Learning Libraries** - scikit-learn, NumPy, Pandas
- **RAG Pipeline** - Retrieval-Augmented Generation
- **Vector Embeddings** - Semantic similarity search
- **Natural Language Processing** - Advanced text understanding
- **Speech Recognition** - Speech-to-text conversion
- **MLflow** - Model tracking and deployment
- **Weights & Biases** - Experiment tracking and visualization

### Infrastructure
- **Docker** - Containerization and orchestration
- **Kubernetes** - Production deployment and scaling
- **Kafka** - Message streaming and event processing
- **Redis** - Caching, session storage, and Celery broker
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Monitoring dashboards and visualization
- **gRPC** - High-performance inter-service communication
- **Celery** - Distributed task queue and background processing
- **Flower** - Celery monitoring and task management

## 📁 Project Structure

```
VoiceBridge_Realtime_App/
├── 📄 README.md, README_TR.md   # Project documentation
├── 📄 LICENSE, SECURITY.md      # Legal and security info
├── 📄 requirements.txt          # Python dependencies
├── 📄 package.json              # Node.js dependencies
├── 📄 main.py                   # Main application entry point
│
├── 📁 src/                      # Source code
│   ├── database/                # Database models and services
│   ├── services/                # Business logic services
│   ├── routes/                  # API endpoints
│   ├── models/                  # Data models
│   ├── middleware/              # Custom middleware
│   └── tasks/                   # Background tasks
│
├── 📁 frontend/                 # React application
│   ├── src/                     # React source code
│   ├── public/                  # Static assets
│   └── package.json             # Frontend dependencies
│
├── 📁 examples/                 # Example applications
│   ├── simple_main.py          # Basic example
│   ├── simple_main_ml.py       # ML example
│   └── test_setup.py           # Setup test
│
├── 📁 storage/                  # Storage implementations
│   ├── cloud/                  # Cloud storage simulators
│   ├── hdfs/                   # HDFS storage
│   ├── s3/                     # S3 storage
│   ├── gcs_storage/            # Google Cloud Storage
│   └── secure/                 # Secure storage
│
├── 📁 deployment/               # Deployment configurations
│   ├── docker/                 # Docker configurations
│   ├── kubernetes/             # K8s configurations
│   └── docker-compose*.yml     # Docker Compose files
│
├── 📁 scripts/                  # Utility scripts
│   ├── setup_*.py              # Setup scripts
│   ├── start-*.bat/.sh         # Startup scripts
│   ├── health_check.bat        # Health monitoring
│   └── README.md               # Script documentation
│
├── 📁 tests/                    # Test suite (pytest)
│   ├── test_api.py             # API tests
│   ├── test_security.py        # Security tests
│   └── README.md               # Test documentation
│
├── 📁 monitoring/               # Monitoring configs
│   ├── prometheus/             # Prometheus configs
│   ├── grafana/                # Grafana configs
│   └── README.md               # Monitoring guide
│
├── 📁 proto/                    # gRPC protobuf files
│   ├── voicebridge.proto       # Protocol definitions
│   └── README.md               # Protobuf guide
│
├── 📁 docs/                     # Documentation
│   ├── images/                 # Documentation images
│   └── monitoring/             # Large dashboard files
│
├── 📁 data/example/             # Sample data (safe for git)
├── 📁 postman/                  # API test collections
└── 📁 analytics/                # Analytics and simulation
```

## 🚀 Quick Start

### Requirements

* **Node.js** 18+
* **Python** 3.11+
* **OpenAI API Key** for real AI functionality
* **Docker** (optional)

### Installation

1. **Clone the repository**  
```bash
git clone https://github.com/KaracaDeer/VoiceBridge_Realtime_App.git  
cd VoiceBridge_Realtime_App
```

2. **Install dependencies**  
```bash
# Using Makefile (Recommended)  
make install  
# Or manually  
npm install  
pip install -r requirements.txt
```

3. **Configure environment variables**  
```bash
cp env.example .env  
# Edit .env file with your OpenAI API key
```

### Run & Test & Deploy

1. **Start the application**  
```bash
# Start both servers  
make dev  
# or  
npm run dev  
# Or separately:  
make backend     # Backend (port 8000)  
make frontend    # Frontend (port 3000)
```

2. **Access the application**  
   * **Frontend (dev)**: http://localhost:3000  
   * **Backend (dev)**: http://localhost:8000  
   * **API Documentation (dev)**: http://localhost:8000/docs

### Postman API Testing

1. **Import Postman collection and environment:**  
   * Collection: `postman/VoiceBridge_API_Collection.json`  
   * Environment: `postman/VoiceBridge_Development_Environment.json`

2. **Configure environment variables:**  
   * Set `base_url` to your API endpoint:  
         * Local development: `http://localhost:8000`  
         * Docker: `http://localhost:8000`  
         * Production: `https://your-domain.com`

3. **Test API endpoints:**  
   * Health check: `GET {{base_url}}/health`  
   * Real-time streaming: `WebSocket {{base_url}}/ws/stream`  
   * Authentication: `POST {{base_url}}/auth/login`  
   * Transcription: `POST {{base_url}}/transcribe`

4. **Available collections:**  
   * **Health & Status** - API health checks  
   * **Authentication** - User registration, login, OAuth  
   * **Real-time Streaming** - WebSocket audio streaming  
   * **Transcription** - ML model transcription services  
   * **Monitoring** - System metrics and health

### CI/CD Testing

**Run local CI/CD pipeline**
```bash
# Windows
scripts\run_local_ci.bat

# Linux/Mac
./scripts/run_local_ci.sh
```

**Setup pre-commit hooks**
```bash
# Windows
scripts\setup_precommit.bat

# Linux/Mac
./scripts/setup_precommit.sh
```

**Test with Docker**
```bash
# Windows
scripts\test_ci_docker.bat
```

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
PORT=8000
HOST=127.0.0.1

# Development
NODE_ENV=development
VITE_API_URL=http://localhost:8000

# JWT Authentication
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret

# Database
DATABASE_URL=sqlite:///./voicebridge.db
MONGODB_URL=mongodb://localhost:27017/voicebridge

# Message Queues
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
REDIS_URL=redis://localhost:6379

# ML Services
MLFLOW_TRACKING_URI=http://localhost:5000
WANDB_API_KEY=your_wandb_api_key

# ML Framework Configuration
TENSORFLOW_GPU_ENABLED=true
PYTORCH_DEVICE=cuda
SKLEARN_N_JOBS=4

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
```

## 📋 Available Commands

### Makefile Commands (Recommended)

* `make install` - Install all dependencies
* `make dev` - Start development servers
* `make build` - Production build
* `make test` - Run all tests
* `make lint` - Code linting
* `make clean` - Clean cache and build files
* `make docker-up` - Start Docker services
* `make docker-down` - Stop Docker services
* `make health` - Check service health
* `make monitor` - Start performance monitoring
* `make quick-start` - Complete setup and start

### CI/CD Commands

* `python scripts/local_ci.py` - Local CI/CD testing
* `pre-commit install` - Pre-commit setup
* `pre-commit run --all-files` - Run all pre-commit hooks
* `docker build -t voicebridge:test -f docker/Dockerfile .` - Docker testing

### NPM Commands

* `npm run dev` - Start backend + frontend together
* `npm run build` - Production build
* `npm run start` - Start production server
* `npm run test` - Run tests
* `npm run backend` - Start backend only
* `npm run docker-up` - Start Docker services
* `npm run docker-prod` - Start production Docker

## 📖 Usage

### Real-time Voice Processing

1. Start a WebSocket connection
2. Send audio data in real-time
3. Receive live transcription results
4. Get AI-powered insights and analysis

### Voice Interaction

1. Click the microphone button
2. Speak your message naturally
3. Get instant speech-to-text conversion
4. Receive AI-generated responses

### ML Model Management

1. **Track Model Performance**  
   * Monitor accuracy and latency metrics with MLflow
   * Real-time model performance tracking with Weights & Biases
   * A/B testing for model comparison
   * TensorFlow and PyTorch model integration

2. **Model Deployment**  
   * Deploy new model versions
   * Version control and rollback capabilities
   * Automated model serving
   * scikit-learn model pipeline integration

### System Monitoring

1. **Real-time Metrics**  
   * View system metrics in Grafana dashboards
   * Monitor system health with Prometheus
   * Track performance and resource usage

2. **Alerting**  
   * Get alerts for system issues
   * Performance threshold monitoring
   * Automated incident response

## 🐳 Docker

### Quick Start

#### Docker Compose Files Overview
| File | Purpose | Description |
|------|---------|-------------|
| `docker-compose.yml` | Development | Basic backend + frontend services |
| `docker-compose.production.yml` | Production | Full production stack with nginx, SSL |
| `docker-compose.monitoring.yml` | Monitoring | Prometheus + Grafana monitoring stack |

#### Quick Start Commands
```bash
# Development mode (backend + frontend)
docker-compose up -d

# Production mode (all services + nginx)
docker-compose -f docker-compose.production.yml up -d

# Monitoring stack (Prometheus + Grafana)
docker-compose -f docker-compose.monitoring.yml up -d

# All services (production + monitoring)
docker-compose -f docker-compose.production.yml -f docker-compose.monitoring.yml up -d
```

### Docker Commands
```bash
# Build all images
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Check health
docker-compose ps
```

### Docker Services

* **Backend**: FastAPI on port 8000
* **Frontend**: React app on port 3000
* **Redis**: Cache and Celery broker on port 6379
* **Celery Worker**: Background task processing
* **Celery Flower**: Task monitoring on port 5555
* **MLflow**: Model tracking on port 5000
* **Prometheus**: Metrics collection on port 9090
* **Grafana**: Monitoring dashboards on port 3001
* **Node Exporter**: System metrics on port 9100

## 🤝 Contributing & Support

### Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run CI/CD tests**: `python scripts/local_ci.py`
5. **Submit a pull request**

**For detailed guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)**

**Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing**

### Support

* **Issues**: [GitHub Issues](https://github.com/KaracaDeer/VoiceBridge_Realtime_App/issues)
* **Discussions**: [GitHub Discussions](https://github.com/KaracaDeer/VoiceBridge_Realtime_App/discussions)
* **LinkedIn**: [Fatma Karaca Erdogan](https://www.linkedin.com/in/fatma-karaca-erdogan-32201a378/)
* **Email**: fatmakaracaerdogan@gmail.com

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

* **OpenAI** - For providing state-of-the-art AI models
* **TensorFlow Team** - For the deep learning framework
* **PyTorch Team** - For the machine learning framework
* **scikit-learn** - For machine learning algorithms
* **FastAPI** - For the high-performance backend framework
* **React Team** - For the amazing frontend library
* **MLflow** - For model tracking and deployment
* **Weights & Biases** - For experiment tracking
* **Prometheus & Grafana** - For monitoring and observability
* **Celery** - For distributed task processing
* **Redis** - For caching and message brokering
* **Docker** - For containerization and deployment
