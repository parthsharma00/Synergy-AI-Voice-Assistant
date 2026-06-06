<div align="center">
  <h1>🎤 Synergy - Voice-Activated Desktop AI Assistant</h1>
  <p>Your personal AI assistant that responds to voice commands</p>
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/OS-Mac%20%7C%20Windows-lightgrey.svg" alt="Supported OS">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</div>

## ✨ Features

- **Voice Activation**: Say "Synergy" to wake up your assistant
- **Music Control**: Play, pause, skip music on Spotify
- **Calendar Management**: Add events and check your schedule
- **Web Search**: Get answers from the internet
- **Wikipedia Integration**: Look up facts and information
- **Beautiful GUI**: Modern, dark-themed interface
- **Offline Wake Word Detection**: Works without internet for wake word

## 🚀 Quick Start

### For Mac Users

1. **Install Python 3.8+** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)
   - Or use Homebrew: `brew install python`

2. **Install Homebrew** (if needed for dependencies)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. **Install PortAudio** (required for microphone access)
   ```bash
   brew install portaudio
   ```

4. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd synergy
   ```

5. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

6. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

7. **Run the setup wizard**
   ```bash
   python main.py
   ```
   The wizard will guide you through:
   - Downloading voice models
   - Setting up API keys (optional free tier available)
   - Configuring services

8. **Start using Synergy**
   ```bash
   python main.py
   ```
   Say "Synergy" to activate!

### For Windows Users

1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Install Microsoft Visual C++ Build Tools** (required for PyAudio)
   - Download from: [visualstudio.microsoft.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Install "Desktop development with C++"

3. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd synergy
   ```

4. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If PyAudio fails, try: `pip install pipwin` then `pipwin install pyaudio`*

6. **Run the setup wizard**
   ```bash
   python main.py
   ```

7. **Start using Synergy**
   ```bash
   python main.py
   ```

## 📋 Detailed Setup Guide

For detailed step-by-step instructions with screenshots and troubleshooting, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 🔧 Configuration

### API Keys (Optional)

Synergy works in free tier mode by default. For full functionality, you can add:

- **Gemini API Key** (for AI responses): Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Spotify Credentials** (for music control): Get from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- **Google Calendar** (for calendar integration): Follow Google OAuth setup

The setup wizard will guide you through adding these, or you can manually configure:

1. Copy `config.json.template` to `config.json`
2. Replace the placeholder values with your actual API keys
3. Run `python main.py` to start using Synergy

### Voice Commands

- "Synergy" - Wake up the assistant
- "Play [song name]" - Play music on Spotify
- "Pause" / "Stop" - Pause music
- "Skip" - Next track
- "What's on my calendar?" - Check schedule
- "Add event [description]" - Add calendar event
- "Search for [query]" - Web search
- "Who is [person]?" - Wikipedia lookup
- Any conversational question - General AI chat

## 📁 Project Structure

```
synergy/
├── main.py              # Entry point
├── config.json          # Configuration (created after setup)
├── requirements.txt     # Python dependencies
├── core/               # Core AI components
│   ├── brain.py        # AI brain (Gemini integration)
│   ├── speech.py       # Speech recognition
│   ├── tts.py          # Text-to-speech
│   └── wake_word.py    # Wake word detection
├── agents/             # Service integrations
│   ├── spotify_agent.py
│   ├── calendar_agent.py
│   ├── wikipedia_agent.py
│   ├── search_agent.py
│   └── youtube_agent.py
├── gui/                # User interface
│   └── app.py          # Main GUI application
└── setup/              # Setup wizard
    └── first_run.py   # First-time configuration
```

## 🛠️ Troubleshooting

**Microphone not working?**
- Mac: Check System Preferences > Security & Privacy > Privacy > Microphone
- Windows: Check Settings > Privacy > Microphone

**PyAudio installation fails?**
- Mac: `brew install portaudio`
- Windows: Install Visual C++ Build Tools or use `pipwin install pyaudio`

**Voice model download fails?**
- Check your internet connection
- The model is ~50MB, ensure you have enough space
- You can manually download from: https://alphacephei.com/vosk/models

## 📝 Requirements

- Python 3.8 or higher
- Microphone
- Internet connection (for AI responses and some features)
- Speakers (for voice responses)

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Google Generative AI for the AI brain
- Vosk for offline speech recognition
- Spotipy for Spotify integration
- All other open-source libraries used

---

**Made with ❤️ for voice-activated computing**
