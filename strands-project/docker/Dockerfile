# Strands Framework Demo - Container Deployment
# Multi-stage Docker build for production-ready Strands agents

# Build stage
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.9-slim as production

# Create non-root user for security
RUN groupadd -r strands && useradd -r -g strands strands

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/strands/.local

# Copy application code
COPY --chown=strands:strands . .

# Set environment variables
ENV PATH=/home/strands/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV STRANDS_ENV=production

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp && \
    chown -R strands:strands /app

# Switch to non-root user
USER strands

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from shared.utils import health_check; import sys; sys.exit(0 if health_check()['overall_status'] == 'healthy' else 1)"

# Expose port for health checks and monitoring
EXPOSE 8080

# Default command
CMD ["python", "-m", "strands.runtime", "--config", "strands.yaml"]

# Labels for metadata
LABEL maintainer="your-team@company.com"
LABEL version="1.0.0"
LABEL description="Strands Framework Customer Service Agent"
LABEL org.opencontainers.image.source="https://github.com/your-org/strands-customer-service"