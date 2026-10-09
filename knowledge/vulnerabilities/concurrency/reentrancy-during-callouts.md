---
id: vulnerability-concurrency-reentrancy-during-callouts
title: Reentrancy during callbacks, destructors, allocation, logging, or hooks
kind: vulnerability
topics: [concurrency, reentrancy, callbacks, destructors, hooks, lifetime]
platforms: [cross-platform]
architectures: [any]
---

# Reentrancy during callbacks, destructors, allocation, logging, or hooks

## Definition and violated invariant

A reentrancy vulnerability occurs when an operation calls code that can synchronously or asynchronously enter the same object, subsystem, or security operation before the outer invocation has restored a stable state. The object lifetime, state-machine phase, lock assumptions, one-time effects, and post-call invariants must remain valid across every callout.

Reentrancy does not require a second thread. User callbacks, virtual destructors, allocators, logging sinks, hooks, message dispatch, finalizers and nested IPC can run application-controlled or subsystem code on the current thread.

## Conditions that establish the issue

Identify the callout and prove it can reach a nested entry on the relevant execution path. Record the state and resources exposed before the call, allowed nested operations, locks and recursion policy, object references retained across the call, and every access or effect after return. Show the nested entry changes or destroys something the outer frame later assumes remains valid.

If the callout is asynchronous, treat it as ordinary concurrency and establish the schedule. If it is synchronous, preserve the single-thread call stack and do not invent a race that requires parallel execution.

## Evidence that is not sufficient

An indirect call, callback parameter, destructor, allocation, log statement, recursive mutex, or nested event loop is not sufficient. The target may be closed, trusted, deferred, unable to reach the object, or guarded by an explicit reentrancy state.

A recursive lock prevents self-deadlock for that lock but does not preserve object state or prevent nested operations. A nonrecursive lock may convert the path into deadlock instead of making it safe.

## Investigation sequence

Enumerate all feasible targets of each callout and follow them until return, including error, destruction and registration changes. At the call boundary, snapshot object phase, ownership, locks, pending one-time effects and references. Compare each post-call use with mutations possible in the nested path.

Trace callbacks installed by plugins or untrusted clients and runtime-generated dispatch separately from ordinary internal calls. Verify whether deregistration or object closure can occur from within the callback and whether the outer path revalidates state afterward.

## Constructed callback example

```c
object->state = UPDATING;
object->observer(object);       /* observer can call close(object) */
object->buffer[0] = marker;     /* outer frame assumes object survived */
object->state = READY;
```

Constructed call stack: `update` invokes `observer`; the observer reenters `close`, removes the object and releases its final reference; control returns to `update`, which writes through the stale object. The finding requires that this callback target can invoke `close`, that close is permitted in `UPDATING`, and that no retained reference or deferred-destruction rule covers the outer frame.

## Primitive and impact limits

The direct result can be stale-object access, duplicated action, invalid state transition, lock recursion, or cleanup of an in-use resource. Impact depends on the nested operation and later access; reentrancy alone does not imply attacker control or memory corruption.

## Related knowledge and primary sources

`reference-concurrency-locks-waits-reentrancy`, `reference-concurrency-refcounts-reuse`, and callback-lifetime references cover callout and ownership contracts. This profile repeats target reachability, exposed state, and post-call-use proof locally.

Reviewed 2026-10-09 against the C++ [virtual-call rules during construction and destruction](https://eel.is/c++draft/class.cdtor), [mutex requirements](https://eel.is/c++draft/thread.mutex.requirements.mutex), and [MITRE CWE-663](https://cwe.mitre.org/data/definitions/663.html). The source and call stack are constructed; whether a particular allocator, logger or message API calls out requires its own contract.
