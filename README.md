# Synergy — Voice-Activated Desktop AI Assistant

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Say **"Synergy"** and talk to your computer. Synergy is a desktop voice assistant that listens for its wake word entirely offline, transcribes what you say locally, and then decides what to do: play music on Spotify, check or add to your Google Calendar, search the web, pull a Wikipedia summary, play something from YouTube, or just hold a conversation. I built it because most voice assistants either stream everything you say to the cloud or can't actually *do* anything on your own machine. Synergy keeps the always-listening part on-device and only reaches out to an LLM once you've deliberately woken it up.

> 📸 **Demo:** _screenshot / demo video coming soon_ <!-- replace with ![Synergy GUI](docs/screenshot.png) or a YouTube link -->

## How it works

```
Microphone
  └─> Wake word (Vosk, offline, small English model)
        └─> Speech-to-text (faster-whisper locally, Google STT fallback)
              └─> Brain
                    ├─ Local intent matcher (regex, instant, no network)  ── e.g. "pause", "skip", "play X"
                    └─ Gemini 2.5 Flash (structured JSON intent + reply)    ── anything open-ended
                          └─> Agent router
                                ├─ Spotify    (spotipy, OAuth)
                                ├─ Calendar   (Google Calendar API)
                                ├─ Web search (DuckDuckGo)
                                ├─ Wikipedia
                                └─ YouTube    (yt-dlp + ffplay)
                                      └─> Reply spoken with pyttsx3 + shown in the Tkinter GUI
```

A few design decisions worth calling out:

- **Two-tier intent routing.** Common commands ("pause", "next song", "play Blinding Lights") are matched locally with regex, so they execute instantly and cost nothing. Only ambiguous or conversational requests go to Gemini, which returns a structured `{intent, action, query, response}` object the router can act on.
- **Privacy by default.** The wake-word model runs fully offline. Nothing leaves your machine until you say the wake word.
- **Agents are pluggable.** Each integration is a small class with `is_configured()` and `execute_action()`, so adding a new one doesn't touch the core loop.
- **First-run wizard.** A GUI setup flow writes your `config.json` so non-technical users never edit JSON by hand. `build.py` packages everything (including the Vosk model) into a double-clickable app with PyInstaller.

## Tech stack

Python · Vosk · faster-whisper · Google Gemini API · Spotipy · Google Calendar API · DuckDuckGo Search · yt-dlp · pyttsx3 · Tkinter · PyInstaller

## Getting started

**Requirements:** Python 3.10+, a microphone, and speakers.

```bash
git clone https://github.com/parthsharma00/Synergy-AI-Voice-Assistant.git
cd Synergy-AI-Voice-Assistant

# macOS only: PyAudio needs PortAudio
brew install portaudio

pip install -r requirements.txt
pip install faster-whisper   # optional, for faster local transcription
```

Download the [Vosk small English model](https://alphacephei.com/vosk/models) and unzip it into the project root as `vosk-model-small-en-us/`.

Then run:

```bash
python main.py
```

The first launch opens the setup wizard. You can also configure it by hand: copy `config.json.template` to `config.json` and fill in your keys.

| Key | Where to get it | Needed for |
|---|---|---|
| Gemini API key | [aistudio.google.com](https://aistudio.google.com) (free) | Conversational replies, open-ended commands |
| Spotify client ID / secret | [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) | Music control (Premium required for playback) |
| Google Calendar credentials | Google Cloud Console → OAuth client | Reading and adding events |

Every integration is optional. Synergy skips any agent you haven't configured. `config.json` and the Spotify token cache are gitignored, so your keys never get committed.

See [`SETUP_GUIDE.md`](SETUP_GUIDE.md) and [`HOW_TO_RUN.md`](HOW_TO_RUN.md) for a step-by-step walkthrough and troubleshooting.

### Example commands

| You say | Synergy does |
|---|---|
| "Synergy… play Bohemian Rhapsody" | Plays it on Spotify |
| "Pause" / "Skip" | Controls playback |
| "What's on my calendar?" | Reads your next events |
| "Add an event: dinner with Sam tomorrow at 7" | Creates a calendar event |
| "Who is Ada Lovelace?" | Reads a Wikipedia summary |
| "Search for the best laptop for CS students" | Reads back the top web results |
| Anything else | Chats with you through Gemini |

## Project structure

```
├── main.py               # Entry point: wizard on first run, then GUI + voice loop
├── core/
│   ├── wake_word.py      # Offline Vosk wake-word listener (background thread)
│   ├── speech.py         # faster-whisper / Google STT transcription
│   ├── brain.py          # Local intent matcher + Gemini intent parsing
│   └── tts.py            # pyttsx3 voice output
├── agents/               # Spotify, Calendar, Search, Wikipedia, YouTube
├── gui/app.py            # Tkinter interface with live waveform
├── setup/first_run.py    # First-run configuration wizard
├── build.py              # PyInstaller packaging + optional autostart
└── legacy/               # Earlier assistants Synergy grew out of (see below)
```

## Where it came from

`legacy/` holds the two assistants I wrote before Synergy:

- **`jarvis.py`:** my first voice assistant. It used hard-coded `if "play" in command` branches with Google STT, Wikipedia, and YouTube via pywhatkit.
- **`JEErvisAdvanced.py`:** the second attempt. It added a wake word ("Genius") and used an OpenAI chat model for free-form answers.

Synergy is the rewrite those two taught me I needed. It has an offline wake word, a real intent layer instead of string matching, and pluggable agents instead of one giant loop. The legacy scripts are kept as-is for reference and aren't maintained.

## Roadmap

- [ ] Custom wake-word training
- [ ] Conversation memory across sessions
- [ ] Linux support
- [ ] More agents (email, smart home, notes)

## Author

**Parth Sharma**, Computer Science & Design at the Singapore University of Technology and Design (SUTD)
[GitHub](https://github.com/parthsharma00) · [LinkedIn](https://www.linkedin.com/in/parth-sharmasutd) · parthsharma72007@gmail.com

Released under the [MIT License](LICENSE).
