---
id: vulnerability-concurrency-livelock-starvation-priority-inversion
title: Livelock, starvation, or priority inversion with security consequences
kind: vulnerability
topics: [concurrency, livelock, starvation, priority-inversion, availability]
platforms: [cross-platform]
architectures: [any]
---

# Livelock, starvation, or priority inversion with security consequences

## Definition and violated invariant

Livelock occurs when participants continue reacting or retrying without completing useful work; starvation occurs when a participant is indefinitely or unacceptably denied a required resource; priority inversion occurs when higher-priority work is blocked by lower-priority work while unrelated intermediate-priority execution delays the owner. A vulnerability requires attacker influence and a security-relevant loss of progress, deadline, or resource bound.

These conditions differ from deadlock because some participants or the system may continue executing. Scheduling policy, fairness, priority inheritance, timeouts and admission limits are platform-specific.

## Conditions that establish the issue

Identify the blocked or non-progressing operation, resource owner, scheduler and lock policy, retry or wake loop, competing work, deadlines, queue discipline, and attacker-controlled inputs or load. Prove a feasible execution can deny progress long enough to violate the stated security or availability requirement.

For priority inversion, show the high-priority task waits on a resource held by the low-priority task and that scheduling of intermediate work delays the owner under the actual policy. For starvation, establish lack of a bounding fairness guarantee rather than inferring infinity from one long delay.

## Evidence that is not sufficient

A retry loop, failed compare-and-exchange, high CPU use, priority difference, unfair-looking queue, or delayed request is not sufficient. Retries may be bounded, progress may be guaranteed, the scheduler may boost the owner, or the observed delay may have an unrelated cause.

Priority inheritance support is not proof that the relevant lock uses it, and its presence does not bound work performed while the lock is held.

## Investigation sequence

Recover progress variables, retry exit conditions, lock ownership and scheduler policy. Build a timeline showing which participant executes, which resource it holds or requests, and why each iteration or wake fails to advance the protected operation. Include backoff, timeout, cancellation, queue admission and priority-boost behavior.

Measure the security requirement conceptually as a deadline, finite retry/resource bound, or required eventual action. Trace failure handling because overload paths can drop authorization updates, retain privileged state, or fail open.

## Constructed priority-inversion schedule

Low-priority worker L acquires lock M and is preempted. High-priority security worker H becomes runnable, blocks on M, and cannot complete a credential revocation. A stream of medium-priority work M1 does not need M and repeatedly runs ahead of L, delaying release. This is a priority inversion only under a scheduler and mutex policy that permit the sequence; priority inheritance on that mutex may boost L and change the conclusion.

An attacker-relevant finding additionally needs control over the medium-priority workload or another prerequisite and a meaningful interval in which the delayed revocation or unavailable worker pool causes harm.

## Primitive and impact limits

The direct effect is delayed or absent progress, potentially with CPU, queue, lock or worker retention. Consequences can include denial of service, missed security deadlines, stale authorization, watchdog reset, or unsafe overload handling; it does not inherently provide memory corruption.

## Related knowledge and primary sources

`reference-concurrency-locks-waits-reentrancy` and resource-bound references cover wait classification and end-to-end availability. This profile repeats scheduling-policy and progress-bound proof locally.

Reviewed 2026-10-09 against Linux kernel [priority-inheritance futex documentation](https://docs.kernel.org/locking/pi-futex.html), Linux [scheduling policy documentation](https://man7.org/linux/man-pages/man7/sched.7.html), and [MITRE CWE-667](https://cwe.mitre.org/data/definitions/667.html). The schedule is constructed and is not a universal scheduler guarantee.
