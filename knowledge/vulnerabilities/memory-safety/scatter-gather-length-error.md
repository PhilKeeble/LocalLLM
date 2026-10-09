---
id: vulnerability-memory-scatter-gather-length-error
title: Scatter, gather, and descriptor-chain length error
kind: vulnerability
topics: [memory-safety, scatter-gather, descriptors, vectored-io, lengths]
platforms: [cross-platform]
architectures: [any]
---

# Scatter, gather, and descriptor-chain length error

## Definition and violated invariant

A segmented-buffer vulnerability occurs when a descriptor count, individual range, aggregate length, chain termination, or ownership/lifetime contract does not match the buffers actually processed. The descriptor array must contain the stated entries, each entry must describe a valid range for the operation, and their security-relevant total must be representable and derived from those same entries.

Validation of an externally declared total does not bound the sum of descriptor lengths unless the program proves they agree. Likewise, a valid sum does not validate an individual pointer, range, direction, or lifetime.

## Conditions that establish the issue

Recover descriptor layout, count, per-entry base and byte length, traversal order, end condition, address domain, and operation direction. Prove a reachable entry or aggregate access exceeds a live object, uses stale storage, or violates an ownership boundary. For a contiguous destination, compare every cumulative offset and segment length with its capacity using overflow-safe arithmetic.

For asynchronous or device operations, establish how long descriptors and backing buffers must remain valid and which actor owns each entry. A successfully submitted request is not proof of safe completion.

## Evidence that is not sufficient

Use of `iovec`, `WSABUF`, DMA descriptors, multiple buffers, or an aggregate sum is not sufficient. The operating system or device API may reject an invalid count or total, and the application may correctly preserve every backing range until completion.

An API's byte-count result does not mean that many descriptors were filled. Partial operations require mapping the aggregate result across ordered entry lengths.

## Investigation sequence

Enumerate the descriptor array from its proven extent and cap traversal before following pointers or next fields. Build a table of each base, length, direction, owner, address domain, and lifetime. Accumulate lengths in a representable domain and compare the same computed total with allocation, protocol, and API limits.

Trace partial completion and error paths. In binary code, distinguish the descriptor count from per-entry length and aggregate bytes; recover structure stride and look for cumulative-offset updates that use a different width or source from validation.

## Constructed source example

This hypothetical gather routine trusts a separately supplied total instead of deriving the copy bound from its segment descriptors:

```c
struct segment { const uint8_t *data; size_t length; };

int gather(uint8_t *output, size_t output_capacity,
           const struct segment *segments, size_t count,
           size_t declared_total)
{
    if (declared_total > output_capacity)
        return -1;
    size_t position = 0;
    for (size_t i = 0; i < count; ++i) {
        memcpy(output + position, segments[i].data, segments[i].length);
        position += segments[i].length;
    }
    return 0;
}
```

If `declared_total` is 16 while two readable segments each have length 12 and output capacity is 16, the second copy writes beyond the destination. The example also needs a valid descriptor array and representable cumulative arithmetic; an enforced equality between the checked total and sum would refute it.

## Constructed descriptor-loop representation

The core binary dataflow can be recognized independently of a specific ABI:

```asm
compare declared_total, output_capacity
reject_if_above
position = 0
for each descriptor:
    copy(output + position, descriptor.base, descriptor.length)
    position = position + descriptor.length
```

The vulnerability is the missing relationship between the checked value and the lengths driving copies, not the syntax of the loop. Verify bounds on descriptor count and cumulative addition as separate proof obligations.

## Primitive and impact limits

The direct primitive can be an out-of-bounds read or write, use after free during asynchronous completion, disclosure of uninitialized segment tails, or unbounded/cyclic descriptor traversal. State which contract fails and which concrete effect follows.

Impact depends on direction, address-domain translation, data control, completion behavior, adjacent state, and device or process privilege. A rejected request or short transfer may have no memory-safety effect.

## Related knowledge and primary sources

`reference-native-scatter-gather-buffer-contracts` defines descriptor and partial-transfer semantics. This profile repeats the independent array, range, total, and lifetime obligations so it remains useful without following that link.

Reviewed 2026-10-09 against POSIX [`readv` and `writev`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/readv.html), Microsoft [`WSABUF`](https://learn.microsoft.com/en-us/windows/win32/api/ws2def/ns-ws2def-wsabuf), Microsoft [`WSARecv`](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-wsarecv), and [MITRE CWE-130](https://cwe.mitre.org/data/definitions/130.html). The source and pseudodisassembly are constructed.
