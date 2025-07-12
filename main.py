from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from starlette.requests import Request
from fastapi.responses import JSONResponse
import uvicorn
import hashlib
import json
import copy
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


def calculate_file_hash(file_bytes: bytes) -> str:
    """
    Calculate SHA-256 hash of input bytes, processing data in 64KB chunks for memory efficiency.
    
    Args:
        file_bytes: Bytes object to hash
        
    Returns:
        Hexadecimal digest as string
        
    Special case:
        For empty input, returns standard SHA-256 hash of empty string:
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    """
    # Handle empty input case
    if not file_bytes:
        return "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    
    # Initialize hash object
    sha256 = hashlib.sha256()
    
    # Process data in 64KB chunks
    chunk_size = 64 * 1024  # 64KB
    offset = 0
    
    while offset < len(file_bytes):
        chunk = file_bytes[offset:offset + chunk_size]
        sha256.update(chunk)
        offset += chunk_size
    
    # Return hexadecimal digest
    return sha256.hexdigest()

# Import os for environment variables
import os

# Initialize rate limiter with configurable rate limit from environment
rate_limit = os.environ.get("RATE_LIMIT", "5")
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{rate_limit}/minute"])


def calculate_block_header_hash(block: Dict[str, Any]) -> str:
    """
    Calculate SHA-256 hash of a block header.
    
    Args:
        block: Block dictionary containing index, previous_hash, timestamp, operation, filename, and result
        
    Returns:
        Hexadecimal digest of the block header hash
    """
    # Construct the header string
    header = f"{block['index']}{block['previous_hash']}{block['timestamp']}{block.get('operation', '')}{block.get('filename', '')}{block.get('result', '')}"
    
    # Calculate and return the hash
    return hashlib.sha256(header.encode()).hexdigest()


def create_genesis_block() -> Dict[str, Any]:
    """
    Create a genesis block for the blockchain.
    
    Returns:
        Genesis block dictionary
    """
    # Create the genesis block
    genesis_block = {
        "index": 0,
        "previous_hash": "0" * 64,
        "timestamp": "2023-01-01T00:00:00Z",
        "operation": "GENESIS",
        "filename": "",
        "result": ""
    }
    
    # Calculate and add the block hash
    genesis_block["block_hash"] = calculate_block_header_hash(genesis_block)
    
    return genesis_block


