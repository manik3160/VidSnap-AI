#!/bin/bash

# Ensure necessary directories exist
mkdir -p user_uploads static/reels

# Start the Flask app (which now starts the background worker internally)
echo "🚀 Starting VidSnapAI..."
python main.py
