# Quick Deployment Guide

## Prerequisites

- Python 3.9+
- Docker (for containerized deployment)
- pip (Python package manager)

## Option 1: Automated Deployment (Recommended)

We've provided an automated deployment script that handles everything for you:

```bash
# Make the script executable (if not already)
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

The script will:
1. Install dependencies
2. Run validation tests
3. Build the Docker image
4. Start the container
5. Verify the deployment

## Option 2: Manual Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t blockchain-verifier:latest -f Dockerfile.prod .

# Run the container
docker run -p 10000:10000 blockchain-verifier:latest
```

### Verify Deployment

```bash
# Run validation tests
python validate.py
```

## Environment Variables

The application can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|--------|
| `ENVIRONMENT` | Application environment (development/production) | `development` |
| `PORT` | Port to run the application on | `8000` |
| `MAX_FILE_SIZE` | Maximum file size in MB | `10` |
| `RATE_LIMIT` | Rate limit per minute | `5` |
| `WORKERS` | Number of Gunicorn workers | `2` |
| `TIMEOUT` | Request timeout in seconds | `120` |
| `READ_ONLY_FS` | Enable read-only filesystem | `true` |

## Troubleshooting

- If you encounter Docker permission issues, try running the commands with `sudo`
- If the application fails to start, check the logs with `docker logs blockchain-verifier`
- For validation test failures, ensure the application is running and accessible at the expected URL