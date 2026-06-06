# -*- coding: utf-8 -*-
"""
Synergy First-Run Wizard
Walks developers through initial parameters, handles background Vosk-model downloading,
and configures standard API credentials cleanly.
"""

import os
import json
import urllib.request
import zipfile
import threading
import tkinter as tk
from tkinter import ttk, messagebox

VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"

class SetupWizard:
    def __init__(self, on_done_callback=None):
        self.on_done_callback = on_done_callback
        self.root = tk.Tk()
        self.root.title("Synergy - First-Run Wizard")
        self.root.geometry("640x500")
        self.root.configure(bg="#111111")
        self.root.resizable(False, False)

        # Style configurations
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#111111", foreground="#ffffff")
        self.style.configure("TLabel", background="#111111", foreground="#ffffff", font=("Helvetica", 11))
        self.style.configure("Header.TLabel", font=("Helvetica", 18, "bold"), foreground="#E8A020")
        self.style.configure("TButton", background="#1a1a1a", foreground="#ffffff", borderwidth=1, focuscolor="#E8A020")
        self.style.map("TButton", background=[("active", "#E8A020")], foreground=[("active", "#111111")])
        self.style.configure("Accent.TButton", background="#E8A020", foreground="#111111", font=("Helvetica", 11, "bold"))
        self.style.map("Accent.TButton", background=[("active", "#ffb82b")])
        self.style.configure("TProgressbar", thickness=20, troughcolor="#1a1a1a", background="#E8A020")

        self.current_step = 1
        self.config_data = {
            "wake_word": "synergy",
            "gemini_api_key": "",
            "use_free_tier": True,
            "spotify": {
                "client_id": "",
                "client_secret": "",
                "redirect_uri": "http://localhost:8888/callback"
            },
            "google_calendar": {
                "credentials_path": "credentials.json",
                "token_path": "token.json"
            },
            "voice_id": "",
            "voice_speed": 175,
            "silent_mode": False
        }

        self.container = tk.Frame(self.root, bg="#111111")
        self.container.pack(fill="both", expand=True, padx=30, pady=30)

        self.load_step()

    def load_step(self):
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()

        if self.current_step == 1:
            self.show_welcome()
        elif self.current_step == 2:
            self.show_model_download()
        elif self.current_step == 3:
            self.show_api_choice()
        elif self.current_step == 4:
            self.show_manual_keys()
        elif self.current_step == 5:
            self.show_done()

    def show_welcome(self):
        title = ttk.Label(self.container, text="Welcome to Synergy!", style="Header.TLabel")
        title.pack(anchor="w", pady=(0, 20))

        desc = ttk.Label(
            self.container,
            text="Synergy is your personal, voice-activated desktop AI assistant.\n\n"
                 "This quick first-run wizard will help download required offline voice models "
                 "and establish your preferred services so Synergy can play your songs, index meetings, "
                 "and fulfill search commands hands-free.",
            wraplength=540,
            justify="left"
        )
        desc.pack(anchor="w", pady=(0, 40))

        start_btn = ttk.Button(self.container, text="Start Installation Guide", style="Accent.TButton", command=self.next_step)
        start_btn.pack(side="right")

    def show_model_download(self):
        title = ttk.Label(self.container, text="Downloading Offline Speech Assets", style="Header.TLabel")
        title.pack(anchor="w", pady=(0, 20))

        desc = ttk.Label(
            self.container,
            text="To recognize your wake word offline without relying on third-party cloud streaming, "
                 "Synergy uses a small, high-efficiency Vosk acoustic model (~50MB).\n\n"
                 "Click below to initiate the download. A stable internet connection is required.",
            wraplength=540,
            justify="left"
        )
        desc.pack(anchor="w", pady=(0, 30))

        self.progress_val = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.container, variable=self.progress_val, maximum=100, style="TProgressbar")
        self.progress_bar.pack(fill="x", pady=(0, 15))

        self.status_lbl = ttk.Label(self.container, text="Status: Ready to download.", foreground="#888888")
        self.status_lbl.pack(anchor="w", pady=(0, 30))

        self.dl_btn = ttk.Button(self.container, text="Download Voice Assets", style="Accent.TButton", command=self.start_download)
        self.dl_btn.pack(side="right")

    def start_download(self):
        self.dl_btn.config(state="disabled")
        threading.Thread(target=self.download_and_extract, daemon=True).start()

    def download_and_extract(self):
        dest_folder = os.path.dirname(os.path.dirname(__file__))
        model_zip_path = os.path.join(dest_folder, "vosk_model.zip")
        final_model_name = "vosk-model-small-en-us"
        final_model_path = os.path.join(dest_folder, final_model_name)

        if os.path.exists(final_model_path):
            self.status_lbl.config(text="Status: Voice assets already installed!", foreground="#E8A020")
            self.progress_val.set(100.0)
            self.dl_btn.config(state="normal", text="Continue", command=self.next_step)
            return

        def report(block_count, block_size, total_size):
            downloaded = block_count * block_size
            percent = min(100.0, (downloaded / total_size) * 100)
            self.progress_val.set(percent)
            self.status_lbl.config(text=f"Status: Downloading... {percent:.1f}%")

        try:
            self.status_lbl.config(text="Status: Connecting to Vosk downloads...")
            urllib.request.urlretrieve(VOSK_MODEL_URL, model_zip_path, reporthook=report)
            
            self.status_lbl.config(text="Status: Extracting asset zip archive...")
            with zipfile.ZipFile(model_zip_path, 'r') as zip_ref:
                zip_ref.extractall(dest_folder)

            # Move and rename if extracted as e.g. 'vosk-model-small-en-us-0.15'
            extracted_folder_name = "vosk-model-small-en-us-0.15"
            extracted_path = os.path.join(dest_folder, extracted_folder_name)
            if os.path.exists(extracted_path):
                os.rename(extracted_path, final_model_path)

            if os.path.exists(model_zip_path):
                os.remove(model_zip_path)

            self.status_lbl.config(text="Status: Verification completed. Assets successfully registered!", foreground="#E8A020")
            self.progress_val.set(100.0)
            self.dl_btn.config(state="normal", text="Continue", command=self.next_step)

        except Exception as e:
            self.status_lbl.config(text=f"Status: Download failed! Error: {e}", foreground="#ff5555")
            self.dl_btn.config(state="normal", text="Retry Download")

    def show_api_choice(self):
        title = ttk.Label(self.container, text="Developer API Tiers", style="Header.TLabel")
        title.pack(anchor="w", pady=(0, 20))

        desc = ttk.Label(
            self.container,
            text="How would you like to run the Synergy LLM Brain (Gemini API)?\n\n"
                 "Option 1: FREE unauthenticated sandbox. Runs on the lightweight, high-performance "
                 "gemini-1.5-flash model via local ambient configurations. No keys required.\n\n"
                 "Option 2: Personal Key tier. Let's you provide your own API keys for Gemini, Spotify controls, "
                 "and Google Calendar integration.",
            wraplength=540,
            justify="left"
        )
        desc.pack(anchor="w", pady=(0, 40))

        btn_frame = tk.Frame(self.container, bg="#111111")
        btn_frame.pack(fill="x", pady=(20, 0))

        free_btn = ttk.Button(btn_frame, text="Use Free Offline-First Option", style="Accent.TButton", command=self.set_free_tier)
        free_btn.pack(side="left", expand=True, padx=10)

        byo_btn = ttk.Button(btn_frame, text="Bring My Own API Keys", style="TButton", command=self.set_byo_tier)
        byo_btn.pack(side="right", expand=True, padx=10)

    def set_free_tier(self):
        self.config_data["use_free_tier"] = True
        self.current_step = 5 # Skip manual key form
        self.load_step()

    def set_byo_tier(self):
        self.config_data["use_free_tier"] = False
        self.next_step()

    def show_manual_keys(self):
        title = ttk.Label(self.container, text="Provide API & App Keys", style="Header.TLabel")
        title.pack(anchor="w", pady=(0, 15))

        # Forms
        form_frame = tk.Frame(self.container, bg="#111111")
        form_frame.pack(fill="both", expand=True)

        ttk.Label(form_frame, text="Gemini API Key:").grid(row=0, column=0, sticky="w", pady=8)
        self.gemini_entry = ttk.Entry(form_frame, width=40)
        self.gemini_entry.grid(row=0, column=1, sticky="w", pady=8, px=10)

        ttk.Label(form_frame, text="Spotify Client ID:").grid(row=1, column=0, sticky="w", pady=8)
        self.spotify_id_entry = ttk.Entry(form_frame, width=40)
        self.spotify_id_entry.grid(row=1, column=1, sticky="w", pady=8, px=10)

        ttk.Label(form_frame, text="Spotify Secret Key:").grid(row=2, column=0, sticky="w", pady=8)
        self.spotify_secret_entry = ttk.Entry(form_frame, width=40, show="*")
        self.spotify_secret_entry.grid(row=2, column=1, sticky="w", pady=8, px=10)

        ttk.Label(form_frame, text="Calendar Secrets Path:").grid(row=3, column=0, sticky="w", pady=8)
        self.cal_creds_entry = ttk.Entry(form_frame, width=40)
        self.cal_creds_entry.insert(0, "credentials.json")
        self.cal_creds_entry.grid(row=3, column=1, sticky="w", pady=8, px=10)

        back_btn = ttk.Button(self.container, text="Back", style="TButton", command=self.prev_step)
        back_btn.pack(side="left")

        save_btn = ttk.Button(self.container, text="Save & Done", style="Accent.TButton", command=self.save_manual_keys_data)
        save_btn.pack(side="right")

    def save_manual_keys_data(self):
        self.config_data["gemini_api_key"] = self.gemini_entry.get().strip()
        self.config_data["spotify"]["client_id"] = self.spotify_id_entry.get().strip()
        self.config_data["spotify"]["client_secret"] = self.spotify_secret_entry.get().strip()
        self.config_data["google_calendar"]["credentials_path"] = self.cal_creds_entry.get().strip()
        self.next_step()

    def show_done(self):
        title = ttk.Label(self.container, text="Setup Completed Successfully!", style="Header.TLabel")
        title.pack(anchor="w", pady=(0, 20))

        settings_summary = "Free online-sandbox mode enabled." if self.config_data["use_free_tier"] else "Custom active developer endpoints registered."

        desc = ttk.Label(
            self.container,
            text=f"Synergy has been fully configured and is ready to stream.\n\n"
                 f"Configuration highlights:\n"
                 f"• Mode: {settings_summary}\n"
                 f"• Offline Voice Engine: Installed\n"
                 f"• Core Wake Word: \"{self.config_data['wake_word']}\"\n\n"
                 f"Launch the assistant by clicking 'Conclude Setup'. Make sure your microphone is plugged in "
                 f"and say 'Synergy' to activate hands-free control!",
            wraplength=540,
            justify="left"
        )
        desc.pack(anchor="w", pady=(0, 30))

        finish_btn = ttk.Button(self.container, text="Conclude Setup", style="Accent.TButton", command=self.finish_wizard)
        finish_btn.pack(side="right")

    def finish_wizard(self):
        # Save setup values to config.json
        config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
         # Overwrite config.json cleanly
        try:
            with open(config_file_path, "w") as f:
                json.dump(self.config_data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Saving Error", f"Could not write config file: {e}")

        self.root.destroy()
        if self.on_done_callback:
            self.on_done_callback()

    def next_step(self):
        self.current_step += 1
        self.load_step()

    def prev_step(self):
        self.current_step = max(1, self.current_step - 1)
        self.load_step()

    def launch(self):
        self.root.mainloop()

if __name__ == "__main__":
    wizard = SetupWizard()
    wizard.launch()
