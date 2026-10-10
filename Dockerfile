# Production Dockerfile for Lead Generation Engine
FROM python:3.10-slim

# Prevent Python from writing .pyc files & enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependency list and install requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/

# Create output directory for local JSON cache files and export output
RUN mkdir -p /app/output

# Expose server port (configured via PORT env variable on Render)
EXPOSE 8000

# Start application server
CMD ["python", "app.py"]
