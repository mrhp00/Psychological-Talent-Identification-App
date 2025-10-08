This folder contains a Kivy-based reimplementation of the core functionality in `psycho_app.py` suitable for packaging as an Android APK via Buildozer.

Important notes:
- I did not modify `psycho_app.py`. The Android app is a separate Kivy app in this folder that uses the same `keys.json` and `entries.json` data model.
- Building an APK requires a Linux environment (WSL or a Linux machine) with Buildozer and the Android SDK/NDK installed. See Buildozer docs: https://buildozer.readthedocs.io/

Quick build steps (on Ubuntu / WSL):
1. Install dependencies: sudo apt update; sudo apt install -y python3-pip python3-venv build-essential git
2. Create a venv and activate it: python3 -m venv venv; source venv/bin/activate
3. pip install --upgrade buildozer
4. cd android_app
5. buildozer init (if you want to regenerate spec)
6. buildozer -v android debug

Files in this folder:
- `main.py` — Kivy app entrypoint (reimplements entries/keys management UI)
- `app.kv` — placeholder KV file
- `requirements.txt` — runtime requirements
- `buildozer.spec` — template spec for Buildozer

Limitations and follow-ups:
- I implemented the UI and storage in Kivy and JSON files; not all PyQt features (classes DB, timers, merge dialog) are ported.
- You must build on Linux; Buildozer does not support building APKs on Windows natively.
