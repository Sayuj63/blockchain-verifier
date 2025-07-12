#!/bin/bash

# Color definitions
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
NC="\033[0m" # No Color

echo -e "${GREEN}=== Blockchain Verifier Deployment Script ===${NC}"
echo "Starting deployment process..."

# Function to handle errors
handle_error() {
    echo -e "\n${RED}ERROR: $1${NC}"
    echo -e "${YELLOW}Deployment failed. See error message above.${NC}"
    exit 1
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    handle_error "Docker is not running. Please start Docker and try again."
fi

# Step 1: Install dependencies
echo -e "\n${GREEN}Step 1: Installing dependencies...${NC}"
pip install -r requirements.txt || handle_error "Failed to install dependencies"

# Step 2: Check if container already exists
echo -e "\n${GREEN}Step 2: Checking existing containers...${NC}"
if docker ps -a | grep -q blockchain-verifier; then
    echo -e "${YELLOW}Container 'blockchain-verifier' already exists. Removing it...${NC}"
    docker rm -f blockchain-verifier || handle_error "Failed to remove existing container"
fi

# Step 3: Build Docker image
echo -e "\n${GREEN}Step 3: Building Docker image...${NC}"
docker build -t blockchain-verifier:latest -f Dockerfile.prod . || handle_error "Failed to build Docker image"

# Step 4: Run Docker container
echo -e "\n${GREEN}Step 4: Starting Docker container...${NC}"
docker run -d -p 10000:10000 --name blockchain-verifier blockchain-verifier:latest || handle_error "Failed to start Docker container"

# Step 5: Verify deployment
echo -e "\n${GREEN}Step 5: Verifying deployment...${NC}"
echo "Waiting for container to start..."
sleep 5  # Wait for container to start

# Check if container is running
if ! docker ps | grep -q blockchain-verifier; then
    echo -e "${RED}Container failed to start. Checking logs:${NC}"
    docker logs blockchain-verifier
    handle_error "Container failed to start properly"
fi

# Run validation tests
TEST_URL=http://localhost:10000 python validate.py || handle_error "Validation tests failed"

echo -e "\n${GREEN}=== Deployment completed successfully! ===${NC}"
echo "The application is now running at: http://localhost:10000"
echo "API documentation available at: http://localhost:10000/docs"
echo -e "\nTo monitor the application, run: ${YELLOW}./monitor.sh${NC}"