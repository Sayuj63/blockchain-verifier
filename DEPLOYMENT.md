# Cloud Deployment Guide for Blockchain Verifier

This guide provides instructions for deploying the Blockchain Verifier application to various cloud platforms.

## Table of Contents

- [AWS ECS Deployment](#aws-ecs-deployment)

- [Render.com Deployment](#rendercom-deployment)
- [Environment Variables](#environment-variables)

## AWS ECS Deployment

### Prerequisites

- AWS CLI installed and configured
- Docker installed locally
- ECR repository created for the application

### Steps

1. **Build and push the Docker image to ECR**

```bash
# Login to ECR
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.<your-region>.amazonaws.com

# Build the image
docker build -t blockchain-verifier .

# Tag the image
docker tag blockchain-verifier:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/blockchain-verifier:latest

# Push the image
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/blockchain-verifier:latest
```

2. **Create an ECS Task Definition**

Create a task definition JSON file named `task-definition.json`:

```json
{
  "family": "blockchain-verifier",
  "networkMode": "awsvpc",
  "executionRoleArn": "arn:aws:iam::<your-account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "blockchain-verifier",
      "image": "<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/blockchain-verifier:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "PORT", "value": "8000" },
        { "name": "MAX_FILE_SIZE", "value": "10" },
        { "name": "RATE_LIMIT", "value": "5" },
        { "name": "WORKERS", "value": "2" },
        { "name": "TIMEOUT", "value": "120" },
        { "name": "READ_ONLY_FS", "value": "true" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/blockchain-verifier",
          "awslogs-region": "<your-region>",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 10
      },
      "cpu": 256,
      "memory": 512,
      "memoryReservation": 256
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512"
}
```

Register the task definition:

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

3. **Create an ECS Service**

```bash
aws ecs create-service \
  --cluster <your-cluster> \
  --service-name blockchain-verifier \
  --task-definition blockchain-verifier \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<subnet-id>],securityGroups=[<security-group-id>],assignPublicIp=ENABLED}" \
  --health-check-grace-period-seconds 60
```



### Prerequisites




### Steps



1. **Create a fly.toml file**

Create a file named `fly.toml` in your project root:

```toml
app = "blockchain-verifier"
kill_signal = "SIGINT"
kill_timeout = 30

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"
  MAX_FILE_SIZE = "10"
  RATE_LIMIT = "5"
  WORKERS = "2"
  TIMEOUT = "120"
  READ_ONLY_FS = "true"

[experimental]
  allowed_public_ports = []
  auto_rollback = true

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"
  script_checks = []
  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
    type = "connections"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    grace_period = "1s"
    interval = "15s"
    restart_limit = 0
    timeout = "2s"
    
  [[services.http_checks]]
    interval = 10000
    grace_period = "5s"
    method = "get"
    path = "/health"
    protocol = "http"
    restart_limit = 0
    timeout = 2000
    tls_skip_verify = false
```



```bash
# Initialize the app (first time only)


# For subsequent deployments

```

## Render.com Deployment

### Prerequisites

- Render.com account

### Steps

1. **Create a new Web Service on Render**

   - Log in to your Render.com dashboard
   - Click "New" and select "Web Service"
   - Connect your GitHub repository

2. **Configure the service**

   - Name: `blockchain-verifier`
   - Environment: `Docker`
   - Branch: `main` (or your preferred branch)
   - Root Directory: (leave empty)
   - Environment Variables:
     - `PORT`: `8000`
     - `MAX_FILE_SIZE`: `10`
     - `RATE_LIMIT`: `5`
     - `WORKERS`: `2`
     - `TIMEOUT`: `120`
     - `READ_ONLY_FS`: `true`
   - Health Check Path: `/health`
   - Instance Type: Choose based on your needs (e.g., Starter)

3. **Create Web Service**

   Click "Create Web Service" and Render will automatically build and deploy your application.

## Environment Variables

The application supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|--------|
| `PORT` | Port to run the application on | `8000` |
| `MAX_FILE_SIZE` | Maximum file size in MB | `10` |
| `RATE_LIMIT` | Rate limit per minute | `5` |
| `WORKERS` | Number of Gunicorn workers | `2` |
| `TIMEOUT` | Request timeout in seconds | `120` |
| `READ_ONLY_FS` | Enable read-only filesystem | `true` |

## Persistent Storage

For production deployments, consider using a persistent storage solution for the blockchain data:

- **AWS ECS**: Use EFS (Elastic File System)

- **Render.com**: Use Render Disks

This ensures that your blockchain data persists across container restarts and deployments.