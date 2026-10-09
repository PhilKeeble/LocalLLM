---
id: vulnerability-concurrency-incorrect-memory-ordering-publication
title: Incorrect memory ordering, missing barrier, or publication before initialization
kind: vulnerability
topics: [concurrency, memory-order, barriers, publication, weak-memory]
platforms: [cross-platform]
architectures: [any]
---

# Incorrect memory ordering, missing barrier, or publication before initialization

## Definition and violated invariant

A memory-ordering vulnerability occurs when the synchronization used does not impose an order required between specific accesses for a particular observer. The producer's initialization, ownership or device-descriptor writes must become observable before the publication, doorbell or state that permits the consumer to use them, under the applicable language, compiler, ISA, memory-type and device contracts.

Atomicity, visibility, ordering and completion are different properties. A barrier mnemonic is not sufficient without its access classes, scope and participants, while a correct ordering edge may be supplied by an instruction or API without a standalone fence.

## Conditions that establish the issue

Name the two or more accesses whose order matters, addresses and widths, participating threads, CPUs or devices, memory type, required observer, source-language ordering, emitted instructions, barrier or atomic scope, and the value read. Prove the actual protocol permits the consumer to observe publication without the required prior state and that this reaches a security-relevant effect.

For release/acquire publication, bind the acquire operation to the release sequence on the same atomic object from which it takes its value. For DMA or MMIO, include cache/coherency operations, ownership handoff and I/O ordering separately from CPU-to-CPU shared memory.

## Evidence that is not sufficient

A missing fence instruction, relaxed atomic, ordinary load/store, weakly ordered architecture, barrier import, or rare stale value is not sufficient. Compiler rules, dependencies, locked operations, memory attributes or API contracts may provide the edge, and an apparent stale field may belong to a different generation.

An acquire operation alone does not create a synchronizes-with edge when the observed publication was not a qualifying release on the same object.

## Investigation sequence

Reduce the candidate to concrete producer and consumer events and draw the required order. Recover the source or runtime model, compiler lowering and exact ISA semantics, including qualifiers such as barrier domain and access class. Determine which write the observed atomic value can come from and preserve object lifetime.

For a device, add descriptor writes, cache maintenance, ownership bits, doorbell access, completion and buffer reuse as distinct events. Do not treat an ordering barrier as a wait for arbitrary device completion.

## Constructed AArch64 publication example

Assume `X0` points to a payload, `X3` points to a readiness flag, and the producer uses ordinary cacheable shared memory.

```asm
; producer
str  x1, [x0]          ; initialize payload
str  w2, [x3]          ; publish ready with an ordinary store, not a release store

; consumer
ldar w4, [x3]          ; acquire-load ready
cbz  w4, not_ready
ldr  x5, [x0]          ; consume payload
```

The consumer's `LDAR` supplies acquire semantics, but the shown producer publication is an ordinary `STR`; under a protocol requiring a release/acquire pair, the sequence lacks the matching release edge. This establishes a candidate ordering defect under the stated memory attributes and protocol, not a guarantee that stale payload is observed. Another barrier, dependency or platform API outside the excerpt can change the conclusion.

## Primitive and impact limits

The direct result can be partial or stale state, premature ownership transfer, device use of incomplete descriptors, invalid pointer consumption, or wrong security decision. Impact depends on which invariant the reordered observation violates and whether an attacker can influence timing or contents.

## Related knowledge and primary sources

`reference-concurrency-memory-order-atomic-invariants` and `architecture-memory-ordering-barrier-evidence` define language, compiler, ISA and device layers. This profile repeats the exact-access, exact-observer and exact-edge proof locally.

Reviewed 2026-10-09 against the C++ [atomic ordering rules](https://eel.is/c++draft/atomics.order), Linux kernel [memory-barrier documentation](https://docs.kernel.org/core-api/wrappers/memory-barriers.html), and Arm [memory systems and ordering guidance](https://developer.arm.com/documentation/102336/latest/). The assembly is constructed and does not assert a universal AArch64 lowering.
