#!/bin/bash

# Monitor script for Blockchain Verifier
# This script monitors the application logs and health status

# Default configuration
CONTAINER_NAME="blockchain-verifier"
HEALTH_CHECK_INTERVAL=60  # seconds
PORT=8000  # Default port for local deployment (use 10000 for Docker)
LOG_LINES=10

# Parse command line arguments
USE_DOCKER=true
while [[ $# -gt 0 ]]; do
  case $1 in
    --port|-p)
      PORT="$2"
      shift 2
      ;;
    --interval|-i)
      HEALTH_CHECK_INTERVAL="$2"
      shift 2
      ;;
    --logs|-l)
      LOG_LINES="$2"
      shift 2
      ;;
    --no-docker)
      USE_DOCKER=false
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --port, -p PORT       Port to check (default: 8000, use 10000 for Docker)"
      echo "  --interval, -i SEC    Health check interval in seconds (default: 60)"
      echo "  --logs, -l LINES      Number of log lines to display (default: 10)"
      echo "  --no-docker           Run in non-Docker mode (for local deployment)"
      echo "  --help, -h            Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Colors for output
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}✗ Docker is not running${NC}"
        echo -e "${YELLOW}Please start Docker and try again${NC}"
        return 1
    fi
    return 0
}

# Function to check if container is running
check_container() {
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo -e "${GREEN}✓ Container is running${NC}"
        return 0
    else
        if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
            CONTAINER_STATUS=$(docker inspect --format='{{.State.Status}}' $CONTAINER_NAME)
            echo -e "${RED}✗ Container exists but is not running (Status: $CONTAINER_STATUS)${NC}"
            echo -e "${YELLOW}Try restarting with: docker start $CONTAINER_NAME${NC}"
        else
            echo -e "${RED}✗ Container does not exist${NC}"
            echo -e "${YELLOW}Try deploying with: ./deploy.sh${NC}"
        fi
        return 1
    fi
}

# Function to check application health
check_health() {
    if python3 health_check.py --url http://localhost:$PORT > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Application is healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Application health check failed${NC}"
        echo -e "${YELLOW}The API may be unresponsive at http://localhost:$PORT${NC}"
        return 1
    fi
}

# Function to display container logs
show_logs() {
    echo -e "\n${YELLOW}Recent logs (last $LOG_LINES lines):${NC}"
    docker logs --tail $LOG_LINES $CONTAINER_NAME 2>/dev/null || echo -e "${RED}Cannot retrieve logs${NC}"
}

# Function to display container stats
show_stats() {
    echo -e "\n${YELLOW}Container Stats:${NC}"
    STATS=$(docker stats $CONTAINER_NAME --no-stream --format "CPU: {{.CPUPerc}}\nMemory: {{.MemUsage}}\nNetwork I/O: {{.NetIO}}\nDisk I/O: {{.BlockIO}}" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo -e "${BLUE}$STATS${NC}"
    else
        echo -e "${RED}Cannot retrieve container stats${NC}"
    fi
}

# Main monitoring loop
echo -e "${YELLOW}=== Blockchain Verifier Monitoring ===${NC}"
echo -e "Monitoring on port: ${BLUE}$PORT${NC}, Refresh interval: ${BLUE}$HEALTH_CHECK_INTERVAL${NC} seconds"

while true; do
    clear
    echo -e "${YELLOW}=== Blockchain Verifier Monitoring ===${NC}"
    echo -e "Time: $(date)"
    
    if $USE_DOCKER; then
        # Docker mode
        # Check if Docker is running
        if ! check_docker; then
            echo -e "\n${YELLOW}Press Ctrl+C to exit. Refreshing in $HEALTH_CHECK_INTERVAL seconds...${NC}"
            sleep $HEALTH_CHECK_INTERVAL
            continue
        fi
        
        echo -e "\n${YELLOW}Container Status:${NC}"
        if check_container; then
            echo -e "\n${YELLOW}Application Health:${NC}"
            check_health
            show_stats
            show_logs
        fi
    else
        # Non-Docker mode
        echo -e "\n${BLUE}Running in non-Docker mode${NC}"
        
        # Check if process is running on the port
        if lsof -i :$PORT > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Process is running on port $PORT${NC}"
            
            # Check application health
            echo -e "\n${YELLOW}Application Health:${NC}"
            check_health
        else
            echo -e "${RED}✗ No process is running on port $PORT${NC}"
            echo -e "${YELLOW}Try starting the application with: ./deploy_local.sh${NC}"
        fi
    fi
    
    echo -e "\n${YELLOW}Press Ctrl+C to exit. Refreshing in $HEALTH_CHECK_INTERVAL seconds...${NC}"
    sleep $HEALTH_CHECK_INTERVAL
done