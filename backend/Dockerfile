# Multi-stage build for Python backend
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app ./app

# Copy startup script
COPY backend/start.sh ./start.sh
RUN chmod +x ./start.sh

# Expose port
EXPOSE 8000

# Run the application
CMD ["./start.sh"]
