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

# Expose port (Render provides PORT env var)
EXPOSE 10000

# Set environment variables
ENV PORT=10000
ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1

# Run the application via the startup script
RUN chmod +x start_render.sh
CMD ["./start_render.sh"]
