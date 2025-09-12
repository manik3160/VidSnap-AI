import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from werkzeug.utils import secure_filename

class CloudStorage:
    def __init__(self):
        self.cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        self.api_key = os.getenv('CLOUDINARY_API_KEY')
        self.api_secret = os.getenv('CLOUDINARY_API_SECRET')
        
        if not all([self.cloud_name, self.api_key, self.api_secret]):
            print("⚠️ Cloudinary credentials not found. Using local storage fallback.")
            self.enabled = False
        else:
            cloudinary.config(
                cloud_name=self.cloud_name,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            self.enabled = True
    
    def upload_image(self, file_path, folder="vidsnap/images"):
        """Upload image to Cloudinary"""
        if not self.enabled:
            return None
        try:
            result = cloudinary.uploader.upload(
                file_path,
                folder=folder,
                resource_type="image",
                transformation=[
                    {"width": 1080, "height": 1920, "crop": "fill", "quality": "auto"},
                    {"format": "auto"}
                ]
            )
            return result['secure_url']
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None
    
    def upload_video(self, file_path, folder="vidsnap/videos"):
        """Upload video to Cloudinary"""
        if not self.enabled:
            return None
        try:
            result = cloudinary.uploader.upload(
                file_path,
                folder=folder,
                resource_type="video",
                transformation=[
                    {"width": 1080, "height": 1920, "crop": "fill"},
                    {"format": "mp4", "quality": "auto"}
                ]
            )
            return result['secure_url']
        except Exception as e:
            print(f"Error uploading video: {e}")
            return None
    
    def upload_audio(self, file_path, folder="vidsnap/audio"):
        """Upload audio to Cloudinary"""
        if not self.enabled:
            return None
        try:
            result = cloudinary.uploader.upload(
                file_path,
                folder=folder,
                resource_type="video",  # Cloudinary treats audio as video
                format="mp3"
            )
            return result['secure_url']
        except Exception as e:
            print(f"Error uploading audio: {e}")
            return None
    
    def delete_file(self, public_id):
        """Delete file from Cloudinary"""
        if not self.enabled:
            return False
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_thumbnail_url(self, video_url):
        """Generate thumbnail URL from video URL"""
        if not self.enabled or not video_url:
            return None
        try:
            # Extract public_id from URL
            public_id = video_url.split('/')[-1].split('.')[0]
            thumbnail_url = f"https://res.cloudinary.com/{self.cloud_name}/video/upload/w_400,h_auto,c_fill,q_auto,f_auto/{public_id}.jpg"
            return thumbnail_url
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
