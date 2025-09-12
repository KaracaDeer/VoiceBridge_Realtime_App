#!/usr/bin/env python3
"""
Simple error checker script
"""

import os
import subprocess
import sys


def run_check(command, name):
    """Run a check and return result"""
    print(f"\n🔍 Running {name}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )

        if result.returncode == 0:
            print(f"✅ {name} - PASSED")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {name} - FAILED")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return False
    except Exception as e:
        print(f"❌ {name} - ERROR: {e}")
        return False


def main():
    print("🔍 VoiceBridge Error Checker")
    print("=" * 50)

    checks = [
        ("flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics", "Critical flake8 errors"),
        (
            "flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics",
            "General flake8 linting",
        ),
        ("black --check src tests", "Black formatting check"),
        ("isort --check-only src tests", "isort import sorting"),
        ("mypy src --ignore-missing-imports --no-strict-optional", "mypy type checking"),
        (
            "pytest tests/test_api.py tests/test_simple_startup.py --maxfail=1 --disable-warnings -v --tb=short",
            "Unit tests",
        ),
    ]

    results = []
    for command, name in checks:
        result = run_check(command, name)
        results.append((name, result))

    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:30} {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} checks passed")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\n🎉 All checks passed! No errors found.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} checks failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
