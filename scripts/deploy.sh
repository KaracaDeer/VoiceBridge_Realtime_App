#!/bin/bash

# VoiceBridge Deployment Script
# This script deploys the VoiceBridge application

set -e  # Exit on any error

echo "🚀 Starting VoiceBridge deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_warning "Please update .env file with your actual configuration values."
    else
        print_error ".env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p storage/audio
mkdir -p storage/metadata

# Set proper permissions
chmod 755 logs data storage
chmod 755 storage/audio storage/metadata

# Build and start services
print_status "Building and starting services..."
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check Redis
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    print_status "✅ Redis is running"
else
    print_error "❌ Redis is not responding"
fi

# Check Backend API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ Backend API is running"
else
    print_warning "⚠️  Backend API is not responding (may still be starting)"
fi

# Check Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "✅ Frontend is running"
else
    print_warning "⚠️  Frontend is not responding (may still be starting)"
fi

# Check MLFlow
if curl -f http://localhost:5000 > /dev/null 2>&1; then
    print_status "✅ MLFlow is running"
else
    print_warning "⚠️  MLFlow is not responding (may still be starting)"
fi

# Check Prometheus
if curl -f http://localhost:9090 > /dev/null 2>&1; then
    print_status "✅ Prometheus is running"
else
    print_warning "⚠️  Prometheus is not responding (may still be starting)"
fi

# Check Grafana
if curl -f http://localhost:3001 > /dev/null 2>&1; then
    print_status "✅ Grafana is running"
else
    print_warning "⚠️  Grafana is not responding (may still be starting)"
fi

# Display service URLs
echo ""
print_status "🎉 Deployment completed!"
echo ""
echo "Service URLs:"
echo "  Frontend:        http://localhost:3000"
echo "  Backend API:     http://localhost:8000"
echo "  API Docs:        http://localhost:8000/docs"
echo "  MLFlow:          http://localhost:5000"
echo "  Prometheus:      http://localhost:9090"
echo "  Grafana:         http://localhost:3001 (admin/admin)"
echo "  Celery Flower:   http://localhost:5555"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f [service_name]"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "To restart services:"
echo "  docker-compose restart [service_name]"
