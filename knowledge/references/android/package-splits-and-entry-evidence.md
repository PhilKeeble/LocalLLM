---
id: reference-android-package-entry-evidence
title: Android APKs, manifests, DEX, ABI splits and entry evidence
kind: reference
topics: [android, apk, dex, manifest, abi, splits, entry-points]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# Android package and execution scope

## A publishing bundle is different from the installed APK set

An APK is an installable app archive; an Android App Bundle is a publishing
format from which device-specific APKs can be generated. Feature/configuration
delivery can separate code and resources across installed packages. [1][2]

Record the available base/splits, package identity and delivery state. A single
APK or AAB cannot prove the complete installed code surface. Missing a split is
an evidence gap, not proof the contained behavior is absent on the device.
Shared archive facts: format-packages-archives-contained-images.

## Manifest components are entry candidates with their own lifecycle

Android components include activities, services, broadcast receivers and content
providers; the manifest declares components used by the system. [1]

Recover the installed declaration, enabled/exported state, permission policy and
actual callback. A declared class is not proof it launched, and an icon/launcher
entry does not cover every component. Join component input to its consumer;
manifest permission requests do not prove effective grants.
Policy facts: reference-android-component-uri-authority.

## DEX and native libraries require separate representation evidence

DEX holds class definitions and associated data. NDK libraries conventionally
reside at /lib/<abi>/lib<name>.so inside an APK. [3][4]

Bind class/method identity and loader context to the selected native ABI and
library. A packaged library is not proof it was loaded or its exports called.
Do not equate DEX register numbers with CPU registers or assume every code-bearing
asset follows the standard native-library path. Recover additional dynamic loading
only where evidence supports it.

## Sources and scope

Reviewed 2026-10-08. [Application fundamentals](https://developer.android.com/guide/components/fundamentals)
[1], package/components/manifest purpose; [App Bundles](https://developer.android.com/guide/app-bundle)
[2], device/feature delivery; [DEX format](https://source.android.com/docs/core/runtime/dex-format)
[3], class-data purpose; [Android ABIs](https://developer.android.com/ndk/guides/abis)
[4], Native code in app packages. No release-specific installation defaults or
complete DEX layout assumed. Workflow: playbook-android-native-evidence.
