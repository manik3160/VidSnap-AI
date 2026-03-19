#!/bin/bash

# VidSnap-AI Startup Script
echo "🚀 Starting VidSnap-AI..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one with your API keys."
    echo "Example:"
    echo "ELEVENLABS_API_KEY=your_api_key_here"
    exit 1
fi

# Start the background processor
echo "🎬 Starting video processor..."
python background_processor.py &
PROCESSOR_PID=$!

# Start the Flask app
echo "🌐 Starting Flask application..."
python main.py

# Cleanup on exit
trap "kill $PROCESSOR_PID 2>/dev/null" EXIT
