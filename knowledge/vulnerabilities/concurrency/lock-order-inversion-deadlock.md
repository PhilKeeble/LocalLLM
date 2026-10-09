---
id: vulnerability-concurrency-lock-order-inversion-deadlock
title: Lock-order inversion and security-relevant deadlock
kind: vulnerability
topics: [concurrency, deadlock, lock-order, availability, resource-exhaustion]
platforms: [cross-platform]
architectures: [any]
---

# Lock-order inversion and security-relevant deadlock

## Definition and violated invariant

A lock-order deadlock occurs when concurrent execution creates a cycle of held resources and waits so that no participant can progress. A vulnerability exists when an untrusted actor can reach and sustain the cycle across a security boundary or cause a security-relevant service, cleanup, watchdog, or fail-open path to stop.

Opposite acquisition order is a candidate, not proof. The relevant holds and blocking waits must coexist, and timeouts or detection may change the result.

## Conditions that establish the issue

Recover exact lock identities, modes, ownership, acquisition order, blocking behavior, callbacks and waits for every participant. Prove a feasible schedule in which each participant holds a resource required by the next and cannot release its current resources while waiting. Then establish attacker influence over the prerequisite requests, timing or retained resources and the resulting security consequence.

Include joins, completion waits, IPC replies, event-loop dispatch and callback drains in the dependency graph. A thread can hold a mutex while waiting for work that needs that same mutex without a second explicit lock acquisition.

## Evidence that is not sufficient

Two reversed lock sequences, a hang, blocked threads, a recursive call, or a detector warning is not sufficient. States may be mutually exclusive, try-lock or timeout paths may break the cycle, the locks may be different instances, or a paused thread may explain the observation.

A bounded timeout prevents indefinite deadlock only if its recovery releases the cycle safely; repeated timeouts can still create denial of service or fail-open behavior.

## Investigation sequence

Build a wait-for graph at the object-instance level: participant, held resource, requested resource, wait type and release prerequisite. Add the state predicates required for every edge and determine whether they can hold simultaneously. Preserve object generations so recycled lock addresses do not create a false cycle.

Trace what remains unavailable during the cycle, how cancellation and watchdogs react, and whether repeated untrusted requests can recreate it. Distinguish permanent deadlock from long contention, starvation and active livelock.

## Constructed two-lock schedule

Thread A handles an untrusted account operation, acquires `account_lock`, invokes audit code, and blocks acquiring `audit_lock`. Thread B processes audit rotation, already holds `audit_lock`, and waits for `account_lock` to update the account's audit cursor. If both holds coexist and neither path has a timeout or releases before waiting, the wait-for graph contains a cycle.

This becomes a vulnerability only if an attacker can trigger or sustain the overlapping states and the blocked service or recovery has a security consequence. Merely finding both acquisition orders in disassembly does not prove concurrency or identical lock instances.

## Primitive and impact limits

The direct effect is loss of progress for the participants and resources they hold. Consequences can include denial of service, exhaustion of worker pools, blocked security updates, unavailable cleanup, or unsafe timeout recovery; deadlock alone does not provide memory corruption or code execution.

## Related knowledge and primary sources

`reference-concurrency-locks-waits-reentrancy` defines lock identity, wait dependencies and timeout limits. This profile repeats cycle feasibility and attacker-controlled consequence locally.

Reviewed 2026-10-09 against the C++ [mutex requirements](https://eel.is/c++draft/thread.mutex.requirements.mutex), C++ [lock algorithms](https://eel.is/c++draft/thread.lock.algorithm), and [MITRE CWE-833](https://cwe.mitre.org/data/definitions/833.html). The schedule is constructed.
