[app]
title = AI Virus Guard
package.name = aivirusguard
package.domain = org.inspire
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3,kivy,android
p4a.branch = 2024.1.21

orientation = portrait
osx.kivy_version = 1.9.1

fullname = AI Virus Guard

# Storage Permissions
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# Android API Settings
android.api = 33
android.minapi = 24
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
