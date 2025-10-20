[app]
title = Psychological Talent
package.name = psychotalent
package.domain = org.psychotalent
source.dir = .
source.include_exts = py,kv,json,png,jpg,ico
version = 1.0
requirements = python3,kivy==2.3.0,jdatetime,python-dateutil
orientation = portrait
fullscreen = 0

# Android specific
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

# iOS specific (for future)
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

[buildozer]
log_level = 2
warn_on_root = 1
