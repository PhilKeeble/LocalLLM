---
id: vulnerability-memory-missing-invalid-string-terminator
title: Missing, misplaced, or overwritten string terminator
kind: vulnerability
topics: [memory-safety, strings, null-termination, over-read, ffi]
platforms: [cross-platform]
architectures: [any]
---

# Missing, misplaced, or overwritten string terminator

## Definition and violated invariant

A terminator vulnerability occurs when a consumer scans a character sequence until a sentinel that is absent from the valid readable or writable object, placed in the wrong unit or position, or overwritten before use. A C string requires a reachable null character within accessible storage; a counted byte sequence does not acquire that contract merely because it contains text.

The missing terminator is dangerous only when a sentinel-based operation is reachable. A fixed-width field consumed exclusively with a validated count may be intentionally unterminated.

## Conditions that establish the issue

Identify the producer, exact representation, character or code-unit width, object extent, initialized extent, and later sentinel-based consumer. Prove there is a feasible path with no valid terminator before the consumer crosses the object's readable range. For a terminator write, prove its full width and offset fit the destination.

Across an FFI or platform API, establish whether the parameter is counted, null-terminated, or uses a sentinel count such as `-1`. A terminator in an adjacent allocation or readable page may prevent a fault while still allowing disclosure or semantic confusion.

## Evidence that is not sufficient

Use of `memcpy`, a fixed-width record, or absence of an explicit final zero is not sufficient. The source may include a terminator in the copied extent, the destination may have been zero-initialized and remain so at a reachable position, or every consumer may be count bounded.

Do not infer safety from one noncrashing execution: incidental zero bytes beyond the object are not part of its contract. Conversely, do not infer an over-read without locating a sentinel-based load or API.

## Investigation sequence

Trace initialization, copies, concatenation, mutation, and final use of the buffer. Mark where a terminator is known to exist and whether later writes can overwrite it. Distinguish bytes from wide code units and determine whether returned lengths include the terminator.

In assembly, identify the scan loop or imported string routine, its starting pointer, access width, stopping comparison, and any independent bound. Compare the scan's possible range with the live object's extent and initialized bytes. Inspect empty, exact-capacity, embedded-null, and delimiter-free cases.

## Constructed source example

This hypothetical function fills a fixed-size byte array and then passes it to a C-string consumer:

```c
size_t measured_name(const char *input)
{
    char name[16];
    memcpy(name, input, sizeof name);
    return strlen(name);
}
```

If the 16 copied bytes contain no null, `strlen` continues reading beyond `name` until it encounters a zero or faults. The copy also requires 16 readable source bytes. If the input contract guarantees a null within those bytes and that guarantee is enforced, the constructed over-read is absent.

## Constructed Windows x64 representation

Under Windows x64, the input pointer arrives in `RCX`. This complete local layout reserves 32 bytes of call space and a 16-byte array while maintaining call alignment:

```asm
sub  rsp, 38h
mov  rdx, rcx             ; memcpy source
lea  rcx, [rsp+20h]       ; 16-byte local destination
mov  r8d, 10h
call memcpy
lea  rcx, [rsp+20h]
call strlen               ; no length argument
add  rsp, 38h
ret
```

The call to `strlen` has no independent bound and therefore relies on a null within readable storage. Confirm the imported or inlined routine, input guarantee, stack layout, and whether the compiler proved termination by another route.

## Primitive and impact limits

The direct primitive is usually a sequential over-read, but a misplaced terminator write can instead be an out-of-bounds write. Record direction, code-unit width, maximum reachable extent, surrounding data, fault behavior, and whether the result influences an observable output or later allocation.

An over-read may expose adjacent stack or heap data, but disclosure requires a sink that returns, logs, compares, or otherwise reveals it. A fault alone supports denial of service; code execution needs an additional write or control-flow mechanism.

## Related knowledge and primary sources

`reference-native-bounds-objects-terminators` owns object and terminator capacity, while `reference-native-strings-copy-format` distinguishes counted ranges from C strings. This profile includes the consumer and reachable-sentinel proof needed in isolation.

Reviewed 2026-10-09 against [MITRE CWE-170](https://cwe.mitre.org/data/definitions/170.html), C string definitions and `strlen` in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), POSIX [`strlen`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/strlen.html), and the [Windows x64 stack and calling convention](https://learn.microsoft.com/en-us/cpp/build/stack-usage). The source and assembly are constructed.
