#!/bin/bash

# Color definitions
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
NC="\033[0m" # No Color

echo -e "${GREEN}=== Blockchain Verifier Local Deployment Script ===${NC}"
echo "Starting local deployment process..."

# Function to handle errors
handle_error() {
    echo -e "\n${RED}ERROR: $1${NC}"
    echo -e "${YELLOW}Deployment failed. See error message above.${NC}"
    exit 1
}

# Step 1: Create virtual environment if it doesn't exist
echo -e "\n${GREEN}Step 1: Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv || handle_error "Failed to create virtual environment"
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Step 2: Activate virtual environment and install dependencies
echo -e "\n${GREEN}Step 2: Installing dependencies...${NC}"
source venv/bin/activate || handle_error "Failed to activate virtual environment"
pip install -r requirements.txt || handle_error "Failed to install dependencies"

# Step 3: Run tests
echo -e "\n${GREEN}Step 3: Running tests...${NC}"
python validate.py --skip-server-check || echo -e "${YELLOW}Warning: Some tests failed, but continuing deployment${NC}"

# Step 4: Start the application
echo -e "\n${GREEN}Step 4: Starting the application...${NC}"
echo "The application will run on http://localhost:8000"
echo -e "${YELLOW}Press Ctrl+C to stop the application${NC}"

# Start the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000