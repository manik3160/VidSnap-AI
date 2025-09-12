#!/usr/bin/env python3
"""
Railway startup script for VidSnap-AI
Starts both the Flask app and background processor
"""

import os
import subprocess
import threading
import time
from main import app, db

def start_background_processor():
    """Start the background processor in a separate thread"""
    try:
        from background_processor import process_reels
        process_reels()
    except Exception as e:
        print(f"Background processor error: {e}")

def main():
    """Main startup function"""
    print("🚀 Starting VidSnap-AI on Railway...")
    
    # Initialize database
    with app.app_context():
        db.create_all()
        print("✅ Database initialized")
    
    # Start background processor in a separate thread
    bg_thread = threading.Thread(target=start_background_processor, daemon=True)
    bg_thread.start()
    print("✅ Background processor started")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5001))
    print(f"🌐 Starting Flask app on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)

if __name__ == "__main__":
    main()
