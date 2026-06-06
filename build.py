# -*- coding: utf-8 -*-
"""
Synergy Standalone Packaging Script
==================================
Compiles the offline-compatible desktop voice assistant with PyInstaller,
moving all models, settings, and icon definitions into double-clickable bundles.
Includes auto-install/login registration parameters.
"""

import os
import sys
import subprocess
import shutil

def register_startup_autostart():
    """Injects registry entries or plist commands to launch Synergy on user login."""
    try:
        if sys.platform == "win32":
            import winreg
            key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            app_name = "SynergyVoiceAssistant"
            exe_path = os.path.abspath(sys.argv[0]) # Executable target path

            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}"')
            winreg.CloseKey(key)
            print("[*] Checked: Registered Synergy in Windows User Startup registry.")
            
        elif sys.platform == "darwin":
            # macOS launchctl / AppleScript login-item registration
            import subprocess
            app_name = "Synergy"
            app_path = f"/Applications/{app_name}.app"
            applescript_cmd = f'tell application "System Events" to make new login item at end with properties {{path:"{app_path}", hidden:false, name:"{app_name}"}}'
            
            # Run quietly as background configuration
            if os.path.exists(app_path):
                subprocess.run(["osascript", "-e", applescript_cmd], capture_output=True)
                print("[*] Checked: Registered Synergy in macOS login items.")
    except Exception as e:
        print(f"[!] Warning: Auto-start registration skipped: {e}")

def run_pyinstaller_build():
    """Runs PyInstaller compilation with the appropriate assets, directories, and models."""
    print("======================================================")
    print("              SYNERGY CUSTOM APPLICATION BUNDLER      ")
    print("======================================================")

    # Double check if PyInstaller is present
    try:
        import PyInstaller
    except ImportError:
        print("[!] pyinstaller package not loaded. Run: pip install pyinstaller")
        sys.exit(1)

    project_root = os.path.dirname(os.path.abspath(__file__))
    main_py_path = os.path.join(project_root, "main.py")
    
    # Locate model files to embed
    model_dir = "vosk-model-small-en-us"
    model_abs_path = os.path.join(project_root, model_dir)
    
    # Path divider parameters
    path_sep = ";" if sys.platform == "win32" else ":"

    # Build basic parameters
    pyinstaller_args = [
        "pyinstaller",
        "--noconfirm",
        "--onedir" if sys.platform == "darwin" else "--onefile", # onedir for mac .app bundle, onefile for win .exe
        "--windowed", # Suppress command prompt window (creates purely Tkinter GUI)
        "--name=Synergy",
    ]

    # Dynamically inject the acoustic Vosk model data directory if downloaded
    if os.path.exists(model_abs_path):
        print(f"[+] Embedding offline Vosk Speech Acoustic Folder: '{model_dir}'")
        pyinstaller_args.append(f"--add-data={model_dir}{path_sep}{model_dir}")
    else:
        print("[!] Warning: Acoustic model directory not found locally. It will need to download on launch.")

    # Include default configuration layout
    config_file = "config.json"
    if os.path.exists(os.path.join(project_root, config_file)):
        pyinstaller_args.append(f"--add-data={config_file}{path_sep}.")

    pyinstaller_args.append(main_py_path)

    print(f"[*] Compiling using PyInstaller command:\n{' '.join(pyinstaller_args)}\n")
    try:
        subprocess.run(pyinstaller_args, check=True)
        print("\n[+] Compilation finished successfully!")
        print("[+] Check your 'dist/' directory for executable bundles.")
        
        # Try autostart registration for binary check
        register_startup_autostart()
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Compilation failed: Process exited with exception code {e.returncode}")

if __name__ == "__main__":
    run_pyinstaller_build()
