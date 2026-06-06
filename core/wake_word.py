# -*- coding: utf-8 -*-
"""
Synergy Offline Wake Word Engine
Handles background audio intelligence using Vosk and PyAudio.
"""

import os
import json
import pyaudio
import threading
from typing import Callable

CHUNK_SIZE = 1024
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16

def process_audio_chunk(audio_chunk):
    import noisereduce as nr
    import numpy as np
    try:
        audio_np = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32)
        reduced = nr.reduce_noise(y=audio_np, sr=SAMPLE_RATE, stationary=False)
        return reduced.astype(np.int16).tobytes()
    except Exception:
        return audio_chunk  # if it fails just pass through raw audio

# Read wake word from local config
def get_configured_wake_word() -> str:
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                return config.get("wake_word", "synergy").lower().strip()
        except Exception:
            pass
    return "synergy"

class WakeWordDetector(threading.Thread):
    def __init__(self, callback: Callable[[], None], error_callback: Callable[[str], None] = None):
        super().__init__()
        self.callback = callback
        self.error_callback = error_callback
        self.daemon = True
        self.running = False
        self.wake_word = get_configured_wake_word()
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vosk-model-small-en-us")

    def run(self):
        self.running = True
        self.wake_word = get_configured_wake_word()
        
        # Import vosk lazily to ensure correct startup if package is initializing
        try:
            import vosk
        except ImportError:
            if self.error_callback:
                self.error_callback("Vosk library not installed. Please run pip install vosk.")
            return

        if not os.path.exists(self.model_path):
            import urllib.request, zipfile
            print("[*] Vosk model not found — auto-downloading (~50MB, one time only)...")
            model_zip = self.model_path + ".zip"
            url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
            try:
                urllib.request.urlretrieve(url, model_zip)
                extract_dir = os.path.dirname(self.model_path)
                with zipfile.ZipFile(model_zip, 'r') as zf:
                    zf.extractall(extract_dir)
                os.remove(model_zip)
                extracted = os.path.join(extract_dir, "vosk-model-small-en-us-0.15")
                if os.path.exists(extracted):
                    os.rename(extracted, self.model_path)
                print("[*] Vosk model ready.")
            except Exception as dl_err:
                print(f"[!] Auto-download failed: {dl_err}")
                return

        try:
            model = vosk.Model(self.model_path)
            recognizer = vosk.KaldiRecognizer(model, 16000)
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Failed to initialize Vosk recognizer: {str(e)}")
            return

        try:
            mic = pyaudio.PyAudio()
            # Standard single-channel audio stream at 16000 Hz, native for Vosk
            stream = mic.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=4096
            )
            stream.start_stream()
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Microphone access error: {str(e)}\nMake sure a recording device is connected and PyAudio is configured.")
            return

        print(f"[*] Standby mode active. Listening for keyword: '{self.wake_word}'...")

        while self.running:
            try:
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                data = process_audio_chunk(data)  # filter out speaker noise
                if len(data) == 0:
                    continue
                if recognizer.AcceptWaveform(data):
                    result_dict = json.loads(recognizer.Result())
                    text = result_dict.get("text", "").lower()
                    if self.wake_word in text:
                        print(f"[!] Wake word '{self.wake_word}' detected!")
                        # Trigger wake callback in a separate thread to prevent blocking audio stream
                        threading.Thread(target=self.callback, daemon=True).start()
            except Exception as e:
                print(f"[!] Error in audio detection stream: {e}")
                break

        # Cleanup
        try:
            stream.stop_stream()
            stream.close()
            mic.terminate()
        except Exception:
            pass

    def stop(self):
        self.running = False
