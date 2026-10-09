---
id: vulnerability-lifetime-reference-count-premature-release
title: Reference-count error causing premature release or wraparound
kind: vulnerability
topics: [lifetime, reference-counting, overflow, underflow, ownership]
platforms: [cross-platform]
architectures: [any]
---

# Reference-count error causing premature release or wraparound

## Definition and violated invariant

A reference-count vulnerability occurs when increments and decrements do not match actual owning references, acquisition occurs after lifetime protection is lost, or fixed-width arithmetic reaches an unintended zero or wrapped state. Every owner must acquire while the object is live, retain through its last use, and release exactly once; the zero transition must initiate destruction only after no owner or admitted use remains.

Atomic arithmetic protects an update from tearing or loss but does not prove safe lookup, ownership accounting, payload synchronization, or object generation.

## Conditions that establish the issue

Recover initial count, counter width and behavior, every ownership acquisition, transfer and release, lookup protection, zero transition, destruction, and later use. Prove one feasible sequence produces premature zero, unsafe acquisition from zero or freed storage, or reachable wraparound that changes destruction behavior.

For saturating implementations, apply the exact target contract. Saturation can prevent premature release while causing a leak; it is not equivalent to ordinary wrapping arithmetic.

## Evidence that is not sufficient

An increment/decrement pair, atomic instruction, large count, missing nearby retain, or nonzero counter is not sufficient. Ownership may transfer without changing the count, another owner may cover the use, or a helper may combine lookup and acquisition safely.

Count underflow often produces a large count and leak rather than immediate free. State the actual transition and consumer instead of assuming every arithmetic error is UAF.

## Investigation sequence

Draw an ownership graph and event timeline. Label borrowed and owning references, protection around lookup, handoff, callback or queue admission, final decrement, release callback, and storage reclamation. Relate each machine update to one semantic ownership edge.

In assembly, recover update width, atomicity, zero test, and release target. Inspect whether a pointer remains protected while its count is acquired and whether count storage can already have been freed or reused.

## Constructed source and assembly example

```c
void submit(struct object *object)
{
    queue_work(run_object, object);       /* queued owner not retained */
}

void owner_done(struct object *object)
{
    release(object);                      /* may reach zero before worker */
}
```

If the queue borrows the raw pointer and `release` implements `if (atomic_fetch_sub(&object->refs,1) == 1) destroy(object)`, the owner can destroy the object before `run_object` uses it. A machine pattern such as `lock sub dword ptr [object+refs],1; jne still_live; call destroy` proves only the decrement mechanics; the missing queued ownership and later use complete the finding.

## Primitive and impact limits

The direct result can be premature destruction, stale acquisition, reference leak, or resurrection of invalid state. A UAF, double release, resource exhaustion, or controlled dispatch must be traced as a separate consequence.

## Related knowledge and primary sources

`reference-concurrency-refcounts-reuse` defines acquisition, zero transition, saturation, and ABA distinctions. This profile repeats the ownership-to-count mapping required alone.

Reviewed 2026-10-09 against Linux [kref](https://docs.kernel.org/core-api/kref.html), Linux [`refcount_t` versus `atomic_t`](https://docs.kernel.org/core-api/refcount-vs-atomic.html), C++ [`shared_ptr` ownership](https://eel.is/c++draft/util.smartptr.shared), and [MITRE CWE-911](https://cwe.mitre.org/data/definitions/911.html). The example and instruction pattern are constructed.
