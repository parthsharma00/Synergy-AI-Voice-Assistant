# -*- coding: utf-8 -*-
"""
Synergy Text-To-Speech Engine
Handles offline voices with pyttsx3, incorporating silent modes, audio rates, and selected speech actors.
"""

import os
import json
import time

class SpeechSynthesizer:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        """Initializes the offline pyttsx3 speech synthesizer."""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.update_settings_from_config()
        except Exception as e:
            print(f"[!] pyttsx3 initialization skipped or failed: {e}")
            self.engine = None

    def update_settings_from_config(self):
        """Reloads settings from config.json and configures pyttsx3 engine parameters."""
        if not self.engine:
            return

        # Load configurations
        config = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
            except Exception:
                pass

        speed = config.get("voice_speed", 175)
        voice_id = config.get("voice_id", "")
        
        # Configure Speech speed/rate (normal is usually 200, we use 175 by default)
        try:
            self.engine.setProperty("rate", speed)
        except Exception:
            pass

        # Select custom voice ID if specified and present
        if voice_id:
            try:
                self.engine.setProperty("voice", voice_id)
            except Exception:
                pass

    def get_available_voices(self):
        """Retrieves list of installed voice modules on host machine (OS-dependent)."""
        if not self.engine:
            return []
        try:
            voices = self.engine.getProperty("voices")
            return [{"id": v.id, "name": v.name, "languages": v.languages} for v in voices]
        except Exception:
            return []

    def speak(self, text: str):
        """Speaks the input text unless silent mode (notification-only) is set in config."""
        # Query silent mode configuration
        config = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
            except Exception:
                pass

        silent_mode = config.get("silent_mode", False)
        if silent_mode:
            print(f"[*] [SILENT MODE] Notification: \"{text}\"")
            return

        print(f"[*] Speaking: \"{text}\"")
        if not self.engine:
            print("[!] pyttsx3 not loaded; speech ignored.")
            return

        try:
            self.engine.say(text)
            time.sleep(0.8)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[!] Speech Synthesis error: {e}")
