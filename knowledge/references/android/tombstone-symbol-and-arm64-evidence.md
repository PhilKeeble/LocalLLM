---
id: reference-android-native-crash-evidence
title: Android tombstones, build identity, symbols and ARM64 diagnostic limits
kind: reference
topics: [android, tombstones, native-crashes, build-id, symbols, arm64, mte]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# Android native crash interpretation

## A tombstone is a crash-time observation with scoped coverage

Android tombstones can include signal/fault details, registers, thread backtraces
and memory mappings. Available fields depend on collection and target support.
[1]

Bind process/thread, collection time, architecture and faulting operation.
A stack ending in abort can report a deliberate failure rather than the original
bad access. A crash is evidence of failure on that path; it does not alone prove
attacker control, unauthorized effects or reliable exploitation.

## Build IDs help bind symbols to the actual mapped image

Android crash documentation uses a mapped image's BuildId, when present, to
identify the relevant code build. [1]

Match the actual image/debug artifact and address coordinate before accepting a
symbol or source line. Filename equality is insufficient; absent IDs remain a
gap requiring other identity evidence. A correct symbol does not certify a
decompiler prototype, and optimized/inlined frames need their own interpretation.
Do not subtract an arbitrary mapping start as a universal file-offset conversion.

## Asynchronous memory-tagging reports need different fault-site reasoning

For supported ARM memory tagging (MTE), Android distinguishes synchronous faults
from asynchronous reports. An asynchronous report's stack describes detection
rather than necessarily the original invalid access, and lacks a precise fault
address. [2]

Record actual mode and signal information before attributing a line to the bug.
Do not apply MTE interpretation to every ARM64 crash or confuse memory tags with
pointer authentication. A nearby suspect access remains an inference until its
object, extent and lifetime evidence supports it.

## Sources and scope

Reviewed 2026-10-08. [Diagnose native crashes](https://source.android.com/docs/core/tests/debug/native-crash)
[1], dump fields and Read tombstones/BuildId; [MTE reports](https://source.android.com/docs/security/test/memory-safety/mte-reports?hl=en)
[2], sync/async distinction. No tombstone retention count, required release,
universal pointer mask or target execution claimed. Workflow: playbook-android-native-evidence.
