---
id: reference-concurrency-cancellation-completion-shutdown
title: Cancellation, late completion, shutdown and reconnect lifetimes
kind: reference
topics: [concurrency, cancellation, completion, shutdown, callbacks, lifetime]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Cancellation, late completion, shutdown and reconnect lifetimes

## Scope and distinct events
Reviewed 2026-10-02. General statements here are investigation obligations;
specific API facts concern Windows CancelIoEx. Separate request acceptance,
execution, cancellation request, terminal I/O result, completion delivery,
callback return and final resource release. APIs can combine some events but
must document that guarantee. A request is not necessarily quiescent merely
because its caller timed out, a cancel function returned or an owner was closed.

Track independently the lifetime of request object, transfer buffer, callback
context, completion queue and session/owner. A live request reference does not
necessarily retain the callback's owner or nested payload buffer.

## Windows CancelIoEx does not wait for completion
CancelIoEx requests cancellation of matching outstanding I/O; it does not wait
for canceled operations to finish. The ultimate result can be normal completion,
cancellation or another error. A successful return is not completed cancellation.
The associated OVERLAPPED must not be freed or reused until I/O completion.
ERROR_NOT_FOUND means no matching request was found, not proof that every callback
using the context has returned. [1]

For Windows investigation, identify how this operation reports completion and
which code owns cleanup. An I/O-completed indication can still be followed by
application-level work using the owner. Check that buffer and owner retention
cover their respective last uses; do not assume all pending I/O APIs have
identical notification or synchronous-completion behavior.
For Win32 issue/notification selection and callback accounting, use
`reference-windows-overlapped-io-lifetime-cancellation`,
`reference-windows-iocp-packets-notification` and
`reference-windows-threadpool-alertable-io`.

## Duplicate and late terminal paths
Constructed race: timeout path marks request failed and frees context; completion
path later uses the context or releases it again. Another variant permits both
paths to send a response or debit a balance. Evidence needs the same request
identity/generation and both feasible paths, not two unrelated frees in a listing.

Recover a terminal-state transition that chooses one owner for each one-time
effect, plus lifetime protection for paths that lose the transition. A successful
CAS selecting the cleanup winner does not protect a loser that dereferences
already freed state to perform that CAS. Repeated completion may instead be an
intentional progress notification; determine terminal versus nonterminal contract.

## Shutdown and queued work
Constructed shutdown obligation: prevent new admissions, account for already
accepted work, request stop/cancel where supported, establish the required
quiescence, then reclaim dependent state. These are logical requirements, not
one universal API sequence; holding locks while waiting can deadlock workers.

Queue-empty does not necessarily mean no in-flight worker or nested callback.
Unregistering a callback may prevent future dispatch without draining callbacks
already running, depending on the API. Trace admission concurrent with shutdown,
dequeued work, timers, callback-generated work and final release. A worker join
is useful only for work whose execution/lifetime it actually covers.

## Reconnect and stale session completions
Constructed example: request R belongs to session generation 7; disconnect
releases that session; reconnect creates generation 8 in the same slot; R's
late completion updates the slot without checking generation and affects the
new client's state. The slot/address being valid does not prove correct binding.

Record the session/object token captured at submission, how callbacks resolve
it, and the commit-time generation/ownership check. Check counter wrap/reset,
identifier reuse and whether retained references intentionally keep the old
session alive. A retained old object may make memory access valid while a
global current-session lookup still routes the result to the wrong client.
For retained partial messages, input buffers and parser reset, use
reference-parser-stream-recovery-limits and playbook-re-incremental-parser-state.

## Sufficiency and negative evidence
A useful lifecycle finding records the last guaranteed owner, invalidating event,
later use and missing protection on a feasible schedule. Explicitly distinguish
candidate, reproduced schedule, confirmed lifetime/logic violation and unresolved
external reachability. A cancellation name, a timeout or failure to observe a
callback in a short run is not enough.

Counterevidence includes a documented drain guarantee, a retained owner through
callback return, serialized terminal transitions with live losers, or generation
binding that prevents stale completion. Check each guarantee in the exact API
and target build rather than importing it from another asynchronous subsystem.

## Source and related evidence
Reviewed 2026-10-02. [1] [Windows CancelIoEx contract](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex)
supports the Windows-specific section; the other sections are constructed
lifecycle proof obligations, not claims about all OS cancellation APIs.

Related: reference-native-ownership-release-dangling for alias lifetimes;
reference-concurrency-refcounts-reuse for safe acquisition and generations;
reference-concurrency-locks-waits-reentrancy for wait dependency and callouts.
