#!/usr/bin/env python3
"""
Simple startup script for VidSnap-AI (without cloud storage)
Use this if cloud storage setup is not ready
"""

import os

def main():
    """Main startup function"""
    print("🚀 Starting VidSnap-AI (Simple Mode)...")
    
    try:
        # Import and initialize Flask app
        from main import app, db
        
        # Initialize database
        with app.app_context():
            db.create_all()
            print("✅ Database initialized")
        
        # Start Flask app
        port = int(os.environ.get('PORT', 5001))
        print(f"🌐 Starting Flask app on port {port}")
        app.run(debug=False, host='0.0.0.0', port=port)
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        raise

if __name__ == "__main__":
    main()
