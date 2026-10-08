---
id: playbook-re-go-boundary
title: Recover Go value, goroutine and native boundaries in a binary investigation
kind: playbook
topics: [go, reverse-engineering, data-flow, goroutines, cgo, vulnerability-analysis, malware-analysis]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm, arm64, riscv64]
---

# Recover a Go operation from input to effect

## Scope and required evidence

Reviewed 2026-10-02. Use for vulnerability analysis or malware behavior recovery
in Go application logic, concurrent work or native boundaries. The output is an input-to-effect
argument with explicit identities and invariants, not a list of suspicious
runtime helpers. Preserve the original artifact and distinguish static evidence,
documented contracts and independently available runtime observations.

An invariant is a condition that must hold, such as a count staying within a
buffer or an operation using the authorized identity. A sink is the operation
that consumes a value, such as a copy, file write, process launch or network send.

## Establish artifact and call coordinates

Recover executable architecture, build metadata, compiler identity, module
information and available function/line tables. Match file and loaded address
bases. Inspect actual call sites and wrappers before assigning prototypes;
record receiver, composite components and all return values. Distinguish runtime
infrastructure from application code even when symbols are missing.

Factual home: reference-go-binary-runtime-evidence. If the toolchain or private
layout remains unknown, carry that uncertainty into the reconstruction instead
of fixing every object to a guessed current runtime layout.

## Follow the value actually consumed

For each controlled field, record origin, type, width, unit, conversions, checks
and final consumer. For slices, distinguish the header from backing storage and
enumerate aliases that can change it. For interfaces, resolve dynamic type,
nil state and effective method. For strings, preserve raw bytes alongside any
decoded or normalized representation.

Question the exact invariant: authorized identity, complete message, bounded
count or immutable validated value. A bounds-safe access can still use the wrong
message, identity or resource. Factual home: reference-go-values-and-aliasing.

## Separate malware capability from executed behavior

Recover the path from entry or callback through configuration, decoding and
dispatch to the relevant effect. Distinguish a retained library routine from an
application call, an embedded endpoint from a used destination, and a decoded
command from one actually dispatched. Preserve branch conditions, arguments,
caller authority and any required external response.

For suspected collection, process execution, persistence or network transfer,
identify the concrete resource and data involved. Do not infer maliciousness
from Go runtime size, goroutine creation, cgo presence or error recovery alone.
Report static capability, reachable behavior and observed execution separately;
intent and deployment context can remain unresolved. Never execute an unknown
sample merely to complete the behavior description.

## Build an operation timeline across goroutines

Identify creation, queueing, matching communication, cancellation observation,
callback completion and final release. Assign logical operation identities
instead of using thread IDs or recycled addresses as proof of continuity.
For a claimed synchronization edge, name the actual events and the state they
order. For a claimed race, identify conflicting accesses and missing ordering.

Trace both ready branches of cancellation-versus-work selection. Determine
whether the consumer receives a snapshot or a shared view and whether shutdown
excludes new work. Factual home: reference-go-concurrency-and-unwind.

## Join Go ownership with the native contract

At each native transition, identify effective ABI, converted representation,
allocator, initialized extent, retention permissions and callback path. Follow
both ordinary failure and successful submission with delayed completion.
Distinguish rooting, pinning, native allocation and opaque-token retention.

A complete lifetime argument identifies the final user and exactly when the
relevant lease ends. Do not infer that cancellation, wrapper return or garbage
collection closes a native ownership obligation. Factual home:
reference-go-cgo-and-unsafe.

## Reconstruct failure, cleanup and observable outcome

Follow returned errors, panic unwinding, recovery, deferred mutations and process
termination separately. Determine which external effects preceded failure and
which cleanup operations really execute on that path. A caught panic does not
itself prove rollback, and a crash does not itself prove memory corruption.

Compare counterevidence: rejected input, an independent copy, a correctly bounded
view, synchronization covering every borrower, or an unreachable native call.
Report the smallest supported violated invariant and security consequence.
Unresolved reachability, runtime behavior or resource ownership remains a stated
gap, not an assumed exploit or a requirement to alter a shared running service.
