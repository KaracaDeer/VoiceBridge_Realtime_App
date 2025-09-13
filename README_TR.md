# VoiceBridge - Gerçek Zamanlı Konuşma-Metin Dönüştürme ve Büyük Veri İşleme

[![Versiyon](https://img.shields.io/badge/versiyon-1.0.0-blue.svg)](https://github.com/KaracaDeer/VoiceBridge_Realtime_App)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Lisans](https://img.shields.io/badge/lisans-MIT-green.svg)](LICENSE)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Fatma%20Karaca%20Erdogan-blue.svg)](https://www.linkedin.com/in/fatma-karaca-erdogan-32201a378/)


**VoiceBridge, işitme engelli kullanıcıların toplantı, sınıf veya sosyal ortamlarda gerçek zamanlı konuşmaları bir saniyeden kısa bir süre transkripsiyon gecikmesi ile takip etmelerini sağlar.** Modern mikroservis mimarisi ile inşa edilmiş olup, AI/ML modelleri, WebSocket streaming ve erişilebilirlik odaklı tasarımı birleştirerek doğru, ölçeklenebilir konuşma-metin hizmetleri sunar.

🇺🇸 [English README](README.md)

## 🎯 Demo

<img src="docs/images/demo.gif" alt="VoiceBridge Demo" width="300" height="533">

## 🚀 Hızlı Başlangıç

```bash
# 1. Klonla ve kur
git clone https://github.com/KaracaDeer/VoiceBridge_Realtime_App.git
cd VoiceBridge_Realtime_App
make install

# 2. Ortam değişkenlerini yapılandır
cp .env.example .env
# .env dosyasını OpenAI API anahtarınızla düzenleyin

# 3. Geliştirme sunucularını başlat
make dev
```

**Erişim**: Frontend (http://localhost:3000) | Backend (http://localhost:8000) | API Docs (http://localhost:8000/docs)

### Docker Hızlı Başlangıç
```bash
docker-compose up -d
```

## 🏗️ Mimari

<img src="docs/images/architecture.png" alt="VoiceBridge Mimari" width="600">

```
Kullanıcı → Frontend → WebSocket → Backend → ML Modelleri → Metin Çıktısı
  ↓         ↓          ↓         ↓         ↓          ↓
React     Ses      Gerçek     FastAPI   Whisper   Görüntüleme
UI       Yakalama  Zamanlı    Sunucu    Wav2Vec2  Sonuçları
```

📖 [Detaylı Mimari](docs/images/architecture.md)

## ✨ Temel Özellikler

- 🎤 **Ses İşleme** - Bir saniyeden kısa bir süre gecikme ile gerçek zamanlı konuşma tanıma
- 🤖 **AI/ML Entegrasyonu** - OpenAI Whisper, Wav2Vec2, TensorFlow & PyTorch ile özel modeller
- 🔄 **Gerçek Zamanlı Streaming** - WebSocket tabanlı canlı ses işleme
- 🚀 **Mikroservisler & Ölçeklendirme** - Docker, Kubernetes, dağıtık mimari
- 🔐 **Güvenlik & Kimlik Doğrulama** - JWT, OAuth2, AES-256 şifreleme
- 📊 **İzleme & Analitik** - Prometheus, Grafana, kapsamlı loglama

## 🤖 AI/ML Performansı

### Model Performansı

| Model | Doğruluk | Gecikme | Güven | Diller |
|-------|----------|---------|-------|--------|
| **OpenAI Whisper** | 95.2% | 0.8s | 0.89 | 50+ |
| **Wav2Vec2** | 87.5% | 1.2s | 0.82 | İngilizce |

### Örnek Transkripsiyonlar

**Yüksek Kaliteli Ses:**
- Giriş: "Merhaba, bu VoiceBridge sisteminin bir testidir."
- Çıkış: "Merhaba, bu VoiceBridge sisteminin bir testidir."
- Güven: 0.96 | İşleme Süresi: 0.7s

**Gürültülü Ses:**
- Giriş: [Arka plan gürültüsü ile ses]
- Çıkış: "Merhaba, bu VoiceBridge sisteminin bir testidir."
- Güven: 0.78 | İşleme Süresi: 1.1s

### MLflow Dashboard
- **Yerel**: http://localhost:5000
- **Özellikler**: Model versiyonlama, deney takibi, performans metrikleri
- **TensorFlow ve PyTorch model entegrasyonu** özel model dağıtımı için

📊 [Detaylı ML Performans Raporu](docs/ml_performance.md)

## 🛠️ Teknoloji Yığını

### Frontend
- React 18, JavaScript, gerçek zamanlı UI

### Backend  
- FastAPI, Python 3.11+, WebSocket streaming

### AI/ML
- OpenAI Whisper, Wav2Vec2 gerçek zamanlı transkripsiyon için
- **TensorFlow & PyTorch ile eğitilmiş özel ML modelleri**
- **scikit-learn ile veri ön işleme ve özellik mühendisliği**
- MLflow, Weights & Biases deney takibi için

### Altyapı
- Docker, Kubernetes, Kafka, Celery, Redis

## 📁 Proje Yapısı

```
VoiceBridge_Realtime_App/
├── src/                    # Backend kaynak kodu
│   ├── services/          # İş mantığı ve ML servisleri
│   ├── routes/            # API endpoint'leri
│   ├── models/            # Veri modelleri
│   └── tasks/             # Arka plan görevleri
├── frontend/              # React uygulaması
├── tests/                 # Test paketi
├── docs/                  # Dokümantasyon
├── deployment/            # Docker & K8s konfigürasyonları
└── scripts/               # Yardımcı scriptler
```

📖 [Detaylı Proje Yapısı](docs/architecture.md)

## 🧪 Test & Geliştirme

```bash
make test          # Tüm testleri çalıştır (85%+ kapsam)
make lint          # Kod linting
make format        # Kod formatlama
```

📋 [Test Dokümantasyonu](tests/README.md)

## 📚 Dokümantasyon

- 📖 [Mimari Kılavuzu](docs/architecture.md)
- 🤖 [ML Performans Raporu](docs/ml_performance.md)
- 🧪 [Test Dokümantasyonu](tests/README.md)
- 🚀 [Dağıtım Kılavuzu](docs/deployment.md)
- 📋 [API Dokümantasyonu](http://localhost:8000/docs)

## 🔧 Konfigürasyon

### Ortam Değişkenleri
```bash
# Gerekli
OPENAI_API_KEY=your_openai_api_key_here

# Opsiyonel
PORT=8000
HOST=127.0.0.1
DATABASE_URL=sqlite:///./voicebridge.db
REDIS_URL=redis://localhost:6379
MLFLOW_TRACKING_URI=http://localhost:5000
```

📝 [Tam Konfigürasyon Kılavuzu](docs/configuration.md)

## 📋 Mevcut Komutlar

| Komut | Açıklama |
|-------|----------|
| `make install` | Tüm bağımlılıkları kur |
| `make dev` | Geliştirme sunucularını başlat |
| `make test` | Tüm testleri çalıştır |
| `make lint` | Kod linting |
| `make format` | Kod formatlama |
| `make docker-up` | Docker servislerini başlat |
| `make health` | Servis sağlığını kontrol et |

📋 [Tam Komut Referansı](docs/commands.md)

## 🤝 Katkıda Bulunma & Destek

### 🚀 Katkıda Bulunma
1. **Repository'yi fork edin**
2. **Özellik dalı oluşturun**: `git checkout -b feature/amazing-feature`
3. **Değişikliklerinizi yapın**
4. **Testleri çalıştırın**: `make test`
5. **Pull request gönderin**

**Detaylı kılavuzlar için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasına bakın**

### 💬 Destek
- **🐛 Sorunlar**: [GitHub Issues](https://github.com/KaracaDeer/VoiceBridge_Realtime_App/issues)
- **💭 Tartışmalar**: [GitHub Discussions](https://github.com/KaracaDeer/VoiceBridge_Realtime_App/discussions)
- **💼 LinkedIn**: [Fatma Karaca Erdogan](https://www.linkedin.com/in/fatma-karaca-erdogan-32201a378/)
- **📧 E-posta**: fatmakaracaerdogan@gmail.com

## 📝 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

* **OpenAI** - En son teknoloji AI modelleri sağladığı için
* **FastAPI** - Yüksek performanslı backend framework'ü için
* **React Ekibi** - Harika frontend kütüphanesi için
* **MLflow** - Model takibi ve dağıtımı için
* **Prometheus & Grafana** - İzleme ve gözlemlenebilirlik için
* **Docker** - Konteynerleştirme ve dağıtım için