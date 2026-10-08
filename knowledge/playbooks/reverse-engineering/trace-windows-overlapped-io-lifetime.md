---
id: playbook-re-windows-overlapped-io-lifetime
title: Trace Windows asynchronous I/O from issue through notification and final release
kind: playbook
topics: [reverse-engineering, windows, overlapped-io, iocp, cancellation, lifetime, validation]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Trace Windows asynchronous I/O from issue through notification and final release

## Recover the actual handle and completion mechanism

Scope: authorized user-mode Windows binary investigation; reviewed 2026-10-02.
Record build, architecture, wrapper/API, object type and successful handle-creation
flags. Follow IOCP association, notification-mode calls, OVERLAPPED hEvent and
thread-pool registrations. For completion routines, identify issuing thread and
alertable waits. Do not classify asynchronous behavior from a pointer parameter
or a function name alone.

Deliver a per-handle/per-operation map: issue API, request identity, buffer,
notification path, completion decoder, cancellation selector and cleanup owner.
Separate file handle, port handle, TP_IO, callback context and enclosing object.
Use `reference-windows-overlapped-io-lifetime-cancellation`,
`reference-windows-iocp-packets-notification` and
`reference-windows-threadpool-alertable-io` for API-specific facts.
[Win32 overlapped request structure](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped).

## Classify all submission branches before counting terminal paths

For each Windows I/O issue, preserve return value and immediately relevant error.
Separate immediate success, accepted pending and API-specific error/partial-data
paths. Recover skip-on-success and hEvent-low-bit settings before predicting a
later packet. Match StartThreadpoolIo and its applicable balancing paths; a
FALSE return with ERROR_IO_PENDING is not a no-notification issue failure.

Constructed candidate: an immediate-success branch frees a request, then a
normally enabled completion packet dispatches through it. This becomes a finding
only with evidence that this operation emits that packet, that the freed record
is still referenced, and that no retention/discrimination prevents the use.
Conversely, a skipped callback can leak or stall shutdown if bookkeeping still
waits for it. Neither candidate is established merely by two cleanup functions.

## Decode packets and counts before trusting a reconstructed request pointer

For GetQueuedCompletionStatus, distinguish FALSE/NULL no-packet from FALSE/non-NULL
failed I/O; the latter still carries work to retire. Inventory PostQueuedCompletionStatus
producers before dereferencing pointers or applying container offsets. For Ex
batch dequeue, use the returned entry count and each operation's status. Keep
ULONG_PTR completion keys at target width.

Trace operation-specific count semantics into parsing, copying and retries. A
connection notification is not a received message; allocation capacity is not
initialized length. Preserve evidence linking key, request generation, buffer
and owner. If one structure is reused, establish the last old notification/use
before interpreting a new completion as belonging to the same logical request.
Use `reference-windows-iocp-packets-notification` for genuine versus posted packets.

## Prove cancellation, notification and ownership on the same schedule

For Windows timeout/shutdown candidates, name the issuing and canceling threads,
handle and optional OVERLAPPED selector. CancelIo cannot cancel another thread's
requests; CancelIoEx does not block future submissions. A synchronous-cancel
thread target can advance to another request. Record ordinary completion,
aborted completion and other failure outcomes, not just cancel-function success.

For every resource, identify allocation/retention, last required use and release.
Distinguish underlying I/O from queued/running callbacks and delegated work.
CancelThreadpoolIo and canceled queued callbacks do not stop underlying I/O.
Inspect DisassociateCurrentThreadFromCallback before treating a callback wait
as proof of actual return. Apply
`reference-concurrency-cancellation-completion-shutdown` to the resulting schedule.

## Check shutdown admission, dependency cycles and exactly-once effects

For the Windows target, prove new submissions cannot race past the intended
shutdown boundary. Then account for already accepted requests and all notification
variants. Check waits against callback lock/owner dependencies, APC reentrancy,
and workers that create more work. Closing a port or posting a sentinel is not
by itself a drain proof.

Retain evidence for the one-time terminal effect and for the lifetime of losing
paths. A CAS that picks one releaser does not protect another path that accesses
freed state before its CAS. Check stale completion routing into a reconnected
owner/generation as well as double release. These are investigative obligations,
not a universal shutdown sequence to impose without reading the chosen API.

## Preserve the evidence for each relevant completion path

Compare recovered pending, immediate-success, failure and partial-transfer paths
under the actual notification configuration. Include delayed callbacks, request
reuse and concurrent shutdown when they can affect the proposed violation.
Record the instruction/API evidence for each event and ordering constraint;
distinguish proved paths, unresolved assumptions and observed executions.

If separately authorized runtime observations supplement the analysis, retain
their isolation, inputs, initial state and scheduling/instrumentation limits.
Changing a working service or host-wide I/O settings changes the analyzed
conditions and is not a prerequisite for using this workflow.

Application-posted packets and empty-port timeouts do not establish actual
device completion, CancelIoEx races, thread-pool drains or vulnerability
reachability. A final finding needs same-request identity, the violated buffer/ownership/state invariant,
feasible ordering, observed or statically proved effect and counterevidence.
Keep completion-mechanism evidence separate from claims of exploitable impact.
