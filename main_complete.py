from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import uuid
from werkzeug.utils import secure_filename
import os
import glob
import subprocess
import threading
import time
from datetime import datetime

# Try to import database components, fallback if not available
try:
    from flask_sqlalchemy import SQLAlchemy
    from models import db, Reel
    from cloud_storage import CloudStorage
    from text_to_audio import generate_audio
    DB_AVAILABLE = True
    print("✅ All components loaded successfully")
except ImportError as e:
    print(f"⚠️ Some components not available: {e}")
    DB_AVAILABLE = False

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Database configuration (only if available)
if DB_AVAILABLE:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///vidsnap.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    cloud_storage = CloudStorage()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_reel_background(reel_id, description, title):
    """Process a reel in the background"""
    try:
        print(f"🎬 Processing reel: {reel_id}")
        
        # Find the user upload folder
        upload_dir = os.path.join(UPLOAD_FOLDER, reel_id)
        
        if not os.path.exists(upload_dir):
            print(f"❌ Upload directory not found: {upload_dir}")
            return
        
        # Generate audio
        desc_file = os.path.join(upload_dir, "desc.txt")
        if os.path.exists(desc_file):
            with open(desc_file, 'r') as f:
                description = f.read().strip()
            
            # Generate audio
            audio_path = os.path.join(upload_dir, "audio.mp3")
            if DB_AVAILABLE:
                generate_audio(description, audio_path)
            else:
                # Create a dummy audio file for testing
                with open(audio_path, 'w') as f:
                    f.write("dummy audio")
            print(f"✅ Audio generated: {audio_path}")
        else:
            print(f"❌ Description file not found: {desc_file}")
            return
        
        # Create video using FFmpeg
        video_path = os.path.join(UPLOAD_FOLDER, f"{reel_id}.mp4")
        
        # Get image files
        image_files = glob.glob(os.path.join(upload_dir, "*.jpg")) + glob.glob(os.path.join(upload_dir, "*.jpeg")) + glob.glob(os.path.join(upload_dir, "*.png"))
        
        if not image_files:
            print(f"❌ No images found in {upload_dir}")
            return
        
        print(f"✅ Found {len(image_files)} images")
        
        # Create FFmpeg command
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-loop', '1',
            '-i', image_files[0],  # Use first image
            '-i', audio_path,
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
            video_path
        ]
        
        print(f"🎥 Running FFmpeg: {' '.join(ffmpeg_cmd)}")
        
        # Run FFmpeg
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ FFmpeg error: {result.stderr}")
            return
        
        print(f"✅ Video created: {video_path}")
        
        # Update database
        if DB_AVAILABLE:
            try:
                reel = Reel.query.filter_by(reel_id=reel_id).first()
                if reel:
                    reel.status = 'completed'
                    reel.video_url = f"/static/reels/{reel_id}.mp4"
                    reel.thumbnail_url = f"/static/reels/{reel_id}.jpg"
                    reel.audio_url = f"/static/audio/{reel_id}.mp3"
                    db.session.commit()
                    print(f"✅ Database updated for reel {reel_id}")
                else:
                    print(f"❌ Reel {reel_id} not found in database")
            except Exception as e:
                print(f"❌ Database update error: {e}")
        
        # Move video to static folder
        static_reels_dir = "static/reels"
        os.makedirs(static_reels_dir, exist_ok=True)
        
        if os.path.exists(video_path):
            import shutil
            shutil.move(video_path, os.path.join(static_reels_dir, f"{reel_id}.mp4"))
            print(f"✅ Video moved to static folder")
        else:
            print(f"⚠️ Video file not found: {video_path}")
        
        print(f"🎉 Reel {reel_id} processing completed!")
        
    except Exception as e:
        print(f"❌ Error processing reel {reel_id}: {e}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    myid = str(uuid.uuid1())

    if request.method == "POST":
        rec_id = request.form.get("uuid")
        desc = request.form.get("text")
        title = request.form.get("title", "My Reel")
        
        if not rec_id or not desc:
            return render_template("create.html", myid=myid, error="Missing required fields")
            
        input_files = []
        try:
            # Create upload directory
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save uploaded files
            for key, value in request.files.items():
                file = request.files[key]
                if file and file.filename != '':
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(upload_dir, filename))
                        input_files.append(filename)
                    else:
                        return render_template("create.html", myid=myid, error="Invalid file type")
            
            # Save description
            with open(os.path.join(upload_dir, "desc.txt"), "w") as file:
                file.write(desc)
            
            # Create reel record in database (if available)
            if DB_AVAILABLE:
                try:
                    new_reel = Reel(
                        reel_id=rec_id,
                        title=title,
                        description=desc,
                        status='processing'
                    )
                    db.session.add(new_reel)
                    db.session.commit()
                    print(f"✅ Reel {rec_id} added to database")
                except Exception as e:
                    print(f"⚠️ Database error: {e}")
            
            # Start background processing
            thread = threading.Thread(target=process_reel_background, args=(rec_id, desc, title))
            thread.daemon = True
            thread.start()
            print(f"🚀 Background processing started for reel {rec_id}")
                    
        except Exception as e:
            return render_template("create.html", myid=myid, error=f"Upload failed: {str(e)}")
        
        # If we reach here, upload was successful
        flash("Reel creation started! Your reel will be ready shortly.", "success")
        return redirect(url_for('gallery'))
     
    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    try:
        if DB_AVAILABLE:
            # Get reels from database
            reels = Reel.query.all()  # Get all reels, not just completed
            reel_data = []
            
            for reel in reels:
                reel_data.append({
                    'id': reel.reel_id,
                    'name': reel.title,
                    'video_url': reel.video_url or f"/static/reels/{reel.reel_id}.mp4",
                    'thumbnail_url': reel.thumbnail_url or f"/static/reels/{reel.reel_id}.jpg",
                    'status': reel.status,
                    'created_at': reel.created_at.strftime('%Y-%m-%d') if reel.created_at else 'Recently'
                })
            
            print(f"✅ Found {len(reel_data)} reels in database")
            return render_template("gallery.html", reels=reel_data)
        else:
            # Fallback: check static folder for videos
            static_reels_dir = "static/reels"
            if os.path.exists(static_reels_dir):
                video_files = glob.glob(os.path.join(static_reels_dir, "*.mp4"))
                reel_data = []
                for video_file in video_files:
                    reel_id = os.path.basename(video_file).replace('.mp4', '')
                    reel_data.append({
                        'id': reel_id,
                        'name': f"Reel {reel_id[:8]}",
                        'video_url': f"/static/reels/{reel_id}.mp4",
                        'thumbnail_url': f"/static/reels/{reel_id}.jpg",
                        'status': 'completed',
                        'created_at': 'Recently'
                    })
                print(f"✅ Found {len(reel_data)} videos in static folder")
                return render_template("gallery.html", reels=reel_data)
            else:
                return render_template("gallery.html", reels=[], message="No reels found")
            
    except Exception as e:
        print(f"Error loading gallery: {e}")
        return render_template("gallery.html", reels=[], error=str(e))

