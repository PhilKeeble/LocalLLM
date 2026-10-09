---
id: vulnerability-concurrency-cancellation-misinterpreted-as-completion
title: Cancellation interpreted as completion while work still uses resources
kind: vulnerability
topics: [concurrency, cancellation, asynchronous-io, completion, lifetime]
platforms: [cross-platform]
architectures: [any]
---

# Cancellation interpreted as completion while work still uses resources

## Definition and violated invariant

A cancellation-lifetime vulnerability occurs when code treats a cancellation request, timeout, close, or deregistration result as proof that the operation is quiescent and releases resources that work or completion delivery can still access. Cancellation request, cancellation acceptance, terminal operation result, completion notification, callback return and resource release are distinct events unless the selected API explicitly combines them.

Cancellation can race with normal completion, fail to find the operation, or stop future dispatch without draining a callback already running. The terminal status must be observed through the operation's documented completion mechanism.

## Conditions that establish the issue

Identify request identity and generation, issue point, every retained buffer and context, cancellation API and return semantics, worker or device state, terminal-result channel, completion callbacks or packets, cleanup owner and last use. Prove cleanup can occur after only a cancellation request or timeout while a feasible path still accesses the released resource.

Also inspect duplicate terminal paths: normal completion and cancellation recovery may both send a response, release a reference or reuse a request slot unless one live transition selects the owner.

## Evidence that is not sufficient

A cancellation call, successful return, timeout, closed handle, aborted status, or late completion is not sufficient. The caller may retain resources until terminal completion, the API may provide a synchronous drain, or the late path may not touch reclaimed state.

Failure to find a request does not universally prove it completed; it can reflect identity mismatch, earlier completion, or a race whose result must be learned elsewhere.

## Investigation sequence

Create a lifecycle timeline for issue, execution, cancellation request, terminal state, notification, callback return and cleanup. Attach each resource to the final event that guarantees no further access. Follow all statuses because normal completion can win a cancellation race.

Preserve request generation and completion-channel behavior when structures are reused. Verify losing cleanup paths retain enough lifetime to observe the terminal transition safely.

## Constructed Windows overlapped-I/O example

```c
CancelIoEx(file, overlapped);
free(buffer);
free(overlapped);
```

For Windows overlapped I/O, a successful `CancelIoEx` return means cancellation was requested; it does not wait for the operation to complete, and the operation can complete normally, as canceled, or with another error. The associated `OVERLAPPED` structure must not be freed or reused until completion. The shown cleanup is therefore unsafe when the request remains outstanding and still refers to either allocation.

## Primitive and impact limits

The direct result can be use-after-free, buffer corruption, double completion, stale-generation update, or disclosure through reused storage. Impact depends on the outstanding operation, its authority, and attacker control over contents and timing.

## Related knowledge and primary sources

`reference-concurrency-cancellation-completion-shutdown`, `reference-windows-overlapped-io-lifetime-cancellation`, and request-ownership references define platform completion contracts. This profile repeats event separation and last-use proof locally.

Reviewed 2026-10-09 against Microsoft [CancelIoEx](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex), Microsoft [OVERLAPPED](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped), and [MITRE CWE-416](https://cwe.mitre.org/data/definitions/416.html). The source is constructed and Windows-specific; other cancellation APIs require their own drain guarantees.
