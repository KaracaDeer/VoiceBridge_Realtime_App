#!/usr/bin/env python3
"""
Simple test script to verify CI setup
"""

import subprocess
import sys


def test_tool(tool_name, command):
    """Test if a tool is available and working"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {tool_name} - OK")
            return True
        else:
            print(f"❌ {tool_name} - FAILED")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {tool_name} - ERROR: {e}")
        return False


def main():
    print("Testing CI tools setup...")
    print("=" * 40)

    tools = [
        ("Python", "python --version"),
        ("pip", "pip --version"),
        ("flake8", "flake8 --version"),
        ("black", "black --version"),
        ("isort", "isort --version"),
        ("mypy", "mypy --version"),
        ("pytest", "pytest --version"),
        ("bandit", "bandit --version"),
        ("safety", "safety --version"),
    ]

    passed = 0
    total = len(tools)

    for tool_name, command in tools:
        if test_tool(tool_name, command):
            passed += 1

    print("=" * 40)
    print(f"Results: {passed}/{total} tools working")

    if passed == total:
        print("🎉 All CI tools are ready!")
        return 0
    else:
        print("⚠️  Some tools are missing. Install them with:")
        print("   pip install -r requirements-ci.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
