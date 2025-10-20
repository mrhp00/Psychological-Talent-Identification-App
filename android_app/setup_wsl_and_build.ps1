# PowerShell script to set up WSL and build Android APK
# Run this script as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Android APK Build Setup (WSL)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Step 1: Checking WSL installation..." -ForegroundColor Green

# Check if WSL is installed
$wslInstalled = (Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux).State -eq "Enabled"

if (-not $wslInstalled) {
    Write-Host "Installing WSL..." -ForegroundColor Yellow
    wsl --install -d Ubuntu
    Write-Host ""
    Write-Host "WSL installed. Please restart your computer and run this script again." -ForegroundColor Yellow
    pause
    exit 0
}

Write-Host "WSL is installed." -ForegroundColor Green

# Check if Ubuntu distribution exists
$ubuntuInstalled = wsl --list --quiet | Select-String "Ubuntu"

if (-not $ubuntuInstalled) {
    Write-Host "Installing Ubuntu distribution..." -ForegroundColor Yellow
    wsl --install -d Ubuntu
    Write-Host "Ubuntu installed. Please complete Ubuntu setup (username/password) and run this script again." -ForegroundColor Yellow
    pause
    exit 0
}

Write-Host "Ubuntu distribution found." -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Setting up build environment in WSL..." -ForegroundColor Green

# Create setup script for WSL
$wslSetupScript = @'
#!/bin/bash
set -e

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git zip unzip \
    openjdk-11-jdk autoconf libtool pkg-config zlib1g-dev \
    libncurses5-dev libncursesw5-dev libtinfo-dev cmake \
    libffi-dev libssl-dev build-essential

echo "Installing Python build tools..."
pip3 install --user buildozer cython==0.29.33

# Add pip binaries to PATH
if ! grep -q "/.local/bin" ~/.bashrc; then
    echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
fi

echo "Setup complete!"
'@

# Save setup script to temp file
$tempScript = [System.IO.Path]::GetTempFileName() + ".sh"
$wslSetupScript | Out-File -FilePath $tempScript -Encoding UTF8

# Copy script to WSL and execute
wsl bash -c "dos2unix < /mnt/c/$(($tempScript -replace '\\', '/') -replace 'C:', 'c') > ~/setup_buildozer.sh && chmod +x ~/setup_buildozer.sh && ~/setup_buildozer.sh"

Remove-Item $tempScript

Write-Host "Build environment set up successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Copying project to WSL..." -ForegroundColor Green

$projectPath = Split-Path -Parent $PSScriptRoot
$wslProjectPath = "~/psycho_app"

wsl bash -c "mkdir -p $wslProjectPath && cp -r '/mnt/g/New folder/Desktop/New folder/android_app/'* $wslProjectPath/"

Write-Host "Project copied to WSL at $wslProjectPath" -ForegroundColor Green
Write-Host ""

Write-Host "Step 4: Building APK (this will take 20-40 minutes for first build)..." -ForegroundColor Green

# Create build script
$buildScript = @'
#!/bin/bash
cd ~/psycho_app
buildozer -v android debug 2>&1 | tee build.log
echo "Build complete! APK location:"
ls -lh bin/*.apk
'@

$tempBuildScript = [System.IO.Path]::GetTempFileName() + ".sh"
$buildScript | Out-File -FilePath $tempBuildScript -Encoding UTF8

wsl bash -c "dos2unix < /mnt/c/$(($tempBuildScript -replace '\\', '/') -replace 'C:', 'c') > ~/build_apk.sh && chmod +x ~/build_apk.sh && ~/build_apk.sh"

Remove-Item $tempBuildScript

Write-Host ""
Write-Host "Step 5: Copying APK back to Windows..." -ForegroundColor Green

wsl bash -c "cp ~/psycho_app/bin/*.apk '/mnt/g/New folder/Desktop/New folder/android_app/' 2>/dev/null || echo 'No APK found'"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "APK location: G:\New folder\Desktop\New folder\android_app\*.apk" -ForegroundColor Yellow
Write-Host ""
Write-Host "To install on Android device:" -ForegroundColor Green
Write-Host "1. Copy APK to device (email, Google Drive, etc.)" -ForegroundColor White
Write-Host "2. Tap APK file on device" -ForegroundColor White
Write-Host "3. Allow installation from unknown sources if prompted" -ForegroundColor White
Write-Host ""
Write-Host "Or use ADB (if device connected via USB):" -ForegroundColor Green
Write-Host "  adb install *.apk" -ForegroundColor White
Write-Host ""

pause
