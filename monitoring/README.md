# Monitoring Setup

This directory contains monitoring configuration files for Prometheus and Grafana.

## Quick Start

### 1. Start Prometheus
```bash
# Using Docker Compose
docker-compose -f docker-compose.monitoring.yml up -d prometheus

# Or manually
prometheus --config.file=prometheus/prometheus.yml --web.listen-address=:9090
```

### 2. Start Grafana
```bash
# Using Docker Compose
docker-compose -f docker-compose.monitoring.yml up -d grafana

# Or manually
grafana-server --config grafana/grafana.ini
```

### 3. Access Dashboards
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Configuration Files

### Prometheus
- `prometheus/prometheus.yml` - Main Prometheus configuration
- `prometheus/rules.yml` - Alerting rules

### Grafana
- `grafana/grafana.ini` - Grafana server configuration
- `grafana/datasources.yml` - Data source configurations
- `grafana/dashboard.json` - Main dashboard (moved to docs/monitoring/)

## Docker Compose Setup

Use the provided `docker-compose.monitoring.yml`:

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Stop monitoring stack
docker-compose -f docker-compose.monitoring.yml down

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

The compose file includes:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards  
- **Node Exporter**: System metrics (optional)

## Metrics Collection

The application exposes metrics on `/metrics` endpoint:
- API request counts and durations
- Database connection metrics
- System resource usage
- Custom business metrics

## Alerting

Configure alerts in `prometheus/rules.yml`:
- High error rates
- Slow response times
- Resource usage thresholds
- Service availability

## Dashboard Import

1. Access Grafana at http://localhost:3000
2. Go to "+" → "Import"
3. Upload `docs/monitoring/grafana-dashboard.json`
4. Configure data source (Prometheus)

## Troubleshooting

### Common Issues
- **Port conflicts**: Change ports in docker-compose.yml
- **Permission issues**: Check file permissions on config files
- **Data persistence**: Mount volumes for data directories

### Logs
```bash
# View Prometheus logs
docker logs prometheus

# View Grafana logs
docker logs grafana
```
