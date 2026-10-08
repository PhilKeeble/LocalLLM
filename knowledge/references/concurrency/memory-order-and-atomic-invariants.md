---
id: reference-concurrency-memory-order-atomic-invariants
title: Data races, publication, memory ordering and atomic invariants
kind: reference
topics: [concurrency, atomics, memory-order, data-races, reverse-engineering]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Data races, publication, memory ordering and atomic invariants

## Scope and evidence layers
Reviewed 2026-10-02. C++ rules below concern the language abstract machine;
Linux kernel primitives use the kernel memory model, not automatically the
C++ model. A binary investigation must separately identify compiler lowering,
executed instruction semantics, memory type and inter-thread protocol. The
absence of a standalone fence instruction does not establish absent ordering:
ordering can come from an instruction, an API or the target architecture.
Conversely, a fence import or mnemonic does not establish the required protocol.
Examples here are constructed, not observed vulnerabilities.

## Data race versus logical race
For ordinary C++ threads, conflicting accesses with at least one non-atomic
access and no happens-before ordering constitute a data race; this is undefined
behavior, not merely a choice between two intuitive results. Conflicts include
overlapping lifetime changes, not only two assignments. Signal handlers have
additional rules. [1]

A logical race can exist with every access properly synchronized. Constructed
example: two clients each lock, observe one remaining reservation, unlock, then
each lock and allocate a reservation without rechecking. No unsynchronized
memory access is needed to exceed the quota. Distinguish the broken operation
invariant from a language data race; a data-race detector is not a logical
transaction verifier. In a binary, preserve actual accesses and synchronization
edges rather than reconstructing a racy source expression as a reliable model.

## Observed race reports and clean runs have different evidence limits

ThreadSanitizer reports conflicting accesses under its observed synchronization
model; missing instrumentation can hide accesses or synchronization. Preserve
the two sites, actual object and ordering evidence rather than interpreting only
the top stack frame. A clean exercised path does not establish that every schedule
is safe. A compound quota check/update can be logically incorrect even when
each individual access is locked. Detector contracts live in
reference-validation-tsan-race-evidence.

For binary investigations, connect reported sites to matching machine code and
the target's actual synchronization contract. A report from a modified diagnostic
build does not establish identical timing or layout in the shipped executable.
This distinction supports vulnerability classification without calling ordinary
threading primitives evidence of malicious intent.

## Release and acquire publication
In C++, an acquire operation that reads from a release operation (or its qualifying
release sequence) on the same atomic object establishes synchronization. Relaxed
atomicity alone does not publish surrounding non-atomic state. [2]

Constructed one-shot example: producer initializes payload, then release-stores
ready=true; consumer acquire-loads that published true before reading payload.
This covers prior initialization only under the stated matching and lifetime
conditions. An acquire load that observes the old false value provides no such
edge. Reusing ready=true for a new payload, or mutating payload after publication,
requires another valid protocol. A pointer's visibility is not its lifetime,
and an acquire operation on a different unrelated flag is not evidence of a
matching release. Record which write the observed value can come from.

## Atomic fields do not create a compound transaction
C++ sequentially consistent atomics constrain ordering but do not make several
operations one indivisible transaction. [2] Constructed example: two threads
each load available=1, then each decrement and grant access. Even sequentially
consistent loads and decrements permit both grants if no successful conditional
reservation binds the check to the update. Separate atomic pointer and length
loads can likewise produce a pair from different logical updates.

For investigation, state the compound invariant (pointer/extent, balance/charge,
owner/generation), identify its commit point, and test whether all competing paths
participate. A mutex around each field separately does not necessarily protect
the pair. An atomic snapshot of metadata still does not freeze the referenced
payload or prevent its reclamation.

## Compare-exchange retry semantics
C++ compare_exchange (compare-and-exchange, CAS) conditionally replaces an atomic
value when it matches the expected representation. It updates expected on failure;
weak compare-exchange may
fail even when the compared representations match. Success is a read-modify-write;
failure is a load, with its own ordering requirements. [3] A failed weak CAS
does not by itself prove another thread modified the object.

In a retry loop, recover the value used to recompute desired after each failure.
Check whether retries repeat a charge, free, callback or other non-repeatable
side effect. On success, distinguish the replaced value from the new value.
Check the actual success/failure memory orders and the applicable language or
OS primitive; do not infer them solely from a decompiler's generic CAS name.
Successful equality comparison does not prove intervening history was unchanged;
see reference-concurrency-refcounts-reuse for ABA and lifetime evidence.

## Linux barrier(), READ_ONCE and WRITE_ONCE are not general CPU barriers
Linux barrier() constrains compiler transformations; it is not a general CPU
memory barrier. READ_ONCE/WRITE_ONCE constrain specified accesses and related
transformations but are not universal release/acquire or full-barrier substitutes.
Kernel read, write, general and dependency barriers have different guarantees;
the kernel guide explicitly is not a complete hardware specification. [4]

For binary analysis, separate normal shared memory from MMIO, DMA and cache
maintenance. Recover access width, alignment, memory attributes, participating
CPUs/devices and the exact synchronization API. A protocol demonstrated on one
CPU or under a debugger does not prove portability to weaker ordering. A proposed
hardware reorder must be permitted by the target ISA and memory type, not merely
by a generic statement that processors reorder accesses.

## Primary sources
Reviewed 2026-10-02: living C++ draft clauses; Linux kernel documentation as served.
Target compiler/language edition and kernel/ISA versions still require matching.

1. [C++ data races and happens-before](https://eel.is/c++draft/intro.races).
2. [C++ atomic order and consistency](https://eel.is/c++draft/atomics.order).
3. [C++ atomic operations and compare-exchange](https://eel.is/c++draft/atomics.types.operations).
4. [Linux kernel memory barriers](https://docs.kernel.org/core-api/wrappers/memory-barriers.html).
