# Blockchain Verifier – Portfolio Showcase

## Project Overview
Blockchain Verifier is a production-grade FastAPI application that provides tamper-proof file verification and audit logging using a blockchain-inspired approach. It enables users to hash, verify, and audit files with cryptographic integrity, supporting immutable logs and chain validation.

## Architecture Diagram
```mermaid
graph TD
    A[User/API Client] -->|HTTP| B[FastAPI App]
    B --> C[Rate Limiter]
    B --> D[Blockchain Log (JSON)]
    B --> E[Hashing Engine]
    B --> F[Audit Trail Endpoint]
    B --> G[Chain Validation]
    B --> H[Docker Container]
    
```

## Key Features
- File hashing with SHA-256
- Tamper-proof verification and audit trail
- Blockchain-style immutable log
- Chain validation endpoint
- Configurable rate limiting and file size
- Production-ready Docker and Compose setup
- Health check and resource limits for cloud

## Technical Challenges Overcome
- Ensured blockchain immutability and append-only log
- Handled time zone and datetime validation edge cases
- Optimized for low memory usage with chunked file reads
- Hardened Docker image for security and minimal size
- Enabled persistent storage for cloud deployments

## Future Enhancements Roadmap
- Add user authentication and API keys
- Integrate with cloud object storage (S3, GCS)
- Real-time event notifications (webhooks)
- Web dashboard for audit trail visualization
- Multi-algorithm and multi-chain support