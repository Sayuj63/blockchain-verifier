#!/bin/sh
set -e

echo "Starting Blockchain Verifier API"

# Apply environment variables
MAX_FILE_SIZE=${MAX_FILE_SIZE:-10}
RATE_LIMIT=${RATE_LIMIT:-5}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-2}
TIMEOUT=${TIMEOUT:-120}

# Print configuration
echo "Configuration:"
echo "- Port: $PORT"
echo "- Max file size: $MAX_FILE_SIZE MB"
echo "- Rate limit: $RATE_LIMIT requests/minute"
echo "- Workers: $WORKERS"
echo "- Timeout: $TIMEOUT seconds"

# Apply read-only filesystem if enabled
if [ "$READ_ONLY_FS" = "true" ]; then
    echo "- Read-only filesystem: enabled (except /app/tmp)"
    # Mount temporary filesystem for runtime files if needed
    # This would be implemented in a production environment
fi

# Wait for dependencies (if any)
# This would be used if the application had external dependencies like databases

# Initialize blockchain if empty
# This is handled automatically by the application

# Start the application with Gunicorn and Uvicorn workers
exec gunicorn main:app \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout $TIMEOUT \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --forwarded-allow-ips='*' \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50