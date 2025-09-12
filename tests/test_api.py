"""
Simple test script to verify VoiceBridge API functionality.
"""
import json
import threading
import time

import requests
import websocket


def test_health_endpoint():
    """Test the health check endpoint."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
            assert True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            assert False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False


def test_root_endpoint():
    """Test the root endpoint."""
    print("🔍 Testing root endpoint...")
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
            assert True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            assert False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False


def test_websocket_connection():
    """Test WebSocket connection."""
    print("🔍 Testing WebSocket connection...")

    def on_message(ws, message):
        print(f"📨 Received message: {message}")
        data = json.loads(message)
        if data.get("type") == "acknowledgment":
            print("✅ WebSocket acknowledgment received")
        ws.close()

    def on_error(ws, error):
        print(f"❌ WebSocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("🔌 WebSocket connection closed")

    def on_open(ws):
        print("🔌 WebSocket connection opened")
        # Send a test message
        test_audio = b"fake_audio_data_for_testing"
        ws.send(test_audio, opcode=websocket.ABNF.OPCODE_BINARY)

    try:
        ws = websocket.WebSocketApp(
            "ws://localhost:8000/ws/test_client",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )

        # Run WebSocket in a separate thread
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()

        # Wait for connection to complete
        time.sleep(3)

        print("✅ WebSocket test completed")
        assert True

    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
        return False


def test_api_docs():
    """Test API documentation endpoint."""
    print("🔍 Testing API documentation...")
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
            assert True
        else:
            print(f"❌ API documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API documentation error: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 VoiceBridge API Test Suite")
    print("=" * 40)

    tests = [
        test_health_endpoint,
        test_root_endpoint,
        test_api_docs,
        test_websocket_connection,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
        print()

    print("📊 Test Results")
    print("=" * 40)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All tests passed! VoiceBridge API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the service status.")
        print("   Run: docker-compose logs -f")


if __name__ == "__main__":
    main()
