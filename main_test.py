from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import uuid
from werkzeug.utils import secure_filename
import os
import glob

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('SECRET_KEY', 'test-secret-key-123')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        print(f"📁 Upload folder: {UPLOAD_FOLDER}")
        
        if not rec_id or not desc:
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
            
            # Create a simple status file
            status_file = os.path.join(upload_dir, "status.txt")
            with open(status_file, "w") as file:
                file.write("uploaded")
            print(f"✅ Created status file: {status_file}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            return render_template("create.html", myid=myid, error=f"Upload failed: {str(e)}")
        
        # If we reach here, upload was successful
        flash(f"Reel {rec_id} uploaded successfully! Check gallery to see it.", "success")
        return redirect(url_for('gallery'))
     
    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    try:
        print("🖼️ Loading gallery...")
        
        # Check for uploaded reels
        reel_data = []
        
        if os.path.exists(UPLOAD_FOLDER):
            print(f"📁 Checking upload folder: {UPLOAD_FOLDER}")
            for item in os.listdir(UPLOAD_FOLDER):
                item_path = os.path.join(UPLOAD_FOLDER, item)
                if os.path.isdir(item_path):
                    print(f"📁 Found reel folder: {item}")
                    
                    # Check if it has description
                    desc_file = os.path.join(item_path, "desc.txt")
                    if os.path.exists(desc_file):
                        with open(desc_file, 'r') as f:
                            description = f.read().strip()
                        
                        # Check for images
                        image_files = glob.glob(os.path.join(item_path, "*.jpg")) + glob.glob(os.path.join(item_path, "*.jpeg")) + glob.glob(os.path.join(item_path, "*.png"))
                        
                        reel_data.append({
                            'id': item,
                            'name': f"Reel {item[:8]}",
                            'description': description,
                            'image_count': len(image_files),
                            'status': 'uploaded',
                            'created_at': 'Recently'
                        })
                        print(f"✅ Added reel: {item} with {len(image_files)} images")
        
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
            return {"success": True, "message": "Reel deleted successfully"}
        else:
            return {"success": False, "message": "Reel not found"}
            
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
        "files_in_upload_folder": []
    }
    
    if os.path.exists(UPLOAD_FOLDER):
        status_info["files_in_upload_folder"] = os.listdir(UPLOAD_FOLDER)
    
    return jsonify(status_info)

@app.route("/debug")
def debug():
    """Debug information"""
    debug_info = {
        "python_version": os.sys.version,
        "working_directory": os.getcwd(),
        "environment_variables": dict(os.environ),
        "upload_folder_contents": []
    }
    
    if os.path.exists(UPLOAD_FOLDER):
        debug_info["upload_folder_contents"] = os.listdir(UPLOAD_FOLDER)
    
    return jsonify(debug_info, indent=2)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 Starting VidSnap-AI Test Version on port {port}")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🔑 Secret key set: {bool(app.secret_key)}")
    app.run(debug=False, host='0.0.0.0', port=port)
