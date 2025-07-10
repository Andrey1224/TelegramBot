# Use Python 3.13 slim image for smaller size
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Kiev \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies and tzdata in single layer to minimize image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tzdata \
        ca-certificates && \
    ln -fs /usr/share/zoneinfo/Europe/Kiev /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    find /usr/local -name '*.pyc' -delete && \
    find /usr/local -name '__pycache__' -delete

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    find /usr/local -name '*.pyc' -delete && \
    find /usr/local -name '__pycache__' -delete

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

# Switch to non-root user
USER appuser

# Expose port (if needed for webhooks)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; conn = sqlite3.connect('bot.db'); conn.close()" || exit 1

# Run the application
CMD ["python", "main.py"]
