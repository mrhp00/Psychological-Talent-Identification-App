[app]
title = Psychological Talent Identification
package.name = psycho_app_android
package.domain = org.example
source.dir = .
source.include_exts = py,kv,json,png,jpg
version = 0.1
requirements = python3,kivy==2.2.1,jdatetime,python-dateutil
orientation = portrait
android.arch = armeabi-v7a
# Recommended p4a / NDK settings for CI
android.api = 31
android.ndk = 23b
android.ndk_path = /usr/local/lib/android-ndk
presplash.filename = %(source.dir)s/data/presplash.png

[app]
# (buildozer will fill other defaults)

[buildozer]
log_level = 2
warn_on_root = 1
