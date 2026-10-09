---
id: vulnerability-type-jit-generated-code-metadata-inconsistency
title: JIT, deoptimization, stack-map, or generated-code metadata inconsistency
kind: vulnerability
topics: [jit, deoptimization, stack-maps, garbage-collection, generated-code, type-confusion]
platforms: [cross-platform]
architectures: [any]
---

# JIT, deoptimization, stack-map, or generated-code metadata inconsistency

## Definition and violated invariant

A generated-code metadata vulnerability occurs when executable code and the runtime metadata used to interpret, relocate, invalidate, unwind, patch, or reconstruct its state disagree. At every transition point, the runtime must bind the active code version and program counter to metadata that correctly describes each required value's location, width, representation, object relation, and continuation state.

Optimized code legitimately omits source variables, changes representations, inlines calls, and reconstructs values during deoptimization. An unfamiliar frame or missing source-like value is not itself inconsistency.

## Conditions that establish the issue

Identify the runtime, active generated-code range and version, exact transition PC, metadata record selected for that PC, machine state before the transition, and state consumed afterward. Prove the selected record describes a required value or continuation incompatibly with the code that produced it and that a reachable deoptimization, safepoint, garbage collection, exception, patch, or on-stack replacement consumes the disagreement.

For moving collection, distinguish a live base reference, a derived interior reference, and a stale pre-relocation address. For deoptimization, account for inlined frames, constants, eliminated values, unboxed values, and side effects that occurred before fallback.

## Evidence that is not sufficient

A deoptimization event, stack-map section, executable private mapping, internal entry point, changed native address, absent ordinary prologue, or value that is not visible in the native frame is not sufficient. These are normal properties of many runtimes.

Metadata from another code version or build cannot establish the live contract. A crash at a safepoint does not by itself identify whether the defect is in application data, runtime metadata, generated code, collector behavior, or analysis symbolization.

## Investigation sequence

Freeze the runtime and code identity at the observation time, then map the transition PC to the exact metadata entry. Reconstruct each live value from the stated register, stack slot, constant, or recovery expression and compare its representation with the producer instructions and its next consumer.

Trace invalidation and transition ordering, including code replacement and address reuse. For a relocation issue, verify which pointer copies the collector can see and which post-safepoint uses consume relocated values. For a deoptimization issue, compare the reconstructed logical frames and resume point with already-completed side effects.

## Constructed x86-64 example

```asm
mov  dword ptr [rsp+28h], eax  ; store an unboxed 32-bit integer in a spill slot
cmp  eax, 1000
ja   deopt_entry               ; transition at the metadata-covered PC
```

Assume the selected deoptimization record describes `[RSP+28h]` as a full-width tagged object reference and reconstructs an object-valued local from it. The code and record then disagree about both width and representation; stale upper bytes can also enter the reconstructed value because the shown store writes only four bytes of memory. The finding still requires proof that this record belongs to this code version and transition PC and that reconstruction consumes the slot as stated.

## Primitive and impact limits

The direct result can be wrong-type state reconstruction, stale-reference use, missed or incorrect relocation, unintended control flow, repeated effects, or invalid memory access. Impact depends on the affected value, transition reachability, runtime validation, and whether attacker-influenced execution can create the required state.

## Related knowledge and primary sources

`reference-jit-deoptimization-gc-state`, `reference-jit-guards-specialization`, and `reference-jit-code-identity` define the surrounding mechanisms. This profile repeats the required code-version, PC, representation, and consumer binding locally.

Reviewed 2026-10-09 against LLVM [stack maps and patch points](https://llvm.org/docs/StackMaps.html), LLVM [garbage-collection statepoints](https://llvm.org/docs/Statepoints.html), and V8's [Maglev deoptimization model](https://v8.dev/blog/maglev). The assembly and metadata disagreement are constructed and do not describe a specific runtime layout.
