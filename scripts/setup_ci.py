#!/usr/bin/env python3
"""
CI/CD Setup Script
This script installs CI/CD tools and sets up pre-commit hooks.
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, cwd: str = None) -> bool:
    """Run command and return success status."""
    if cwd is None:
        cwd = str(Path(__file__).parent.parent)

    print(f"🔄 Running: {command}")

    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Success")
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def setup_ci_environment():
    """Setup CI environment."""
    print("🚀 Setting up CI/CD Environment")
    print("=" * 50)

    # 1. Create virtual environment (optional)
    print("\n📦 Setting up virtual environment...")
    if not os.path.exists("venv"):
        if not run_command("python -m venv venv"):
            print("⚠️  Virtual environment creation failed, continuing with system Python")
    else:
        print("✅ Virtual environment already exists")

    # 2. Install dependencies
    print("\n📦 Installing dependencies...")
    if not run_command("pip install -r requirements.txt"):
        print("❌ Failed to install dependencies")
        return False

    # 3. Install pre-commit
    print("\n🔧 Installing pre-commit...")
    if not run_command("pip install pre-commit"):
        print("❌ Failed to install pre-commit")
        return False

    # 4. Install pre-commit hooks
    print("\n🪝 Installing pre-commit hooks...")
    if not run_command("pre-commit install"):
        print("❌ Failed to install pre-commit hooks")
        return False

    # 5. Test pre-commit hooks
    print("\n🧪 Testing pre-commit hooks...")
    if not run_command("pre-commit run --all-files"):
        print("⚠️  Pre-commit hooks found issues, but setup is complete")

    print("\n🎉 CI/CD setup completed!")
    print("\n📋 Next steps:")
    print("1. Run 'python scripts/local_ci.py' to test the full pipeline")
    print("2. Make a test commit to verify pre-commit hooks work")
    print("3. Push to GitHub to test Actions")

    return True


def main():
    """Main function."""
    success = setup_ci_environment()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
