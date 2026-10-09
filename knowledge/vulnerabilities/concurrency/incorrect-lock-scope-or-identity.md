---
id: vulnerability-concurrency-incorrect-lock-scope-or-identity
title: Incorrect lock scope, missing lock, or protection of the wrong object
kind: vulnerability
topics: [concurrency, locks, synchronization, lock-scope, object-identity]
platforms: [cross-platform]
architectures: [any]
---

# Incorrect lock scope, missing lock, or protection of the wrong object

## Definition and violated invariant

A lock-coverage vulnerability occurs when a shared invariant is accessed without its required synchronization, the lock is released before the protected operation is complete, or competing paths use different lock objects or modes. Every conflicting participant must use a protocol that protects the same state for the full interval required by its invariant and lifetime.

The presence of lock and unlock calls near an access is not sufficient. Lock identity, ownership mode, object generation and coverage boundaries determine whether operations actually serialize.

## Conditions that establish the issue

Identify the shared fields and compound invariant, every reader and writer, exact lock address or synchronization object selected on each path, acquisition mode, recursion, acquisition success, release point, and object lifetime. Prove a competing access can occur outside compatible protection and reaches a security-relevant state or memory effect.

For pointers copied under a lock, determine what retains the pointee after unlock. A lock can protect lookup without extending object lifetime unless the protocol acquires a reference or otherwise prevents reclamation.

## Evidence that is not sufficient

A field access outside a visibly bracketed critical section, different symbolic lock names, a failed try-lock branch, or a short critical section is not sufficient. Synchronization may be inlined, held by the caller, supplied by an epoch or ownership protocol, or unnecessary for immutable state.

Conversely, identical lock function imports do not prove identical lock objects. A per-object lock cannot protect a global invariant when operations on distinct objects can overlap.

## Investigation sequence

For each shared invariant, build a table of access site, object generation, lock address, mode, acquisition result and protected interval. Include callbacks, error exits, waits and helper calls that can release, replace or bypass protection. Compare actual addresses at runtime or through object-offset recovery when names are ambiguous.

Construct the smallest schedule in which two incompatible operations proceed and follow the resulting mixed state, stale lifetime, duplicate action or unauthorized decision. Check whether a later revalidation closes the window.

## Constructed wrong-lock example

```c
void reserve(struct client *client)
{
    lock(&client->lock);
    if (global_reserved < global_limit)
        ++global_reserved;
    unlock(&client->lock);
}
```

Constructed schedule: requests for clients A and B acquire different `client->lock` objects, both observe the same remaining global slot, and both increment `global_reserved`. Each critical section is internally serialized for one client, but neither excludes the other from the global invariant. The finding requires the counter and limit to be shared and no separate atomic reservation or global lock around the operation.

## Primitive and impact limits

The direct result can be mixed state, stale-object use, quota or authorization bypass, duplicate operation, or memory corruption. Impact depends on the unprotected invariant and attacker control over concurrency and object selection.

## Related knowledge and primary sources

`reference-concurrency-locks-waits-reentrancy`, `reference-concurrency-memory-order-atomic-invariants`, and `reference-concurrency-refcounts-reuse` cover lock identity, compound operations and lifetime. This profile repeats exact-lock and full-coverage requirements locally.

Reviewed 2026-10-09 against the C++ [mutex requirements](https://eel.is/c++draft/thread.mutex.requirements.mutex), [data-race rules](https://eel.is/c++draft/intro.races), and [MITRE CWE-667](https://cwe.mitre.org/data/definitions/667.html). The source and schedule are constructed.
