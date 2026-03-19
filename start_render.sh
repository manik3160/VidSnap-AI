#!/bin/bash

# Ensure log file exists before starting
mkdir -p static
touch static/processor.log

# Start the background processor and redirect logs to static folder for web access
echo "🎬 Starting video processor..."
python background_processor.py > static/processor.log 2>&1 &
PROCESSOR_PID=$!

# Start the Flask app
echo "🌐 Starting Flask application..."
python main.py

# Cleanup on exit
trap "kill $PROCESSOR_PID 2>/dev/null" EXIT
