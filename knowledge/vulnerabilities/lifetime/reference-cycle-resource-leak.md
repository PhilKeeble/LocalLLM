---
id: vulnerability-lifetime-reference-cycle-resource-leak
title: Reference cycle or missed release with security-relevant resource growth
kind: vulnerability
topics: [lifetime, memory-leak, reference-cycle, resource-exhaustion, ownership]
platforms: [cross-platform]
architectures: [any]
---

# Reference cycle or missed release with security-relevant resource growth

## Definition and violated invariant

A lifetime leak occurs when ownership remains after the resource is no longer logically needed, including a reference-count cycle with no external owner or a missing release on a feasible path. It becomes a security vulnerability when an actor can repeat or amplify the leak until a relevant memory, handle, descriptor, thread, mapping, quota, or privileged-resource limit is exhausted or isolation state is retained incorrectly.

Garbage collection can reclaim unreachable managed cycles, while ordinary strong reference counting cannot collect a cycle solely by decrementing external owners. Apply the actual ownership system rather than treating every graph cycle as a leak.

## Conditions that establish the issue

Identify every strong ownership edge, roots, weak edges, release conditions, and non-memory resources retained by the object graph. Prove that the graph or resource remains live after its intended terminal event and that attacker-reachable repetition or duration can exceed a concrete limit or preserve a security-sensitive capability.

For one missing cleanup, establish that no later owner, cache eviction, arena teardown, process lifetime, or documented transfer accounts for it. Intentional bounded caching is not unbounded leakage.

## Evidence that is not sufficient

A cycle in a heap graph, absent destructor call, growing counter, or one unreleased allocation is not sufficient. The runtime may trace cycles, an owner may deliberately retain a bounded cache, or another cleanup scope may release the resource.

High memory usage alone does not identify the retained object or attacker-controlled growth path.

## Investigation sequence

Build an ownership graph with strong, weak, borrowed, and external-resource edges. Remove temporary analysis roots, then identify which edge prevents the expected terminal release. Trace all normal, error, cancellation, timeout, and shutdown paths.

Quantify retained bytes or scarce objects per attacker action, maximum concurrent instances, reclamation events, and effective system or application limit. Keep the lifetime root cause distinct from the resulting resource-exhaustion primitive.

## Allocator fragmentation as a separate exhaustion path

Fragmentation can deny an allocation even when total free memory exceeds the requested size because the allocator cannot satisfy the required size, alignment, address-space or pool constraints from available extents. Establish attacker influence over allocation sizes and lifetimes, the target allocator or pool behavior, and a consequential failed request. Allocation/free churn or a fragmented-looking heap snapshot alone is not proof; compaction, segregated pools, virtual remapping or an adequate largest free extent may preserve service.

Track internal fragmentation, unusable space within live allocations, separately from external fragmentation between them. A retained-object leak monotonically removes capacity, while fragmentation depends on the shape and ordering of live and free extents; an investigation may establish either or both.

## Constructed source example

```cpp
struct peer {
    std::shared_ptr<peer> other;
    native_handle channel;
};

void connect(std::shared_ptr<peer> a, std::shared_ptr<peer> b)
{
    a->other = b;
    b->other = a;
}
```

After external owners release `a` and `b`, their mutual strong references keep both objects and channels alive unless another path breaks the cycle. A vulnerability claim still needs repeatable untrusted creation and a consequential channel, handle, or memory limit; one intentional process-lifetime pair is insufficient.

## Primitive and impact limits

The direct primitive is retained ownership or missing cleanup. Consequences can include denial of service, quota bypass, stale authority, or cross-tenant state retention. Memory corruption does not follow from a leak alone.

## Related knowledge and primary sources

`reference-concurrency-refcounts-reuse` defines ownership accounting, while runtime references distinguish tracing collectors from reference counting. This profile repeats the repeatability and concrete-limit requirements locally.

Reviewed 2026-10-09 against C++ [`shared_ptr`](https://eel.is/c++draft/util.smartptr.shared), C++ [`weak_ptr`](https://eel.is/c++draft/util.smartptr.weak), [MITRE CWE-401](https://cwe.mitre.org/data/definitions/401.html), and Vulkan's distinct [`VK_ERROR_FRAGMENTED_POOL`](https://registry.khronos.org/vulkan/specs/latest/man/html/VkResult.html) result as one concrete pool contract. The example is constructed, `native_handle` intentionally leaves platform release details unspecified, and fragmentation behavior remains allocator-specific.
