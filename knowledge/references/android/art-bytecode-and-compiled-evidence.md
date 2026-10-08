---
id: reference-android-art-code-evidence
title: ART bytecode, interpreted code, JIT and compiled-artifact evidence
kind: reference
topics: [android, art, dex, jit, aot, bytecode, code-identity]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# ART representation and execution evidence

## DEX register semantics are distinct from machine registers

The Dalvik bytecode model is register based. Bit-value registers are 32 bits and
wide values use adjacent register pairs; object-reference registers hold a
reference. Instruction formats use 16-bit code units. [1][2]

Recover method registers, instruction width and reference/value role from the
applicable bytecode format. A decompiler temporary or register pair does not prove
a CPU argument location or live object address. Bound instruction/payload decoding
to the selected method and format rather than treating every aligned word as code.

## ART can execute interpreted, JIT-compiled or AOT-compiled methods

ART executes DEX; its documented execution model includes interpretation,
just-in-time (JIT) and ahead-of-time (AOT) compilation. JIT and AOT outputs can
differ, and an .oat artifact need not contain compiled code for every method. [3][4]

Bind artifact, DEX/class loader, method and runtime state to the investigation.
An absent machine-code body does not prove the method is unreachable. A compiled
cache or profile also does not prove a particular invocation executed it.
No fixed OAT/VDEX header or private runtime-object layout is assumed.

## A collected code snapshot does not certify complete execution history

AOSP's JIT workflow notes that code-cache/profile collection can omit methods
and that memory pressure can discard data. [4]

Recover the observation interval, collector and artifact identity before using
absence as evidence. Optimized/inlined or regenerated code requires a supported
mapping back to the relevant method; address resemblance alone is insufficient.
Runtime helper calls can implement dispatch or lifetime work rather than the
sample's application behavior. Preserve unresolved edges.

## Sources and scope

Reviewed 2026-10-08. [Dalvik bytecode](https://source.android.com/docs/core/runtime/dalvik-bytecode)
[1], General design; [instruction formats](https://source.android.com/docs/core/runtime/instruction-formats)
[2], code units; [ART overview](https://source.android.com/docs/core/runtime)
[3], DEX runtime purpose; [ART JIT](https://source.android.com/docs/core/runtime/jit-compiler)
[4], execution states and collection limits. No compilation-filter defaults,
private offsets or required OS release adopted. Workflow: playbook-android-native-evidence.
