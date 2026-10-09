---
id: vulnerability-failure-result-and-output-validity-misuse
title: API result, partial progress or output-validity misuse
kind: vulnerability
topics: [error-handling, return-value, status-code, out-parameter, partial-read, stale-output]
platforms: [cross-platform]
architectures: [any]
---

# API result, partial progress or output-validity misuse

## Definition and violated invariant

This vulnerability occurs when code ignores or misinterprets a return value, status, exception, last-error channel, byte count, or out-parameter contract and then treats an operation or output as successfully complete. The invariant is that every consumed output and committed assumption must be justified by the exact success or partial-progress result defined by that API.

Failure conventions are not interchangeable. Zero can mean success, end of input, no progress, false, or failure; negative values can be errors or valid domain values; warning/status success classes can still describe partial or alternate outcomes.

## Conditions that establish the issue

Recover the exact API and overload, return type width/signedness, success predicate, when secondary error state is valid, which outputs are initialized for each result, units of progress, retry rules, and consumer. Prove a feasible result leaves an output invalid, stale, partial, or shorter than assumed and that later code uses the unsupported portion or success state in a security-sensitive operation.

For exceptions or asynchronous completion, distinguish submission success from terminal success and identify where the result is observed. A last-error value is meaningful only when the API contract says to consult it for the returned result.

## Evidence that is not sufficient

An unchecked-looking call, nonzero error variable, short operation, or output buffer reused across calls is not sufficient. The API may guarantee full progress, initialize outputs on failure, encode success in the apparent error value, or have a caller/callee wrapper that enforces the result. A stale value is harmless if no unsupported bytes or state are consumed.

## Investigation sequence

Build a result table for success, zero progress/end, partial progress, retryable interruption, terminal failure, timeout, cancellation, and exception. For each row record valid outputs and lengths. Trace the actual branch predicate and conversions, then follow only initialized or completed extents to their consumers.

At machine level, preserve condition-code provenance and return-register width. A 32-bit status compared as a 64-bit pointer or a signed count widened as unsigned can change the apparent success domain.

## Constructed POSIX example

```c
unsigned char header[16];
ssize_t n = read(fd, header, sizeof header);
if (n < 0) return ERROR;
return parse_header(header, sizeof header);
```

POSIX `read` can successfully return fewer bytes than requested and returns zero at end of file. The example passes 16 bytes to the parser even when only `n` bytes were defined by this call, so stale stack contents can affect parsing. The finding disappears if `parse_header` receives `n`, the code loops until the required framing is complete, or another proven initialization makes the unfilled bytes semantically irrelevant.

## Constructed System V AMD64 result check

```asm
call read
test rax, rax
js   error
mov  esi, 10h            ; parse_header length = 16, ignoring RAX progress
lea  rdi, [rsp+30h]      ; parse_header buffer = header
call parse_header
```

The arguments for `read` are assumed to have been staged before the excerpt; System V AMD64 returns its `ssize_t` result in `RAX` and passes the first two `parse_header` arguments in `RDI` and `RSI`. The defect is the mismatch between returned progress and consumed extent.

## Primary sources and scope

Reviewed 2026-10-09 against POSIX [`read`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/read.html), POSIX [`write`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/write.html), Microsoft [`ReadFile`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile), and Microsoft [last-error handling](https://learn.microsoft.com/en-us/windows/win32/debug/retrieving-the-last-error-code). The exact API contract controls output validity; the examples are not universal short-I/O rules.
