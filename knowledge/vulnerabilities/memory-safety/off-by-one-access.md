---
id: vulnerability-memory-off-by-one-access
title: Off-by-one read or write at an object boundary
kind: vulnerability
topics: [memory-safety, off-by-one, terminators, bounds, fencepost]
platforms: [cross-platform]
architectures: [any]
---

# Off-by-one read or write at an object boundary

## Definition and violated invariant

An off-by-one vulnerability accepts or produces exactly one element beyond or before the intended range because a count, endpoint or loop condition differs by one from the required contract. An `N`-element array has valid indices `0` through `N-1`; an exclusive end pointer may be formed under applicable language rules but not dereferenced.

The one extra access can be a read or write and can span more than one byte when the element width is larger. Missing capacity for a string terminator is a common instance, not the only form.

## Conditions that establish the issue

Recover whether each value is a count, last valid index, inclusive end or exclusive end. Prove a reachable access at `index == N`, `index == -1`, or another one-element boundary error relative to the actual object. Include element width and any terminator, sentinel, header or trailer required by the consumer.

For a write, identify the byte values and adjacent state. For a read, identify how the extra value is used or exposed. A one-element logical error that remains within a deliberately larger object can still be an intra-object violation if it crosses a subobject boundary.

## Evidence that is not sufficient

Use of `<=`, increment-before-test, a capacity-sized copy or a write of zero after a copy is not sufficient. The endpoint may be inclusive by contract, the allocation may include a sentinel slot, the loop may skip the apparent boundary on all feasible paths, or the terminator may be written inside reserved capacity.

Do not assume byte capacity and element count are interchangeable. Determine the element type, encoded unit and actual instruction width.

## Investigation sequence

Write the intended range using half-open notation and label every boundary value. Trace allocation count, accepted payload, copied elements and final sentinel independently. Inspect branch order to determine whether an access occurs before or after the bound test, especially in post-increment and do-while loops.

At assembly level, recover comparison operands, signedness, branch condition, index update and access width. Check empty, one-element, full-capacity and first-rejected cases as mathematical paths, while ensuring those values can reach the binary representation.

## Constructed source example

This hypothetical function permits a payload equal to destination capacity, then writes a terminator at the exclusive end:

```c
int copy_text(char *destination, const char *source,
              size_t payload_length, size_t capacity)
{
    if (payload_length > capacity)
        return -1;
    memcpy(destination, source, payload_length);
    destination[payload_length] = '\0';
    return 0;
}
```

When `payload_length == capacity`, the copy can fill the object and the terminator writes one byte beyond it. If the caller's object has `capacity + 1` bytes and `capacity` intentionally denotes payload capacity, the same code can be valid; recover the parameter contract and real object extent.

## Constructed Windows x64 representation

Under Windows x64 the constructed arguments arrive as destination `RCX`, source `RDX`, payload length `R8` and capacity `R9`. An omitted prologue preserves `RDI` and `RBX` and reserves call space:

```asm
cmp  r8, r9
ja   reject               ; equality is accepted
mov  rdi, rcx
mov  rbx, r8
call memcpy               ; existing argument registers already match
mov  byte ptr [rdi+rbx], 0
```

The `JA` condition accepts equality, and the later byte store uses the exclusive endpoint. Confirm that `capacity` is the full object extent and no extra terminator slot exists. Different register allocation or inlining does not change that proof obligation.

## Primitive and impact limits

The direct primitive is one element of out-of-bounds access. Record direction, element width, byte value, neighboring object and subsequent use. A zero-byte overwrite may alter a pointer, length or flag only under a demonstrated layout; it may instead touch padding or fault.

Information disclosure and code execution require observable use or control-bearing corruption. The phrase "off by one" describes the boundary error, not its severity.

## Related knowledge and primary sources

`reference-native-bounds-objects-terminators` owns inclusive/exclusive endpoints, one-past pointers and terminator capacity. This profile repeats the count-versus-endpoint distinction and equality case needed to recognize the vulnerability in isolation.

Reviewed 2026-10-09 against [MITRE CWE-193](https://cwe.mitre.org/data/definitions/193.html), C array and string rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [pointer arithmetic](https://eel.is/c++draft/expr.add), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The source and assembly are constructed.
