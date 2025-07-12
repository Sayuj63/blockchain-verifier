#!/usr/bin/env python3
"""
Validation Script for Blockchain Verifier

This script validates the deployment of the Blockchain Verifier application
by testing key API endpoints and verifying expected responses.

Usage:
    python validate.py [--url URL] [--skip-server-check] [--verbose]

Options:
    --url URL               The base URL of the deployed application (default: from TEST_URL env var or http://localhost:8000)
    --skip-server-check     Skip checking if server is running before tests
    --verbose, -v           Show detailed information including response bodies
"""

import requests
import os
import socket
import sys
import json
import argparse
from urllib.parse import urlparse

# ANSI color codes
COLORS = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'reset': '\033[0m',
    'bold': '\033[1m'
}

def colorize(text, color):
    """Add color to text if output is to a terminal."""
    if sys.stdout.isatty():
        return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"
    return text

def is_server_running(host, port, timeout=2):
    """Check if server is running at the specified host and port"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except Exception as e:
        print(colorize(f"Error checking server: {str(e)}", 'red'))
        return False

def parse_url(url):
    """Parse URL to extract host and port"""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        return host, port
    except Exception as e:
        print(colorize(f"Error parsing URL: {str(e)}", 'red'))
        return 'localhost', 80

def test_deployment(base_url=None, skip_server_check=False, verbose=False):
    """Run validation tests against the deployed application"""
    # Get base URL from environment variable or use default
    if not base_url:
        base_url = os.getenv("TEST_URL", "http://localhost:8000")
    
    # Ensure base_url has proper format
    if not base_url.startswith("http"):
        base_url = f"http://{base_url}"
    
    # Check if server is running
    if not skip_server_check:
        host, port = parse_url(base_url)
        if not is_server_running(host, port):
            print(colorize(f"\nERROR: Server not running at {host}:{port}", 'red'))
            print(colorize("Please start the server before running validation tests.", 'yellow'))
            print("You can start the server using:")
            print(colorize("  1. docker-compose up", 'cyan'))
            print(colorize("  2. ./deploy.sh", 'cyan'))
            print(colorize("  3. python main.py (for development)", 'cyan'))
            sys.exit(1)
    
    # Define tests: (method, endpoint, data, expected_status, description)
    tests = [
        ("GET", "/health", None, 200, "Health check endpoint"),
        ("POST", "/hash", {"file": ("test.txt", b"test")}, 200, "File hash calculation"),
        ("GET", "/blockchain-log", None, 200, "Blockchain log retrieval")
    ]
    
    print(colorize(f"\n=== Blockchain Verifier Validation ===", 'bold'))
    print(f"Running validation tests against {colorize(base_url, 'cyan')}...\n")
    
    success_count = 0
    failure_count = 0
    
    for method, endpoint, data, expected_status, description in tests:
        url = f"{base_url}{endpoint}"
        print(f"Testing {colorize(description, 'blue')} ({method} {endpoint})...")
        
        try:
            if method == "GET":
                resp = requests.get(url, timeout=5)
            else:
                resp = requests.post(url, files=data, timeout=5)
            
            if resp.status_code == expected_status:
                success_count += 1
                print(colorize(f"  ✅ PASS: {method} {endpoint} → {resp.status_code}", 'green'))
                if verbose:
                    try:
                        print("  Response:")
                        print(f"  {json.dumps(resp.json(), indent=2)}")
                    except:
                        print(f"  Response: {resp.text[:100]}{'...' if len(resp.text) > 100 else ''}")
            else:
                failure_count += 1
                print(colorize(f"  ❌ FAIL: {method} {endpoint} → {resp.status_code} (expected {expected_status})", 'red'))
                if verbose:
                    print(f"  Response: {resp.text[:200]}")
        except requests.exceptions.ConnectionError as e:
            failure_count += 1
            print(colorize(f"  ❌ FAIL: {method} {endpoint} → Connection error", 'red'))
            print(colorize(f"  Error details: {str(e)}", 'yellow'))
        except requests.exceptions.Timeout:
            failure_count += 1
            print(colorize(f"  ❌ FAIL: {method} {endpoint} → Request timed out", 'red'))
        except Exception as e:
            failure_count += 1
            print(colorize(f"  ❌ FAIL: {method} {endpoint} → {str(e)}", 'red'))
    
    # Print summary
    print("\n" + "="*50)
    print(f"Tests completed: {success_count + failure_count}")
    print(colorize(f"Passed: {success_count}", 'green'))
    print(colorize(f"Failed: {failure_count}", 'red' if failure_count > 0 else 'green'))
    print("="*50)
    
    # Return exit code based on test results
    return 0 if failure_count == 0 else 1

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Validation tests for Blockchain Verifier")
    parser.add_argument("--url", help="Base URL of the deployed application")
    parser.add_argument("--skip-server-check", action="store_true", 
                        help="Skip checking if server is running")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed information including response bodies")
    args = parser.parse_args()
    
    # Run validation tests
    exit_code = test_deployment(
        base_url=args.url,
        skip_server_check=args.skip_server_check,
        verbose=args.verbose
    )
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()