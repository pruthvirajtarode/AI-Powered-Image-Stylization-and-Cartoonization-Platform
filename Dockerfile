# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for OpenCV and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Create necessary directories
RUN mkdir -p backend/data/processed_images backend/data/cache

# Expose the port (Render overrides with $PORT env var)
EXPOSE 5000

# Use $PORT injected by Render; fall back to 5000 locally
# --preload ensures DB initializes once before workers fork
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 300 --preload --chdir /app/backend backend:app
