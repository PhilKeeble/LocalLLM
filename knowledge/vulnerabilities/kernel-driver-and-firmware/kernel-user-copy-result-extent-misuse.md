---
id: vulnerability-kernel-user-copy-result-extent-misuse
title: Kernel user-copy result or extent misuse
kind: vulnerability
topics: [kernel, drivers, user-copy, partial-copy, bounds, information-disclosure]
platforms: [cross-platform, linux, windows, android, freebsd]
architectures: [any]
---

# Kernel user-copy result or extent misuse

## Definition and violated invariant

This vulnerability occurs when privileged code requests, interprets or consumes a user/kernel copy with the wrong extent or result semantics, including treating partial transfer as complete. The invariant is that every kernel byte consumed must be established by the copy that succeeded, and every byte returned must fit both the caller's capacity and the kernel-defined response range.

Copy helpers differ: Linux bulk `copy_from_user` and `copy_to_user` return the number of bytes not copied, while single-value helpers use zero or a negative error. Windows request transfer methods provide different captured buffers and lengths. Never transfer one API's result convention to another.

## Conditions that establish the issue

Identify the exact helper, source and destination address spaces, requested extent, return convention, actual result, initialized ranges and later consumer. Prove a feasible fault or short-copy path leaves bytes invalid yet code parses, authorizes, copies back or reports them as complete.

For output, establish recipient capacity, bytes actually defined, completion count and delivery path. A partial user copy can be an availability or information-integrity issue without memory corruption if all accessed ranges remain allocated.

## Evidence that is not sufficient

An unchecked-looking copy call, nonzero return, user pointer or fixed structure size is not sufficient. A wrapper may convert the result, the helper may initialize a defined tail under its specific contract, the caller may reject later or the request layer may have already captured a bounded buffer.

Do not assume a successful pointer probe freezes contents or guarantees subsequent direct accesses. Immutability and result handling are separate conditions.

## Investigation sequence

Recover request origin, source/destination base, capacity and exact helper contract. Follow the return register or out-parameter through every branch. Track which byte intervals become valid and whether error, retry or fallback code consumes the remainder. For output, follow completion status and count to the actual boundary.

At binary level, distinguish a returned residual count from bytes copied and preserve signedness when it is compared. Identify whether a loop advances pointers and decrements the remaining count correctly after partial progress.

## Constructed Linux example

This hypothetical Linux handler reverses the meaning of `copy_from_user`:

```c
struct request req;
if (copy_from_user(&req, user_ptr, sizeof(req)) != sizeof(req))
    process(&req);
```

Linux bulk user-copy returns zero on complete success and a positive uncopied-byte count on partial transfer. The condition therefore processes full success and every partial copy for which at least one byte was transferred, while rejecting only the case where all `sizeof(req)` bytes were not copied. A finding still requires the reached fields and security consequence to be identified.

## Primitive and impact limits

The direct primitive can be stale/uninitialized kernel-data use, malformed request consumption, incomplete output, disclosure or denial of service. Out-of-bounds access requires an additional extent error; privilege escalation requires a controlled privileged effect or exploitable memory primitive.

## Related knowledge and primary sources

`reference-linux-kernel-interface-representations` and `reference-windows-driver-ioctl-buffer-access` provide platform contracts. This profile repeats the result-versus-valid-range rule locally.

Reviewed 2026-10-09 against Linux kernel [user-space memory access documentation](https://docs.kernel.org/core-api/mm-api.html#user-space-memory-access), Linux [kernel-hacking common routines](https://docs.kernel.org/kernel-hacking/hacking.html#copy-to-user-copy-from-user-get-user-put-user) and Microsoft [IOCTL buffer descriptions](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/buffer-descriptions-for-i-o-control-codes). The example is constructed and Linux-specific.
