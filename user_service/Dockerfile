# user_service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies - added run to match task_service
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for database
RUN mkdir -p /app/data

# Expose port
EXPOSE 6001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:6001/health || exit 1

# Run the application
CMD ["python", "app.py"]