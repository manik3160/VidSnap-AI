from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import uuid
from werkzeug.utils import secure_filename
import os
import glob
import threading
import time
from datetime import datetime

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('SECRET_KEY', 'test-secret-key-123')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_reel_simple(reel_id, description, title):
    """Process a reel without FFmpeg - just create a placeholder video"""
    try:
        print(f"🎬 Processing reel: {reel_id}")
        print(f"📝 Description: {description}")
        print(f"🏷️ Title: {title}")
        
        # Find the user upload folder
        upload_dir = os.path.join(UPLOAD_FOLDER, reel_id)
        print(f"📁 Looking for upload directory: {upload_dir}")
        
        if not os.path.exists(upload_dir):
            print(f"❌ Upload directory not found: {upload_dir}")
            return
        
        print(f"✅ Upload directory found: {upload_dir}")
        
        # List files in directory
        files_in_dir = os.listdir(upload_dir)
        print(f"📋 Files in directory: {files_in_dir}")
        
        # Create a simple status file
        status_file = os.path.join(upload_dir, "status.txt")
        with open(status_file, "w") as f:
            f.write("processing")
        print(f"📄 Created status file: {status_file}")
        
        # Simulate processing time
        print(f"⏳ Simulating processing time...")
        time.sleep(2)
        
        # Create static reels directory
        static_reels_dir = "static/reels"
        os.makedirs(static_reels_dir, exist_ok=True)
        print(f"📁 Created static reels directory: {static_reels_dir}")
        
        # Create a placeholder video file (just copy an image as video for now)
        image_files = glob.glob(os.path.join(upload_dir, "*.jpg")) + glob.glob(os.path.join(upload_dir, "*.jpeg")) + glob.glob(os.path.join(upload_dir, "*.png"))
        print(f"🖼️ Found {len(image_files)} image files: {image_files}")
        
        if image_files:
            # Copy first image as placeholder video
            import shutil
            placeholder_video = os.path.join(static_reels_dir, f"{reel_id}.mp4")
            shutil.copy2(image_files[0], placeholder_video)
            print(f"✅ Created placeholder video: {placeholder_video}")
        else:
            print(f"⚠️ No image files found to create video from")
        
        # Update status
        with open(status_file, "w") as f:
            f.write("completed")
        print(f"📄 Updated status to completed")
        
        print(f"🎉 Reel {reel_id} processing completed!")
        
    except Exception as e:
        print(f"❌ Error processing reel {reel_id}: {e}")
        import traceback
        print(f"🔍 Full error traceback: {traceback.format_exc()}")

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
        
        print(f"🎬 Creating reel: {rec_id}")
        print(f"📝 Description: {desc}")
        print(f"🏷️ Title: {title}")
        print(f"📎 Files received: {list(request.files.keys())}")
        
        if not rec_id or not desc:
            print(f"❌ Missing required fields - rec_id: {rec_id}, desc: {desc}")
            return render_template("create.html", myid=myid, error="Missing required fields")
            
        input_files = []
        try:
            # Create upload directory
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
            os.makedirs(upload_dir, exist_ok=True)
            print(f"📁 Created directory: {upload_dir}")
            
            # Save uploaded files
            for key, value in request.files.items():
                file = request.files[key]
                if file and file.filename != '':
                    print(f"📎 Processing file: {file.filename}")
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(upload_dir, filename)
                        file.save(file_path)
                        input_files.append(filename)
                        print(f"✅ Saved file: {file_path}")
                    else:
                        return render_template("create.html", myid=myid, error="Invalid file type")
            
            # Save description
            desc_file = os.path.join(upload_dir, "desc.txt")
            with open(desc_file, "w") as file:
                file.write(desc)
            print(f"✅ Saved description: {desc_file}")
            
            # Start background processing
            thread = threading.Thread(target=process_reel_simple, args=(rec_id, desc, title))
            thread.daemon = True
            thread.start()
            print(f"🚀 Background processing started for reel {rec_id}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            return render_template("create.html", myid=myid, error=f"Upload failed: {str(e)}")
        
        # If we reach here, upload was successful
        flash(f"Reel {rec_id} uploaded successfully! Processing in background...", "success")
        return redirect(url_for('gallery'))
     
    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    try:
        print("🖼️ Loading gallery...")
        
        # Check for completed reels
        reel_data = []
        
        # Check static folder for videos
        static_reels_dir = "static/reels"
        if os.path.exists(static_reels_dir):
            video_files = glob.glob(os.path.join(static_reels_dir, "*.mp4"))
            for video_file in video_files:
                reel_id = os.path.basename(video_file).replace('.mp4', '')
                
                # Check if this reel has a description
                desc_file = os.path.join(UPLOAD_FOLDER, reel_id, "desc.txt")
                description = "No description"
                if os.path.exists(desc_file):
                    with open(desc_file, 'r') as f:
                        description = f.read().strip()
                
                reel_data.append({
                    'id': reel_id,
                    'name': f"Reel {reel_id[:8]}",
                    'description': description,
                    'video_url': f"/static/reels/{reel_id}.mp4",
                    'thumbnail_url': f"/static/reels/{reel_id}.jpg",
                    'status': 'completed',
                    'created_at': 'Recently'
                })
        
        # Also check for processing reels
        if os.path.exists(UPLOAD_FOLDER):
            for item in os.listdir(UPLOAD_FOLDER):
                item_path = os.path.join(UPLOAD_FOLDER, item)
                if os.path.isdir(item_path):
                    status_file = os.path.join(item_path, "status.txt")
                    status = "uploaded"
                    if os.path.exists(status_file):
                        with open(status_file, 'r') as f:
                            status = f.read().strip()
                    
                    # Only add if not already in reel_data
                    if not any(reel['id'] == item for reel in reel_data):
                        desc_file = os.path.join(item_path, "desc.txt")
                        description = "No description"
                        if os.path.exists(desc_file):
                            with open(desc_file, 'r') as f:
                                description = f.read().strip()
                        
                        reel_data.append({
                            'id': item,
                            'name': f"Reel {item[:8]}",
                            'description': description,
                            'video_url': f"/static/reels/{item}.mp4" if status == "completed" else None,
                            'thumbnail_url': f"/static/reels/{item}.jpg" if status == "completed" else None,
                            'status': status,
                            'created_at': 'Recently'
                        })
        
        print(f"🖼️ Gallery loaded with {len(reel_data)} reels")
        return render_template("gallery.html", reels=reel_data)
            
    except Exception as e:
        print(f"❌ Error loading gallery: {e}")
        return render_template("gallery.html", reels=[], error=str(e))

@app.route("/delete_reel/<reel_name>", methods=["POST"])
def delete_reel(reel_name):
    try:
        print(f"🗑️ Deleting reel: {reel_name}")
        
        # Security check: ensure the filename is safe
        if not reel_name or '..' in reel_name or '/' in reel_name:
            return {"success": False, "message": "Invalid reel name"}, 400
        
        # Delete the folder
        reel_path = os.path.join(UPLOAD_FOLDER, reel_name)
        if os.path.exists(reel_path):
            import shutil
            shutil.rmtree(reel_path)
            print(f"✅ Deleted reel folder: {reel_path}")
        
        # Delete the video file
        video_path = os.path.join("static/reels", f"{reel_name}.mp4")
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"✅ Deleted video file: {video_path}")
        
        return {"success": True, "message": "Reel deleted successfully"}
            
    except Exception as e:
        print(f"❌ Error deleting reel {reel_name}: {e}")
        return {"success": False, "message": f"Error deleting reel: {str(e)}"}, 500

@app.route("/status")
def status():
    """Check app status"""
    status_info = {
        "status": "running",
        "upload_folder": UPLOAD_FOLDER,
        "upload_folder_exists": os.path.exists(UPLOAD_FOLDER),
        "secret_key_set": bool(app.secret_key),
        "working_directory": os.getcwd(),
        "reels_count": 0
    }
    
    if os.path.exists(UPLOAD_FOLDER):
        status_info["reels_count"] = len([d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))])
    
    return jsonify(status_info)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 Starting VidSnap-AI Working Version on port {port}")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🔑 Secret key set: {bool(app.secret_key)}")
    app.run(debug=False, host='0.0.0.0', port=port)
