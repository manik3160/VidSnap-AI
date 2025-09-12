import os
import time
import subprocess
import uuid
from flask import Flask
from models import db, Reel
from cloud_storage import CloudStorage
from text_to_audio import generate_audio
import glob

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///vidsnap.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def process_reels():
    """Process pending reels in the background"""
    app = create_app()
    cloud_storage = CloudStorage()
    
    with app.app_context():
        while True:
            try:
                # Get all processing reels
                processing_reels = Reel.query.filter_by(status='processing').all()
                
                for reel in processing_reels:
                    print(f"Processing reel: {reel.reel_id}")
                    
                    try:
                        # Process the reel
                        result = process_single_reel(reel, cloud_storage)
                        
                        if result['success']:
                            reel.status = 'completed'
                            reel.video_url = result['video_url']
                            reel.thumbnail_url = result['thumbnail_url']
                            reel.audio_url = result['audio_url']
                        else:
                            reel.status = 'failed'
                        
                        db.session.commit()
                        print(f"Reel {reel.reel_id} processed successfully")
                        
                    except Exception as e:
                        print(f"Error processing reel {reel.reel_id}: {e}")
                        reel.status = 'failed'
                        db.session.commit()
                
                # Sleep for 10 seconds before checking again
                time.sleep(10)
                
            except Exception as e:
                print(f"Error in background processor: {e}")
                time.sleep(30)

def process_single_reel(reel, cloud_storage):
    """Process a single reel"""
    try:
        # Find the user upload folder
        upload_dir = f"user_uploads/{reel.reel_id}"
        
        if not os.path.exists(upload_dir):
            return {"success": False, "error": "Upload directory not found"}
        
        # Generate audio
        desc_file = os.path.join(upload_dir, "desc.txt")
        if os.path.exists(desc_file):
            with open(desc_file, 'r') as f:
                description = f.read().strip()
            
            # Generate audio
            audio_path = os.path.join(upload_dir, "audio.mp3")
            generate_audio(description, audio_path)
            
            # Upload audio to cloud
            audio_url = cloud_storage.upload_audio(audio_path)
        else:
            return {"success": False, "error": "Description file not found"}
        
        # Create video using FFmpeg
        video_path = os.path.join(upload_dir, f"{reel.reel_id}.mp4")
        
        # Get image files
        image_files = glob.glob(os.path.join(upload_dir, "*.jpg")) + glob.glob(os.path.join(upload_dir, "*.jpeg")) + glob.glob(os.path.join(upload_dir, "*.png"))
        
        if not image_files:
            return {"success": False, "error": "No images found"}
        
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
        
        # Run FFmpeg
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {"success": False, "error": f"FFmpeg error: {result.stderr}"}
        
        # Upload video to cloud
        video_url = cloud_storage.upload_video(video_path)
        thumbnail_url = cloud_storage.get_thumbnail_url(video_url)
        
        return {
            "success": True,
            "video_url": video_url,
            "thumbnail_url": thumbnail_url,
            "audio_url": audio_url
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    process_reels()
