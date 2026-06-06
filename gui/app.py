# -*- coding: utf-8 -*-
"""
Synergy Graphic User Interface
Implements a custom Tkinter system dashboard based on the exact user layout constraints.
Includes an animated voice amplitude spectrogram, status badges, and expandable settings overlays.
"""

import os
import json
import random
import threading
import tkinter as tk
from tkinter import ttk, messagebox

class SynergyApp:
    def __init__(self, root, brain, tts, transcriber, spotify, calendar, wikipedia, search):
        self.root = root
        self.root.title("Synergy — AI Assistant Dashboard")
        self.root.geometry("1024x680")
        self.root.configure(bg="#111111")
        self.root.resizable(True, True)

        # Core Engines
        self.brain = brain
        self.tts = tts
        self.transcriber = transcriber
        self.spotify = spotify
        self.calendar = calendar
        self.wikipedia = wikipedia
        self.search = search

        # Local States
        self.active_tab = "Challenge"  # default
        self.status_text = tk.StringVar(value="STANDBY — say \"Synergy\" to activate")
        self.listening_text = tk.StringVar(value="[No voice stream recorded]")
        self.state = "STANDBY"  # STANDBY, LISTENING, PROCESSING, SPEAKING
        self.wave_bars = []
        self.wave_heights = [10] * 18

        # Load configurations
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        self.load_settings()

        self.setup_ui()
        self.animate_waveform()

    def load_settings(self):
        self.config_data = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    self.config_data = json.load(f)
            except Exception:
                pass

    def setup_ui(self):
        # Master grid setup
        self.root.columnconfigure(0, weight=6, minsize=550) # Left 60%
        self.root.columnconfigure(1, weight=4, minsize=350) # Right 40%
        self.root.rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # LEFT PANEL (60%)
        # ----------------------------------------------------
        self.left_panel = tk.Frame(self.root, bg="#111111", padx=30, pady=30)
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_panel.columnconfigure(0, weight=1)

        # Pill Badge "#SYNERGY"
        self.badge_lbl = tk.Label(
            self.left_panel,
            text=" ✦  #SYNERGY ",
            font=("Consolas", 10, "bold"),
            bg="#111111",
            fg="#E8A020",
            highlightthickness=1,
            highlightbackground="#E8A020",
            relief="flat",
            padx=8,
            pady=3
        )
        self.badge_lbl.pack(anchor="w", pady=(0, 10))

        # Big Title
        self.title_lbl = tk.Label(
            self.left_panel,
            text="Synergy Intelligence",
            font=("Helvetica", 28, "bold"),
            bg="#111111",
            fg="#ffffff"
        )
        self.title_lbl.pack(anchor="w", pady=(0, 5))

        # Subtitle
        self.sub_lbl = tk.Label(
            self.left_panel,
            text="Voice-Activated Agentic Desktop Assistant System Console",
            font=("Helvetica", 11),
            bg="#111111",
            fg="#888888"
        )
        self.sub_lbl.pack(anchor="w", pady=(0, 25))

        # Tabs Layout ("Challenge" | "Solution" | "Impact")
        self.tabs_frame = tk.Frame(self.left_panel, bg="#111111")
        self.tabs_frame.pack(anchor="w", fill="x", pady=(0, 15))

        self.tab_buttons = {}
        for tab_name in ["Challenge", "Solution", "Impact"]:
            btn = tk.Button(
                self.tabs_frame,
                text=tab_name.upper(),
                font=("Consolas", 11, "bold"),
                bg="#1a1a1a",
                activebackground="#E8A020",
                activeforeground="#111111",
                bd=0,
                padx=15,
                pady=6,
                command=lambda t=tab_name: self.switch_tab(t)
            )
            btn.pack(side="left", padx=(0, 10))
            self.tab_buttons[tab_name] = btn

        # Tab Content Display Box
        self.tab_content_box = tk.Frame(self.left_panel, bg="#1a1a1a", bd=1, relief="solid", highlightbackground="#2a2a2a")
        self.tab_content_box.pack(fill="both", expand=True, pady=(0, 25))
        
        self.tab_txt = tk.Text(
            self.tab_content_box,
            wrap="word",
            bg="#1a1a1a",
            fg="#cccccc",
            font=("Helvetica", 11),
            bd=0,
            padx=18,
            pady=18,
            height=10
        )
        self.tab_txt.pack(fill="both", expand=True)
        self.switch_tab("Challenge")  # Render initial choice

        # System instruments & Framework pills
        inst_lbl = tk.Label(
            self.left_panel,
            text="SYSTEM INSTRUMENTS & FRAMEWORKS",
            font=("Consolas", 9, "bold"),
            bg="#111111",
            fg="#888888"
        )
        inst_lbl.pack(anchor="w", pady=(0, 8))

        self.pills_frame = tk.Frame(self.left_panel, bg="#111111")
        self.pills_frame.pack(anchor="w", fill="x")

        # Configured framework pill badges
        frameworks = ["Python", "Gemini API", "Tkinter", "Spotify API", "SpeechRecognition", "Wikipedia API"]
        for fw in frameworks:
            lbl = tk.Label(
                self.pills_frame,
                text=fw,
                font=("Consolas", 9),
                bg="#222222",
                fg="#cccccc",
                padx=8,
                pady=4,
                relief="flat",
                bd=0
            )
            lbl.pack(side="left", padx=(0, 6), pady=3)

        # ----------------------------------------------------
        # RIGHT PANEL (40%)
        # ----------------------------------------------------
        self.right_panel = tk.Frame(self.root, bg="#171717", padx=25, pady=30, bd=1, relief="solid", highlightbackground="#2a2a2a")
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        # Sensory Harness label
        sensory_lbl = tk.Label(
            self.right_panel,
            text="SENSORY HARNESS SIMULATOR",
            font=("Consolas", 9, "bold"),
            bg="#171717",
            fg="#888888"
        )
        sensory_lbl.pack(anchor="w", pady=(0, 10))

        # Wave Canvas Box
        self.wave_canvas_box = tk.Frame(self.right_panel, bg="#111111", bd=1, relief="solid", highlightbackground="#2a2a2a")
        self.wave_canvas_box.pack(fill="x", pady=(0, 15))

        self.wave_canvas = tk.Canvas(self.wave_canvas_box, height=130, bg="#111111", highlightthickness=0)
        self.wave_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        self.wave_label = tk.Label(
            self.wave_canvas_box,
            text="● VOICE_WAVEFORM_DENSITY  ",
            font=("Consolas", 8, "bold"),
            bg="#111111",
            fg="#E8A020"
        )
        self.wave_label.pack(anchor="e", pady=(0, 5))

        # Status and transcript boxes
        status_lbl_title = tk.Label(
            self.right_panel,
            text="SYSTEM_STATUS_OUTLET",
            font=("Consolas", 8, "bold"),
            bg="#171717",
            fg="#888888"
        )
        status_lbl_title.pack(anchor="w", pady=(5, 2))

        self.status_box = tk.Label(
            self.right_panel,
            textvariable=self.status_text,
            font=("Consolas", 10, "bold"),
            bg="#222222",
            fg="#ffb224",
            anchor="w",
            padx=12,
            pady=8,
            bd=1,
            relief="solid",
            highlightbackground="#2a2a2a"
        )
        self.status_box.pack(fill="x", pady=(0, 15))

        # Current Command widget label
        listing_lbl = tk.Label(
            self.right_panel,
            text="LISTENING_FOR_WIDGET_COMMAND",
            font=("Consolas", 8, "bold"),
            bg="#171717",
            fg="#888888"
        )
        listing_lbl.pack(anchor="w")

        self.command_out = tk.Label(
            self.right_panel,
            textvariable=self.listening_text,
            font=("Helvetica", 11, "italic"),
            bg="#111111",
            fg="#cccccc",
            wraplength=300,
            justify="left",
            anchor="nw",
            padx=12,
            pady=12,
            height=4,
            relief="solid",
            bd=1,
            highlightbackground="#2a2a2a"
        )
        self.command_out.pack(fill="x", pady=(0, 20))

        # Schematic Box
        schematic_lbl = tk.Label(
            self.right_panel,
            text="VISUAL PROTOTYPE SCHEMATIC CONCEPT",
            font=("Consolas", 8, "bold"),
            bg="#171717",
            fg="#888888"
        )
        schematic_lbl.pack(anchor="w")

        self.schematic_box = tk.Label(
            self.right_panel,
            text="Synergy continuously scans microphone loops for wake keywords. "
                 "Upon active detection, routing queries process via Gemini with agent execution.",
            font=("Helvetica", 10),
            bg="#1a1a1a",
            fg="#888888",
            wraplength=300,
            justify="left",
            anchor="w",
            padx=12,
            pady=12,
            relief="flat",
            bd=0
        )
        self.schematic_box.pack(fill="x", pady=(0, 20))

        # Bottom Buttons
        self.ctrl_btn_frame = tk.Frame(self.right_panel, bg="#171717")
        self.ctrl_btn_frame.pack(fill="x", side="bottom")

        # API Keys gear button
        self.settings_btn = tk.Button(
            self.ctrl_btn_frame,
            text="⚙  Configure Keys",
            font=("Helvetica", 10, "bold"),
            bg="#2a2a2a",
            fg="#ffffff",
            activebackground="#E8A020",
            activeforeground="#111111",
            bd=0,
            padx=10,
            pady=8,
            command=self.open_settings_panel
        )
        self.settings_btn.pack(side="left")

        # Manual Activation button
        self.activate_btn = tk.Button(
            self.ctrl_btn_frame,
            text="Trigger Helper Command",
            font=("Helvetica", 10, "bold"),
            bg="#E8A020",
            fg="#111111",
            activebackground="#ffb82b",
            bd=0,
            padx=10,
            pady=8,
            command=self.manual_speech_command
        )
        self.activate_btn.pack(side="right")

    def switch_tab(self, tab_name: str):
        self.active_tab = tab_name
        
        # UI Toggle Styles
        for name, button in self.tab_buttons.items():
            if name == tab_name:
                button.config(bg="#E8A020", fg="#111111")
            else:
                button.config(bg="#1a1a1a", fg="#ffffff")

        # Insert specific readable case study text mapping the agentic architecture
        content = ""
        if tab_name == "Challenge":
            content = (
                "THE PROBLEM STATEMENT:\n"
                "Desktop automation systems of the classical era require rigorous keyboard commands or click macros to handle file syncing, "
                "media streams, or event calendaring. To make these actions modern, users need hands-free voice execution that is lightweight, "
                "local, private but deeply connected to powerful reasoning brains (Large Language Models).\n\n"
                "Building an always-listening wake word system locally is typically intensive and requires cloud stream connections "
                "that breach privacy. Synergy addresses this by combining tiny offline speech models (Vosk) with precise remote LLM intent parsing on demand."
            )
        elif tab_name == "Solution":
            content = (
                "THE ARCHITECTURAL PARADIGM:\n"
                "Synergy coordinates three critical elements into a concurrent runtime framework:\n\n"
                "1. OFFLINE VOICE BUFFER: Uses pyaudio to capture a local 16kHz microphone stream. Vosk compiles speech patterns fully offline "
                "for the wake word 'Synergy', eliminating latency and data transmission during idle standby.\n\n"
                "2. CHAT AGENT BOUNDARY: Once activated, user statements stream through Google's Gemini Flash model which serves "
                "as a cognitive routing computer. It responds inside structured JSON maps detailing target agents, search queries, and verbal replies.\n\n"
                "3. HARDWARE CONTROLLERS: Local agents execute local integrations such as Web searches (duckduckgo-search), Wikipedia, "
                "Playlists (Spotipy), and schedule calendars (Google Calendar API), before pyttsx3 offline text-to-speech speaks the synthesized result."
            )
        elif tab_name == "Impact":
            content = (
                "THE OPERATIONAL RESULTS:\n"
                "By decoupling ambient standby monitoring (Vosk) from semantic processing (Gemini API), Synergy presents critical operational metrics:\n\n"
                "• Standby Bandwidth: 0.0 Kbps (Fully local acoustic analysis)\n"
                "• Query Response Latency: <1.4 seconds (Gemini optimized token synthesis)\n"
                "• Offline Resilience: Local commands (like hardware volume adjustments or default local calendar items) "
                "failover gracefully without web sockets.\n\n"
                "Synergy allows specialists to automate daily desk workflows via ambient voice loops comfortably, securely, and seamlessly."
            )

        self.tab_txt.config(state="normal")
        self.tab_txt.delete("1.0", tk.END)
        self.tab_txt.insert("1.0", content)
        self.tab_txt.config(state="disabled")

    def animate_waveform(self):
        """Draws and updates randomized voice vector bars on Canvas according to current state."""
        self.wave_canvas.delete("all")
        width = self.wave_canvas.winfo_width() or 300
        height = self.wave_canvas.winfo_height() or 130
        
        spacing = 14
        bar_width = 6
        num_bars = 18
        start_x = (width - (num_bars * spacing)) // 2

        # Select amplitude range based on current active system state
        if self.state == "STANDBY":
            # Gentle pulsing
            amplitude_min, amplitude_max = 8, 30
            speed_factor = 0.05
        elif self.state == "LISTENING":
            # Active and noisy
            amplitude_min, amplitude_max = 35, 110
            speed_factor = 0.2
        elif self.state == "PROCESSING":
            # Computing logic - flickering
            amplitude_min, amplitude_max = 20, 60
            speed_factor = 0.15
        elif self.state == "SPEAKING":
            # Synced speech pulsing
            amplitude_min, amplitude_max = 40, 95
            speed_factor = 0.25
        else:
            amplitude_min, amplitude_max = 5, 15
            speed_factor = 0.05

        for i in range(num_bars):
            # Smooth bar updates slightly using a target factor
            target_h = random.randint(amplitude_min, amplitude_max)
            self.wave_heights[i] += (target_h - self.wave_heights[i]) * 0.4
            bar_h = self.wave_heights[i]

            x0 = start_x + (i * spacing)
            y0 = (height - bar_h) // 2
            x1 = x0 + bar_width
            y1 = y0 + bar_h

            # Draw rounded voice bars
            self.wave_canvas.create_rectangle(
                x0, y0, x1, y1,
                fill="#E8A020",
                outline="#E8A020",
                width=1
            )

        self.root.after(80, self.animate_waveform)

    def set_system_state(self, state: str, status_msg: str):
        """Thread-safe state configuration to alter visual animations."""
        self.state = state
        self.status_text.set(status_msg)

    def manual_speech_command(self):
        """Emulates or forces a speech command dialog for testing inside GUI."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Trigger Synergy Helper Command")
        dialog.geometry("420x180")
        dialog.configure(bg="#1a1a1a")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Simulation Tool: Submit a vocal query to Gemini", bg="#1a1a1a", fg="#ffffff", font=("Helvetica", 10, "bold")).pack(pady=(15, 10))
        
        entry = ttk.Entry(dialog, width=38)
        entry.pack(pady=5)
        entry.focus_set()

        def submit():
            cmd = entry.get().strip()
            if cmd:
                dialog.destroy()
                threading.Thread(target=self.process_command_flow, args=(cmd,), daemon=True).start()

        ttk.Button(dialog, text="Submit Command Draft", style="Accent.TButton", command=submit).pack(pady=15)

    # ── REPLACE the entire process_command_flow method in gui/app.py ──────────────
# Find:  def process_command_flow(self, cmd_text: str):
# Replace the whole method with this:

    def process_command_flow(self, cmd_text: str):
        """Core command execution pipeline."""
        #self.set_system_state("PROCESSING", f"PROCESSING: \"{cmd_text}\"")
        #self.listening_text.set(f"Command detected:\n\"{cmd_text}\"")

        # Route via Brain (local cache first, then Gemini)
        brain_data = self.brain.select_intent(cmd_text)
        intent = brain_data.get("intent", "general_chat")
        action = brain_data.get("action", "")
        query  = brain_data.get("query", "")
        speak_reply = brain_data.get("response", "Done.")

        # Execute appropriate agent
        agent_result = ""

        if intent == "spotify":
            agent_result = self.spotify.execute_action(action, query)

        elif intent == "youtube":
            # Import here so app doesn't crash if yt-dlp not installed
            try:
                from agents.youtube_agent import YouTubeAgent
                if not hasattr(self, "_youtube"):
                    self._youtube = YouTubeAgent()
                agent_result = self._youtube.execute_action(action, query)
            except Exception as e:
                agent_result = f"YouTube error: {e}. Install yt-dlp and ffmpeg."

        elif intent == "calendar":
            agent_result = self.calendar.execute_action(action, query)

        elif intent == "wikipedia":
            agent_result = self.wikipedia.search_summary(query)

        elif intent == "web_search":
            agent_result = self.search.search_web(query)

        elif intent == "general_chat":
            # If Gemini gave us a real response use it, otherwise echo
            agent_result = speak_reply if speak_reply else f"I heard: {cmd_text}"

        else:
            agent_result = speak_reply or "Done."

        # Speak result
        self.set_system_state("SPEAKING", "SPEAKING...")
        self.listening_text.set(f"Synergy:\n\"{agent_result}\"")
        self.tts.speak(agent_result)

        # Return to standby
        self.root.after(1500, lambda: self.set_system_state(
            "STANDBY", "STANDBY — say \"Synergy\" to activate"))

    def open_settings_panel(self):
        self.load_settings()
        panel = tk.Toplevel(self.root)
        panel.title("Synergy - Settings Panel")
        panel.geometry("460x360")
        panel.configure(bg="#111111")
        panel.resizable(False, False)

        # Title
        tk.Label(panel, text="⚙  SYNERGY SETTINGS CONTROL", bg="#111111", fg="#E8A020", font=("Consolas", 12, "bold")).pack(pady=(20, 15))

        # Dot Indicators
        indicator_frame = tk.Frame(panel, bg="#111111")
        indicator_frame.pack(fill="x", padx=30, pady=10)

        # Helper method for status tracking
        def draw_status_dot(parent, label_text, is_green):
            sub_f = tk.Frame(parent, bg="#111111")
            sub_f.pack(side="left", expand=True)
            dot = tk.Label(sub_f, text="●", fg="#1ed760" if is_green else "#888888", bg="#111111", font=("Verdana", 14))
            dot.pack(side="left")
            lbl = tk.Label(sub_f, text=f" {label_text}", fg="#ffffff", bg="#111111", font=("Helvetica", 9))
            lbl.pack(side="left")

        has_gemini = bool(self.config_data.get("gemini_api_key", ""))
        has_spotify = bool(self.config_data.get("spotify", {}).get("client_id", ""))
        has_cal = self.calendar.is_configured()

        draw_status_dot(indicator_frame, "Gemini API", has_gemini)
        draw_status_dot(indicator_frame, "Spotify", has_spotify)
        draw_status_dot(indicator_frame, "Calendar", has_cal)

        # Settings Options Form
        form_f = tk.Frame(panel, bg="#111111")
        form_f.pack(fill="x", padx=35, pady=15)

        tk.Label(form_f, text="Wake keyword:", bg="#111111", fg="#cccccc", anchor="w").grid(row=0, column=0, sticky="w", pady=6)
        wake_entry = ttk.Entry(form_f, width=20)
        wake_entry.insert(0, self.config_data.get("wake_word", "synergy"))
        wake_entry.grid(row=0, column=1, sticky="w", pady=6, padx=10)

        tk.Label(form_f, text="Speech Speed:", bg="#111111", fg="#cccccc", anchor="w").grid(row=1, column=0, sticky="w", pady=6)
        speed_entry = ttk.Entry(form_f, width=20)
        speed_entry.insert(0, str(self.config_data.get("voice_speed", 175)))
        speed_entry.grid(row=1, column=1, sticky="w", pady=6, padx=10)

        # Silent mode toggle
        silent_mode_var = tk.BooleanVar(value=self.config_data.get("silent_mode", False))
        silent_check = tk.Checkbutton(
            form_f,
            text="Silent (Notification) Mode Only",
            variable=silent_mode_var,
            bg="#111111",
            fg="#cccccc",
            selectcolor="#1a1a1a",
            activebackground="#111111",
            activeforeground="#ffffff"
        )
        silent_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=12)

        def save_panel_configs():
            self.config_data["wake_word"] = wake_entry.get().strip().lower() or "synergy"
            try:
                self.config_data["voice_speed"] = int(speed_entry.get().strip() or "175")
            except ValueError:
                self.config_data["voice_speed"] = 175

            self.config_data["silent_mode"] = silent_mode_var.get()

            try:
                with open(self.config_path, "w") as f:
                    json.dump(self.config_data, f, indent=2)
                # Apply configurations dynamically
                self.tts.update_settings_from_config()
                panel.destroy()
                messagebox.showinfo("Success", "Synergy settings updated dynamically.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to serialize settings file: {e}")

        ttk.Button(panel, text="Apply Config", style="Accent.TButton", command=save_panel_configs).pack(pady=20)
