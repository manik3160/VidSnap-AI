# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p user_uploads static/reels

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV FLASK_APP=main_working.py

# Run the application
CMD ["python", "main_working.py"]
