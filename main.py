from flask import Flask, render_template, request, redirect, url_for, flash
import uuid
from werkzeug.utils import secure_filename
import os

# --- Configuration ---
UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# --- App Initialization ---
app = Flask(__name__)
# It's good practice to set a secret key for flashing messages
app.config['SECRET_KEY'] = 'your-super-secret-key' 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Helper Functions ---
def allowed_file(filename):
    """Checks if a filename has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- App Routes ---
@app.route("/")
def home():
    """Renders the home page."""
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    """
    Handles the creation page.
    GET: Displays the upload form with a new unique ID.
    POST: Processes the uploaded files and description.
    """
    if request.method == "POST":
      
        rec_id = request.form.get("uuid")
        desc = request.form.get("text")
       
        uploaded_files = request.files.getlist("files") 

        if not rec_id:
            flash("Error: Missing submission ID. Please try again.", "error")
            return redirect(request.url)

        saved_filenames = []
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)

      
        os.makedirs(upload_path, exist_ok=True)

       
        for file in uploaded_files:
            
            if file.filename == '':
                continue 

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_path, filename))
                saved_filenames.append(filename)
            else:
                
                flash(f"File '{file.filename}' has an invalid type and was not uploaded.", "warning")

        
        if saved_filenames:
        
            with open(os.path.join(upload_path, "desc.txt"), "w") as f:
                f.write(desc or "")

            
            with open(os.path.join(upload_path, "input.txt"), "w") as f:
                for filename in saved_filenames:
                    f.write(f"file '{filename}'\n")
                    f.write("duration 1\n")
            
            flash(f"Successfully uploaded {len(saved_filenames)} file(s)!", "success")
        else:
            flash("No valid files were uploaded.", "info")

        
        return redirect(url_for('gallery'))

    
    myid = uuid.uuid4()
    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    """Displays a gallery of previously created reels."""
   
    try:
        reels = os.listdir(os.path.join("static", "reels"))
    except FileNotFoundError:
        reels = []
        flash("Could not find the 'reels' directory.", "warning")
        
    return render_template("gallery.html", reels=reels)

# --- Run the App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
