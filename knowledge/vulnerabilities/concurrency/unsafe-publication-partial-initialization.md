---
id: vulnerability-concurrency-unsafe-publication-partial-initialization
title: Initialization race, unsafe publication, or partially initialized object use
kind: vulnerability
topics: [concurrency, initialization, publication, memory-order, object-lifetime]
platforms: [cross-platform]
architectures: [any]
---

# Initialization race, unsafe publication, or partially initialized object use

## Definition and violated invariant

An unsafe-publication vulnerability occurs when an object or readiness state becomes observable before its construction and required initialization are ordered before every consumer. Consumers must not use the object until its lifetime has begun, all required fields and invariants are established, and the publication mechanism makes those writes visible under the applicable memory model.

Pointer visibility, field initialization and object lifetime are separate. An atomic pointer or flag prevents tearing of that atomic object but does not automatically publish surrounding non-atomic state.

## Conditions that establish the issue

Identify allocation and lifetime start, every initialization write, constructor escape, publication store or registration, consumer load, synchronization or dependency edge, and first field use. Prove a consumer can observe the published identity without the ordering required to observe initialization and that the resulting partial state reaches a security-relevant operation.

For reused objects or flags, show the consumer observes the publication for the intended generation. A release/acquire pair on an unrelated atomic does not bind the object, and a previously true readiness flag may not publish later mutations.

## Evidence that is not sufficient

An atomic pointer, singleton pattern, constructor callback, relaxed operation, missing fence instruction, or field with a default value is not sufficient. The target language or runtime may provide initialization synchronization, the relevant machine ordering may be supplied by another instruction or API, or the consumer may not run until after a join or lock edge.

Conversely, observing fully initialized state in one run does not establish the required ordering for every permitted execution.

## Investigation sequence

Build a publication graph from each initialization write to the exact store or registration that exposes the object, then from the consumer's observation to each field read. Label language-level synchronizes-with edges, compiler lowering, executed instructions, memory type and observer. Verify the consumer actually reads from the release sequence or equivalent mechanism claimed to publish the object.

Check constructor callouts, global registration, work-queue submission, callbacks and reference handoff for early escape. Preserve generation and lifetime when storage or readiness flags are reused.

## Constructed C++ relaxed-publication example

```c++
payload.value = attacker_selected;
ready.store(true, std::memory_order_relaxed);       // producer

if (ready.load(std::memory_order_relaxed))          // consumer
    authorize(payload.value);
```

Under the C++ model, relaxed operations make the flag accesses atomic but do not order the ordinary payload access. If producer and consumer are concurrent and no other happens-before edge exists, the ordinary accesses can form a data race and the source program has undefined behavior. Binary investigation must still establish the emitted accesses, target memory model and security effect rather than claim that one particular stale value is guaranteed.

## Primitive and impact limits

The direct result can be use of partial, stale, wrong-generation or invalid-lifetime state. Consequences can include incorrect authorization, type confusion, invalid pointer use, disclosure, corruption, or crash, depending on the prematurely consumed fields.

## Related knowledge and primary sources

`reference-concurrency-memory-order-atomic-invariants` and `architecture-memory-ordering-barrier-evidence` define publication and machine-order evidence. This profile repeats lifetime, publication-object, observed-write, and consumer binding locally.

Reviewed 2026-10-09 against the C++ [atomic ordering rules](https://eel.is/c++draft/atomics.order), [data-race and happens-before rules](https://eel.is/c++draft/intro.races), and [object lifetime rules](https://eel.is/c++draft/basic.life). The source is constructed.
