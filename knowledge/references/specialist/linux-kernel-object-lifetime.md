---
id: reference-linux-kernel-object-lifetime
title: Linux kernel references, RCU, locks, user copies and object teardown
kind: reference
topics: [linux-kernel, refcounts, rcu, locks, user-copy, lifetime, teardown]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Kernel ownership and concurrency evidence

## Taking a kref requires a still-valid object

Linux kref rules require retaining a reference before handing a pointer to another
execution context. The last kref_put invokes the release routine. Acquiring a
reference without already holding a valid pointer requires synchronization that
keeps the structure valid during acquisition. [1]

Recover lookup, acquisition, publication, handoff and release as separate events.
An increment on an already stale pointer cannot retroactively keep it alive.
Atomic counter arithmetic alone does not prove safe lookup or synchronization of
mutable fields. This is the kref contract; other ownership schemes need their
own acquisition and reclamation rules.

## RCU removal and a grace period do not serialize all writers

Linux RCU separates removal from later reclamation. synchronize_rcu waits for
relevant preexisting read-side critical sections; call_rcu schedules a callback
after a grace period. Publication/read primitives support reader visibility,
while updater coordination remains a separate requirement. [2]

Recover the actual RCU flavor, reader region, unpublication and final free.
An RCU-protected lookup does not automatically retain a pointer after leaving its
read-side region. A grace period is not a wait for every unrelated worker or DMA
user. Mixed RCU/refcount ownership requires evidence for both; do not diagnose
missing immediate free as a leak without the deferred release path.

## A kernel lock name does not supply every execution-context guarantee

Linux raw_spinlock_t remains a strict spinning lock; spinlock_t semantics depend
on PREEMPT_RT configuration. Sleeping locks, local protection and interrupt
exclusion have distinct contracts. [3]

Identify configuration, context, held lock and shared object before reasoning
about sleeping, preemption or interrupt exclusion. A lock protecting a list does
not necessarily protect fields or references once lookup ends. CPU-local exclusion
must not be assumed to serialize other CPUs or devices. Recover the actual lock
scope and permitted nested operations; no universal non-RT rule is imported.

## User-copy, request completion and object reclamation need separate results

For Linux request representation and bulk/single-value user-copy result contracts,
use reference-linux-kernel-interface-representations. Follow the exact copied
extent and error path into validated kernel state; a checked address does not
freeze later external reads.

For teardown, recover admission stop, lookup removal, pending callbacks/work,
device activity, final ownership release and backing storage reclamation. A
close or cancellation request alone is not proof asynchronous users stopped.
Report the specific unsupported use or violated lifetime condition, rather than
equating a counter or user-copy call with a defect. Workflow:
playbook-specialist-kernel-boundary.

## Sources and scope

Reviewed 2026-10-08, rolling upstream Linux API documentation. No structure
offsets, allocation defaults or whole-kernel lifetime proof.

1. [kref](https://docs.kernel.org/core-api/kref.html): Kref rules 1-3 and release behavior.
2. [What is RCU?](https://docs.kernel.org/RCU/whatisRCU.html): removal/reclamation, publication and grace-period interfaces.
3. [Lock types](https://docs.kernel.org/locking/locktypes.html): raw_spinlock_t/spinlock_t and PREEMPT_RT distinctions.

Related: reference-concurrency-refcounts-reuse,
reference-concurrency-cancellation-completion-shutdown.
