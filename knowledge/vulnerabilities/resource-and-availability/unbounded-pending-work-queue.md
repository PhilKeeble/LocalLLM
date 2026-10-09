---
id: vulnerability-resource-unbounded-pending-work-queue
title: Unbounded queue, backlog, pending I/O or callback accumulation
kind: vulnerability
topics: [resource-exhaustion, queue, backlog, pending-io, callbacks, denial-of-service]
platforms: [cross-platform]
architectures: [any]
---

# Unbounded queue, backlog, pending I/O or callback accumulation

## Definition and violated invariant

This vulnerability occurs when an actor can admit work faster than it completes and pending requests, I/O operations, callbacks or completions accumulate without an effective bound or backpressure. The violated invariant is that admission must reserve finite queue capacity and reject, defer or charge excess work before shared availability is lost.

Queue length, in-flight work, retained payload bytes and downstream fan-out are separate budgets. A bounded item count can still retain unbounded bytes.

## Conditions that establish the issue

Identify producer and consumer rates, queue ownership, item and byte costs, concurrency, completion dependency, cancellation, timeouts and quotas. Show a reachable actor can sustain arrival above service or prevent completion long enough to exceed a consequential bound.

Include work admitted across retries, reconnects and multiple frontends. If a client disconnects, establish whether its queued and downstream work is canceled or remains live.

## Evidence that is not sufficient

An asynchronous API, queue object, large backlog or transient traffic spike is not sufficient. The queue may be bounded, producers may block, overload may shed work, deadlines may reclaim items or each tenant may have isolated capacity. A configured maximum is meaningful only if all admission paths enforce it atomically.

Do not infer unbounded growth from a snapshot; compare arrival, completion and reclamation over the relevant interval.

## Investigation sequence

Trace admission from request through queue insertion, downstream queues, execution, completion and removal. Recover all counters and whether they measure items, bytes, cost or only active workers. Examine races where multiple producers pass a capacity check before reservations are committed.

At binary level, locate enqueue and completion callbacks, pending lists, reference ownership and cancellation paths. Determine whether timeouts merely stop waiting while leaving work queued. Map overload behavior to the caller and to unrelated authorized work.

## Constructed timeline

A hypothetical endpoint enqueues one job before checking whether the caller is still connected. Four workers each complete ten jobs per second, while an unauthenticated client can enqueue 100 per second and queued jobs have no deadline. The pending count grows by roughly 60 per second while the rate persists.

The arithmetic supports a candidate only if the stated rates, retained lifetime and shared queue apply in deployment. Admission caps, per-client quotas or cancellation can change the conclusion.

## Primitive and impact limits

Report item and byte growth rates, maximum queue state, worker capacity, duration and affected scope. Direct effects include memory pressure, latency, descriptor retention and starvation. A later stale callback or use-after-free is a separate lifetime defect.

## Related knowledge and primary sources

Asymmetric work, retry and cancellation profiles cover common producers and retention paths. This profile owns the backlog and admission-accounting invariant.

Reviewed 2026-10-09 against [MITRE CWE-770](https://cwe.mitre.org/data/definitions/770.html), [MITRE CWE-400](https://cwe.mitre.org/data/definitions/400.html) mapping guidance and [RFC 4732](https://www.rfc-editor.org/rfc/rfc4732.html) application resource-exhaustion analysis. The timeline is constructed; queue semantics and capacities require target evidence.
