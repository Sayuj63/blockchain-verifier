#!/usr/bin/env python3
"""
Health Check Script for Blockchain Verifier

This script performs a health check on the deployed Blockchain Verifier application.
It checks the /health endpoint and verifies that the blockchain is valid.

Usage:
    python health_check.py [--url URL] [--quiet] [--json] [--timeout SECONDS]

Options:
    --url URL           The base URL of the deployed application (default: http://localhost:10000)
    --quiet, -q         Suppress output and only return exit code
    --json, -j          Output results in JSON format
    --timeout SECONDS   Request timeout in seconds (default: 10)
    --verbose, -v       Show detailed information
"""

import argparse
import json
import sys
import socket
import requests
from datetime import datetime

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

def is_port_open(host, port, timeout=2):
    """Check if a port is open on the host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except socket.error:
        return False

def check_health(base_url, timeout=10, quiet=False, json_output=False, verbose=False):
    """Check the health of the deployed application."""
    result = {
        'timestamp': datetime.now().isoformat(),
        'url': base_url,
        'success': False,
        'status': 'unknown',
        'blockchain_valid': False,
        'block_count': 0,
        'port': 'unknown',
        'version': 'unknown',
        'error': None
    }
    
    # Extract host and port from URL for connection check
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(base_url)
        host = parsed_url.hostname or 'localhost'
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        
        # Check if port is open before making request
        if not is_port_open(host, port):
            error_msg = f"Connection failed: {host}:{port} is not reachable"
            result['error'] = error_msg
            if not quiet and not json_output:
                print(colorize(f"\n❌ {error_msg}", 'red'))
                print(colorize("Check if the server is running and the port is correct.", 'yellow'))
            return result, False
    except Exception as e:
        if verbose and not quiet:
            print(colorize(f"URL parsing error: {str(e)}", 'red'))
    
    try:
        # Check the /health endpoint
        resp = requests.get(f"{base_url}/health", timeout=timeout)
        resp.raise_for_status()
        health_data = resp.json()
        
        # Update result with health data
        result['success'] = True
        result['status'] = health_data.get('status', 'unknown')
        result['blockchain_valid'] = health_data.get('blockchain', {}).get('valid', False)
        result['block_count'] = health_data.get('blockchain', {}).get('block_count', 0)
        result['port'] = health_data.get('port', 'unknown')
        result['version'] = health_data.get('version', 'unknown')
        
        # Print health information if not in quiet mode
        if not quiet and not json_output:
            print(colorize(f"\n=== Health Check: {result['timestamp']} ===", 'bold'))
            print(f"URL: {colorize(base_url, 'cyan')}")
            print(f"Status: {colorize(result['status'], 'green' if result['status'] == 'ok' else 'yellow')}")
            print(f"Blockchain valid: {colorize(str(result['blockchain_valid']), 'green' if result['blockchain_valid'] else 'red')}")
            print(f"Block count: {colorize(str(result['block_count']), 'blue')}")
            print(f"Port: {colorize(str(result['port']), 'magenta')}")
            print(f"Version: {colorize(result['version'], 'cyan')}")
            
            if verbose:
                print("\nRaw response:")
                print(json.dumps(health_data, indent=2))
        
        # Check if blockchain is valid
        if not result['blockchain_valid']:
            if not quiet and not json_output:
                print(colorize("\n⚠️ WARNING: Blockchain is not valid!", 'yellow'))
            return result, False
        
        if not quiet and not json_output:
            print(colorize("\n✅ Health check passed!", 'green'))
        return result, True
        
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Connection error: {str(e)}"
        result['error'] = error_msg
        if not quiet and not json_output:
            print(colorize(f"\n❌ {error_msg}", 'red'))
            print(colorize("Check if the server is running and the URL is correct.", 'yellow'))
        return result, False
    except requests.exceptions.Timeout as e:
        error_msg = f"Request timed out after {timeout} seconds"
        result['error'] = error_msg
        if not quiet and not json_output:
            print(colorize(f"\n❌ {error_msg}", 'red'))
        return result, False
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error: {e.response.status_code} - {e.response.reason}"
        result['error'] = error_msg
        if not quiet and not json_output:
            print(colorize(f"\n❌ {error_msg}", 'red'))
        return result, False
    except requests.exceptions.RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        result['error'] = error_msg
        if not quiet and not json_output:
            print(colorize(f"\n❌ {error_msg}", 'red'))
        return result, False
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        result['error'] = error_msg
        if not quiet and not json_output:
            print(colorize(f"\n❌ {error_msg}", 'red'))
        return result, False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Health check for Blockchain Verifier")
    parser.add_argument("--url", default="http://localhost:8000", 
                        help="Base URL of the deployed application (default: http://localhost:8000, use 10000 for Docker)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress output and only return exit code")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output results in JSON format")
    parser.add_argument("--timeout", type=int, default=10,
                        help="Request timeout in seconds")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed information")
    args = parser.parse_args()
    
    # Run health check
    result, success = check_health(
        args.url, 
        timeout=args.timeout, 
        quiet=args.quiet, 
        json_output=args.json,
        verbose=args.verbose
    )
    
    # Output JSON if requested
    if args.json:
        print(json.dumps(result, indent=2 if args.verbose else None))
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()