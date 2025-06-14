# 🎬 VidSnap-AI

**VidSnap-AI** is an AI-powered application that generates short-form videos (like Instagram Reels or YouTube Shorts) from plain text descriptions. It uses text-to-speech synthesis and combines it with royalty-free background music and visuals to output complete reels automatically — perfect for content creators, educators, and marketers.

---

## 🧠 How It Works

1. **User uploads** a folder containing a `desc.txt` file in `/user_uploads`.
2. **Text-to-speech** (TTS) converts the description into an audio file.
3. **Music and visuals** from `songs/` and `reels/` are combined with the voiceover.
4. A final short-form video is generated using **FFmpeg** and saved.

---

## 🚀 Features

- ✅ AI-based narration via text-to-speech
- 🎵 Auto-background music from `songs/`
- 🎥 Random reel visuals or B-rolls from `reels/`
- 🗂️ Batch input support via folders
- ⚙️ Flask-based interface (minimal UI in `templates/`)
- 🖥️ Locally runnable with basic system dependencies

---

## 🛠 Tech Stack

- **Backend**: Python, Flask
- **Audio/Video Processing**: FFmpeg (CLI), Python `subprocess`
- **TTS**:ElevenLabs API
- **Frontend**: HTML,CSS
- **Other Tools**: `uuid`, `os`, `glob`, `time`

---

# 📽️ VidSnap-AI

VidSnap-AI is an AI-powered application that generates short video reels by combining audio (generated from text), background images, and music using FFmpeg and Flask.

---

## 📁 Folder Structure

```bash
VidSnap-AI/
├── static/                   # Static assets
│   ├── css/                  # Optional CSS files
│   ├── reels/                # Reel background visuals (videos/images)
│   └── songs/                # Background music (mp3/wav)
│
├── templates/                # Flask HTML templates
│   ├── base.html
│   ├── create.html
│   ├── gallery.html
│   └── index.html
│
├── user_uploads/             # Uploaded folders with desc.txt and media
│   └── <uuid-folder>/        # e.g. 376273cf-xxxx...
│       └── desc.txt
│
├── __pycache__/              # Python bytecode cache (ignored)
│
├── 1.jpg - 5.jpg             # Sample images for reels
├── config.py                 # Contains API keys (should NOT be pushed)
├── done.txt                  # Marker file for completed tasks
├── ffmpeg_command.txt        # Reference FFmpeg command
├── generate_process.py       # Logic to generate and merge video/audio
├── main.py                   # Flask app entry point
├── requirements.txt          # Python dependencies
├── sample_input_ffmpeg.txt   # Sample FFmpeg input
├── text_to_audio.py          # Text-to-speech using gTTS or ElevenLabs
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/manik3160/VidSnap-AI.git
cd VidSnap-AI
```

### 2. Install Python Requirements
```bash
pip install -r requirements.txt
```

> ✅ **Note:** Make sure **FFmpeg** is installed and added to your system's environment `PATH`.  
> You can check it by running:
```bash
ffmpeg -version
```

### 3. Run the Application
```bash
python main.py
```

Then open your browser and visit: [http://localhost:5000](http://localhost:5000)
