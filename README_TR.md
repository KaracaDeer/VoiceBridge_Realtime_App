# VoiceBridge - Gerçek Zamanlı Konuşma-Metin Dönüştürme ve Büyük Veri İşleme

[![Versiyon](https://img.shields.io/badge/versiyon-1.0.0-blue.svg)](https://github.com/KaracaDeer/VoiceBridge_Realtime_App)
[![Build Durumu](https://img.shields.io/badge/build-başarılı-brightgreen.svg)](https://github.com/KaracaDeer/VoiceBridge_Realtime_App)
[![Lisans](https://img.shields.io/badge/lisans-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org)
[![React](https://img.shields.io/badge/react-18.2.0-blue.svg)](https://reactjs.org)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Fatma%20Karaca%20Erdogan-blue.svg)](https://www.linkedin.com/in/fatma-karaca-erdogan-32201a378/)

VoiceBridge, işitme engelli bireyler için iletişim boşluklarını kapatmak amacıyla tasarlanmış gerçek zamanlı konuşma-metin dönüştürme uygulamasıdır.
Derin öğrenme, dağıtık sistemler ve büyük veri teknolojilerini birleştirerek doğru, ölçeklenebilir ve erişilebilir transkripsiyon hizmetleri sunar.

🇺🇸 [English README](README.md)

🎯 Demo

![VoiceBridge Demo](docs/images/demo.gif)

✨ Özellikler
🎤 Gerçek Zamanlı Ses İşleme - Gelişmiş konuşma tanıma ve transkripsiyon
🤖 AI Destekli Transkripsiyon - Whisper, Wav2Vec2 ve OpenAI dahil çoklu ML modelleri
🧠 Derin Öğrenme Entegrasyonu - TensorFlow ve PyTorch model desteği
📊 Makine Öğrenmesi Pipeline - scikit-learn, NumPy ve Pandas entegrasyonu
🔄 Gerçek Zamanlı Streaming - WebSocket tabanlı canlı ses akışı
📱 Responsive Tasarım - Tüm cihazlarda çalışan modern, minimalist arayüz
🚀 Mikroservis Mimarisi - Ölçeklenebilir dağıtık sistem tasarımı
📚 ML Model Yönetimi - Model takibi ve dağıtımı için MLflow entegrasyonu
🔬 Deney Takibi - ML deneylerini görselleştirme için Weights & Biases
🔐 Kullanıcı Kimlik Doğrulama - Güvenli kullanıcı yönetimi ve oturum takibi
🔑 JWT Kimlik Doğrulama - Güvenli token tabanlı kimlik doğrulama sistemi
🌐 OAuth 2.0 Entegrasyonu - Google, GitHub ve Microsoft ile sosyal giriş
📊 Gerçek Zamanlı İzleme - Prometheus metrikleri ve Grafana panelleri
🔄 Mesaj Kuyrukları - Yüksek performanslı mesajlaşma için Kafka ve Redis
🔍 Gelişmiş Analitik - Spark tabanlı veri işleme ve analitik
🛡️ Güvenlik Özellikleri - AES-256 şifreleme, hız sınırlama ve güvenli depolama
⚡ Görev İşleme - Arka plan iş işleme için Celery worker'ları
🌐 gRPC Servisleri - Yüksek performanslı servisler arası iletişim
📈 Performans İzleme - Gerçek zamanlı sistem metrikleri ve sağlık kontrolleri
🔧 CI/CD Pipeline - Otomatik test, linting ve dağıtım

## 🔍 Detaylı Özellikler

### Gerçek Zamanlı Ses İşleme
**Gelişmiş Konuşma Tanıma**
- Çoklu ML modelleri (Whisper, Wav2Vec2, OpenAI)
- WebSocket ile gerçek zamanlı ses akışı
- Düşük gecikme transkripsiyon işleme
- Çoklu dil desteği (Whisper modeli ile)

**Ses Ön İşleme**
- Gürültü azaltma ve ses geliştirme
- Format dönüştürme ve normalizasyon
- Gerçek zamanlı ses kalitesi izleme

### ML Model Yönetimi
**MLflow Entegrasyonu**
- Model versiyonlama ve takibi
- Deney yönetimi
- Model dağıtımı ve servisi

**Performans İzleme**
- Gerçek zamanlı model performans metrikleri
- Doğruluk takibi ve raporlama
- Model karşılaştırması için A/B testi

### Mikroservis Mimarisi
**Servis İletişimi**
- Yüksek performanslı servisler arası iletişim için gRPC
- Dış entegrasyonlar için RESTful API'ler
- Asenkron işleme için mesaj kuyrukları

**Ölçeklenebilir Altyapı**
- Docker konteynerleştirme
- Kubernetes dağıtım hazır
- Yük dengeleme ve otomatik ölçeklendirme

### Kimlik Doğrulama ve Kullanıcı Yönetimi
**Yerel Kayıt/Giriş**
- Kullanıcı adı, e-posta ve şifre ile hesap oluşturma
- bcrypt ile güvenli şifre hashleme
- JWT token tabanlı kimlik doğrulama

**OAuth 2.0 Sosyal Giriş**
- Google, GitHub ve Microsoft entegrasyonu
- Durum doğrulama ile güvenli OAuth akışı
- OAuth kullanıcıları için otomatik hesap oluşturma

**Kullanıcı Profil Yönetimi**
- Profil bilgilerini görüntüleme ve güncelleme
- Giriş geçmişi ve kimlik doğrulama sağlayıcısını takip etme
- Güvenli token yenileme mekanizması

## 🏗️ Teknoloji Stack

### Frontend
- React 18 + JavaScript - Modern UI framework
- Vite - Şimşek hızında build aracı
- CSS3 - Modern stil ve animasyonlar
- WebSocket Client - Gerçek zamanlı iletişim
- Audio Processing - Web Audio API entegrasyonu

### Backend
- FastAPI - Yüksek performanslı Python web framework
- SQLAlchemy - SQL toolkit ve ORM
- MongoDB - Metadata için NoSQL veritabanı
- MySQL - Kullanıcı verileri için ilişkisel veritabanı
- ChromaDB - AI-native vektör veritabanı
- LangChain - LLM uygulama framework
- OpenAI Entegrasyonu - GPT-4, Whisper ve Embeddings
- JWT & OAuth2 - Kimlik doğrulama ve yetkilendirme servisleri

### AI & ML
- **Çoklu ML Modelleri** - Whisper, Wav2Vec2, OpenAI
- **Derin Öğrenme Framework'leri** - TensorFlow, PyTorch
- **Makine Öğrenmesi Kütüphaneleri** - scikit-learn, NumPy, Pandas
- **RAG Pipeline** - Retrieval-Augmented Generation
- **Vektör Embeddings** - Semantik benzerlik arama
- **Doğal Dil İşleme** - Gelişmiş metin anlama
- **Konuşma Tanıma** - Konuşma-metin dönüştürme
- **MLflow** - Model takibi ve dağıtımı
- **Weights & Biases** - Deney takibi ve görselleştirme

### Altyapı
- **Docker** - Konteynerleştirme ve orkestrasyon
- **Kubernetes** - Production dağıtımı ve ölçeklendirme
- **Kafka** - Mesaj akışı ve olay işleme
- **Redis** - Önbellekleme, oturum depolama ve Celery broker
- **Prometheus** - Metrik toplama ve uyarı
- **Grafana** - İzleme panelleri ve görselleştirme
- **gRPC** - Yüksek performanslı iletişim
- **Celery** - Dağıtık görev kuyruğu ve arka plan işleme
- **Flower** - Celery izleme ve görev yönetimi

## 📁 Proje Yapısı

```
VoiceBridge_Realtime_App/
├── 📄 README.md, README_TR.md   # Proje dokümantasyonu
├── 📄 LICENSE, SECURITY.md      # Yasal ve güvenlik bilgileri
├── 📄 requirements.txt          # Python bağımlılıkları
├── 📄 docker-compose*.yml       # Docker konfigürasyonları
│
├── 📁 src/                      # Kaynak kod
│   ├── database/                # Veritabanı modelleri ve servisleri
│   ├── services/                # İş mantığı servisleri
│   ├── routes/                  # API endpoint'leri
│   ├── models/                  # Veri modelleri
│   ├── middleware/              # Özel middleware
│   └── tasks/                   # Arka plan görevleri
│
├── 📁 frontend/                 # React uygulaması
│   ├── src/                     # React kaynak kodu
│   ├── public/                  # Statik varlıklar
│   └── package.json             # Node.js bağımlılıkları
│
├── 📁 tests/                    # Test paketi (pytest)
│   ├── test_api.py             # API testleri
│   ├── test_security.py        # Güvenlik testleri
│   └── README.md               # Test dokümantasyonu
│
├── 📁 scripts/                  # Yardımcı scriptler
│   ├── setup_ci.py             # CI/CD kurulumu
│   ├── health_check.bat        # Sağlık izleme
│   └── README.md               # Script dokümantasyonu
│
├── 📁 monitoring/               # İzleme konfigürasyonları
│   ├── prometheus/             # Prometheus konfigürasyonları
│   ├── grafana/                # Grafana konfigürasyonları
│   └── README.md               # İzleme kılavuzu
│
├── 📁 proto/                    # gRPC protobuf dosyaları
│   ├── voicebridge.proto       # Protokol tanımları
│   └── README.md               # Protobuf kılavuzu
│
├── 📁 docs/                     # Dokümantasyon
│   └── monitoring/             # Büyük dashboard dosyaları
│
├── 📁 data/example/             # Örnek veriler (git için güvenli)
├── 📁 secure_storage/example/   # Örnek konfigürasyonlar (git için güvenli)
└── 📁 postman/                  # API test koleksiyonları
```

## 🚀 Hızlı Başlangıç

### Gereksinimler

* **Node.js** 18+
* **Python** 3.11+
* **OpenAI API Key** gerçek AI işlevselliği için
* **Docker** (opsiyonel)

### Kurulum

1. **Repository'yi klonlayın**  
```bash
git clone https://github.com/KaracaDeer/VoiceBridge_Realtime_App.git  
cd VoiceBridge_Realtime_App
```

2. **Bağımlılıkları yükleyin**  
```bash
# Makefile kullanarak (Önerilen)  
make install  
# Veya manuel olarak  
npm install  
pip install -r requirements.txt
```

3. **Ortam değişkenlerini yapılandırın**  
```bash
cp env.example .env  
# .env dosyasını OpenAI API anahtarınızla düzenleyin
```

### Çalıştır & Test & Dağıt

1. **Uygulamayı başlatın**  
```bash
# Her iki sunucuyu da başlat  
make dev  
# veya  
npm run dev  
# Veya ayrı ayrı:  
make backend     # Backend (port 8000)  
make frontend    # Frontend (port 3000)
```

2. **Uygulamaya erişin**  
   * **Frontend (dev)**: http://localhost:3000  
   * **Backend (dev)**: http://localhost:8000  
   * **API Dokümantasyonu (dev)**: http://localhost:8000/docs

### Postman API Testi

1. **Postman koleksiyonu ve ortamını import edin:**  
   * Koleksiyon: `postman/VoiceBridge_API_Collection.json`  
   * Ortam: `postman/VoiceBridge_Development_Environment.json`

2. **Ortam değişkenlerini yapılandırın:**  
   * `base_url`'i API endpoint'inize ayarlayın:  
         * Yerel geliştirme: `http://localhost:8000`  
         * Docker: `http://localhost:8000`  
         * Production: `https://your-domain.com`

3. **API endpoint'lerini test edin:**  
   * Sağlık kontrolü: `GET {{base_url}}/health`  
   * Gerçek zamanlı streaming: `WebSocket {{base_url}}/ws/stream`  
   * Kimlik doğrulama: `POST {{base_url}}/auth/login`  
   * Transkripsiyon: `POST {{base_url}}/transcribe`

4. **Mevcut koleksiyonlar:**  
   * **Sağlık & Durum** - API sağlık kontrolleri  
   * **Kimlik Doğrulama** - Kullanıcı kaydı, giriş, OAuth  
   * **Gerçek Zamanlı Streaming** - WebSocket ses akışı  
   * **Transkripsiyon** - ML model transkripsiyon servisleri  
   * **İzleme** - Sistem metrikleri ve sağlık

### CI/CD Testi

**Yerel CI/CD pipeline'ını çalıştırın**
```bash
# Windows
scripts\run_local_ci.bat

# Linux/Mac
./scripts/run_local_ci.sh
```

**Pre-commit hook'larını kurun**
```bash
# Windows
scripts\setup_precommit.bat

# Linux/Mac
./scripts/setup_precommit.sh
```

**Docker ile test edin**
```bash
# Windows
scripts\test_ci_docker.bat
```

## 🔧 Konfigürasyon

### Ortam Değişkenleri

```bash
# OpenAI Konfigürasyonu
OPENAI_API_KEY=your_openai_api_key_here

# Sunucu Konfigürasyonu
PORT=8000
HOST=127.0.0.1

# Geliştirme
NODE_ENV=development
VITE_API_URL=http://localhost:8000

# JWT Kimlik Doğrulama
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth Konfigürasyonu
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret

# Veritabanı
DATABASE_URL=sqlite:///./voicebridge.db
MONGODB_URL=mongodb://localhost:27017/voicebridge

# Mesaj Kuyrukları
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
REDIS_URL=redis://localhost:6379

# ML Servisleri
MLFLOW_TRACKING_URI=http://localhost:5000
WANDB_API_KEY=your_wandb_api_key

# ML Framework Konfigürasyonu
TENSORFLOW_GPU_ENABLED=true
PYTORCH_DEVICE=cuda
SKLEARN_N_JOBS=4

# İzleme
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
```

## 📋 Mevcut Komutlar

### Makefile Komutları (Önerilen)

* `make install` - Tüm bağımlılıkları yükle
* `make dev` - Geliştirme sunucularını başlat
* `make build` - Production build
* `make test` - Tüm testleri çalıştır
* `make lint` - Kod linting
* `make clean` - Önbellek ve build dosyalarını temizle
* `make docker-up` - Docker servislerini başlat
* `make docker-down` - Docker servislerini durdur
* `make health` - Servis sağlığını kontrol et
* `make monitor` - Performans izlemeyi başlat
* `make quick-start` - Tam kurulum ve başlatma

### CI/CD Komutları

* `python scripts/local_ci.py` - Yerel CI/CD testi
* `pre-commit install` - Pre-commit kurulumu
* `pre-commit run --all-files` - Tüm pre-commit hook'larını çalıştır
* `docker build -t voicebridge:test -f docker/Dockerfile .` - Docker testi

### NPM Komutları

* `npm run dev` - Backend + frontend'i birlikte başlat
* `npm run build` - Production build
* `npm run start` - Production sunucusunu başlat
* `npm run test` - Testleri çalıştır
* `npm run backend` - Sadece backend'i başlat
* `npm run docker-up` - Docker servislerini başlat
* `npm run docker-prod` - Production Docker'ı başlat

## 📖 Kullanım

### Gerçek Zamanlı Ses İşleme

1. WebSocket bağlantısı başlatın
2. Ses verilerini gerçek zamanlı olarak gönderin
3. Canlı transkripsiyon sonuçlarını alın
4. AI destekli içgörüler ve analizler alın

### Ses Etkileşimi

1. Mikrofon butonuna tıklayın
2. Mesajınızı doğal olarak konuşun
3. Anında konuşma-metin dönüştürme alın
4. AI tarafından üretilen yanıtlar alın

### ML Model Yönetimi

1. **Model Performansını Takip Edin**  
   * MLflow ile doğruluk ve gecikme metriklerini izleyin
   * Weights & Biases ile gerçek zamanlı model performans takibi
   * Model karşılaştırması için A/B testi

2. **Model Dağıtımı**  
   * Yeni model versiyonlarını dağıtın
   * Versiyon kontrolü ve geri alma yetenekleri
   * Otomatik model servisi

### Sistem İzleme

1. **Gerçek Zamanlı Metrikler**  
   * Grafana panellerinde sistem metriklerini görüntüleyin
   * Prometheus ile sistem sağlığını izleyin
   * Performans ve kaynak kullanımını takip edin

2. **Uyarılar**  
   * Sistem sorunları için uyarılar alın
   * Performans eşik izleme
   * Otomatik olay yanıtı

## 🐳 Docker

### Hızlı Başlangıç

#### Docker Compose Dosyaları Genel Bakış
| Dosya | Amaç | Açıklama |
|-------|------|----------|
| `docker-compose.yml` | Geliştirme | Temel backend + frontend servisleri |
| `docker-compose.production.yml` | Production | nginx, SSL ile tam production stack |
| `docker-compose.monitoring.yml` | İzleme | Prometheus + Grafana izleme stack'i |

#### Hızlı Başlangıç Komutları
```bash
# Geliştirme modu (backend + frontend)
docker-compose up -d

# Production modu (tüm servisler + nginx)
docker-compose -f docker-compose.production.yml up -d

# İzleme stack'i (Prometheus + Grafana)
docker-compose -f docker-compose.monitoring.yml up -d

# Tüm servisler (production + izleme)
docker-compose -f docker-compose.production.yml -f docker-compose.monitoring.yml up -d
```

### Docker Komutları

```bash
# Tüm görüntüleri oluştur
docker-compose build

# Servisleri başlat
docker-compose up -d

# Servisleri durdur
docker-compose down

# Logları görüntüle
docker-compose logs -f

# Sağlığı kontrol et
docker-compose ps
```

### Docker Servisleri

* **Backend**: Port 8000'de FastAPI
* **Frontend**: Port 3000'de React uygulaması
* **Redis**: Port 6379'da önbellek ve Celery broker
* **Celery Worker**: Arka plan görev işleme
* **Celery Flower**: Port 5555'te görev izleme
* **MLflow**: Port 5000'de model takibi
* **Prometheus**: Port 9090'da metrik toplama
* **Grafana**: Port 3001'de izleme panelleri
* **Node Exporter**: Port 9100'de sistem metrikleri

## 🤝 Katkıda Bulunma & Destek

### Katkıda Bulunma

1. **Repository'yi fork edin**
2. **Özellik dalı oluşturun**: `git checkout -b feature/amazing-feature`
3. **Değişikliklerinizi yapın**
4. **CI/CD testlerini çalıştırın**: `python scripts/local_ci.py`
5. **Pull request gönderin**

**Detaylı kılavuzlar için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasına bakın**

**Katkıda bulunmadan önce lütfen [Code of Conduct](CODE_OF_CONDUCT.md) dosyamızı okuyun**

### Destek

* **Sorunlar**: [GitHub Issues](https://github.com/KaracaDeer/VoiceBridge_Realtime_App/issues)
* **Tartışmalar**: [GitHub Discussions](https://github.com/KaracaDeer/VoiceBridge_Realtime_App/discussions)
* **Linkedın**: [Fatma Karaca Erdogan](https://www.linkedin.com/in/fatma-karaca-erdogan-32201a378/)
* **E-posta**: fatmakaracaerdogan@gmail.com

## 📝 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için LICENSE dosyasına bakın.

## 🙏 Teşekkürler

* **OpenAI** - En son teknoloji AI modelleri sağladığı için
* **TensorFlow Team** - Derin öğrenme framework'ü için
* **PyTorch Team** - Makine öğrenmesi framework'ü için
* **scikit-learn** - Makine öğrenmesi algoritmaları için
* **FastAPI** - Yüksek performanslı backend framework'ü için
* **React Team** - Harika frontend kütüphanesi için
* **MLflow** - Model takibi ve dağıtımı için
* **Weights & Biases** - Deney takibi için
* **Prometheus & Grafana** - İzleme ve gözlemlenebilirlik için
* **Celery** - Dağıtık görev işleme için
* **Redis** - Önbellekleme ve mesaj broker'ı için
* **Docker** - Konteynerleştirme ve dağıtım için
