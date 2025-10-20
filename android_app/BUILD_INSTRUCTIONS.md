# Building Android APK - Instructions

## Important Note
**Buildozer for Android requires Linux.** Windows native Python cannot build Android APKs with Buildozer.

You have **3 options** to build the APK:

---

## Option 1: Using WSL (Windows Subsystem for Linux) - RECOMMENDED

This is the easiest method for Windows users.

### Step 1: Install WSL with Ubuntu
```powershell
# Run in PowerShell as Administrator
wsl --install -d Ubuntu
```

After installation, restart your computer if prompted.

### Step 2: Launch Ubuntu and Set Up Build Environment
```bash
# Open Ubuntu from Start menu, then run:
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git zip unzip openjdk-11-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo-dev cmake libffi-dev libssl-dev

# Install Buildozer
pip3 install --user buildozer cython==0.29.33

# Add pip binaries to PATH
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Copy Project to WSL
```bash
# In Ubuntu terminal, navigate to Windows drive
cd /mnt/g/New\ folder/Desktop/New\ folder/android_app

# Or copy the entire folder to WSL home for faster builds:
cp -r /mnt/g/New\ folder/Desktop/New\ folder/android_app ~/psycho_app
cd ~/psycho_app
```

### Step 4: Build APK
```bash
# First build (downloads SDK/NDK, takes 20-40 minutes)
buildozer -v android debug

# Subsequent builds are much faster (2-5 minutes)
```

### Step 5: Retrieve APK
The APK will be in: `bin/psychotalent-1.0-arm64-v8a_armeabi-v7a-debug.apk`

Copy it back to Windows:
```bash
cp bin/*.apk /mnt/g/New\ folder/Desktop/New\ folder/android_app/
```

---

## Option 2: Using Docker (If You Have Docker Desktop)

### Step 1: Install Docker Desktop for Windows
Download from: https://www.docker.com/products/docker-desktop

### Step 2: Build with Docker
```powershell
# In PowerShell, navigate to android_app folder
cd "G:\New folder\Desktop\New folder\android_app"

# Run Buildozer in Docker container
docker run --rm -v ${PWD}:/app kivy/buildozer android debug

# APK will be in bin/ folder after build completes
```

---

## Option 3: GitHub Actions (Cloud Build) - NO LOCAL SETUP REQUIRED

This builds the APK in the cloud for free.

### Step 1: Push Code to GitHub
```powershell
cd "G:\New folder\Desktop\New folder\android_app"
git init
git add .
git commit -m "Initial commit"
gh repo create psycho-talent-app --private --source=. --remote=origin --push
```

### Step 2: Add GitHub Actions Workflow
Create `.github/workflows/build-apk.yml`:

```yaml
name: Build Android APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          sudo apt update
          sudo apt install -y openjdk-11-jdk autoconf libtool
          pip install buildozer cython==0.29.33
      
      - name: Build APK
        run: |
          buildozer -v android debug
      
      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: android-apk
          path: bin/*.apk
```

Push workflow and download APK from GitHub Actions tab after build completes.

---

## Troubleshooting

### Build fails with "NDK not found"
Buildozer will automatically download NDK. If it fails:
```bash
buildozer android clean
buildozer -v android debug
```

### Build fails with "Java not found"
Install Java:
```bash
sudo apt install openjdk-11-jdk
```

### WSL is slow
Copy project to WSL filesystem (`~/psycho_app`) instead of accessing Windows drive (`/mnt/g/...`).

### Permission denied errors in WSL
```bash
chmod +x ~/.local/bin/buildozer
```

---

## Testing the APK

### Install on Android Device (via USB)
```bash
# Enable USB debugging on Android device (Settings > Developer Options)
# Connect device via USB
adb install bin/psychotalent-1.0-armeabi-v7a-debug.apk
```

### Install on Android Device (wireless)
1. Copy APK to Google Drive or email it to yourself
2. Download on Android device
3. Tap APK file and allow installation from unknown sources if prompted

---

## App Features

The Android app includes:
- ✅ **Data Snapshot Integrity**: Changing question keys doesn't affect historical scores
- ✅ **Automatic Migration**: On first launch, existing entries are migrated with key snapshots
- ✅ **Professional UI**: Material-style design with search, add/edit/delete functionality
- ✅ **Keys Editor**: Edit question scores and descriptions (JSON format)
- ✅ **Persistent Storage**: Data saved in app's private storage (`/data/data/org.psychotalent.psychotalent/`)

---

## Next Steps After Building

1. Install APK on Android device
2. Test adding entries and changing keys
3. Verify scores remain correct after key changes (snapshot protection)
4. Run migration if importing old data

---

## Files Modified

| File | Purpose |
|------|---------|
| `main.py` | Kivy app with snapshot support (305 lines) |
| `buildozer.spec` | Build configuration (updated for Android API 31, NDK 25b) |
| `requirements.txt` | Python dependencies |
| `app.kv` | Kivy layout (placeholder, UI built in Python) |

---

**Need Help?** Check build logs in `build_logs/buildozer-output.log` or `.buildozer/android/platform/build-*/logs/`
