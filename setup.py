"""
Setup script for VoiceBridge real-time speech-to-text application.
"""
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_docker():
    """Check if Docker is installed and running."""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        print("✅ Docker and Docker Compose are available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker or Docker Compose not found. Please install Docker Desktop.")
        return False


def create_kafka_topics():
    """Create Kafka topics for the application."""
    topics = ["audio_stream", "transcription_results"]

    for topic in topics:
        command = f"""
        docker exec voicebridge_kafka kafka-topics --create \
            --topic {topic} \
            --bootstrap-server localhost:9092 \
            --partitions 3 \
            --replication-factor 1 \
            --if-not-exists
        """
        run_command(command, f"Creating Kafka topic: {topic}")


def wait_for_services():
    """Wait for services to be ready."""
    print("\n⏳ Waiting for services to start...")

    services = [
        ("Redis", "docker exec voicebridge_redis redis-cli ping"),
        ("Kafka", "docker exec voicebridge_kafka kafka-topics --list --bootstrap-server localhost:9092"),
    ]

    for service_name, command in services:
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                subprocess.run(command, shell=True, check=True, capture_output=True)
                print(f"✅ {service_name} is ready")
                break
            except subprocess.CalledProcessError:
                if attempt < max_attempts - 1:
                    print(f"⏳ Waiting for {service_name}... ({attempt + 1}/{max_attempts})")
                    import time

                    time.sleep(2)
                else:
                    print(f"❌ {service_name} failed to start")
                    return False

    return True


def main():
    """Main setup function."""
    from version import get_build_info

    build_info = get_build_info()
    print("🚀 VoiceBridge Real-time Speech-to-Text Setup")
    print("=" * 50)
    print(f"📦 Version: {build_info['version']}")
    print(f"📅 Build Date: {build_info['build_date']}")
    print(f"👤 Author: {build_info['author']}")
    print(f"📝 Description: {build_info['description']}")
    print("=" * 50)

    # Check Docker
    if not check_docker():
        sys.exit(1)

    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("\n📝 Creating .env file...")
        env_content = """# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_AUDIO_TOPIC=audio_stream
KAFKA_TRANSCRIPTION_TOPIC=transcription_results

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# Audio Processing Configuration
MAX_AUDIO_SIZE_MB=10
SUPPORTED_AUDIO_FORMATS=wav,mp3,m4a,flac
SAMPLE_RATE=16000
"""
        env_file.write_text(env_content)
        print("✅ .env file created")

    # Start services with Docker Compose
    if not run_command("docker-compose up -d", "Starting services with Docker Compose"):
        sys.exit(1)

    # Wait for services to be ready
    if not wait_for_services():
        print("❌ Some services failed to start. Please check the logs.")
        sys.exit(1)

    # Create Kafka topics
    create_kafka_topics()

    print("\n🎉 Setup completed successfully!")
    print("\n📋 Service URLs:")
    print("  • API: http://localhost:8000")
    print("  • API Docs: http://localhost:8000/docs")
    print("  • Celery Flower: http://localhost:5555")
    print("  • Redis: localhost:6379")
    print("  • Kafka: localhost:9092")

    print("\n🔧 Useful commands:")
    print("  • View logs: docker-compose logs -f")
    print("  • Stop services: docker-compose down")
    print("  • Restart services: docker-compose restart")
    print("  • Scale workers: docker-compose up -d --scale celery_worker=3")

    print("\n📖 Next steps:")
    print("  1. Test the API: curl http://localhost:8000/health")
    print("  2. Upload audio: POST /transcribe endpoint")
    print("  3. Connect WebSocket: ws://localhost:8000/ws/{client_id}")


if __name__ == "__main__":
    main()
