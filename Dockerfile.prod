# Builder stage
FROM python:3.9-slim AS builder
WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add gunicorn for production
RUN pip install --no-cache-dir gunicorn

# Runner stage
FROM python:3.9-alpine

# Install runtime dependencies
RUN apk add --no-cache curl

# Create non-root user
RUN adduser -D nonroot && \
    mkdir -p /app/tmp /app/data && \
    chown -R nonroot:nonroot /app

WORKDIR /app
USER nonroot

# Copy virtual environment from builder
COPY --from=builder --chown=nonroot:nonroot /opt/venv /opt/venv

# Copy application code
COPY --chown=nonroot:nonroot . .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PORT=8000 \
    MAX_FILE_SIZE=10 \
    RATE_LIMIT=5 \
    WORKERS=2 \
    TIMEOUT=120 \
    READ_ONLY_FS=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]