def validate_blockchain() -> Tuple[bool, Optional[int]]:
    """
    Validate the entire blockchain.
    
    Returns:
        Tuple containing:
        - Boolean indicating if the blockchain is valid
        - Index of the first invalid block, or None if all blocks are valid
    """
    # If the blockchain is empty, it's valid
    if not BLOCKCHAIN_LOG:
        return True, None
    
    # Check if the first block is a valid genesis block
    if BLOCKCHAIN_LOG[0]["index"] != 0 or BLOCKCHAIN_LOG[0]["previous_hash"] != "0" * 64:
        return False, 0
    
    # Validate each block in the chain
    for i in range(1, len(BLOCKCHAIN_LOG)):
        current_block = BLOCKCHAIN_LOG[i]
        previous_block = BLOCKCHAIN_LOG[i-1]
        
        # Check if the block's previous_hash matches the previous block's hash
        previous_block_hash = previous_block.get("block_hash", None)
        if not previous_block_hash:
            # For backward compatibility with old blocks
            previous_block_hash = previous_block.get("hash", previous_block.get("current_hash", None))
        
        if current_block["previous_hash"] != previous_block_hash:
            return False, i
        
        # Check if the block's hash is valid
        if "block_hash" in current_block:
            calculated_hash = calculate_block_header_hash(current_block)
            if current_block["block_hash"] != calculated_hash:
                return False, i
        
        # Check if timestamps are sequential
        # Convert to offset-naive datetimes for comparison
        current_time = datetime.fromisoformat(current_block["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None)
        previous_time = datetime.fromisoformat(previous_block["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None)
        
        if current_time < previous_time:
            return False, i
    
    # All blocks are valid
    return True, None


app = FastAPI(
    title="Blockchain Verifier",
    description="A service to verify blockchain transactions and data",
    version="1.0.0"
)

# Configure rate limiter with FastAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def get_app():
    """Factory function for Gunicorn"""
    return app


@app.get("/")
async def root():
    return {"message": "Welcome to Blockchain Verifier API"}


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration systems"""
    # Check if blockchain is valid
    is_valid, _ = validate_blockchain()
    
    # Get system information
    system_info = {
        "status": "healthy" if is_valid else "degraded",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "port": os.getenv("PORT", "8000"),
        "version": app.version,
        "blockchain": {
            "valid": is_valid,
            "block_count": len(BLOCKCHAIN_LOG)
        },
        # Add environment configuration (without sensitive data)
        "config": {
            "max_file_size": os.environ.get("MAX_FILE_SIZE", "10"),
            "rate_limit": os.environ.get("RATE_LIMIT", "5")
        }
    }
    
    return system_info


@app.post("/verify/hash")
async def verify_hash(data: str = Form(...), hash_value: str = Form(...), algorithm: str = Form("sha256")):
    """Verify if a hash matches the provided data"""
    try:
        # Select hashing algorithm
        if algorithm.lower() == "sha256":
            calculated_hash = hashlib.sha256(data.encode()).hexdigest()
        elif algorithm.lower() == "sha1":
            calculated_hash = hashlib.sha1(data.encode()).hexdigest()
        elif algorithm.lower() == "md5":
            calculated_hash = hashlib.md5(data.encode()).hexdigest()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported algorithm: {algorithm}")
        
        # Compare hashes
        is_valid = calculated_hash.lower() == hash_value.lower()
        
        return {
            "is_valid": is_valid,
            "calculated_hash": calculated_hash,
            "provided_hash": hash_value,
            "algorithm": algorithm
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify/transaction")
async def verify_transaction(transaction_file: UploadFile = File(...), signature: Optional[str] = Form(None)):
    """Verify a blockchain transaction from a JSON file"""
    try:
        # Read transaction data
        content = await transaction_file.read()
        transaction = json.loads(content)
        
        # Basic validation of transaction format
        required_fields = ["sender", "receiver", "amount", "timestamp"]
        missing_fields = [field for field in required_fields if field not in transaction]
        
        if missing_fields:
            return JSONResponse(
                status_code=400,
                content={
                    "is_valid": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            )
        
        # If signature is provided, verify it (simplified example)
        if signature:
            # In a real implementation, this would use cryptographic verification
            # This is just a placeholder for demonstration
            signature_valid = len(signature) > 10  # Dummy validation
        else:
            signature_valid = None
        
        return {
            "is_valid": True,
            "transaction": transaction,
            "signature_valid": signature_valid
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify/merkle-proof")
async def verify_merkle_proof(
    data: str = Form(...),
    merkle_root: str = Form(...),
    proof: str = Form(...)
):

    """Verify a Merkle proof for data inclusion in a blockchain"""
    try:
        # Parse the proof (assuming it's a JSON array of hashes)
        proof_hashes = json.loads(proof)
        
        # Calculate the Merkle path (simplified example)
        current_hash = hashlib.sha256(data.encode()).hexdigest()
        
        for proof_hash in proof_hashes:
            # In a real implementation, we would need to know if each hash is a left or right sibling
            # For simplicity, we'll just concatenate and hash
            combined = current_hash + proof_hash
            current_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        # Verify if the calculated root matches the provided root
        is_valid = current_hash.lower() == merkle_root.lower()
        
        return {
            "is_valid": is_valid,
            "calculated_root": current_hash,
            "provided_root": merkle_root
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid proof format, expected JSON array")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify/file-hash")
async def verify_file_hash(file: UploadFile = File(...), expected_hash: Optional[str] = Form(None)):
    """Calculate SHA-256 hash of an uploaded file and optionally verify against expected hash"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Calculate hash using our efficient function
        calculated_hash = calculate_file_hash(file_content)
        
        # Prepare response
        response = {
            "filename": file.filename,
            "file_size_bytes": len(file_content),
            "calculated_hash": calculated_hash,
        }
        
        # If expected hash is provided, verify it
        if expected_hash:
            is_valid = calculated_hash.lower() == expected_hash.lower()
            response["is_valid"] = is_valid
            response["expected_hash"] = expected_hash
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/hash", status_code=200)
@limiter.limit(f"{os.environ.get('RATE_LIMIT', '5')}/minute")
async def hash_file(
    request: Request,
    file: UploadFile = File(..., description=f"File to hash (max {os.environ.get('MAX_FILE_SIZE', '10')}MB)"),
):
    """Calculate SHA-256 hash of an uploaded file and add it to the blockchain audit log
    
    - Accepts any file type
    - 10MB file size limit
    - Rate limited to 5 requests per minute per IP
    - Creates a blockchain-style audit trail entry for each successful hash
    - Implements cryptographic chaining between blocks
    
    Returns a JSON response with the file hash and blockchain block information
    """
    try:
        # Check file size limit from environment variable (default 10MB)
        max_file_size_mb = int(os.environ.get("MAX_FILE_SIZE", "10"))
        file_size_limit = max_file_size_mb * 1024 * 1024  # Convert MB to bytes
        
        # Read file content in chunks to avoid memory issues
        file_content = bytearray()
        chunk_size = 64 * 1024  # 64KB chunks
        
        # Reset file position to start
        await file.seek(0)
        
        # Read and process file in chunks
        total_size = 0
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            
            total_size += len(chunk)
            if total_size > file_size_limit:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {max_file_size_mb}MB."
                )
            
            file_content.extend(chunk)
        
        # Calculate hash using our efficient function
        calculated_hash = calculate_file_hash(file_content)
        
        # Get the previous hash from the blockchain log
        previous_hash = "0" * 64  # Genesis block has all zeros
        if BLOCKCHAIN_LOG:
            previous_block = BLOCKCHAIN_LOG[-1]
            previous_hash = previous_block.get("block_hash", previous_block.get("hash", previous_block.get("current_hash", "0" * 64)))
        
        # Create a new block for the blockchain log
        timestamp = datetime.utcnow().isoformat() + "Z"  # ISO format with Z suffix for UTC
        
        # Check for future timestamps (max 10 min tolerance)
        current_time = datetime.utcnow()
        # Convert timestamp_time to an offset-naive datetime for comparison
        timestamp_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).replace(tzinfo=None)
        if timestamp_time > current_time + timedelta(minutes=10):
            raise HTTPException(
                status_code=400,
                detail="Invalid timestamp: future time exceeds tolerance"
            )
        
        block_index = len(BLOCKCHAIN_LOG)
        
        new_block = {
            "index": block_index,
            "previous_hash": previous_hash,
            "timestamp": timestamp,
            "operation": "HASH",
            "filename": file.filename,
            "result": calculated_hash,
            "hash": calculated_hash  # For backward compatibility
        }
        
        # Calculate and add the block hash
        new_block["block_hash"] = calculate_block_header_hash(new_block)
        
        # Add the new block to the blockchain log (append-only)
        BLOCKCHAIN_LOG.append(new_block)
        
        # Prepare and return the response
        return {
            "status": "success",
            "filename": file.filename,
            "hash": calculated_hash,
            "block_hash": new_block["block_hash"],
            "block_index": block_index,
            "timestamp": timestamp
        }
        
    except RateLimitExceeded:
        # This should be handled by the exception handler, but just in case
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like the 413 we might have raised)
        raise
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/blockchain-log")
async def get_blockchain_log():
    """Retrieve the current blockchain audit log
    
    Returns the complete blockchain log containing all hash operations performed,
    sorted by index in descending order (newest first).
    
    The response includes a chain_validity_status field indicating if the blockchain is valid.
    """
    # Create a deep copy of the blockchain log to prevent tampering
    blockchain_copy = copy.deepcopy(BLOCKCHAIN_LOG)
    
    # Sort blocks by index in descending order (newest first)
    blockchain_copy.sort(key=lambda x: x["index"], reverse=True)
    
    # Validate the blockchain
    is_valid, _ = validate_blockchain()
    
    return {
        "status": "success",
        "block_count": len(blockchain_copy),
        "chain_validity_status": "valid" if is_valid else "invalid",
        "blocks": blockchain_copy
    }


@app.get("/validate-chain")
async def validate_chain():
    """Validate the blockchain integrity
    
    Verifies:
    1. Each block's previous_hash matches the previous block's header hash
    2. The hash chain is unbroken
    3. Timestamps are sequential
    
    Returns a JSON response with validation result and the index of the first invalid block (if any)
    
    Examples:
    - Example 1: Valid blockchain
    - Example 2: Invalid blockchain with specific invalid block index
    """
    # Validate the blockchain
    is_valid, invalid_block_index = validate_blockchain()
    
    # Prepare and return the response
    return {
        "valid": is_valid,
        "invalid_block": invalid_block_index
    }


@app.post("/verify", status_code=200)
@limiter.limit(f"{os.environ.get('RATE_LIMIT', '5')}/minute")
async def verify_file_integrity(
    request: Request,
    file: UploadFile = File(..., description=f"File to verify (max {os.environ.get('MAX_FILE_SIZE', '10')}MB)"),
    stored_hash: str = Form(..., description="Previously stored hash to verify against")
):
    """Verify file integrity by comparing current hash with stored hash
    
    - Accepts any file type
    - 10MB file size limit
    - Rate limited to 5 requests per minute per IP
    - Creates a blockchain-style audit trail entry for each verification attempt
    - Compares calculated hash with provided stored_hash
    
    Returns a JSON response with verification result and blockchain block information
    
    Examples:
    - Example 1: Matching hashes (valid file)
    - Example 2: Mismatched hashes (invalid/tampered file)
    - Example 3: Missing parameters (400 error)
    """
    try:
        # Validate inputs
        if not file:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter: file"
            )
            
        if not stored_hash:
            raise HTTPException(
                status_code=400,
                detail="Missing required parameter: stored_hash"
            )
        
        # Check file size limit from environment variable (default 10MB)
        max_file_size_mb = int(os.environ.get("MAX_FILE_SIZE", "10"))
        file_size_limit = max_file_size_mb * 1024 * 1024  # Convert MB to bytes
        
        # Read file content in chunks to avoid memory issues
        file_content = bytearray()
        chunk_size = 64 * 1024  # 64KB chunks
        
        # Reset file position to start
        await file.seek(0)
        
        # Read and process file in chunks
        total_size = 0
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            
            total_size += len(chunk)
            if total_size > file_size_limit:
                raise HTTPException(
                    status_code=413,
                    detail="File too large. Maximum size is 10MB."
                )
            
            file_content.extend(chunk)
        
        # Calculate current hash using our efficient function
        current_hash = calculate_file_hash(file_content)
        
        # Compare current hash with stored hash
        is_valid = current_hash.lower() == stored_hash.lower()
        status = "valid" if is_valid else "invalid"
        message = "File integrity verified" if is_valid else "File tampering detected"
        
        # Get the previous hash from the blockchain log
        previous_hash = "0" * 64  # Genesis block has all zeros
        if BLOCKCHAIN_LOG:
            previous_block = BLOCKCHAIN_LOG[-1]
            previous_hash = previous_block.get("block_hash", previous_block.get("hash", previous_block.get("current_hash", "0" * 64)))
        
        # Create a new block for the blockchain log
        timestamp = datetime.utcnow().isoformat() + "Z"  # ISO format with Z suffix for UTC
        
        # Check for future timestamps (max 10 min tolerance)
        current_time = datetime.utcnow()
        # Convert timestamp_time to an offset-naive datetime for comparison
        timestamp_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).replace(tzinfo=None)
        if timestamp_time > current_time + timedelta(minutes=10):
            raise HTTPException(
                status_code=400,
                detail="Invalid timestamp: future time exceeds tolerance"
            )
        
        block_index = len(BLOCKCHAIN_LOG)
        
        # Create audit log entry
        new_block = {
            "index": block_index,
            "previous_hash": previous_hash,
            "timestamp": timestamp,
            "operation": "VERIFICATION",
            "filename": file.filename,
            "stored_hash": stored_hash,
            "current_hash": current_hash,
            "result": status
        }
        
        # Calculate and add the block hash
        new_block["block_hash"] = calculate_block_header_hash(new_block)
        
        # Add the new block to the blockchain log
        BLOCKCHAIN_LOG.append(new_block)
        
        # Prepare and return the response
        return {
            "status": status,
            "filename": file.filename,
            "current_hash": current_hash,
            "stored_hash": stored_hash,
            "block_hash": new_block["block_hash"],
            "block_index": block_index,
            "timestamp": timestamp,
            "message": message
        }
        
    except RateLimitExceeded:
        # This should be handled by the exception handler, but just in case
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like the 400 or 413 we might have raised)
        raise
    except Exception as e:
        # Handle any other exceptions
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Initialize blockchain log
BLOCKCHAIN_LOG: List[Dict[str, Any]] = []

