import requests

API_URL = "http://localhost:8000"

# 1. Hash a file and add to blockchain
def hash_file(filepath):
    with open(filepath, "rb") as f:
        files = {"file": (filepath, f)}
        resp = requests.post(f"{API_URL}/hash", files=files)
        print("Hash File Response:", resp.json())

# 2. Verify file integrity
def verify_file(filepath, stored_hash):
    with open(filepath, "rb") as f:
        files = {"file": (filepath, f)}
        data = {"stored_hash": stored_hash}
        resp = requests.post(f"{API_URL}/verify", files=files, data=data)
        print("Verify File Response:", resp.json())

# 3. View blockchain log
def view_log():
    resp = requests.get(f"{API_URL}/blockchain-log")
    print("Blockchain Log:", resp.json())

# 4. Validate chain
def validate_chain():
    resp = requests.get(f"{API_URL}/validate-chain")
    print("Chain Validation:", resp.json())

if __name__ == "__main__":
    # Example usage
    hash_file("test.txt")
    # Replace with actual hash from previous step
    verify_file("test.txt", "<hash-from-hash-file-response>")
    view_log()
    validate_chain()