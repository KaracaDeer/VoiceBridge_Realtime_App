#!/usr/bin/env python3
"""
Simple API test to verify basic functionality
"""
import uvicorn

from main import app

if __name__ == "__main__":
    print("🚀 Starting VoiceBridge API...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 Documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("=" * 50)

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=False)
    except KeyboardInterrupt:
        print("\n🛑 API stopped by user")
    except Exception as e:
        print(f"❌ Error starting API: {e}")
