---
id: vulnerability-concurrency-shared-memory-data-race
title: Shared-memory data race with a security-relevant invariant violation
kind: vulnerability
topics: [concurrency, data-race, shared-memory, lifetime, invariants]
platforms: [cross-platform]
architectures: [any]
---

# Shared-memory data race with a security-relevant invariant violation

## Definition and violated invariant

A shared-memory data race occurs when potentially concurrent operations conflict on the same memory location, at least one is a write, and the applicable language or runtime model supplies no required ordering or synchronization. A vulnerability finding additionally requires the race to violate a security-relevant invariant such as pointer/length consistency, object lifetime, authorization state, ownership, or one-time action.

Under the C++ abstract machine, qualifying non-atomic conflicting accesses without happens-before ordering produce undefined behavior. Binary analysis must still recover the emitted accesses and synchronization rather than assume one intuitive interleaving is the only possible behavior.

## Conditions that establish the issue

Identify the exact shared allocation and byte ranges, all conflicting accesses, participating threads or asynchronous contexts, synchronization objects and ordering edges, object lifetime, and the compound invariant. Show a feasible overlap with no applicable ordering and trace a resulting value combination or lifetime transition into a security-relevant consumer.

Distinguish an ordinary data race from a logical race whose individual accesses are synchronized but whose multi-step operation is not atomic. Both can be vulnerabilities, but they require different evidence.

## Evidence that is not sufficient

Two functions touching the same field, a non-atomic instruction, missing visible fence, ThreadSanitizer report name, or concurrent execution is not sufficient. The accesses may be read-only, mutually exclusive, protected by an inlined or API-level primitive, or refer to different object generations.

A race report identifies observed conflicting accesses under the tool's model; it does not by itself prove attacker reachability, invariant violation, or impact in the shipped binary.

## Investigation sequence

Bind each access to allocation identity, offset, width, operation and object generation. Build a schedule containing the last protecting acquisition or publication, the conflicting operations, and the first security-relevant consumer. Include lifetime start and end as conflicts where the language model does.

Then recover the actual target model: source-language rules, compiler lowering, machine instructions, memory type, and OS or runtime synchronization. Check all writers and readers, not only the pair that first exposed the race.

## Constructed pointer/length example

```c
void consume(struct channel *channel)
{
    uint8_t *data = channel->data;
    size_t length = channel->length;
    parse(data, length);
}
```

Constructed schedule: thread A loads the old `data`; thread B replaces `data` and `length` and releases the old allocation without synchronization visible to A; thread A loads the new `length` and calls `parse` with a stale pointer and unrelated extent. The finding requires those actual loads, a feasible replacement and reclamation interval, and no retained reference or snapshot protocol. The source fragment alone does not establish that schedule or the compiler's emitted behavior.

## Primitive and impact limits

The direct result can be mixed-version state, stale-object access, missed authorization change, duplicate action, or corrupted accounting. Memory disclosure, corruption, privilege change, or code execution depends on the particular invariant and downstream consumer.

## Related knowledge and primary sources

`reference-concurrency-memory-order-atomic-invariants`, `reference-concurrency-refcounts-reuse`, and `reference-validation-tsan-race-evidence` define ordering, lifetime, and diagnostic limits. This profile repeats the conflicting-access and impact proof locally.

Reviewed 2026-10-09 against the C++ [data-race and happens-before rules](https://eel.is/c++draft/intro.races), [atomic ordering rules](https://eel.is/c++draft/atomics.order), and Linux kernel [memory-barrier documentation](https://docs.kernel.org/core-api/wrappers/memory-barriers.html). The source and schedule are constructed.
