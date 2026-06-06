# Synergy — How to Run

## What this is
A Python desktop voice assistant. Run it on your laptop, NOT in a browser.

---

## Step 1 — Prerequisites

**Mac:**
```bash
brew install portaudio
```
*(Install Homebrew first if you don't have it: https://brew.sh)*

**Windows:**
No extra step needed.

---

## Step 2 — Install Python packages

Open Terminal (Mac) or Command Prompt (Windows), navigate to the `synergy/` folder:

```bash
cd synergy
pip install -r requirements.txt
```

If you get a permissions error on Mac, use:
```bash
pip install -r requirements.txt --user
```

---

## Step 3 — Get your free Gemini API key

1. Go to **https://aistudio.google.com**
2. Sign in with any Google account
3. Click **"Get API key"** → **"Create API key"**
4. Copy the key

---

## Step 4 — Run it

```bash
python main.py
```

On first launch, a setup wizard appears. It will:
- Download the offline voice model (~50MB, one time only)
- Ask if you want to enter your Gemini API key (paste it here)
- Set up Spotify / Google Calendar if you want those (optional)

After setup, say **"Synergy"** to wake it up.

---

## Troubleshooting

**"No module named pyaudio"**
- Mac: Run `brew install portaudio` then `pip install pyaudio`
- Windows: Run `pip install pipwin` then `pipwin install pyaudio`

**"Vosk model not found"**
- Let the setup wizard download it, or manually download from:
  https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
  and unzip it into the `synergy/` folder

**"Gemini API error"**
- Make sure your key is in `synergy/config.json` under `"gemini_api_key"`
- Or set it as an environment variable: `export GEMINI_API_KEY=your_key_here`

---

## What you can say (after saying "Synergy" first)

- "What's the weather in Singapore?"
- "Play some chill music" *(needs Spotify setup)*
- "Who is Elon Musk?"
- "What's on my calendar today?" *(needs Google Calendar setup)*
- "Search for the latest AI news"
- "Tell me a joke"

