---
id: reference-native-stack-growth-and-probing
title: Dynamic stack growth, guard regions, and page probing
kind: reference
topics: [stack, stack-growth, guard-page, probing, alloca, vla]
platforms: [windows, linux, macos, android, freebsd]
architectures: [x86, x64, arm, arm64]
---

# Dynamic stack growth, guard regions, and page probing

## Stack allocation and stack growth are separate contracts

Subtracting from a stack pointer reserves an address range according to an ABI or compiler convention; it does not by itself ensure that every intervening page has been made available under the operating system's stack-growth policy. A large single adjustment can skip a guard region on systems that depend on sequential page faults. Whether that creates a stack-clash path depends on the actual mapping layout, guard size, growth rules, probe spacing, and later accesses.

Recover fixed frames, variable-length arrays, `alloca`-style allocations, recursion, signal or exception frames, and nested callbacks separately. A bounded single frame can still participate in aggregate stack exhaustion, while a large frame that faults safely is an availability outcome rather than proof of memory overlap.

## Probes must cover the allocation path before ordinary use

A probe sequence touches stack pages at intervals compatible with the target policy before code relies on the final stack pointer. Inspect the emitted order, spacing, arithmetic, and failure path. One store at the final address does not prove that intermediate guard pages were crossed safely, and one probe before a larger second adjustment does not cover the second range.

Probe code supports stack growth; it is not a bounds check for arrays inside the allocated frame. A properly probed frame can still contain a stack-buffer overflow, and a missing probe does not establish one.

## Microsoft x64 uses a special prologue helper for large fixed allocations

Microsoft documents that an x64 fixed allocation of at least one page uses `__chkstk` before changing `RSP`. The allocation size is passed in `RAX`; the helper probes the range, preserves `RAX`, argument registers, and nonvolatile registers, and may change `R10`, `R11`, and condition codes. The prologue then subtracts the returned unchanged size from `RSP`.

This is a special helper contract, not the ordinary Windows x64 RCX-first call convention. Identify the actual symbol and target architecture; Windows ARM64 and ARM64EC use different stack-checker conventions. Unwind metadata and prologue restrictions also matter when reconstructing a Windows frame.

## GCC stack-clash protection is target dependent

GCC's `-fstack-clash-protection` option allocates stack space one page at a time and accesses each page immediately so an operating-system stack guard cannot be bypassed under supported target behavior. GCC distinguishes this from older generic stack checking and states that most targets do not fully support protection for static frame allocations.

Compiler option presence in metadata is not proof that every relevant function received an adequate sequence. Inspect the concrete prologue and dynamic adjustment, then relate its maximum probe gap to the target operating-system policy. Do not transfer a compiler-version threshold or page size into an unknown binary without evidence.

## Sources and verification scope

Reviewed 2026-10-09 against Microsoft [x64 prolog and epilog](https://learn.microsoft.com/en-us/cpp/build/prolog-and-epilog), Microsoft [x64 stack usage](https://learn.microsoft.com/en-us/cpp/build/stack-usage), and GCC [`-fstack-clash-protection`](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html#index-fstack-clash-protection). These sources define selected compiler and ABI mechanisms; the actual operating-system mapping and guard policy must be established for the investigated target.
