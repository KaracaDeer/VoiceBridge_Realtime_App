#!/usr/bin/env python3
"""
Production test script for VoiceBridge
Tests all services and endpoints
"""
# type: ignore
# flake8: noqa
import json
import os
import sys
from typing import Dict

import redis
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.auth_service import auth_service
from src.services.encryption_service import encryption_service


class ProductionTester:
    """Test production setup"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {}

    def test_redis_connection(self) -> bool:
        """Test Redis connection"""
        try:
            r = redis.Redis(host="localhost", port=6379, db=0)
            r.ping()
            self.results["redis"] = True
            print("✓ Redis connection successful")
            return True
        except Exception as e:
            self.results["redis"] = False
            print(f"✗ Redis connection failed: {e}")
            return False

    def test_mlflow_connection(self) -> bool:
        """Test MLflow connection"""
        try:
            response = requests.get("http://localhost:5000/health", timeout=15)
            if response.status_code == 200:
                self.results["mlflow"] = True
                print("✓ MLflow connection successful")
                return True
            else:
                self.results["mlflow"] = False
                print(f"✗ MLflow connection failed: {response.status_code}")
                return False
        except Exception as e:
            self.results["mlflow"] = False
            print(f"✗ MLflow connection failed: {e}")
            return False

    def test_api_health(self) -> bool:
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.results["api_health"] = True
                print("✓ API health check successful")
                print(f"  Services: {data.get('services', {})}")
                return True
            else:
                self.results["api_health"] = False
                print(f"✗ API health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.results["api_health"] = False
            print(f"✗ API health check failed: {e}")
            return False

    def test_api_docs(self) -> bool:
        """Test API documentation"""
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.results["api_docs"] = True
                print("✓ API documentation accessible")
                return True
            else:
                self.results["api_docs"] = False
                print(f"✗ API documentation failed: {response.status_code}")
                return False
        except Exception as e:
            self.results["api_docs"] = False
            print(f"✗ API documentation failed: {e}")
            return False

    def test_encryption_service(self) -> bool:
        """Test encryption service"""
        try:
            test_data = b"test audio data"
            encrypted_data, metadata = encryption_service.encrypt_audio_file(test_data, "test.wav")
            decrypted_data, _ = encryption_service.decrypt_audio_file(encrypted_data, metadata)

            if decrypted_data == test_data:
                self.results["encryption"] = True
                print("✓ Encryption service working")
                return True
            else:
                self.results["encryption"] = False
                print("✗ Encryption service failed: data mismatch")
                return False
        except Exception as e:
            self.results["encryption"] = False
            print(f"✗ Encryption service failed: {e}")
            return False

    def test_auth_service(self) -> bool:
        """Test authentication service"""
        try:
            user_data = {"id": 1, "username": "testuser"}
            access_token = auth_service.create_access_token(user_data)
            payload = auth_service.verify_token(access_token, "access")

            if payload.get("sub") == "1":
                self.results["auth"] = True
                print("✓ Authentication service working")
                return True
            else:
                self.results["auth"] = False
                print("✗ Authentication service failed: invalid payload")
                return False
        except Exception as e:
            self.results["auth"] = False
            print(f"✗ Authentication service failed: {e}")
            return False

    def test_websocket_connection(self) -> bool:
        """Test WebSocket connection"""
        try:
            import websocket

            def on_message(ws, message):
                print(f"✓ WebSocket message received: {message}")
                ws.close()

            def on_error(ws, error):
                print(f"✗ WebSocket error: {error}")

            def on_close(ws, close_status_code, close_msg):
                print("WebSocket connection closed")

            def on_open(ws):
                print("✓ WebSocket connection established")
                ws.send(json.dumps({"type": "ping"}))

            ws = websocket.WebSocketApp(
                "ws://localhost:8000/ws/test_client",
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )

            # Run for 5 seconds
            import threading
            import time

            def close_after_delay():
                time.sleep(5)
                ws.close()

            thread = threading.Thread(target=close_after_delay)
            thread.daemon = True
            thread.start()

            ws.run_forever()
            self.results["websocket"] = True
            return True

        except Exception as e:
            self.results["websocket"] = False
            print(f"✗ WebSocket test failed: {e}")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all production tests"""
        print("VoiceBridge Production Test Suite")
        print("=" * 40)

        # Test external services
        self.test_redis_connection()
        self.test_mlflow_connection()

        # Test API
        self.test_api_health()
        self.test_api_docs()

        # Test internal services
        self.test_encryption_service()
        self.test_auth_service()

        # Test WebSocket (optional)
        try:
            self.test_websocket_connection()
        except ImportError:
            print("⚠ WebSocket test skipped (websocket-client not installed)")
            self.results["websocket"] = None

        return self.results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 40)
        print("PRODUCTION TEST SUMMARY")
        print("=" * 40)

        total_tests = len([k for k, v in self.results.items() if v is not None])
        passed_tests = len([k for k, v in self.results.items() if v is True])

        for test_name, result in self.results.items():
            if result is True:
                print(f"✓ {test_name}: PASSED")
            elif result is False:
                print(f"✗ {test_name}: FAILED")
            else:
                print(f"⚠ {test_name}: SKIPPED")

        print(f"\nResults: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 All tests passed! Production setup is ready.")
        else:
            print("⚠ Some tests failed. Check the logs above.")


def main():
    """Main test function"""
    tester = ProductionTester()
    tester.run_all_tests()
    tester.print_summary()


if __name__ == "__main__":
    main()