# Initialize the blockchain with a genesis block if empty
if not BLOCKCHAIN_LOG:
    BLOCKCHAIN_LOG.append(create_genesis_block())

if __name__ == "__main__":
    # Test cases for calculate_file_hash function
    print("\nTest cases for calculate_file_hash function:")
    
    # Test case 1 (empty input)
    result1 = calculate_file_hash(b"")
    expected1 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    print(f"Test case 1 (empty input): {result1}")
    print(f"Expected: {expected1}")
    print(f"Result: {'PASS' if result1 == expected1 else 'FAIL'}")
    
    # Test case 2 ("Hello World")
    result2 = calculate_file_hash(b"Hello World")
    expected2 = "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
    print(f"\nTest case 2 (\"Hello World\"): {result2}")
    print(f"Expected: {expected2}")
    print(f"Result: {'PASS' if result2 == expected2 else 'FAIL'}")
    
    # Final verification
    assert 'BLOCKCHAIN_LOG' in globals(), "Blockchain not initialized"
    assert len(BLOCKCHAIN_LOG) > 0, "Genesis block missing"
    
    if os.getenv("ENVIRONMENT", "development") == "production":
        print("Production mode - use Gunicorn via entrypoint.sh")
    else:
        print("Running in development mode (uvicorn directly)")
        # Run the FastAPI application
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=int(os.getenv("PORT", "8000")), 
            reload=os.getenv("ENVIRONMENT", "development") == "development",
            timeout_keep_alive=30
        )