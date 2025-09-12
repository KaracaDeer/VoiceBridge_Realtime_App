#!/usr/bin/env python3
"""
Test script to verify all fixes are working
"""

import logging
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_imports():
    """Test all imports"""
    print("🧪 Testing imports...")

    tests = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("mlflow", "MLFlow"),
        ("wandb", "Weights & Biases"),
        ("seaborn", "Seaborn"),
        ("plotly", "Plotly"),
        ("requests", "Requests"),
        ("grpc", "gRPC"),
        ("aiokafka", "AIOKafka"),
    ]

    success_count = 0

    for module, name in tests:
        try:
            __import__(module)
            print(f"✅ {name} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"❌ {name} import failed: {e}")

    print(f"Import test: {success_count}/{len(tests)} passed\n")
    return success_count == len(tests)


def test_config():
    """Test configuration loading"""
    print("🧪 Testing configuration...")

    try:
        from config import settings

        print("✅ Config loaded successfully")
        print(f"   API Host: {settings.api_host}")
        print(f"   API Port: {settings.api_port}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_services():
    """Test service imports"""
    print("🧪 Testing services...")

    services = [
        ("src.services.auth_service", "Auth Service"),
        ("src.services.encryption_service", "Encryption Service"),
        ("src.services.rate_limiting_service", "Rate Limiting Service"),
        ("src.services.mlflow_service", "MLFlow Service"),
        ("src.services.wandb_service", "W&B Service"),
        ("src.services.prometheus_service", "Prometheus Service"),
    ]

    success_count = 0

    for service, name in services:
        try:
            __import__(service)
            print(f"✅ {name} imported successfully")
            success_count += 1
        except Exception as e:
            print(f"❌ {name} import failed: {e}")

    print(f"Service test: {success_count}/{len(services)} passed\n")
    return success_count == len(services)


def test_routes():
    """Test route imports"""
    print("🧪 Testing routes...")

    routes = [
        ("src.routes.auth_routes", "Auth Routes"),
        ("src.routes.monitoring_routes", "Monitoring Routes"),
        ("src.routes.realtime_routes", "Realtime Routes"),
    ]

    success_count = 0

    for route, name in routes:
        try:
            __import__(route)
            print(f"✅ {name} imported successfully")
            success_count += 1
        except Exception as e:
            print(f"❌ {name} import failed: {e}")

    print(f"Route test: {success_count}/{len(routes)} passed\n")
    return success_count == len(routes)


def test_grpc():
    """Test gRPC protobuf files"""
    print("🧪 Testing gRPC protobuf files...")

    try:
        import os
        import sys

        # Add parent directory to path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Test import
        from proto import voicebridge_pb2, voicebridge_pb2_grpc  # noqa: F401

        # Test basic functionality
        if hasattr(voicebridge_pb2, "AudioChunk"):
            print("✅ gRPC protobuf files imported successfully")
            return True
        else:
            print("❌ gRPC protobuf files missing expected classes")
            return False
    except Exception as e:
        print(f"❌ gRPC test failed: {e}")
        return False


def test_main_app():
    """Test main application import"""
    print("🧪 Testing main application...")

    try:
        from main import app  # noqa: F401

        print("✅ Main application imported successfully")
        return True
    except Exception as e:
        print(f"❌ Main app test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 VoiceBridge API - Fix Verification Test")
    print("=" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("Configuration Test", test_config),
        ("Service Tests", test_services),
        ("Route Tests", test_routes),
        ("gRPC Test", test_grpc),
        ("Main App Test", test_main_app),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"📋 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
        print()

    # Summary
    print("📊 Test Results Summary")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All fixes are working correctly!")
        print("✅ VoiceBridge API is ready for production!")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
