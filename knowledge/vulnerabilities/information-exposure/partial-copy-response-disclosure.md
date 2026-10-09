---
id: vulnerability-information-partial-copy-response-disclosure
title: Partial operation followed by an excessive response copy
kind: vulnerability
topics: [information-disclosure, partial-read, short-copy, response-length]
platforms: [cross-platform]
architectures: [any]
---

# Partial operation followed by an excessive response copy

## Definition and violated invariant

This vulnerability occurs when a producer defines only part of a destination but a later response exposes a larger range, allowing untouched bytes from that allocation to cross a trust boundary. Common triggers include short reads, partial copies, conversion progress, failed decoding, truncated device transfers and APIs whose result reports bytes actually produced.

The violated invariant is that the transmitted range must be contained in the bytes defined and authorized on that path. A partial operation is normal behavior under many APIs; the defect is ignoring its result or otherwise claiming more valid output than it established.

## Conditions that establish the issue

Recover the producer's contract and its actual result, including zero, partial, failure and pending outcomes. Show that only interval `[0, produced)` is defined by the operation, a later sink uses a count greater than `produced`, the uncovered interval was not independently initialized, and an observer across the relevant boundary receives it.

Track progress and validity separately. Some APIs define partial output on selected errors, while others leave output unspecified or guarantee no transfer. Use the exact platform contract rather than treating all failures alike.

## Evidence that is not sufficient

A call that can complete partially, an unchecked return value or a fixed-size send is a lead, not proof. A prior full clear, complete overwrite on all reaching paths, protocol guarantee of an exact producer length, wrapper enforcement or a sink count clamped elsewhere can refute the candidate.

A short response caused by the same result is not disclosure. An excessive count can instead cause an out-of-bounds read when it exceeds allocation capacity; classify both conditions if the emitted interval is larger than the object itself.

## Investigation sequence

Name four quantities with units: destination capacity, bytes produced, bytes considered logically valid and bytes exposed. Trace their definitions through signedness conversions, error handling, retries and helper calls. At each sink, prove the count and base used on the exercised path and compare the complete interval with both capacity and definite initialization.

At binary level, follow the producer's return register or out-parameter and determine whether it reaches the sink count. A constant or stale count at the sink is suspicious, but confirm that another operation did not initialize the tail. Examine loops because accumulated progress can be correct even when an individual operation is short.

## Constructed source example

POSIX `read` may return fewer bytes than requested, including when interrupted after transferring some data. This hypothetical function sends the requested capacity rather than the positive count returned:

```c
void relay(int source_fd, int client_fd)
{
    unsigned char response[64];
    ssize_t n = read(source_fd, response, sizeof(response));
    if (n > 0)
        send(client_fd, response, sizeof(response), 0);
}
```

If `0 < n < 64`, only the first `n` bytes are established by this `read`; bytes `n` through 63 can expose prior stack contents unless another reaching write defined them. The path is safe from this defect if the send count is `n` or the complete buffer was deliberately initialized and its entire content is authorized.

## Constructed x86-64 representation

Under the System V x86-64 calling convention, a possible construction discards the positive byte count in `RAX` and reloads 64 for the sink:

```asm
lea  rsi, [rsp+32]        ; response
mov  edx, 64              ; requested read count
call read@PLT
test rax, rax
jle  done
mov  edi, dword ptr [client_fd]
lea  rsi, [rsp+32]
mov  edx, 64              ; excessive send count when RAX < 64
xor  ecx, ecx             ; flags
call send@PLT
```

The fixed second count is meaningful only with the producer and sink contracts, no intervening full initialization and a feasible short positive result. Real compilers may preserve values in different registers or inline either operation.

## Primitive and impact limits

Record the maximum uncovered interval, prior storage provenance, repeatability and recipient. The attacker may control the short length without controlling the leaked tail. Demonstrate the protected data present before claiming credential, pointer or cross-tenant exposure.

The condition is an information disclosure primitive. It does not itself establish memory corruption or code execution; a count beyond capacity additionally creates an out-of-bounds read candidate.

## Related knowledge and primary sources

`reference-windows-response-structures-initialization` owns shared definite-write and response-range reasoning. This profile keeps the partial-result contract and producer-to-sink count comparison local for isolated retrieval.

Reviewed 2026-10-09 against the POSIX [`read()`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/read.html) and [`send()`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/send.html) specifications, [MITRE CWE-457](https://cwe.mitre.org/data/definitions/457.html) and the [System V AMD64 ABI](https://gitlab.com/x86-psABIs/x86-64-ABI). The examples are constructed; other producer and transport APIs require their own result and output-validity contracts.
