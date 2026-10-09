---
id: vulnerability-resource-attacker-controlled-critical-section-duration
title: Attacker-controlled expensive work inside a critical section
kind: vulnerability
topics: [resource-exhaustion, locking, critical-section, contention, denial-of-service]
platforms: [cross-platform]
architectures: [any]
---

# Attacker-controlled expensive work inside a critical section

## Definition and violated invariant

This vulnerability occurs when attacker-controlled work executes while holding a lock, disabling preemption or interrupts, or occupying another exclusive critical section long enough to block security-relevant progress. The violated invariant is that exclusive ownership duration must be bounded independently of untrusted input and compatible with the waiters' deadlines.

This differs from deadlock because the owner can eventually release the resource. It differs from general CPU amplification because exclusivity lets one slow operation stall otherwise independent callers.

## Conditions that establish the issue

Identify the exclusive resource, owner and waiters, entry and exit points, attacker-controlled operation or loop bound, scheduling context, timeout and required deadline. Prove a reachable input extends hold time enough to deny service, miss a real-time requirement or delay a security operation.

Include callbacks, logging, allocation, I/O, page faults and retries invoked under the lock. Their cost and blocking behavior may depend on external state even when the local instruction count is small.

## Evidence that is not sufficient

A large function between lock and unlock, a contended mutex or a slow trace is not sufficient. The expensive path may execute outside the critical section, inputs may be bounded, waiters may use another lock instance, or the scheduler may meet all required deadlines.

Holding a spin lock is not automatically a vulnerability; establish target context, maximum duration and affected operation. Decompiler placement can obscure cleanup-based unlocks.

## Investigation sequence

Recover exact acquisition and release paths, including errors and exceptions. Trace untrusted values into iteration counts, parsing, allocation, callbacks and I/O while ownership is held. Build a waiter graph with priorities, deadlines and lock identity. Include interrupt/preemption state for kernel and firmware paths.

At binary level, locate lock primitives and all exits, then identify calls and backward branches dominated by acquisition and post-dominated by release. Resolve indirect calls enough to bound their work and blocking. Check whether cancellation or timeout can leave ownership held.

## Constructed example

This hypothetical handler holds a global session lock while processing every attacker-supplied record:

```c
lock(&sessions);
for (size_t i = 0; i < request_count; ++i)
    parse_and_verify(request[i]);
unlock(&sessions);
```

The pattern is vulnerable only if `request_count` or per-record cost can exceed the required hold-time budget, the global lock is shared with important work and no earlier bound applies. Expensive work moved outside the lock would alter the contention primitive but may leave general CPU amplification.

## Primitive and impact limits

Report maximum or attacker-achievable hold time, waiter set, scheduling context and missed requirement. The direct effect is blocking, latency or denial of service. Priority inversion, deadlock or unsafe timeout cleanup are separate findings when their conditions also hold.

## Related knowledge and primary sources

Lock-order and starvation profiles cover distinct progress failures. This profile owns input-dependent exclusive duration.

Reviewed 2026-10-09 against POSIX thread-cancellation and locking rationale in [The Open Group Base Specifications](https://pubs.opengroup.org/onlinepubs/9799919799/xrat/V4_xsh_chap01.html), Linux kernel [locking documentation](https://docs.kernel.org/locking/index.html) and [MITRE CWE-667](https://cwe.mitre.org/data/definitions/667.html). The example is constructed; scheduling and lock guarantees remain platform-specific.