@app.route("/delete_reel/<reel_name>", methods=["POST"])
def delete_reel(reel_name):
    try:
        # Security check: ensure the filename is safe
        if not reel_name or '..' in reel_name or '/' in reel_name:
            return {"success": False, "message": "Invalid reel name"}, 400
        
        if DB_AVAILABLE:
            # Delete from database
            try:
                reel = Reel.query.filter_by(reel_id=reel_name).first()
                if reel:
                    db.session.delete(reel)
                    db.session.commit()
                    return {"success": True, "message": "Reel deleted successfully"}
                else:
                    return {"success": False, "message": "Reel not found"}
            except Exception as e:
                return {"success": False, "message": f"Database error: {str(e)}"}, 500
        else:
            return {"success": True, "message": "Reel deleted successfully"}
            
    except Exception as e:
        print(f"Error deleting reel {reel_name}: {e}")
        return {"success": False, "message": f"Error deleting reel: {str(e)}"}, 500

@app.route("/init-db")
def init_db():
    """Initialize database tables"""
    if not DB_AVAILABLE:
        return "Database components not available. Please check dependencies."
    
    try:
        with app.app_context():
            db.create_all()
        return "Database initialized successfully!"
    except Exception as e:
        return f"Error initializing database: {e}"

@app.route("/status")
def status():
    """Check app status"""
    return jsonify({
        "status": "running",
        "database_available": DB_AVAILABLE,
        "upload_folder": UPLOAD_FOLDER,
        "upload_folder_exists": os.path.exists(UPLOAD_FOLDER)
    })

if __name__ == "__main__":
    if DB_AVAILABLE:
        with app.app_context():
            db.create_all()
    
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 Starting VidSnap-AI on port {port}")
    print(f"📊 Database available: {DB_AVAILABLE}")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    app.run(debug=False, host='0.0.0.0', port=port)
