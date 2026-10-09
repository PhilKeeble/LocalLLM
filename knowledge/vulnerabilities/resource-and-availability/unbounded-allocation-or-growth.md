---
id: vulnerability-resource-unbounded-allocation-or-growth
title: Unbounded allocation or attacker-controlled collection growth
kind: vulnerability
topics: [resource-exhaustion, memory, allocation, collection-growth, denial-of-service]
platforms: [cross-platform]
architectures: [any]
---

# Unbounded allocation or attacker-controlled collection growth

## Definition and violated invariant

This vulnerability occurs when an actor can cause memory or another allocation-backed resource to grow without an effective per-request, per-principal or service-wide bound. The violated invariant is that admitted work must reserve and charge finite resources to the actor or operation before exhaustion affects other authorized work.

A single large allocation, many individually valid objects and retained collection entries are variants of the same accounting failure. Integer overflow that underallocates storage is a separate memory-safety root cause.

## Conditions that establish the issue

Identify the attacker-controlled count, declared size, key cardinality or repetition; each allocation or retained object; its lifetime; governing budget; release point; and the concrete memory, address-space or quota limit. Prove a reachable sequence can exceed the effective budget faster than reclamation or admission control prevents it.

Include allocator overhead, object graphs, indexes, duplicate keys, capacity growth and concurrent requests. A nominal input-size limit may not bound decoded or retained representation.

## Evidence that is not sufficient

An allocation using input, a growing vector or an out-of-memory path is not sufficient. Protocol framing, authentication quotas, maximum object counts, streaming consumption, eviction or process isolation may impose an effective bound. A theoretical machine-wide limit can be acceptable if a smaller enforced service budget protects availability.

Do not infer unbounded retention from peak memory without proving the objects remain reachable or unreclaimed for the relevant interval.

## Investigation sequence

Trace the controlling value through parsing, conversion and multiplication into allocation and container operations. Build an accounting table for bytes and objects charged per request, principal and service. Follow resizing, copies, temporary buffers, rollback and cleanup on success, error, cancellation and timeout.

At binary level, identify allocator calls, growth loops, capacity comparisons and ownership transfers. Recover environmental caps such as address-space limits, cgroups, job objects or runtime heap policy, then determine whether exhaustion remains security-relevant within that containment.

## Constructed example

This hypothetical handler retains one allocation for each supplied key without a request or account quota:

```c
for (uint32_t i = 0; i < request->count; ++i)
    map_insert(session, request->keys[i], allocate_record());
```

The loop is vulnerable only if the count or repeated requests are attacker-controlled, inserted records remain live and no earlier framing, quota, deduplication or eviction bound prevents consequential growth. A finite 32-bit count alone is not a useful operational bound.

## Primitive and impact limits

State bytes or objects per action, maximum concurrency, reclamation rate, containment and the first exhausted resource. The direct effect is allocation pressure or denial of service. Memory corruption follows only if a separate allocation-failure, arithmetic or bounds error mishandles exhaustion.

## Related knowledge and primary sources

Allocation arithmetic profiles cover size correctness; lifetime profiles cover missing release. This profile owns admission and growth accounting when allocations are otherwise correctly sized and live.

Reviewed 2026-10-09 against [MITRE CWE-770](https://cwe.mitre.org/data/definitions/770.html) and [MITRE CWE-789](https://cwe.mitre.org/data/definitions/789.html). The example is constructed; effective resource limits and failure behavior remain platform- and deployment-specific.
