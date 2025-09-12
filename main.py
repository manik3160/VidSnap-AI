from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.utils import secure_filename
import os
from models import db, Reel
from cloud_storage import CloudStorage

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///vidsnap.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize database
db.init_app(app)
cloud_storage = CloudStorage()


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
            
            # Create reel record in database
            new_reel = Reel(
                reel_id=rec_id,
                title=title,
                description=desc,
                status='processing'
            )
            db.session.add(new_reel)
            db.session.commit()
                    
        except Exception as e:
            return render_template("create.html", myid=myid, error=f"Upload failed: {str(e)}")
        
        # If we reach here, upload was successful
        flash("Reel creation started! Your reel will be ready shortly.", "success")
        return redirect(url_for('gallery'))
     
    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    try:
        # Get reels from database
        reels = Reel.query.filter_by(status='completed').all()
        reel_data = []
        
        for reel in reels:
            reel_data.append({
                'id': reel.reel_id,
                'name': reel.title,
                'video_url': reel.video_url,
                'thumbnail_url': reel.thumbnail_url,
                'created_at': reel.created_at.strftime('%Y-%m-%d') if reel.created_at else 'Recently'
            })
        
        return render_template("gallery.html", reels=reel_data)
    except Exception as e:
        print(f"Error loading gallery: {e}")
        return render_template("gallery.html", reels=[])

@app.route("/delete_reel/<reel_name>", methods=["POST"])
def delete_reel(reel_name):
    try:
        # Security check: ensure the filename is safe
        if not reel_name.endswith('.mp4') or '..' in reel_name or '/' in reel_name:
            return {"success": False, "message": "Invalid filename"}, 400
            
        reel_path = os.path.join("static/reels", reel_name)
        
        if os.path.exists(reel_path):
            os.remove(reel_path)
            print(f"Deleted reel: {reel_name}")
            return {"success": True, "message": "Reel deleted successfully"}
        else:
            return {"success": False, "message": "Reel not found"}, 404
            
    except Exception as e:
        print(f"Error deleting reel {reel_name}: {e}")
        return {"success": False, "message": f"Error deleting reel: {str(e)}"}, 500

@app.route("/init-db")
def init_db():
    """Initialize database tables"""
    try:
        with app.app_context():
            db.create_all()
        return "Database initialized successfully!"
    except Exception as e:
        return f"Error initializing database: {e}"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
