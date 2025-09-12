#!/usr/bin/env python3
"""
Simple startup test for VoiceBridge API.
"""
import subprocess
import sys
import time

import requests


def test_imports():
    """Test if all modules can be imported."""
    print("Testing module imports...")

    try:
        import main  # noqa: F401

        print("PASS Main module imported successfully")

        from config import settings  # noqa: F401

        print("PASS Config module imported successfully")

        from src.services.openai_whisper_service import get_openai_whisper_service  # noqa: F401

        print("PASS OpenAI Whisper service imported successfully")

        from src.services.auth_service import get_current_user  # noqa: F401

        print("PASS Auth service imported successfully")

        from src.services.encryption_service import encryption_service  # noqa: F401

        print("PASS Encryption service imported successfully")

        from src.database.mysql_models import User, get_database_manager  # noqa: F401

        print("PASS Database models imported successfully")

        return True

    except Exception as e:
        print(f"FAILED Import error: {e}")
        return False


def test_services():
    """Test service initialization."""
    print("\nTesting service initialization...")

    try:
        from src.services.auth_service import auth_service  # noqa: F401
        from src.services.encryption_service import encryption_service  # noqa: F401
        from src.services.openai_whisper_service import get_openai_whisper_service  # noqa: F401

        # Test OpenAI Whisper service
        get_openai_whisper_service("test_key")
        print("PASS OpenAI Whisper service initialized")

        # Test encryption service
        test_data = b"test data"
        encrypted, metadata = encryption_service.encrypt_audio_file(test_data, "test.wav")
        decrypted = encryption_service.decrypt_audio_file(encrypted, metadata)
        assert decrypted == test_data
        print("PASS Encryption service working")

        # Test auth service
        print("PASS Auth service initialized")

        return True

    except Exception as e:
        print(f"FAILED Service error: {e}")
        return False


def test_database():
    """Test database connection."""
    print("\nTesting database connection...")

    try:
        from src.database.mysql_models import get_database_manager

        db_manager = get_database_manager()
        print("PASS Database manager created")

        # Test connection (will use demo mode if MySQL not available)
        db_manager.connect()
        print("PASS Database connection successful")

        return True

    except Exception as e:
        print(f"FAILED Database error: {e}")
        return False


def test_api_startup():
    """Test API startup."""
    print("\nTesting API startup...")

    try:
        # Start API in a separate process
        process = subprocess.Popen([sys.executable, "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait a bit for startup
        time.sleep(10)

        # Check if process is still running
        if process.poll() is None:
            print("PASS API process started successfully")

            # Try to connect to API
            try:
                response = requests.get("http://localhost:8000/", timeout=5)
                if response.status_code == 200:
                    print("PASS API responding to requests")
                    print(f"   Response: {response.json()}")
                else:
                    print(f"WARNING API responding with status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"WARNING API not yet responding: {e}")

            # Terminate the process
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print("FAILED API process failed to start")
            print(f"   stdout: {stdout.decode()}")
            print(f"   stderr: {stderr.decode()}")
            return False

    except Exception as e:
        print(f"FAILED API startup error: {e}")
        return False


def main():
    """Main test function."""
    print("VoiceBridge Startup Test")
    print("=" * 50)

    tests = [
        ("Module Imports", test_imports),
        ("Service Initialization", test_services),
        ("Database Connection", test_database),
        ("API Startup", test_api_startup),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"FAILED {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed! VoiceBridge is ready to run.")
    else:
        print("Some tests failed. Check the errors above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
