from flask import Flask, render_template, request, redirect, url_for, flash
import uuid
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

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
                    
        except Exception as e:
            return render_template("create.html", myid=myid, error=f"Upload failed: {str(e)}")
        
        # If we reach here, upload was successful
        flash("Reel creation started! Your reel will be ready shortly.", "success")
        return redirect(url_for('gallery'))
     
    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    try:
        # Simple gallery - just show a message for now
        return render_template("gallery.html", reels=[])
    except Exception as e:
        print(f"Error loading gallery: {e}")
        return render_template("gallery.html", reels=[])

@app.route("/delete_reel/<reel_name>", methods=["POST"])
def delete_reel(reel_name):
    try:
        # Security check: ensure the filename is safe
        if not reel_name or '..' in reel_name or '/' in reel_name:
            return {"success": False, "message": "Invalid reel name"}, 400
        
        # For now, just return success
        return {"success": True, "message": "Reel deleted successfully"}
            
    except Exception as e:
        print(f"Error deleting reel {reel_name}: {e}")
        return {"success": False, "message": f"Error deleting reel: {str(e)}"}, 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
