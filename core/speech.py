"""
core/speech.py
Handles audio recording and speech-to-text transcription.
Uses faster-whisper for fast local transcription (no API calls, no internet needed).
Falls back to Google Speech Recognition if faster-whisper is not installed.
"""

import io
import time
import queue
import threading
import tempfile
import os

import pyaudio
import wave


# ─── Constants ────────────────────────────────────────────────────────────────

SAMPLE_RATE     = 16000
CHANNELS        = 1
FORMAT          = pyaudio.paInt16
CHUNK_SIZE      = 1024
SILENCE_LIMIT   = 2.0    # seconds of silence before stopping recording
MAX_RECORD_SECS = 8      # hard cap on recording length
SILENCE_THRESH  = 500    # amplitude below this = silence


# ─── Whisper model (loaded once, stays in memory) ─────────────────────────────

_whisper_model = None

def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            print("[*] Loading Whisper tiny model (first time only)...")
            # cpu with int8 is fastest on Mac, loads in ~1 second
            _whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            print("[*] Whisper model ready.")
        except ImportError:
            print("[!] faster-whisper not installed. Falling back to Google STT.")
            _whisper_model = "google"
    return _whisper_model


# ─── Audio recording ──────────────────────────────────────────────────────────

def record_command(is_speaking_flag=None) -> bytes:
    """
    Record audio from microphone until silence or max duration.
    Returns raw WAV bytes.
    
    is_speaking_flag: optional lambda/callable that returns True while
                      the assistant is speaking (so we don't record our own voice).
    """
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    frames = []
    silence_start = None
    start_time = time.time()

    # Wait for speaking to finish before starting to record
    if is_speaking_flag:
        while is_speaking_flag():
            time.sleep(0.05)
        time.sleep(0.3)  # small buffer after speech ends

    print("[*] Listening for voice command...")

    while True:
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        frames.append(data)

        # Check amplitude to detect silence
        import struct
        shorts = struct.unpack('%dh' % (len(data) // 2), data)
        amplitude = max(abs(s) for s in shorts) if shorts else 0

        if amplitude < SILENCE_THRESH:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start > SILENCE_LIMIT:
                break  # enough silence — done
        else:
            silence_start = None  # reset silence timer on sound

        # Hard cap
        if time.time() - start_time > MAX_RECORD_SECS:
            break

    stream.stop_stream()
    stream.close()
    pa.terminate()

    # Convert frames to WAV bytes
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pa.get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))

    return buf.getvalue()


# ─── Transcription ────────────────────────────────────────────────────────────

def transcribe(audio_bytes: bytes) -> str:
    """
    Transcribe WAV audio bytes to text.
    Uses faster-whisper locally if available, otherwise Google STT.
    """
    model = _get_whisper_model()

    if model == "google":
        return _transcribe_google(audio_bytes)
    else:
        return _transcribe_whisper(model, audio_bytes)


def _transcribe_whisper(model, audio_bytes: bytes) -> str:
    """Local transcription using faster-whisper. Fast, offline, free."""
    # Write to a temp file — whisper needs a file path
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name

    try:
        segments, _ = model.transcribe(
            tmp_path,
            language="en",
            beam_size=1,          # fastest setting
            vad_filter=True,      # skip silent parts automatically
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        text = " ".join(seg.text for seg in segments).strip()
        return text
    except Exception as e:
        print(f"[!] Whisper transcription error: {e}")
        return ""
    finally:
        os.unlink(tmp_path)


def _transcribe_google(audio_bytes: bytes) -> str:
    """Fallback: Google Speech Recognition (requires internet)."""
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        print(f"[!] Google STT error: {e}")
        return ""


# ─── Main interface ───────────────────────────────────────────────────────────

class SpeechTranscriber:
    """
    Main class used by the rest of the app.
    Matches the interface the existing code expects.
    """

    def __init__(self):
        # Pre-load the model at startup so first command is fast
        threading.Thread(target=_get_whisper_model, daemon=True).start()

    def listen_and_transcribe(self, is_speaking_flag=None, timeout=None) -> str:
        """Record audio and return transcribed text."""
        try:
            audio_bytes = record_command(is_speaking_flag=is_speaking_flag)
            print("[*] Transcribing audio...")
            text = transcribe(audio_bytes)
            if text:
                print(f"[+] Transcribed Speech: '{text}'")
            else:
                print("[!] Speech Recognition could not understand the audio.")
            return text
        except Exception as e:
            print(f"[!] Speech error: {e}")
            return ""

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """Transcribe pre-recorded audio bytes."""
        return transcribe(audio_bytes)
