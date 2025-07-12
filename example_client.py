#!/usr/bin/env python3
"""
Example Client for Blockchain Verifier

This script demonstrates how to use the Blockchain Verifier API.

Usage:
    python example_client.py [--url URL]

Options:
    --url URL    The base URL of the deployed application (default: http://localhost:8000)
"""

import argparse
import requests
import json
import os

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Example client for Blockchain Verifier")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="Base URL of the deployed application (default: http://localhost:8000)")
    args = parser.parse_args()
    
    base_url = args.url
    
    # Example 1: Check health
    print("\n1. Checking health...")
    try:
        resp = requests.get(f"{base_url}/health")
        resp.raise_for_status()
        print("Health check successful!")
        print_json(resp.json())
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Example 2: Hash a file
    print("\n2. Hashing a file...")
    try:
        # Create a test file
        with open("test_file.txt", "w") as f:
            f.write("Hello, Blockchain!")
        
        # Hash the file
        with open("test_file.txt", "rb") as f:
            files = {"file": ("test_file.txt", f)}
            resp = requests.post(f"{base_url}/hash", files=files)
            resp.raise_for_status()
            hash_result = resp.json()
            print("File hash created!")
            print_json(hash_result)
            
            # Save the hash for later verification
            file_hash = hash_result["hash"]
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Example 3: Verify a file
    print("\n3. Verifying a file...")
    try:
        with open("test_file.txt", "rb") as f:
            files = {"file": ("test_file.txt", f)}
            data = {"stored_hash": file_hash}
            resp = requests.post(f"{base_url}/verify", files=files, data=data)
            resp.raise_for_status()
            print("File verification result:")
            print_json(resp.json())
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Example 4: Get blockchain log
    print("\n4. Getting blockchain log...")
    try:
        resp = requests.get(f"{base_url}/blockchain-log")
        resp.raise_for_status()
        print("Blockchain log:")
        print_json(resp.json())
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Clean up
    if os.path.exists("test_file.txt"):
        os.remove("test_file.txt")

if __name__ == "__main__":
    main()