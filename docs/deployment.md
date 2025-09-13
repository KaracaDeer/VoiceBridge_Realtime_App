# Deployment Guide

## Docker Deployment

### Development Mode
```bash
# Start basic services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Mode
```bash
# Start production stack
docker-compose -f docker-compose.production.yml up -d

# Start with monitoring
docker-compose -f docker-compose.production.yml -f docker-compose.monitoring.yml up -d
```

### Monitoring Stack
```bash
# Start monitoring services
docker-compose -f docker-compose.monitoring.yml up -d
```

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster
- kubectl configured
- Helm (optional)

### Deploy with kubectl
```bash
# Apply configurations
kubectl apply -f deployment/kubernetes/

# Check status
kubectl get pods
kubectl get services
```

### Deploy with Helm
```bash
# Install with Helm
helm install voicebridge ./deployment/kubernetes/helm/

# Upgrade
helm upgrade voicebridge ./deployment/kubernetes/helm/
```

## Environment Configuration

### Required Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
```

### Optional Variables
```bash
PORT=8000
HOST=0.0.0.0
MLFLOW_TRACKING_URI=http://mlflow:5000
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
```

## Health Checks

### Service Health
```bash
# Check API health
curl http://localhost:8000/health

# Check Docker services
docker-compose ps

# Check Kubernetes pods
kubectl get pods -l app=voicebridge
```

### Monitoring Access
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **MLflow**: http://localhost:5000
- **Flower**: http://localhost:5555

## Scaling

### Horizontal Scaling
```bash
# Scale backend replicas
kubectl scale deployment voicebridge-backend --replicas=3

# Scale with Docker Compose
docker-compose up -d --scale backend=3
```

### Load Balancing
- Nginx configuration included
- Kubernetes ingress ready
- Auto-scaling policies configured

## Security

### SSL/TLS
- Certificates in `deployment/ssl/`
- Nginx SSL configuration
- Kubernetes TLS secrets

### Network Security
- Firewall rules
- Network policies
- Service mesh ready (Istio)

## Backup & Recovery

### Database Backup
```bash
# MySQL backup
mysqldump -u user -p database > backup.sql

# MongoDB backup
mongodump --uri="mongodb://host:port/database"
```

### Configuration Backup
```bash
# Backup configurations
tar -czf config-backup.tar.gz deployment/
```

## Troubleshooting

### Common Issues
1. **Port conflicts**: Check port availability
2. **Memory issues**: Increase container memory limits
3. **Database connection**: Verify connection strings
4. **API key issues**: Check OpenAI API key validity

### Logs
```bash
# Docker logs
docker-compose logs -f service-name

# Kubernetes logs
kubectl logs -f deployment/voicebridge-backend
```

### Performance Tuning
- Adjust container resources
- Optimize database queries
- Configure caching strategies
- Monitor resource usage
