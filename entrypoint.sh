#!/bin/sh
set -e

# Use Render's PORT if available (fallback to 8000 for local)
ACTUAL_PORT=${PORT:-8000}

echo "Starting Blockchain Verifier API"
echo "Configuration:"
echo "- Port: $ACTUAL_PORT"
echo "- Max file size: ${MAX_FILE_SIZE:-10} MB"
echo "- Rate limit: ${RATE_LIMIT:-5} requests/minute"
echo "- Workers: ${WORKERS:-2}"
echo "- Timeout: ${TIMEOUT:-120} seconds"

if [ "$READ_ONLY_FS" = "true" ]; then
    echo "- Read-only filesystem: enabled (except /app/tmp)"
fi

# Start with Gunicorn (compatible with both Render and local)
exec gunicorn main:app \
    --bind 0.0.0.0:$ACTUAL_PORT \
    --workers ${WORKERS:-2} \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout ${TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    --log-level info