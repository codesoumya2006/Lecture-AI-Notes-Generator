# QUICK START GUIDE

## 🚀 One-Command Launch

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File setup\setup_windows.ps1
```

### Linux / macOS (Bash)
```bash
bash setup/setup_linux.sh
```

---

## What the Setup Does (Automatically!)

✅ Detects your OS
✅ Installs FFmpeg (if needed)
✅ Downloads and installs Ollama
✅ Creates Python virtual environment
✅ Installs all Python dependencies
✅ Pulls Mistral 7B model (2.7GB)
✅ Launches Streamlit app automatically
✅ Opens browser to http://localhost:8501

---

## Usage Flow

### Step 1: Get Audio
- **Record** - Click "Record Lecture" tab → Start → Stop
- **Upload** - Choose audio file (MP3, WAV, M4A, etc.)
- **YouTube** - Paste YouTube URL → Download

### Step 2: Transcribe
- Go to "Transcribe" tab
- Click "🚀 Transcribe"
- Wait for completion (usually 2-3 min for 30-min lecture)

### Step 3: Generate Materials
- **Study Notes** - Click "📚 Generate Notes"
- **Summary** - Click "📋 Summary"
- **Study Guide** - Click "📖 Study Guide"
- **Exams** - Go to "Exam Generator" tab → Choose question type

### Step 4: Export
- Go to "Export" tab
- Click "💾 Export Transcript/Notes/Exam"
- PDFs save to `./pdfs/` folder

---

## System Requirements

✓ Python 3.8 or higher
✓ 4GB RAM (8GB recommended)
✓ 2GB free disk space
✓ Windows / Linux / macOS

---

## Troubleshooting

### Setup takes long time
- Normal! First run downloads Ollama (500MB) and Mistral model (2.7GB)
- Subsequent runs are much faster

### Port 8501 already in use
- Streamlit will automatically use next available port
- Check terminal for actual URL

### Audio quality issues
- Ensure microphone is working
- Use quiet environment for recording
- For uploads, use high-quality audio files

### Transcription errors
- Check internet during first setup (for model downloads)
- Ensure audio file is valid WAV/MP3/M4A format
- Try shorter audio clips first

---

## Advanced Configuration

Edit variables in the app (sidebar):
- **LLM Model** - Choose between mistral, neural-chat, dolphin-mixtral
- **Transcription Model** - base (fast), small, medium (accurate)

---

## Performance Tips

- Use "base" transcription model for speed
- Keep browser tab in focus while processing
- Close unnecessary applications
- Ensure good internet for first setup
- Restart app if slow after long use

---

## Model Information

**Whisper Base**
- Size: 140MB
- Accuracy: 90%+
- Speed: Real-time 30x (CPU)
- Language: 99 languages

**Mistral 7B**
- Size: 2.7GB
- Knowledge cutoff: April 2024
- Speed: ~10-20 tokens/sec (CPU)
- Specialties: Notes, questions, summaries

---

## File Organization

```
lecture_ai/
├── app.py              ← Main app (don't modify)
├── requirements.txt    ← Dependencies (don't modify)
├── README.md          ← Full documentation
│
├── setup/             ← Auto-setup scripts
│   ├── setup_windows.ps1
│   ├── setup_linux.sh
│   └── setup_mac.sh
│
├── core/              ← Processing modules
├── services/          ← Feature modules
├── prompts/           ← LLM prompts
│
├── recordings/        ← Your recorded audio
├── downloads/         ← Downloaded from YouTube
├── uploads/           ← Uploaded files
├── pdfs/              ← Exported PDFs
└── models/            ← Downloaded models
```

---

## First Run Expected Behavior

1. **Setup Script Runs** (5-10 minutes)
   - Downloads FFmpeg
   - Downloads Ollama (500MB)
   - Installs Python packages
   - Pulls Mistral model (2.7GB) - this takes 3-5 minutes

2. **Streamlit Starts** (30 seconds)
   - Shows local URL: http://localhost:8501
   - Automatically opens browser

3. **Ready to Use!**
   - Start recording or uploading audio
   - Follow the UI flow

---

## Keyboard Shortcuts

- **Ctrl+C** - Stop Streamlit (in terminal)
- **R** - Rerun app
- **I** - Show/hide info
- **H** - Show/hide help

---

## Support

If something doesn't work:

1. Check terminal for error messages
2. Ensure Python 3.8+ installed: `python --version`
3. Ensure FFmpeg installed: `ffmpeg -version`
4. Ensure Ollama running: `ollama serve` (separate terminal)
5. Check README.md for detailed troubleshooting

---

## Next Steps

✨ **Ready to transform your lectures into study superpowers!**

```
python auto_run.py
```

Or use platform-specific command above.

**Happy Learning! 📚**
