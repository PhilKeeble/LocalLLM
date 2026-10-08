---
id: reference-jit-deoptimization-gc-state
title: JIT deoptimization, on-stack replacement, reconstructed frames and GC relocation
kind: reference
topics: [jit, deoptimization, on-stack-replacement, safepoints, garbage-collection, stack-maps]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---
# JIT execution-state transitions

## Deoptimization reconstructs continuation state, not a transaction rollback

V8's Wasm deoptimizer saves optimized register/stack state, translates it into
baseline state and resumes at the corresponding continuation. Earlier side
effects cannot simply be undone; restarting the function would repeat them.
An optimized frame may become multiple baseline frames after inlining. [1]

For an error or state-corruption investigation, locate the deopt point and the
values required after it. Distinguish a valid fallback from a wrong continuation,
lost value or repeated effect. A deopt log proves a transition was reported, not
that application state rolled back or that a security boundary was violated.

## Deoptimization metadata supplies values absent from source-like disassembly

Maglev associates deoptimization points with abstract interpreter frame state.
Generated metadata maps optimized values into the interpreter state required
when optimization assumptions fail. Optimized values may be unboxed rather than
stored as ordinary language-level objects. [2]

Do not read every native stack word as a source variable or heap pointer. Identify
the active code version, metadata entry and representation of each reconstructed
value. An apparent missing source local may have been constant-folded, held in a
register or reconstructed; it is not automatically uninitialized storage.

## On-stack replacement can change code while a function invocation continues

On-stack replacement (OSR) changes the implementation of an active invocation.
V8's Sparkplug account describes transitions involving hot loops and compatible
interpreter/baseline frames. Its native-PC to bytecode-offset mapping is distinct
from an interpreter's stored current bytecode offset. [3]

A method need not return and be called again before its executing native body
changes. Tie a breakpoint or crash address to the code version active at that
time, including any OSR entry. Do not identify a missing conventional prologue
at an internal transition target as proof of shellcode or corrupted control flow.

## An inlined Wasm call can become guarded arithmetic instead of a call

V8's 2025 Wasm optimization description shows indirect-call inlining, target and
instance checks, and deoptimization when a specialization no longer applies. [1]

For behavior recovery, absence of a native CALL instruction does not establish
that the source/Wasm callee's effect is absent. Recover inlined operations and
their guards. Instance context matters: two functions with similar instructions
may use different globals, memories or imports. Do not turn this historical V8
implementation's exact check sequence into a universal Wasm engine requirement.

## GC safepoints and relocation are separate from application ownership

LLVM's statepoint model describes locations where a collector can identify live
references and relocate objects. It records live pointers and their associated
allocations; gc.relocate provides the post-safepoint pointer. A moving collector
can change the address while preserving source-level object identity. [4]

For a pointer used across a runtime call, establish whether movement is possible
and how the reference is updated or protected. A register preserved by the native
ABI does not make its old heap address valid. Conversely, an address change does
not establish object replacement or a use-after-free. A GC root keeps an object
reachable; pinning prevents movement for its specified duration. Establish the
target runtime's actual mechanism rather than treating either as ownership policy.

## GC barriers and state maps are not generic authorization checks

LLVM distinguishes collector load/store barriers from safepoints and describes
metadata for base/derived pointers at statepoints. Exact requirements depend on
the collector. [4] A derived pointer is computed from an allocation's base, for
example to address an interior field.

When reversing a small helper around a field store, identify its actual runtime
role before calling it a bounds or permission check. Missing visible helper calls
do not prove a missing barrier: inspect inlined/conditional handling and collector
requirements. A plausible collector helper alone does not prove correct lifetime,
object bounds or application synchronization.

## Primary sources and scope

Reviewed 2026-10-02. These sources explain distinct implementation mechanisms;
not every JIT uses LLVM statepoints, V8 frame layouts or the same deoptimization
target. Statepoint/stack-map layouts require the generating compiler's contract.

1. [V8 Wasm speculative optimization](https://v8.dev/blog/wasm-speculative-optimizations), 2025-06-24: inlining checks, frame translation and preserved side effects.
2. [V8 Maglev](https://v8.dev/blog/maglev), 2023-12-05: deoptimization metadata and value representations.
3. [V8 Sparkplug](https://v8.dev/blog/sparkplug), 2021: interpreter-compatible frames, OSR and address mapping.
4. [LLVM garbage-collection statepoints](https://llvm.org/docs/Statepoints.html): relocation model, barriers and base/derived references; living documentation.
