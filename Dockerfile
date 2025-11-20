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

# Note: No Docker HEALTHCHECK needed for LiveKit workers
# The worker maintains connection to LiveKit server and auto-reconnects

# Run the voice agent
# Using 'dev' mode for live reloading during development
CMD ["python", "voice_agent_m4markets.py", "dev"]
