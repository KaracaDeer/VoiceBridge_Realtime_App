#!/usr/bin/env python3
"""
Local CI/CD Pipeline Script
Mirrors the exact steps from GitHub Actions to test locally before pushing.

This script runs the same checks that GitHub Actions runs:
- Linting with flake8
- Code formatting with black
- Import sorting with isort
- Type checking with mypy
- Unit tests with pytest
- Security checks with bandit and safety
"""

import subprocess
import sys
import time
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_step(step_name):
    """Print a step header"""
    print(f"\n{Colors.YELLOW}🔧 {step_name}{Colors.END}")
    print(f"{Colors.YELLOW}{'-'*50}{Colors.END}")


def run_command(command, description, allow_failure=False):
    """Run a command and handle the result"""
    print(f"Running: {command}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent)

        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ {description} - PASSED{Colors.END}")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            if allow_failure:
                print(f"{Colors.YELLOW}⚠️  {description} - FAILED (allowed){Colors.END}")
                if result.stderr.strip():
                    print(f"Error: {result.stderr.strip()}")
                return True
            else:
                print(f"{Colors.RED}❌ {description} - FAILED{Colors.END}")
                if result.stderr.strip():
                    print(f"Error: {result.stderr.strip()}")
                if result.stdout.strip():
                    print(f"Output: {result.stdout.strip()}")
                return False

    except Exception as e:
        print(f"{Colors.RED}❌ {description} - ERROR: {e}{Colors.END}")
        return False


def check_dependencies():
    """Check if all required tools are installed"""
    print_step("Checking Dependencies")

    tools = [
        ("python", "Python interpreter"),
        ("pip", "Python package manager"),
        ("flake8", "Linting tool"),
        ("black", "Code formatter"),
        ("isort", "Import sorter"),
        ("mypy", "Type checker"),
        ("pytest", "Testing framework"),
        ("bandit", "Security linter"),
        ("safety", "Security checker"),
    ]

    all_installed = True
    for tool, description in tools:
        if run_command(f"{tool} --version", f"Checking {description}", allow_failure=True):
            continue
        else:
            print(f"{Colors.RED}❌ {tool} is not installed. Please install it first.{Colors.END}")
            all_installed = False

    return all_installed


def run_linting():
    """Run flake8 linting (same as GitHub Actions)"""
    print_step("Linting with flake8")

    # Critical errors check
    critical_check = run_command(
        "flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics", "Critical flake8 errors check"
    )

    # General linting check
    run_command(
        "flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics",
        "General flake8 linting check",
        allow_failure=True,
    )

    return critical_check


def run_formatting():
    """Run black formatting check"""
    print_step("Code Formatting with black")

    return run_command("black --check src tests", "Black formatting check")


def run_import_sorting():
    """Run isort import sorting check"""
    print_step("Import Sorting with isort")

    return run_command("isort --check-only src tests", "isort import sorting check")


def run_type_checking():
    """Run mypy type checking"""
    print_step("Type Checking with mypy")

    return run_command("mypy src --ignore-missing-imports --no-strict-optional", "mypy type checking")


def run_tests():
    """Run unit tests"""
    print_step("Running Unit Tests")

    return run_command(
        "pytest tests/test_api.py tests/test_simple_startup.py --maxfail=1 --disable-warnings -v --tb=short",
        "Unit tests with pytest",
    )


def run_security_checks():
    """Run security checks"""
    print_step("Security Checks")

    # Bandit security check
    run_command("bandit -r src/ -f json", "Bandit security check", allow_failure=True)

    # Safety vulnerability check
    run_command("safety check --json", "Safety vulnerability check", allow_failure=True)

    return True  # Security checks are allowed to fail in CI


def run_frontend_tests():
    """Run frontend tests (if Node.js is available)"""
    print_step("Frontend Tests")

    # Check if Node.js is available
    if not run_command("node --version", "Checking Node.js", allow_failure=True):
        print(f"{Colors.YELLOW}⚠️  Node.js not available, skipping frontend tests{Colors.END}")
        return True

    # Check if npm is available
    if not run_command("npm --version", "Checking npm", allow_failure=True):
        print(f"{Colors.YELLOW}⚠️  npm not available, skipping frontend tests{Colors.END}")
        return True

    # Install frontend dependencies
    install_check = run_command("cd frontend && npm ci", "Installing frontend dependencies", allow_failure=True)

    if not install_check:
        print(f"{Colors.YELLOW}⚠️  Frontend dependencies installation failed, skipping tests{Colors.END}")
        return True

    # Run frontend tests
    run_command("cd frontend && npm test -- --coverage --watchAll=false", "Frontend tests", allow_failure=True)

    return True  # Frontend tests are optional


def main():
    """Main CI pipeline function"""
    start_time = time.time()

    print_header("VoiceBridge Local CI/CD Pipeline")
    print(f"{Colors.BLUE}This script runs the same checks as GitHub Actions{Colors.END}")
    print(f"{Colors.BLUE}Run this before pushing to catch issues early!{Colors.END}")

    # Check dependencies first
    if not check_dependencies():
        print(f"\n{Colors.RED}❌ Some dependencies are missing. Please install them first.{Colors.END}")
        print(f"{Colors.YELLOW}Run: pip install -r requirements-ci.txt{Colors.END}")
        sys.exit(1)

    # Run all checks
    checks = [
        ("Linting", run_linting),
        ("Code Formatting", run_formatting),
        ("Import Sorting", run_import_sorting),
        ("Type Checking", run_type_checking),
        ("Unit Tests", run_tests),
        ("Security Checks", run_security_checks),
        ("Frontend Tests", run_frontend_tests),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"{Colors.RED}❌ {check_name} failed with exception: {e}{Colors.END}")
            results.append((check_name, False))

    # Print summary
    end_time = time.time()
    duration = end_time - start_time

    print_header("CI Pipeline Results")

    passed = 0
    total = len(results)

    for check_name, result in results:
        status = f"{Colors.GREEN}✅ PASSED{Colors.END}" if result else f"{Colors.RED}❌ FAILED{Colors.END}"
        print(f"{check_name:20} {status}")
        if result:
            passed += 1

    print(f"\n{Colors.BOLD}Summary:{Colors.END}")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print(f"Duration: {duration:.2f} seconds")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All checks passed! Ready to push to GitHub.{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some checks failed. Please fix them before pushing.{Colors.END}")
        print(f"{Colors.YELLOW}💡 Run individual commands to see detailed error messages.{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
