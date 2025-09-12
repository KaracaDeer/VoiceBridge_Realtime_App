#!/usr/bin/env python3
"""
Quick production test for VoiceBridge
"""
from pathlib import Path

import requests


def test_env_file():
    """Test if .env file exists and has required keys"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("Please run: scripts\\setup_production.bat")
        return False

    print("✅ .env file exists")

    # Check for API keys
    with open(env_path, "r") as f:
        content = f.read()

    if "OPENAI_API_KEY=sk-your-" in content:
        print("⚠️  OpenAI API key needs to be updated in .env file")
    else:
        print("✅ OpenAI API key configured")

    if "WANDB_API_KEY=your-" in content:
        print("⚠️  W&B API key needs to be updated in .env file")
    else:
        print("✅ W&B API key configured")

    return True


def test_api_import():
    """Test if API can be imported"""
    try:
        from main import app  # noqa: F401

        print("✅ API imports successfully")
        return True
    except Exception as e:
        print(f"❌ API import failed: {e}")
        return False


def test_api_startup():
    """Test if API can start"""
    try:
        from fastapi.testclient import TestClient

        from main import app

        client = TestClient(app)
        response = client.get("/health")

        if response.status_code == 200:
            print("✅ API health check passed")
            data = response.json()
            print(f"   Services: {data.get('services', {})}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API startup test failed: {e}")
        return False


def test_services():
    """Test external services"""
    print("\n🔍 Testing external services...")

    # Test MLflow
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            print("✅ MLflow is running")
        else:
            print("⚠️  MLflow not responding")
    except Exception:
        print("⚠️  MLflow not running (optional)")

    # Test Redis
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
    except Exception:
        print("⚠️  Redis not running (optional)")


def main():
    """Main test function"""
    print("🚀 VoiceBridge Quick Production Test")
    print("=" * 40)

    tests = [
        ("Environment File", test_env_file),
        ("API Import", test_api_import),
        ("API Startup", test_api_startup),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1

    test_services()

    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! VoiceBridge is ready for production.")
        print("\n🚀 To start the API:")
        print("   python main.py")
        print("\n🌐 Access URLs:")
        print("   - API: http://localhost:8000")
        print("   - Docs: http://localhost:8000/docs")
        print("   - Health: http://localhost:8000/health")
    else:
        print("⚠️  Some tests failed. Check the output above.")
        print("\n🔧 Next steps:")
        print("   1. Update API keys in .env file")
        print("   2. Install missing dependencies")
        print("   3. Start required services")


if __name__ == "__main__":
    main()
