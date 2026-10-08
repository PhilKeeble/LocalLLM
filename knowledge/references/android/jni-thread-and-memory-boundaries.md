---
id: reference-android-jni-boundary-evidence
title: Android JNI binding, strings, arrays, exceptions and callback context
kind: reference
topics: [android, jni, strings, arrays, exceptions, threads, callbacks, ownership]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# Android JNI evidence

## Native binding and transition ABI must match the actual method

Android JNI supports explicit RegisterNatives binding and dynamic native-method
lookup. Its CriticalNative annotation changes the transition ABI and excludes
ordinary JNIEnv/class parameters; support must be established on the target. [1]

Recover declaring class, signature, loader and installed native address before
assigning arguments. Normal JNI conventions are not a template for every fast
entry. Shared type/call facts: reference-jvm-jni-binding-and-calls; its named JDK
extensions are not assumed to be available in Android.

## String and array leases need their own units and release boundary

JNI uses UTF-16 code units and modified UTF-8; ordinary UTF-8 is not automatically
valid modified UTF-8. Array-element access can copy or expose direct storage.
JNI_ABORT cannot undo earlier writes made through a direct array pointer. [1]

Track byte capacity, element count, actual access result and matching release.
Do not infer termination from a pointer type or retain leased storage after
release. JNI_COMMIT of a copy needs a later final release. Shared lifetime facts:
reference-jvm-jni-memory-and-lifetimes, with target/API support retained locally.

## A pending exception does not act like a C++ exception unwinding native code

Android's JNI guidance requires examining pending Java exception state and limits
which JNI operations may run while an exception is pending. [1]

Follow both returned value and exception channel into cleanup and caller-visible
result. Native execution can continue after a JNI call leaves a pending exception;
do not count later code as unreachable merely because the managed operation failed.
Use the actual allowed cleanup contract, not a universal 'all JNI calls are safe'
or 'no cleanup is allowed' rule.

## JNIEnv is thread scoped; retained callbacks need live references

Android documents JNIEnv as thread specific and requires native threads to attach
before JNI calls and detach before exit. Local references on an attached worker
do not automatically expire at every internal work-item boundary. [1]

Bind callback thread, loader, live strong/global reference and teardown. Saving a
local handle or another thread's JNIEnv does not promote it. A live managed wrapper
does not establish the lifetime of a separately owned native allocation. Workflow:
playbook-re-jni-boundary and playbook-android-native-evidence.

## Source and scope

Reviewed 2026-10-08. [Android JNI tips](https://developer.android.com/ndk/guides/jni-tips)
[1], native binding/fast entries, string/array leases, exceptions and thread/local
reference sections. Shared JNI references retain earlier specification review;
no Android private layout, JDK-only function availability or guaranteed string
termination is inferred from an implementation example.
