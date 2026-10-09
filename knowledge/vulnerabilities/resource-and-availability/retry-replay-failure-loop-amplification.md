---
id: vulnerability-resource-retry-replay-failure-loop-amplification
title: Retry storm, replay amplification or failure-loop resource consumption
kind: vulnerability
topics: [resource-exhaustion, retry-storm, replay, failure-loop, amplification]
platforms: [cross-platform]
architectures: [any]
---

# Retry storm, replay amplification or failure-loop resource consumption

## Definition and violated invariant

This vulnerability occurs when failure, timeout, reconnect or replay causes work to be resubmitted without an effective terminal limit, backoff, deduplication or budget, amplifying load and delaying recovery. The violated invariant is that retries must converge or stop and repeated delivery must not multiply expensive work or non-idempotent effects beyond the caller's authority.

A retry storm can be self-sustaining when overload increases failures and failures immediately generate more work. Replay can also repeat a successful side effect when completion was lost but execution occurred.

## Conditions that establish the issue

Recover the trigger, retry owner, attempt counter, delay and jitter, maximum duration, concurrency, deduplication or idempotency key, downstream fan-out and cancellation. Show a reachable failure or attacker-induced ambiguity produces a consequential increase in work or repeated effect under deployed timeout and recovery behavior.

Trace retries at every layer because application, proxy, client library and transport retries can multiply. Determine whether attempt counters reset on reconnect, failover or process restart.

## Evidence that is not sufficient

A loop, retry API, replayable message or exponential backoff is not sufficient. Attempts may be finite, operations idempotent, duplicates suppressed and capacity reserved. Exponential backoff reduces rate but does not by itself cap infinite retention or synchronized clients; jitter, limits and recovery behavior still matter.

A duplicate request ID is only protective if the consumer binds it to the caller and operation and retains the result for the relevant replay window.

## Investigation sequence

Draw one logical operation across layers and label each attempt, timeout, acknowledgment and side effect. Recover exact conditions that increment, reset and terminate counters. Identify whether timeout means no result was observed or no operation occurred. Follow orphaned work after callers retry or disconnect.

At binary level, locate failure branches, timer scheduling, counter comparisons, queue insertion and deduplication lookups. Check arithmetic and sentinel handling for unlimited-attempt values. Compare retry timing with service recovery and shared queue capacity.

## Constructed timeline

A hypothetical client has no terminal attempt limit and retries immediately after a 2-second timeout. The service continues each original 10-second operation after disconnect. Five overlapping attempts can therefore execute for one logical action before the first completes, and many synchronized clients can amplify an outage.

This candidate is refuted if cancellation reliably terminates earlier operations, an idempotency record coalesces attempts, or admission control caps the aggregate below harmful load.

## Primitive and impact limits

Report attempts per logical action, overlap, fan-out, backoff, replay window and resulting CPU, queue, storage or side effects. The direct effect is resource amplification or duplicate state change. Unauthorized state change additionally requires a failure of caller/action/object binding or idempotency policy.

## Related knowledge and primary sources

Queue and CPU-amplification profiles cover downstream resources. This profile owns failure-driven resubmission and replay convergence.

Reviewed 2026-10-09 against [RFC 5390](https://www.rfc-editor.org/rfc/rfc5390.html) overload and load-amplification requirements, [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html) TCP exponential-backoff requirements and [MITRE CWE-405](https://cwe.mitre.org/data/definitions/405.html). The timeline is constructed; application retry and idempotency semantics require target evidence.
