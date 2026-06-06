# -*- coding: utf-8 -*-
"""
Synergy Spotify Agent
Integrates desktop Spotify controls and play queuing using the Spotipy library and Spotify Web APIs.
"""

import os
import json

class SpotifyAgent:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        self.sp = None
        self._init_spotify_client()

    def _init_spotify_client(self):
        """Initializes the spotipy client if keys are present in config.json."""
        if not os.path.exists(self.config_path):
            return

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
            
            spotify_config = config.get("spotify", {})
            client_id = spotify_config.get("client_id", "")
            client_secret = spotify_config.get("client_secret", "")
            redirect_uri = spotify_config.get("redirect_uri", "http://localhost:8888/callback")

            if client_id and client_secret:
                import spotipy
                from spotipy.oauth2 import SpotifyOAuth
                
                # Setup scopes requested by user (playback states and controls)
                scope = "user-modify-playback-state user-read-playback-state playlist-read-private"
                auth_manager = SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope=scope,
                    cache_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".spotify_cache")
                )
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                print("[*] Spotify Agent successfully connected.")
            else:
                print("[*] Spotify credentials not fully configured. Running Spotify Agent in dry-run mode.")
        except Exception as e:
            print(f"[!] Warning: Spotipy client authorization skipped: {e}")
            self.sp = None

    def is_configured(self) -> bool:
        return self.sp is not None

    def execute_action(self, action: str, query: str = "") -> str:
        """Executes a voice-directed action and returns a success description string."""
        if not self.is_configured():
            return f"Spotify is using the offline trial mode. Simulated action '{action}' on query '{query}' completed."

        try:
            action = action.lower()
            if "play" in action or "resume" in action:
                if query:
                    if query:
                        # Try exact track name first
                        results = self.sp.search(q=f"track:\"{query}\"", limit=5, type="track")
                        tracks = results.get("tracks", {}).get("items", [])
                        
                        # Filter out remixes/covers unless user asked for them
                        query_lower = query.lower()
                        wants_remix = any(w in query_lower for w in ["remix", "cover", "live", "acoustic"])
                        
                        if not wants_remix:
                            # Remove remixes from results
                            tracks = [t for t in tracks if not any(
                                w in t["name"].lower() 
                                for w in ["remix", "cover", "live version", "acoustic"]
                            )]
                        
                        # Fall back to loose search if nothing found
                        if not tracks:
                            results = self.sp.search(q=query, limit=5, type="track")
                            tracks = results.get("tracks", {}).get("items", [])
                        
                        if not tracks:
                            return f"I couldn't find '{query}' on Spotify."
                        
                        # Pick best match — prioritize exact name match
                        best = tracks[0]
                        for t in tracks:
                            if t["name"].lower() == query_lower:
                                best = t
                                break
                        
                        track_uri = best["uri"]
                        track_name = best["name"]
                        artist_name = best["artists"][0]["name"]
                        # Try to play tracking sequence
                        try:
                            self.sp.start_playback(uris=[track_uri])
                            return f"Playing {track_name} by {artist_name} on Spotify."
                        except Exception:
                            # Playback might fail if no active devices are open on client
                            return f"Found {track_name} by {artist_name} on Spotify, but no active playback device was found. Please open Spotify."
                    else:
                        return f"I couldn't find '{query}' on Spotify."
                else:
                    self.sp.start_playback()
                    return "Resuming music on Spotify."

            elif "pause" in action or "stop" in action:
                self.sp.pause_playback()
                return "Music paused on Spotify."

            elif "skip" in action or "next" in action:
                self.sp.next_track()
                return "Skipping to the next track."

            elif "previous" in action or "prev" in action:
                self.sp.previous_track()
                return "Playing the previous track."

            else:
                return f"Spotify agent does not recognize action '{action}'."

        except Exception as e:
            error_msg = str(e)
            if "Player command failed: No active device" in error_msg:
                return "Could not control playback. Please open Spotify on your device first."
            return f"Spotify controller error: {error_msg}"
