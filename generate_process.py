import os
from text_to_audio import text_to_speech_file
import time
import subprocess

def text_to_audio(folder):
    print("TTA -", folder)
    desc_path = f"user_uploads/{folder}/desc.txt"
    if not os.path.exists(desc_path):
        print(f"No desc.txt found in {folder}")
        return
    with open(desc_path) as f:
        text = f.read()
    print(text, folder)
    text_to_speech_file(text, folder)

def create_reel(folder):
    output_path = f"static/reels/{folder}.mp4"
    os.makedirs("static/reels", exist_ok=True)
    
    input_txt_path = f"user_uploads/{folder}/input.txt"
    audio_path = f"user_uploads/{folder}/audio.mp3"
    
    if not os.path.exists(input_txt_path):
        print(f"Input file not found: {input_txt_path}")
        return False
        
    if not os.path.exists(audio_path):
        print(f"Audio file not found: {audio_path}")
        return False
    
    command = f'''ffmpeg -f concat -safe 0 -i {input_txt_path} -i {audio_path} \
-vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
-c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p {output_path}'''.strip()
    
    try:
        subprocess.run(command, shell=True, check=True)
        print("CR -", folder)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error for {folder}: {e}")
        return False

if __name__ == "__main__":
    while True:
        print("Processing Queue.....")
        if os.path.exists("done.txt"):
            with open("done.txt", "r") as f:
                done_folders = [line.strip() for line in f.readlines()]
        else:
            done_folders = []

        folders = os.listdir("user_uploads")
        for folder in folders:
            if folder not in done_folders and os.path.isdir(f"user_uploads/{folder}"):
                try:
                    print(f"Processing folder: {folder}")
                    text_to_audio(folder)     # 🔁 Step 1: Generate audio
                    if create_reel(folder):   # 🎥 Step 2: Create video with audio
                        with open("done.txt", "a") as f:
                            f.write(folder + "\n")
                        print(f"Successfully processed: {folder}")
                    else:
                        print(f"Failed to create reel for: {folder}")
                except Exception as e:
                    print(f"Error processing {folder}: {e}")
                    continue

        time.sleep(4)
