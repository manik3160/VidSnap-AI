from flask import Flask, render_template, request, redirect, url_for, flash
import uuid
from werkzeug.utils import secure_filename
import os

# Try to import database components, fallback if not available
try:
    from flask_sqlalchemy import SQLAlchemy
    from models import db, Reel
    from cloud_storage import CloudStorage
    DB_AVAILABLE = True
    print("✅ Database components loaded successfully")
except ImportError as e:
    print(f"⚠️ Database components not available: {e}")
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
            
            print(f"✅ Found {len(reel_data)} completed reels in database")
            return render_template("gallery.html", reels=reel_data)
        else:
            # Fallback: show message about database not available
            return render_template("gallery.html", reels=[], message="Database not available - reels will be processed when database is set up")
            
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

if __name__ == "__main__":
    if DB_AVAILABLE:
        with app.app_context():
            db.create_all()
    
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 Starting VidSnap-AI on port {port}")
    print(f"📊 Database available: {DB_AVAILABLE}")
    app.run(debug=False, host='0.0.0.0', port=port)
