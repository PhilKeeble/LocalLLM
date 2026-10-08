---
id: playbook-re-windows-heap-allocation
title: Identify a Windows allocator and trace a heap defect without confusing diagnostic evidence
kind: playbook
topics: [heap, allocator-identification, ownership, heap-corruption, pageheap, reverse-engineering]
platforms: [windows]
architectures: [x86, x64, arm, arm64]
---
# Investigate a Windows heap candidate

## Establish allocator identity before parsing private metadata

Record executable and loaded runtime identities, OS build, process architecture,
manifest, diagnostic configuration and dump coverage. Follow allocator wrappers
to the actual allocation mechanism and heap instance. Distinguish CRT user
pointers, direct Win32 blocks, custom arena suballocations and virtual-memory
regions. Use reference-windows-heap-identity-diagnostics for sourced facts.

Use allocator-aware evidence and matching symbols or recovered implementation
details to interpret the captured state. Record uncertainty when implementation
identity, decoder support or captured memory is insufficient. Do not decode a
segment-heap block with an NT-heap offset table
or infer backend identity from the word "segment". Historical metadata layouts
need the matching runtime build; a library signature is only attribution evidence.

## Build an allocation-generation and extent record

For each candidate, record heap/allocator identity, returned base, wrapper offset,
requested bytes, application capacity, initialized payload, allocation generation,
owners, aliases and release contract. Trace resizing as a transition: old extent,
result, new extent and every alias update. Record inherited and per-call flags.
API facts live in reference-windows-heap-allocation-contracts.
Use playbook-validation-allocation-lifetime-trace for invocation/result pairing,
ownership handoffs and incomplete or cross-thread event history.

Check integer width, count-to-byte conversion, header/trailer sizing and actual
access width. Constructed example: a 64-byte heap block containing a 20-byte
message permits neither a 64-byte disclosure nor arbitrary access beyond an
embedded field. A diagnostic's containing allocation is not the innermost object
bound. Do not replace application payload length with an allocator size query.

## Prove the violated invariant on a feasible path

For UAF/double free, establish the same allocation generation, release and later
use; address equality after reuse is insufficient. For wrong-heap release,
recover the allocating and freeing instances rather than merely different DLL
names. For resize failure, check owner retention and metadata rollback. For
concurrency, show what prevents reclamation between lookup and dereference.

Separate overwrite, disclosure, leak, resource-exhaustion and false-positive
explanations. A heap crash does not prove the allocator caused the first invalid
operation. Follow the faulting operand backward and compare earlier writes,
allocation stacks, free stacks and application state. Repeated release sites
on mutually exclusive paths are not a double free.

## Use diagnostics without treating them as production behavior

Prefer existing dumps/traces first. If additional instrumentation is authorized,
use an isolated test instance, record the baseline and all settings, and preserve
the earliest diagnostic with its parameters. Select checks supported by the
actual allocator/tool build. Do not change shared services or globally enable
heap diagnostics as an incidental analysis step.

Use reference-windows-heap-identity-diagnostics for PageHeap persistence and
launch-time scope. Keep instrumented and uninstrumented observations separate:
a changed crash site can improve detection without reproducing original layout.
Passing validation cannot establish application ownership. Missing allocation
history, incomplete dumps or unsupported heap decoding remain evidence gaps.

## Minimum result and sufficiency check

Deliver the target/build scope, allocator provenance, relevant API contract,
allocation-generation trace, requested/object/initialized ranges, exact failing
instruction or branch, reproducer limits and remaining uncertainty. Distinguish
demonstrated memory-safety impact from untested exploitability.

Ask whether a reviewer can reconstruct why this access or release is invalid
without assuming a universal Windows heap layout. If a diagnosis depends on a
private field, include its verified build-specific meaning and decoding evidence.
If only allocator corruption is observed, report that limited result; do not
invent the prior writer. This workflow is a constructed investigation method,
reviewed 2026-10-02, not a vulnerability reproduction.

## Primary-source basis

Reviewed 2026-10-02. The two reference IDs above retain the scoped offline facts;
the workflow applies them without claiming a target finding.

- [HeapReAlloc](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heaprealloc): resize result and ownership transitions.
- [HeapSize](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heapsize): known-heap precondition and size contract.
- [WinDbg !heap](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-heap): allocator-specific diagnostic capabilities.
- [GFlags and PageHeap](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/gflags-and-pageheap): instrumentation mode, persistence and launch boundary.
