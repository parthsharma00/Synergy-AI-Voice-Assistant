# -*- coding: utf-8 -*-
"""
core/brain.py
AI routing brain for Synergy.
- Local intent cache for instant responses (no Gemini call)
- Conversation memory for context
- Minimal system prompt for speed
- Falls back to Gemini for complex queries
"""

import os
import re
import json

# ─── Minimal system prompt — fewer tokens = faster response ───────────────────

SYSTEM_PROMPT = """You are Synergy, a voice assistant. Respond with JSON only. No extra text.

Format:
{"intent": "spotify|youtube|wikipedia|web_search|general_chat", "action": "play|pause|skip|previous|search", "query": "search terms only", "response": "one short sentence max"}

Intent rules:
- spotify: music, songs, artists, pause, skip, volume
- youtube: videos, YouTube, watch
- wikipedia: who is, what is, define
- web_search: news, weather, prices, current events
- general_chat: everything else

Keep response field to 1 short sentence. Query field should be clean search terms only."""


# ─── Local intent patterns — matched instantly without Gemini ──────────────────

LOCAL_INTENTS = [
    # Spotify play
    (r"(?:on spotify|by|from spotify|in spotify)|play (.+?) spotify", "spotify", "play"),
    (r"(.+)$", "spotify", "play"),
    # Spotify controls
    (r"pause|stop (?:music|spotify|song|playing)", "spotify", "pause", "Pausing."),
    (r"skip|next (?:song|track)|next one", "spotify", "skip", "Skipping."),
    (r"previous|go back|last (?:song|track)|play (?:that )?again", "spotify", "previous", "Going back."),
    (r"resume|continue (?:playing|music)", "spotify", "resume", "Resuming."),
    (r"volume up|louder|turn (?:it )?up", "spotify", "volume_up", "Turning up."),
    (r"volume down|quieter|turn (?:it )?down", "spotify", "volume_down", "Turning down."),
    # YouTube
    (r"(?:on youtube|youtube video|video on youtube)|(.+?) youtube|youtube (.+)", "youtube", "play"),
    (r"show (?:me )?(.+?) (?:on youtube|video)", "youtube", "play"),
    # Wikipedia
    (r"who (?:is|was) (.+)|what (?:is|was|are) (.+)|tell me about (.+)|define (.+)", "wikipedia", "search"),
    # Web search
    (r"(?:what'?s?|whats) the weather|weather (?:in|for|today)", "web_search", "search"),
    (r"latest news|what'?s happening|current (?:news|events)", "web_search", "search"),
    (r"(?:what'?s?|whats) the (?:time|date|day)", "general_chat", "time"),
]


class AIStudioBrain:

    def __init__(self):
        self.conversation_history = []
        self.max_history = 6  # last 3 exchanges
        self._model = None
        self._init_gemini()

    def _init_gemini(self):
        """Initialize Gemini client."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        api_key = ""

        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = json.load(f)
                api_key = config.get("gemini_api_key", "")
            except Exception:
                pass

        try:
            import google.generativeai as genai
            if api_key:
                genai.configure(api_key=api_key)
                print("[*] Gemini Brain initialized with custom API key.")
            else:
                print("[*] Gemini Brain initialized via ambient credentials.")

            self._model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={"temperature": 0.1, "max_output_tokens": 200}
            )
        except Exception as e:
            print(f"[!] Gemini init failed: {e}")
            self._model = None

    def _try_local_intent(self, text: str) -> dict | None:
        """
        Try to match the command locally without calling Gemini.
        Returns a routing dict or None if no match.
        Instant — no network call.
        """
        text_lower = text.lower().strip()
        # Remove filler words
        text_lower = re.sub(r"^(hey synergy|synergy|can you|could you|please|would you)\s*", "", text_lower)

        for entry in LOCAL_INTENTS:
            if len(entry) == 3:
                pattern, intent, action = entry
                fixed_response = None
            else:
                pattern, intent, action, fixed_response = entry

            match = re.search(pattern, text_lower)
            if match:
                # Extract query from capture groups
                groups = [g for g in match.groups() if g]
                query = groups[0].strip() if groups else text_lower

                if fixed_response:
                    response = fixed_response
                else:
                    response = f"On it."

                result = {
                    "intent": intent,
                    "action": action,
                    "query": query,
                    "response": response
                }
                print(f"[*] Local intent matched: {intent} → {action} → '{query}'")
                return result

        return None

    def _call_gemini(self, text: str) -> dict:
        """Call Gemini for complex queries that local matching can't handle."""
        if not self._model:
            return {
                "intent": "general_chat",
                "action": "",
                "query": text,
                "response": "I'm having trouble connecting to my brain right now."
            }

        try:
            # Build prompt with conversation history for context
            history_text = ""
            if self.conversation_history:
                history_text = "\n\nRecent conversation:\n"
                for turn in self.conversation_history[-self.max_history:]:
                    role = "User" if turn["role"] == "user" else "Synergy"
                    history_text += f"{role}: {turn['content']}\n"

            full_prompt = f"{SYSTEM_PROMPT}{history_text}\n\nUser command: {text}\n\nRespond with JSON only:"

            response = self._model.generate_content(full_prompt)
            raw = response.text.strip()

            # Strip markdown code fences if present
            raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()

            data = json.loads(raw)

            # Store in memory
            self.conversation_history.append({"role": "user", "content": text})
            self.conversation_history.append({"role": "assistant", "content": raw})
            if len(self.conversation_history) > self.max_history * 2:
                self.conversation_history = self.conversation_history[-(self.max_history * 2):]

            return data

        except json.JSONDecodeError:
            # Gemini returned non-JSON — treat as general chat
            return {
                "intent": "general_chat",
                "action": "",
                "query": text,
                "response": response.text.strip() if response else "I didn't understand that."
            }
        except Exception as e:
            print(f"[!] Brain routing failed: {e}")
            return {
                "intent": "general_chat",
                "action": "",
                "query": text,
                "response": f"I had trouble with that. I heard you say: {text}."
            }

    def select_intent(self, text: str) -> dict:
        """
        Main routing method called by the GUI.
        1. Try local instant match first
        2. Fall back to Gemini if no local match
        """
        # Fast path — local intent
        local = self._try_local_intent(text)
        if local:
            return local

        # Slow path — Gemini
        print(f"[*] Sending to Gemini: '{text}'")
        return self._call_gemini(text)