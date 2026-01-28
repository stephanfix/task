# task_service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies and curl for health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for database
RUN mkdir -p /app/data

# Expose port
EXPOSE 6002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5002/health || exit 1

# Run the application
CMD ["python", "app.py"]