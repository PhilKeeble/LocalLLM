---
id: vulnerability-kernel-object-lookup-reference-race
title: Kernel object lookup, reference or identifier-reuse race
kind: vulnerability
topics: [kernel, lifetime, refcount, lookup, identifier-reuse, race-condition]
platforms: [cross-platform, linux, windows, android, freebsd]
architectures: [any]
---

# Kernel object lookup, reference or identifier-reuse race

## Definition and violated invariant

This vulnerability occurs when kernel code resolves an identifier or pointer and uses the object without acquiring lifetime protection while the lookup is valid, or when a reused identifier is accepted as the original object. The invariant is that object identity, generation and a live reference must remain bound from lookup through final use.

An atomic reference increment cannot rescue a pointer after its storage may already have been freed. A reference count protects lifetime only for participants following its acquisition and release protocol; it does not authorize operations or freeze mutable fields.

## Conditions that establish the issue

Identify the namespace and identifier, lookup synchronization, object generation, removal/unpublication, reference acquisition, final use and reclamation. Construct an interleaving where removal or reuse occurs between lookup and a valid lifetime acquisition, causing access to reclaimed storage or operation on a replacement object.

For identifier reuse without memory unsafety, show the later object differs in owner or authority and the stale identifier remains accepted. For refcount arithmetic, establish overflow, underflow or missing participant under the actual counter API.

## Evidence that is not sufficient

A pointer returned from a lookup, reference counter, reused numeric ID or concurrent close is not sufficient. The namespace lock, RCU region, hazard protocol, generation field or referenced lookup API may retain the object. Equal numeric identifiers at different times do not prove mistaken binding if generation or owner is revalidated.

Do not infer a refcount bug merely because decrement reaches zero; identify unmatched ownership or a race.

## Investigation sequence

Draw lookup, retain, use, release, unpublish and reclaim events with their locks or epochs. Determine whether the retain operation is permitted from the acquired pointer state. Follow every handoff to workers, timers and devices. Compare identifiers with generation, namespace and owner at the final effect.

At binary level, locate table/tree lookup, atomic increments, zero tests and release callbacks. Recover whether a helper returns a borrowed or retained reference. Inspect failure and retry paths for double release or use after a failed retain.

## Constructed interleaving

Thread A looks up object `id=7` and receives a borrowed pointer, then drops the table lock. Thread B removes and frees it, allocates a replacement whose storage or ID is reused, and publishes that replacement. Thread A then increments or uses the stale pointer. The sequence is vulnerable only if the lookup did not return a retained reference and no grace-period or generation check covers A.

## Primitive and impact limits

The direct primitive can be use-after-free, type confusion, operation on a replacement object or denial of service. Control over replacement contents and resulting memory or authority effect must be shown before claiming kernel execution or elevation.

## Related knowledge and primary sources

Lifetime, handle reuse and RCU profiles cover specialized mechanisms. This profile keeps lookup-time acquisition and object-generation binding together.

Reviewed 2026-10-09 against Linux kernel [`kref` rules](https://docs.kernel.org/core-api/kref.html), Linux [IDR usage](https://docs.kernel.org/core-api/idr.html) and Microsoft [object reference guidance](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/life-cycle-of-an-object). The interleaving is constructed; helper ownership contracts are platform-specific.
