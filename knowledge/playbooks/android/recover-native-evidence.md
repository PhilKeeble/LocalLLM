---
id: playbook-android-native-evidence
title: Recover Android code identity, JNI, shared storage and crash evidence
kind: playbook
topics: [android, native-code, art, jni, shared-memory, crash-analysis, investigation]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# Android native-boundary investigation

## Bind available code to the device and execution representation

Record APK/splits, selected native ABI, DEX/loader identity and actual mapped
image. Distinguish interpreted, JIT and AOT paths and incomplete collection.
A library in an archive or a profile entry does not prove a particular invocation.
Use reference-android-package-entry-evidence and reference-android-art-code-evidence.

## Reconstruct the managed/native transition before its consumer

Recover the bound JNI method, transition ABI, input units, actual thread's JNIEnv
and exception state. Follow callback references, borrowed storage and native
owners through registration, cancellation and teardown. A managed wrapper or
strong reference does not own unrelated native memory.

Use reference-android-jni-boundary-evidence and playbook-re-jni-boundary.
Named newer JDK functions are not assumed available in Android; retain actual
target/API support when consulting the shared JNI references.

## Recover stable bytes and independent mapping lifetimes

Identify passed descriptor, backing object, mapping offsets/extents and writers.
Separate future mapping restrictions, existing mapping permissions and content
immutability. Track descriptors, mappings and async users through final use.
Use reference-android-shared-memory-lifetime. A read-only view cannot certify
another process has no writable alias.

## Interpret a crash under its collection and mitigation scope

Bind tombstone, faulting/detecting thread, build ID, matching symbols and address
coordinate. Determine actual MTE mode where relevant and retain imprecise fault
location as such. Use reference-android-native-crash-evidence. A crash or source
line alone does not establish controlled input or the original bad access.

## Report object, path and effect separately

State the supported input-to-consumer relation, violated extent/lifetime rule and
observed failure, with unresolved code/owner/mapping evidence explicit. Native
libraries and runtime helpers establish neither malicious intent nor sandbox
escape by themselves. Policy evidence belongs in playbook-android-service-authority.

Reviewed 2026-10-08 against linked reference contracts. No target execution,
release-specific decoder, fixed private offsets or exploitation procedure.
