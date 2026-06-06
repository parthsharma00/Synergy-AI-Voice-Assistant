# -*- coding: utf-8 -*-
"""
Synergy Voice-Activated Desktop AI Assistant
===========================================
Copyright (c) 2026

This is the main entry point file. It initiates the system engines,
loads user configurations, triggers the first-run installation helper if needed,
and coordinates standard multithreaded graphical and acoustic runtimes.
"""

import os
import sys
import threading
import time

# Add parent path to import structures correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.brain import AIStudioBrain
from core.tts import SpeechSynthesizer
from core.speech import SpeechTranscriber
from core.wake_word import WakeWordDetector
from agents.spotify_agent import SpotifyAgent
from agents.calendar_agent import CalendarAgent
from agents.wikipedia_agent import WikipediaAgent
from agents.search_agent import WebSearchAgent
from gui.app import SynergyApp

def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    # 1. Trigger First-Run Setup Wizard if configuration does not exist
    if not os.path.exists(config_path):
        from setup.first_run import SetupWizard
        print("[*] Launching introductory Synergy wizard...")
        wizard = SetupWizard(on_done_callback=run_synergy_app)
        wizard.launch()
    else:
        run_synergy_app()

def run_synergy_app():
    import tkinter as tk
    
    print("[*] Initializing Synergy system components...")
    
    # Initialize Engines
    brain = AIStudioBrain()
    tts = SpeechSynthesizer()
    transcriber = SpeechTranscriber()
    
    # Initialize Agent integrations
    spotify = SpotifyAgent()
    calendar = CalendarAgent()
    wikipedia = WikipediaAgent()
    search = WebSearchAgent()
    
    # Create main Tkinter Window
    root = tk.Tk()
    
    # Initialize Master GUI
    app = SynergyApp(
        root=root,
        brain=brain,
        tts=tts,
        transcriber=transcriber,
        spotify=spotify,
        calendar=calendar,
        wikipedia=wikipedia,
        search=search
    )

    # Define the Wake-Word detection callback pipeline
    def on_wake_word_detected():
        # Transition GUI to listening state
        app.set_system_state("LISTENING", "LISTENING...")
        
        # Play a visual confirmation/beep
        print("[!] Synergy wake word heard! Capturing voice command...")
        app.tts.speak("Yes?")
        time.sleep(1)
        
        # Start a background speech-to-text recording to ensure GUI animation runs concurrently
        def record_and_route():
            voice_command = app.transcriber.listen_and_transcribe(timeout=5)
            if voice_command:
                # Thread-safe pipeline execution
                root.after(0, lambda: app.process_command_flow(voice_command))
            else:
                # Fail gracefully back to standby
                app.tts.speak("Standing by.")
                root.after(0, lambda: app.set_system_state("STANDBY", "STANDBY — say \"Synergy\" to activate"))

        threading.Thread(target=record_and_route, daemon=True).start()

    # 2. Boot background acoustic detector thread
    detector = WakeWordDetector(
        callback=on_wake_word_detected,
        error_callback=lambda err_msg: print(f"[!] Detector Warning: {err_msg}")
    )
    
    print("[*] Starting backend voice sensor daemon...")
    detector.start()

    # Define safety shutdowns on close
    def on_close():
        print("[*] Shutting down active Synergy threads and streams...")
        detector.stop()
        root.destroy()
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_close)

    # 3. Spin up main Tkinter message loop
    print("[*] Launching graphical dashboard system. System operational!")
    root.mainloop()

if __name__ == "__main__":
    main()
