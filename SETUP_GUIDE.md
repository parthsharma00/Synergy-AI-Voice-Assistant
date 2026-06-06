# 📘 Synergy Setup Guide

This guide will walk you through setting up Synergy on your computer step by step. We've made it as simple as possible, even if you're not tech-savvy.

---

## 🍎 Setting Up Synergy on Mac

### Step 1: Check if You Have Python

First, let's see if Python is already installed on your Mac:

1. Open **Terminal** (press `Command + Space`, type "Terminal", and press Enter)
2. Type this and press Enter:
   ```
   python3 --version
   ```
3. If you see a version number (like Python 3.8.0 or higher), you're good to go! Skip to Step 2.
4. If you see an error, you need to install Python:
   - Go to [python.org/downloads](https://www.python.org/downloads/)
   - Download the latest Python 3 version
   - Open the installer and follow the instructions

### Step 2: Install Homebrew (Package Manager)

Homebrew makes it easy to install other software we need:

1. In Terminal, copy and paste this command (press Enter):
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Follow the on-screen instructions (you may need to enter your Mac password)
3. This might take a few minutes

### Step 3: Install PortAudio (for Microphone)

Synergy needs PortAudio to use your microphone:

1. In Terminal, type:
   ```
   brew install portaudio
   ```
2. Press Enter and wait for installation to complete

### Step 4: Download Synergy

1. Go to the GitHub repository page
2. Click the green "Code" button
3. Click "Download ZIP"
4. Once downloaded, double-click the ZIP file to extract it
5. Move the extracted folder to your Desktop or Documents

### Step 5: Set Up Virtual Environment

A virtual environment keeps Synergy's files separate from your other Python projects:

1. Open Terminal
2. Navigate to the Synergy folder:
   ```
   cd Desktop/synergy
   ```
   (Replace "Desktop/synergy" with wherever you extracted the folder)
3. Create a virtual environment:
   ```
   python3 -m venv .venv
   ```
4. Activate it:
   ```
   source .venv/bin/activate
   ```
5. You should see `(.venv)` at the start of your terminal line

### Step 6: Install Dependencies

Now let's install all the software packages Synergy needs:

1. In Terminal (with virtual environment activated), type:
   ```
   pip install -r requirements.txt
   ```
2. Press Enter and wait for installation (this may take 5-10 minutes)

### Step 7: Run the Setup Wizard

The first time you run Synergy, a setup wizard will help you configure everything:

1. In Terminal, type:
   ```
   python main.py
   ```
2. Press Enter
3. A window will appear - follow the on-screen instructions:
   - **Step 1**: Click "Start Installation Guide"
   - **Step 2**: Click "Download Voice Assets" (this downloads ~50MB)
   - **Step 3**: Choose "Use Free Offline-First Option" (recommended for beginners)
   - **Step 4**: Click "Conclude Setup"

### Step 8: Start Using Synergy!

1. The main Synergy window will open
2. Make sure your microphone is plugged in
3. Say "Synergy" to wake up the assistant
4. Try commands like:
   - "What time is it?"
   - "Play some music"
   - "Search for weather"

---

## 🪟 Setting Up Synergy on Windows

### Step 1: Install Python

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest Python 3 version for Windows
3. **IMPORTANT**: During installation, check the box that says "Add Python to PATH"
4. Click "Install Now"
5. Wait for installation to complete

### Step 2: Verify Python Installation

1. Open Command Prompt (press `Windows + R`, type "cmd", press Enter)
2. Type:
   ```
   python --version
   ```
3. You should see a version number like Python 3.8.0 or higher

### Step 3: Install Visual C++ Build Tools

This is needed for microphone support:

1. Go to [visualstudio.microsoft.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Download the Build Tools
3. Run the installer
4. Select "Desktop development with C++"
5. Click "Install" (this may take 10-20 minutes)

### Step 4: Download Synergy

1. Go to the GitHub repository page
2. Click the green "Code" button
3. Click "Download ZIP"
4. Once downloaded, right-click the ZIP file and select "Extract All"
5. Extract it to your Desktop or Documents

### Step 5: Set Up Virtual Environment

1. Open Command Prompt
2. Navigate to the Synergy folder:
   ```
   cd Desktop\synergy
   ```
   (Replace "Desktop\synergy" with wherever you extracted the folder)
3. Create a virtual environment:
   ```
   python -m venv .venv
   ```
4. Activate it:
   ```
   .venv\Scripts\activate
   ```
5. You should see `(.venv)` at the start of your command line

### Step 6: Install Dependencies

1. In Command Prompt (with virtual environment activated), type:
   ```
   pip install -r requirements.txt
   ```
2. Press Enter and wait for installation

**If PyAudio installation fails:**
```
pip install pipwin
pipwin install pyaudio
```

### Step 7: Run the Setup Wizard

1. In Command Prompt, type:
   ```
   python main.py
   ```
2. Press Enter
3. Follow the on-screen wizard instructions (same as Mac steps above)

### Step 8: Start Using Synergy!

The same as Mac - say "Synergy" to activate and try voice commands.

---

## 🔧 Troubleshooting Common Issues

### "Python command not found"

**Mac**: Make sure you're using `python3` instead of `python`
**Windows**: Reinstall Python and make sure "Add to PATH" was checked

### "PortAudio not found" (Mac)

Run: `brew install portaudio`

### "PyAudio installation failed" (Windows)

Try the pipwin method mentioned in Step 6

### "Microphone not working"

**Mac**:
1. Go to System Preferences > Security & Privacy > Privacy
2. Click "Microphone" on the left
3. Check the box next to Terminal or Python

**Windows**:
1. Go to Settings > Privacy > Microphone
2. Turn on "Allow apps to access your microphone"
3. Turn on "Allow desktop apps to access your microphone"

### "Voice model download failed"

1. Check your internet connection
2. Make sure you have at least 100MB free space
3. Try clicking "Retry Download" in the wizard

### "Module not found" errors

Make sure your virtual environment is activated:
- **Mac**: You should see `(.venv)` in terminal
- **Windows**: You should see `(.venv)` in command prompt

If not, navigate to the Synergy folder and activate it again.

---

## 🎤 Getting API Keys (Optional but Recommended)

Synergy works in free mode by default, but for full functionality, you can add API keys:

### Gemini API Key (for better AI responses)

1. Go to [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (it starts with "AIza")
5. Open `config.json` in the Synergy folder
6. Replace the empty `gemini_api_key` with your key

### Spotify Credentials (for music control)

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in the details:
   - App name: "Synergy"
   - Description: "Voice assistant"
   - Redirect URI: `http://localhost:8888/callback`
5. Save the Client ID and Client Secret
6. Add them to `config.json` under the spotify section

### Google Calendar (for calendar features)

This is more advanced - follow the Google Calendar API documentation if you want this feature.

---

## 💡 Tips for Best Experience

1. **Use a good microphone** - Built-in laptop mics work, but external mics are better
2. **Speak clearly** - Say "Synergy" clearly and wait for the "Yes?" response
3. **Quiet environment** - Background noise can affect wake word detection
4. **Internet connection** - Required for AI responses and web search
5. **Speakers** - Make sure your volume is up to hear responses

---

## 🔄 Updating Synergy

To get the latest version:

1. Open Terminal/Command Prompt
2. Navigate to the Synergy folder
3. Activate virtual environment
4. Run:
   ```
   git pull
   pip install -r requirements.txt --upgrade
   ```

---

## 🗑️ Uninstalling Synergy

### Mac
1. Delete the Synergy folder
2. Delete the virtual environment folder
3. (Optional) Remove PortAudio: `brew uninstall portaudio`

### Windows
1. Delete the Synergy folder
2. (Optional) Uninstall Python and Visual C++ Build Tools from Control Panel

---

## 📞 Need Help?

If you're still having trouble:

1. Check the [Troubleshooting](#-troubleshooting-common-issues) section above
2. Search for your error message online
3. Open an issue on the GitHub repository
4. Include:
   - Your operating system (Mac/Windows)
   - Python version
   - The exact error message
   - What you were trying to do when it happened

---

**Happy voice computing! 🎤✨**
