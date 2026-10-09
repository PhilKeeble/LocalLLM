---
id: vulnerability-kernel-ring-descriptor-publication-ownership-error
title: Ring or descriptor publication, wrap, length or ownership error
kind: vulnerability
topics: [kernel, drivers, rings, descriptors, virtio, ownership, wraparound]
platforms: [cross-platform, virtualization, embedded]
architectures: [any]
---

# Ring or descriptor publication, wrap, length or ownership error

## Definition and violated invariant

This vulnerability occurs when a producer or consumer publishes, interprets or reuses a ring entry with the wrong index generation, ownership state, direction, length, chain or memory ordering. The invariant is that exactly one side owns each entry at a time, complete descriptor data becomes visible before ownership is published, and reuse occurs only after the matching completion generation.

Ring formats differ. Monotonic counters, masked indices, phase bits, wrap bits and explicit generations are not interchangeable, and virtio split and packed queues use different representations.

## Conditions that establish the issue

Recover negotiated format and features, ring size, counter widths, wrap/generation rule, descriptor layout, readable/writable direction, chain limit, translated buffer ranges, publication barrier, notification, completion and reuse. Prove a feasible producer state makes the consumer read an incomplete, stale, oversized or wrongly owned descriptor.

For indirect or chained entries, bound total nodes and bytes and detect cycles under the actual format. For completions, bind queue generation, descriptor identity and returned length to the outstanding request.

## Evidence that is not sufficient

Index wrap, equal producer/consumer values, a doorbell, reused slot or descriptor-chain loop in decompiler output is not sufficient. A generation bit may distinguish states, arithmetic may intentionally wrap, and the queue may validate or cap chains. Notification does not prove consumption, and completion of one entry does not prove all prior submissions completed unless the protocol orders them.

## Investigation sequence

Draw producer and consumer state for one slot across empty, prepared, published, consumed, completed and reusable phases. Preserve raw counter width before masking to an array index. Trace every descriptor field store and the barrier before the ownership or index update; do the symmetric analysis for completion.

At binary level, identify masks, modulo arithmetic, phase toggles, memory barriers and doorbell MMIO. Separate buffer direction from address permissions and request authorization. Follow reset and queue reinitialization so old completions cannot match new work.

## Constructed ring sequence

A hypothetical producer writes the available index before filling the descriptor's address and length. A device that observes the index first may consume stale fields from the previous slot generation. The sequence is vulnerable only if the memory model and device protocol permit that observation and no release barrier or strongly ordered transport exists.

## Primitive and impact limits

Direct effects include wrong-buffer DMA, stale completion, out-of-bounds device access, cross-request data confusion or denial of service. Host escape requires a host memory or authority effect beyond malformed guest-visible queue state.

## Related knowledge and primary sources

`reference-virtual-device-ring-dma` provides address-space and DMA contracts. This profile retains the ring generation and publication invariant locally.

Reviewed 2026-10-09 against [Virtio 1.2 sections 2.7 and 2.8](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html), Linux kernel [circular-buffer memory barriers](https://docs.kernel.org/core-api/circular-buffers.html) and Linux [DMA barriers](https://docs.kernel.org/core-api/dma-api-howto.html). The sequence is hypothetical and format-dependent.
