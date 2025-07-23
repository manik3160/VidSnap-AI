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
    command = f'''ffmpeg -f concat -safe 0 -i user_uploads/{folder}/input.txt -i user_uploads/{folder}/audio.mp3 \
-vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
-c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p {output_path}'''.strip()
    
    subprocess.run(command, shell=True, check=True)
    print("CR -", folder)

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
            if folder not in done_folders:
                text_to_audio(folder)     # 🔁 Step 1: Generate audio
                create_reel(folder)       # 🎥 Step 2: Create video with audio
                with open("done.txt", "a") as f:
                    f.write(folder + "\n")

        time.sleep(4)
