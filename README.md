# VidSnap-AI 🎬

AI-powered reel generator that transforms your images into engaging Instagram reels with natural-sounding voiceovers.

## Features ✨

- **AI Voice Generation**: Convert text descriptions into natural-sounding voiceovers using ElevenLabs
- **Automatic Video Creation**: Smart algorithm combines images with generated audio
- **Mobile Optimized**: Perfect 9:16 aspect ratio for social media
- **Professional Quality**: High-resolution output with smooth transitions
- **Easy Sharing**: Download and share reels instantly
- **Modern UI**: Beautiful dark theme with gradient effects

## Tech Stack 🛠️

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **AI**: ElevenLabs API for text-to-speech
- **Video Processing**: FFmpeg
- **Styling**: Custom CSS with modern design system

## Installation 🚀

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/VidSnap-AI.git
   cd VidSnap-AI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   ELEVENLABS_API_KEY=your_api_key_here
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Start the video processor** (in a separate terminal)
   ```bash
   python generate_process.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5001`

## Usage 📱

1. **Upload Images**: Select 2-5 photos for your reel
2. **Write Description**: Add compelling text that will be converted to voice
3. **Generate Reel**: Click create and wait for processing
4. **View Gallery**: Browse, play, download, and share your reels

## API Configuration 🔑

Get your ElevenLabs API key:
1. Visit [elevenlabs.io](https://elevenlabs.io)
2. Sign up for an account
3. Go to your profile settings
4. Copy your API key
5. Add it to your `.env` file
4. Set environment variables in Heroku dashboard

## File Structure 📁

```
VidSnap-AI/
├── main.py                 # Flask application
├── generate_process.py     # Background video processor
├── config.py              # API configuration
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── create.html
│   └── gallery.html
├── static/               # Static assets
│   ├── css/
│   ├── reels/           # Generated videos
│   └── songs/           # Background music
└── user_uploads/        # User uploaded files
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License 📄

This project is open source and available under the [MIT License](LICENSE).

## Support 💬

If you have any questions or need help, feel free to:
- Open an issue on GitHub
- Contact us at maniksingh3606@gmail.com

---

Made with ❤️ by Manik
