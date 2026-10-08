---
id: playbook-linux-async-lifetime
title: Recover Linux asynchronous requests, signal effects and terminal ownership
kind: playbook
topics: [linux, asynchronous-io, io-uring, signals, ownership, cancellation, resource-lifetime]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover asynchronous request and resource lifetime

## Identify the request and each resource generation

Preserve ring or queue identity, request generation, selected operation, supplied
buffers, descriptor/object generation and owning thread. Separate prepared,
submitted, running and completed evidence.

Use reference-linux-io-uring-request-lifetime for ring contracts and
reference-linux-descriptors-open-file-descriptions for ordinary references.
Repeated addresses, user_data values or descriptor integers cannot prove the
same request or resource. Missing events limit ownership conclusions; do not
invent a complete history from one completion or a later memory capture.

## Follow every consumer until its actual terminal event

Trace copied submission metadata separately from in-flight data, registrations,
callbacks and output consumption. Retain extent, mutation, release and each
supported final-reader/writer event.

One submission consumed or one CQE observed is not universally final release.
Multishot, notification and registration modes require the actual selected
contract. A backing mapping that remains allocated does not prove an object is
live; apply reference-linux-libc-allocator-identity. Establish the acquire/use/
release relation before reporting a lifetime defect, rather than inferring it
from asynchronous API presence or an unfamiliar mapping.

## Separate cancellation requests from target completion and cleanup

Bind cancellation selector to the original request generation. Preserve cancel
result, target result, terminal flags, retained buffers and cleanup decisions.

Use reference-linux-io-uring-request-lifetime. A cancellation attempt is not
proof the target stopped accessing memory; a not-found result can follow earlier
completion or a wrong selector. Identify the actual terminal condition for the
opcode and mode. Do not release or attribute state in the model merely because
an operation is named cancel or because a request counter reached zero.

## Include signals and process transitions as separate execution edges

For a relevant signal, recover disposition, thread mask, delivery and handler
effect. For fork/exec, identify inherited references/state and successful image
replacement rather than an attempted call.

Apply reference-linux-signals-fork-exec-state. A signal handler can interrupt
partial updates; a multithreaded fork child has copied synchronization state
without every parent thread. These are conditional interpretation limits, not
automatic defect or evasion verdicts. Preserve the observed interleaving and
selected continuation; no new execution is needed to report an unresolved edge.

## Deliver the ownership relation and earliest missing transition

Report resource/request identities, acquisition, consumers, relevant completion,
cancellation, release and supported effect. Keep operation-specific results and
extents with their claims.

An unexplained missing completion may reflect coverage, pending work or a failed
request. State the supported alternative and evidence needed to distinguish it,
without declaring absence or intentional evasion. Shared interleaving validation
remains in the concurrency playbooks; static capability and recorded execution
are separate report statuses.

## Basis and scope

Reviewed 2026-10-08. Focused Linux ring, signal, descriptor and libc references
supply the API facts. No collector default, allocator offsets or universal
completion count is assumed.
