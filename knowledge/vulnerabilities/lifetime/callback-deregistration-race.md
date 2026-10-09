---
id: vulnerability-lifetime-callback-deregistration-race
title: Callback deregistration race and function/context lifetime mismatch
kind: vulnerability
topics: [lifetime, callbacks, deregistration, race-condition, teardown]
platforms: [cross-platform]
architectures: [any]
---

# Callback deregistration race and function/context lifetime mismatch

## Definition and violated invariant

A callback-deregistration vulnerability occurs when teardown releases callback code, context, or referenced state before every callback that can use it has completed. Preventing new registrations or callback admission is distinct from draining callbacks already queued or running. Both the function target and its context must remain valid through the last invocation.

The required terminal event is API-specific: deregistration return, a completion event, rundown barrier, reference release, epoch grace period, or another quiescence condition. A cancellation request alone is not universal proof of quiescence.

## Conditions that establish the issue

Identify registration, callback and context ownership, admission rules, deregistration mode and result, in-flight callbacks, quiescence signal, and release. Prove an ordering where teardown invalidates code or context before an admitted callback's last access.

Also inspect self-deregistration and reentrancy. Waiting synchronously from the same callback can deadlock under APIs that require that callback to finish before deregistration completes.

## Evidence that is not sufficient

A callback API, unregister call, raw context, module unload, or callback near shutdown is not sufficient. Deregistration may synchronously drain, the callback may own its context, or an external lifetime barrier may cover execution.

No new callbacks after deregistration does not imply no previously queued callbacks remain.

## Investigation sequence

Build a timeline for registration, queue admission, callback entry/exit, deregistration, completion signal, owner release, and code unload. Resolve the return and error contract of the exact API. Track callback and context lifetimes independently.

In assembly, identify the stored function pointer and context pair, indirect call, and teardown operations. Bind them to one registration generation; an address reused by a later registration is a different object.

## Constructed Windows example

```c
UnregisterWaitEx(wait_registration, NULL);
free(callback_context);
```

For Windows `UnregisterWaitEx`, a null completion event makes the call nonblocking; no new callbacks are queued, but previously queued callbacks can still execute. Freeing their context immediately is unsafe if they dereference it. Passing `INVALID_HANDLE_VALUE` waits for callbacks to complete, subject to the API's documented deadlock restrictions, and would change this sequence.

## Primitive and impact limits

The direct primitive is an indirect call through unloaded code or a stale callback-context read/write. Impact depends on pending-callback reachability, reuse, controlled contents, and privilege. A safely drained registration has no stale-call primitive.

## Related knowledge and primary sources

`reference-native-ownership-release-dangling` covers callback ownership, while platform callback and asynchronous-I/O references define terminal events. This profile repeats admission-versus-quiescence locally.

Reviewed 2026-10-09 against Microsoft [`UnregisterWaitEx`](https://learn.microsoft.com/en-us/windows/win32/sync/unregisterwaitex), Microsoft [`CancelIoEx`](https://learn.microsoft.com/en-us/windows/win32/fileio/cancelioex-func), and [MITRE CWE-416](https://cwe.mitre.org/data/definitions/416.html). The source fragment is constructed.
