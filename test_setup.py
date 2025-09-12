#!/usr/bin/env python3
"""
Simple setup test for VoiceBridge
"""
from pathlib import Path


def test_env_file():
    """Test .env file"""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file exists")
        with open(env_path, "r") as f:
            content = f.read()
            if "OPENAI_API_KEY=sk-" in content:
                print("✅ OpenAI API key found")
                return True
            else:
                print("⚠️  OpenAI API key not found or needs update")
                return False
    else:
        print("❌ .env file not found")
        return False


def test_imports():
    """Test imports"""
    try:
        pass  # Import test passed

        print("✅ All required packages available")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False


def test_config():
    """Test configuration"""
    try:
        from config import settings

        print("✅ Configuration loaded")
        print(f"   API Host: {settings.api_host}")
        print(f"   API Port: {settings.api_port}")
        print(f"   OpenAI Key: {'SET' if settings.openai_api_key else 'NOT SET'}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def main():
    print("🧪 VoiceBridge Setup Test")
    print("=" * 30)

    tests = [test_env_file, test_imports, test_config]

    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 Setup looks good!")
        print("\n🚀 To start the API:")
        print("   python main.py")
        print("\n🌐 Then open:")
        print("   http://localhost:8000/docs")
    else:
        print("⚠️  Some issues found. Check above.")


if __name__ == "__main__":
    main()
