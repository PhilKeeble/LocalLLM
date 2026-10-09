---
id: reference-native-scatter-gather-buffer-contracts
title: Scatter and gather buffer descriptor contracts
kind: reference
topics: [scatter-gather, buffers, descriptors, vectored-io, lengths]
platforms: [windows, linux, macos, android, freebsd]
architectures: [any]
---

# Scatter and gather buffer descriptor contracts

## Descriptor arrays define multiple independent memory ranges

A scatter/gather request consists of a descriptor-array extent and one memory range per descriptor. Validate that the descriptor count fits the array, each base and length describes suitable live storage for the operation's direction and lifetime, and the aggregate length is representable. A valid total does not prove every descriptor range valid, while valid individual ranges do not prove their sum, ordering, or application-level message size is correct.

Overlapping descriptors may intentionally repeat data for a gather operation, but scatter writes can overwrite earlier results or create races with concurrent users. Determine whether the API assigns overlap semantics; do not infer disjointness from separate descriptors.

## POSIX vectored I/O uses byte lengths and ordered areas

POSIX `readv` and `writev` take an array of `iovec` entries whose `iov_base` identifies an area and whose `iov_len` is its byte length. The operations process areas in array order, completing one before moving to the next. The descriptor count must be positive and at most the implementation limit; an aggregate length that cannot be represented by `ssize_t` is an error under the specified contract.

Successful return values are aggregate bytes transferred, not the number of completed descriptors. Map a partial result back across the ordered lengths before deciding which bytes are initialized or consumed. An operating-system range check can reject an unmapped address but does not know a language allocation's intended subobject boundary.

## Windows WSABUF uses a byte length per entry

Each Windows `WSABUF` contains a buffer pointer and a `ULONG` length in bytes. `WSARecv` accepts a separate descriptor count, fills buffers in order without holes, and reports bytes received; stream receipt need not fill all supplied capacity. For overlapped calls, the service provider captures the `WSABUF` structures before returning, but the pointed-to buffers must still remain valid for the operation's lifetime.

Investigation must distinguish the lifetime of descriptor metadata from the lifetime and extent of its backing buffers. A count of captured descriptors is not ownership of their pointed-to storage, and a completion byte count must be distributed across the declared entries before treating later entries as initialized.

## Descriptor chains add ownership and termination rules

Device, DMA, firmware, and protocol descriptor chains can add next pointers, ownership bits, end markers, direction flags, alignment, and per-entry maximum lengths. Recover those target-specific contracts before following a chain. Bound the number of descriptors and detect cycles where the format forbids them; a valid byte total does not ensure the traversal terminates or that hardware and software agree on ownership.

Treat each address according to its domain: process virtual address, kernel virtual address, guest address, physical address, bus address, or mapped device address. Numeric overlap across domains does not establish aliasing, and address translation success does not establish that the range belongs to the intended object.

## Sources and verification scope

Reviewed 2026-10-09 against POSIX [`readv` and `writev`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/readv.html), Microsoft [`WSABUF`](https://learn.microsoft.com/en-us/windows/win32/api/ws2def/ns-ws2def-wsabuf), and Microsoft [`WSARecv`](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-wsarecv). Device-chain details remain target specific; this reference does not assign one operating system's lifetime or error rules to another.
