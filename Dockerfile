# M4Markets Voice Agent - Production Dockerfile
# Optimized for LiveKit Agents deployment on Railway

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by LiveKit and audio processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for logs
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check endpoint (will be created)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python health_check.py || exit 1

# Expose port for health checks (optional HTTP endpoint)
EXPOSE 8080

# Run the voice agent
# Using 'dev' mode for now, can be changed to 'start' for production
CMD ["python", "voice_agent_m4markets.py", "dev"]
