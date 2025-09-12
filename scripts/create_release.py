#!/usr/bin/env python3
"""
GitHub Release Creation Script for VoiceBridge
"""
import os
import subprocess
import sys

from version import get_build_info, get_version


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None


def check_git_status():
    """Check git status and ensure clean working directory."""
    print("🔍 Checking git status...")

    # Check if we're in a git repository
    if not os.path.exists(".git"):
        print("❌ Not in a git repository")
        return False

    # Check for uncommitted changes
    status = run_command("git status --porcelain", "Checking for uncommitted changes")
    if status:
        print("❌ Uncommitted changes found:")
        print(status)
        return False

    print("✅ Git working directory is clean")
    return True


def create_git_tag():
    """Create a git tag for the current version."""
    version = get_version()
    tag_name = f"v{version}"

    print(f"🏷️  Creating git tag: {tag_name}")

    # Check if tag already exists
    existing_tag = run_command(f"git tag -l {tag_name}", "Checking for existing tag")
    if existing_tag:
        print(f"⚠️  Tag {tag_name} already exists")
        return tag_name

    # Create tag
    tag_message = f"Release {tag_name} - VoiceBridge Real-time Speech-to-Text API"
    result = run_command(f'git tag -a {tag_name} -m "{tag_message}"', "Creating git tag")

    if result is not None:
        print(f"✅ Tag {tag_name} created successfully")
        return tag_name
    else:
        return None


def push_to_github():
    """Push commits and tags to GitHub."""
    print("📤 Pushing to GitHub...")

    # Push commits
    result = run_command("git push origin main", "Pushing commits to GitHub")
    if result is None:
        return False

    # Push tags
    result = run_command("git push origin --tags", "Pushing tags to GitHub")
    if result is None:
        return False

    print("✅ Successfully pushed to GitHub")
    return True


def create_github_release():
    """Create a GitHub release using GitHub CLI."""
    version = get_version()
    build_info = get_build_info()
    tag_name = f"v{version}"

    print(f"🚀 Creating GitHub release: {tag_name}")

    # Check if GitHub CLI is installed
    gh_version = run_command("gh --version", "Checking GitHub CLI")
    if gh_version is None:
        print("❌ GitHub CLI not found. Please install it from: https://cli.github.com/")
        return False

    # Create release notes
    release_notes = f"""# VoiceBridge v{version}

## 🎉 Release Information
- **Version:** {build_info['version']}
- **Build Date:** {build_info['build_date']}
- **Author:** {build_info['author']}

## 📝 Description
{build_info['description']}

## ✨ Features
- Real-time speech-to-text processing
- WebSocket support for live audio streaming
- Multiple ML model support (Whisper, Wav2Vec)
- Comprehensive monitoring and logging
- Docker containerization
- RESTful API with OpenAPI documentation

## 🔧 Installation
```bash
git clone https://github.com/yourusername/voicebridge.git
cd voicebridge
pip install -r requirements.txt
python main.py
```

## 📖 Documentation
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 🐛 Bug Reports
Please report bugs and issues on the GitHub repository.

## 📄 License
This project is licensed under the MIT License.
"""

    # Create release
    release_file = f"release_notes_{version}.md"
    with open(release_file, "w", encoding="utf-8") as f:
        f.write(release_notes)

    try:
        result = run_command(
            f'gh release create {tag_name} --title "VoiceBridge v{version}" --notes-file {release_file}',
            "Creating GitHub release",
        )

        # Clean up release notes file
        os.remove(release_file)

        if result is not None:
            print(f"✅ GitHub release {tag_name} created successfully")
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ Failed to create GitHub release: {e}")
        return False


def main():
    """Main function to create a GitHub release."""
    print("🚀 VoiceBridge GitHub Release Creator")
    print("=" * 50)

    build_info = get_build_info()
    print(f"📦 Current Version: {build_info['version']}")
    print(f"📅 Build Date: {build_info['build_date']}")
    print("=" * 50)

    # Check git status
    if not check_git_status():
        print("❌ Git status check failed. Please commit your changes first.")
        sys.exit(1)

    # Create git tag
    tag_name = create_git_tag()
    if not tag_name:
        print("❌ Failed to create git tag")
        sys.exit(1)

    # Push to GitHub
    if not push_to_github():
        print("❌ Failed to push to GitHub")
        sys.exit(1)

    # Create GitHub release
    if not create_github_release():
        print("❌ Failed to create GitHub release")
        sys.exit(1)

    print("\n🎉 Release created successfully!")
    print(f"🔗 Check your GitHub repository for the new release: {tag_name}")
    print(f"📦 Version: {build_info['version']}")
    print(f"📅 Build Date: {build_info['build_date']}")


if __name__ == "__main__":
    main()
