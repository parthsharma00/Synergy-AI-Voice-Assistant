# -*- coding: utf-8 -*-
"""
agents/youtube_agent.py
Plays YouTube audio using yt-dlp and ffplay.
No API key needed. Completely free.
"""

import subprocess
import threading
import os

# Track current playback process so we can stop it
_current_process = None
_process_lock = threading.Lock()


def _is_ffplay_available() -> bool:
    try:
        subprocess.run(["ffplay", "-version"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False


def _is_ytdlp_available() -> bool:
    try:
        import yt_dlp
        return True
    except ImportError:
        return False


def play_youtube(query: str) -> str:
    """Search YouTube for query and play the top result audio."""
    global _current_process

    if not _is_ytdlp_available():
        return "yt-dlp is not installed. Run: pip install yt-dlp"

    if not _is_ffplay_available():
        return "ffplay is not installed. Run: brew install ffmpeg"

    try:
        import yt_dlp

        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

        search_query = f"ytsearch1:{query}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if not info or "entries" not in info or not info["entries"]:
                return f"Could not find '{query}' on YouTube."

            entry = info["entries"][0]
            url = entry.get("url") or entry.get("webpage_url")
            title = entry.get("title", query)
            channel = entry.get("channel") or entry.get("uploader", "")

        # Stop any currently playing YouTube audio
        stop_youtube()

        # Play in background thread so it doesn't block
        def _play():
            global _current_process
            proc = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            with _process_lock:
                _current_process = proc
            proc.wait()
            with _process_lock:
                _current_process = None

        threading.Thread(target=_play, daemon=True).start()

        if channel:
            return f"Playing {title} by {channel} from YouTube."
        return f"Playing {title} from YouTube."

    except Exception as e:
        return f"YouTube playback error: {e}"


def stop_youtube() -> str:
    """Stop current YouTube playback."""
    global _current_process
    with _process_lock:
        if _current_process and _current_process.poll() is None:
            _current_process.terminate()
            _current_process = None
            return "YouTube playback stopped."
    return "Nothing playing."


class YouTubeAgent:
    """Agent wrapper matching the interface of other agents."""

    def is_configured(self) -> bool:
        return _is_ytdlp_available() and _is_ffplay_available()

    def execute_action(self, action: str, query: str = "") -> str:
        action = action.lower()
        if "play" in action or "search" in action:
            return play_youtube(query)
        elif "stop" in action or "pause" in action:
            return stop_youtube()
        return f"YouTube agent doesn't know how to '{action}'."