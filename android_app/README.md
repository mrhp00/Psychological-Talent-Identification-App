# Psychological Talent Identification - Android App 🎯

A professional Kivy-based Android application for psychological talent assessment with **data snapshot integrity**.

## ✨ Features
- ✅ **Entity Management**: Add, edit, delete entries with name, phone, answers
- ✅ **Score Calculation**: Automatic scoring based on answer keys
- ✅ **Data Snapshot Integrity**: Changing question keys doesn't affect historical scores
- ✅ **Auto Migration**: Existing entries automatically migrated with key snapshots on first launch
- ✅ **Keys Editor**: Edit question scores and descriptions (JSON format)
- ✅ **Search & Sort**: Find entries by name/phone, sorted by score
- ✅ **Persistent Storage**: Data saved in app's private storage

---

## 🚀 **RECOMMENDED: GitHub Actions Build** (No Local Setup!)

**Build APK in the cloud for FREE - No WSL/Linux required!**

### Steps:
1. **Push code to GitHub** (if not already pushed)
2. **Go to "Actions" tab** in your GitHub repository
3. **Select "Build Android APK"** workflow
4. **Click "Run workflow"** → "Run workflow" button
5. **Wait 15-20 minutes** for build to complete ☕
6. **Download APK** from Artifacts section at bottom of workflow run

✅ The `.github/workflows/build-apk.yml` file is already configured!  
✅ No network issues, no dependency hell, just works!

---

## ⚠️ Local WSL Build Status

**Current Issue**: OpenSSL download blocked (HTTP 403 Forbidden)  
**Cause**: openssl.org blocks automated downloads from some regions/IPs

### Quick Fix Option 1: Download from GitHub Mirror
```bash
# In WSL Ubuntu
cd ~/psycho_app
mkdir -p .buildozer/android/packages/openssl
wget https://github.com/openssl/openssl/archive/refs/tags/OpenSSL_1_1_1w.tar.gz \
  -O .buildozer/android/packages/openssl/openssl-1.1.1w.tar.gz

# Retry build
export PIP_BREAK_SYSTEM_PACKAGES=1
~/.local/bin/buildozer -v android debug
```

### Quick Fix Option 2: Use VPN
If openssl.org is blocked, enable VPN and retry:
```bash
cd ~/psycho_app
~/.local/bin/buildozer android clean
~/.local/bin/buildozer -v android debug
```

### Quick Fix Option 3: Just Use GitHub Actions! 🎉
Seriously, it's easier and more reliable. See above.

---

## 📱 Installing APK on Android Device

### Method 1: USB (ADB - for developers)
```bash
adb install bin/psychotalent-1.0-*.apk
```

### Method 2: Cloud Transfer (easiest)
1. Upload APK to **Google Drive** or **Dropbox**
2. Download on Android device from Drive/Dropbox app
3. Tap APK file → Allow "Install from unknown sources" if prompted
4. Install!

### Method 3: Direct File Transfer
1. Connect phone to PC via USB
2. Copy APK to phone's **Downloads** folder
3. On phone: open **Files** app → Downloads → tap APK
4. Install!

---

## 🔒 Data Integrity Feature (IMPORTANT!)

### ❌ Problem We Solved
Old behavior: Changing question keys retroactively changed ALL historical scores because scores were recalculated from current keys.

### ✅ Solution Implemented: Snapshot Pattern
Each entry now stores a **snapshot of the keys** at save time:

```json
{
  "name": "John Doe",
  "phone": "123-456-7890",
  "answers": "abcdabcd",
  "score": 85,
  "keys_snapshot": [
    {"a": 10, "b": 5, "c": 0, "d": -5},
    {"a": 8, "b": 3, "c": -2, "d": -8},
    ...
  ]
}
```

**Result**: Historical scores are **frozen** and won't change when you edit keys!

### Migration on First Launch
- App automatically detects old entries without snapshots
- Migrates them with current keys as snapshot
- You can also manually trigger via "Migrate" button in toolbar

---

## 🛠️ Development & Testing

### Test App Locally (Without Building APK)
```bash
# Install Kivy on your PC
pip install kivy jdatetime python-dateutil

# Run the app
cd android_app
python main.py
```

### Modify UI
Edit `main.py` - UI is built programmatically in Python (not in `.kv` file for better control).

### Change Dependencies
1. Edit `buildozer.spec` (line with `requirements =`)
2. Edit `requirements.txt`
3. Rebuild APK

---

## 📁 Project Structure
```
android_app/
├── main.py                    # Kivy app with snapshot support (305 lines)
├── app.kv                     # Kivy layout placeholder
├── buildozer.spec             # Build config (API 31, NDK 25b)
├── requirements.txt           # Python deps (kivy, jdatetime, etc.)
├── BUILD_INSTRUCTIONS.md      # Detailed WSL build guide
├── setup_wsl_and_build.ps1    # PowerShell automation script
└── .github/workflows/
    └── build-apk.yml          # GitHub Actions CI/CD ⭐ RECOMMENDED
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Network unreachable** | Use GitHub Actions build (no network issues) |
| **OpenSSL 403 Forbidden** | Download from GitHub mirror (see Quick Fix above) or use VPN |
| **Cython not found** | `sudo apt install cython3` in WSL |
| **WSL is slow** | Copy project to WSL home: `cp -r /mnt/g/... ~/psycho_app` |
| **APK won't install** | Enable "Unknown sources" in Android Settings → Security |
| **Build takes forever** | First build: 20-40min (downloads 2GB). Subsequent: 2-5min |

---

## 📋 Technical Requirements
- **Python**: 3.11+
- **Kivy**: 2.3.0
- **Android**: API 21+ (Android 5.0 Lollipop or newer)
- **Build Environment**: Linux (WSL/Ubuntu) or GitHub Actions

---

## 📝 What's Implemented
✅ Add/Edit/Delete entries with data validation  
✅ Keys editor (JSON format with score values)  
✅ Search by name/phone  
✅ Sort by score (descending)  
✅ Snapshot integrity (historical scores preserved)  
✅ Auto migration for old data  
✅ Persistent storage in app private directory  
✅ Material-style UI with confirmation dialogs  

## ❌ Not Ported from Desktop App
- Class management (SQLite database)
- Merge duplicate entries dialog
- Export/import features
- Advanced filtering

---

**Built with ❤️ using Kivy & Python**  
**Part of the Psychological Talent Identification App project**
