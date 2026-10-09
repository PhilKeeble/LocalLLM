---
id: vulnerability-kernel-rcu-lifetime-misuse
title: RCU unpublication, grace-period or post-read lifetime misuse
kind: vulnerability
topics: [kernel, linux, rcu, lifetime, use-after-free, concurrency]
platforms: [linux, android]
architectures: [any]
---

# RCU unpublication, grace-period or post-read lifetime misuse

## Definition and violated invariant

This vulnerability occurs when Read-Copy Update publication, reader protection, unpublication or reclamation is ordered incorrectly, or a borrowed pointer escapes its protected read-side lifetime without another valid reference. The invariant is that readers observe properly published state and reclamation occurs only after every reader covered by the selected RCU flavor can no longer access it.

An RCU grace period waits for the relevant preexisting read-side critical sections; it is not a general drain for arbitrary workers, DMA or references held outside those regions. Updater serialization and object lifetime are separate obligations.

## Conditions that establish the issue

Identify the exact RCU flavor, publication primitive, reader entry/exit, pointer load, unpublication, updater synchronization, grace-period operation, reference transfer and final free. Prove a reader can observe partially published state, retain a borrowed pointer after its region, or access storage reclaimed without the required grace period.

For RCU plus refcount, show where a still-valid object reference is acquired before leaving the read-side region and how failed acquisition is handled.

## Evidence that is not sufficient

An `rcu_dereference`, `call_rcu`, delayed free or lockless list is not sufficient. The use may be covered by the correct reader region and grace period, or another ownership reference may extend lifetime. Immediate free after removal is suspicious only when a feasible RCU reader can still hold the object.

A grace-period call does not prove mutable field consistency or writer exclusion. Recover those separately.

## Investigation sequence

Mark publication, reader, unpublication and reclamation events and the ordering primitive on each edge. Track the pointer into callbacks and workers and determine whether a retained reference replaces RCU protection. Identify the RCU domain relevant to each execution context.

At binary level, helper calls may compile to light barriers or ordinary loads depending on architecture and configuration. Analyze their semantic role from symbols, inlining and surrounding critical sections rather than demanding one instruction signature.

## Constructed timeline

Reader A enters an RCU read-side section, loads object P and exits, then queues P to a worker without incrementing its lifetime reference. Updater B removes P, waits for a grace period and frees it. The grace period can validly finish after A exits even though the later worker still holds P, so the worker's dereference is unprotected.

The finding is refuted if queueing transfers a valid reference or the worker itself remains within a supported extended reader contract.

## Primitive and impact limits

The direct primitive can be use-after-free, stale state, partial publication or conflicting update. Kernel execution requires controllable replacement or corruption and mitigation analysis; an invalid access alone may only support denial of service.

## Related knowledge and primary sources

`reference-linux-kernel-object-lifetime` provides shared kref and RCU contracts. This profile retains the selected flavor, reader boundary and reclamation proof for isolated use.

Reviewed 2026-10-09 against Linux kernel [What is RCU?](https://docs.kernel.org/RCU/whatisRCU.html), [RCU list usage](https://docs.kernel.org/RCU/listRCU.html) and [`kref` rules](https://docs.kernel.org/core-api/kref.html). The timeline is constructed and Linux-specific.
