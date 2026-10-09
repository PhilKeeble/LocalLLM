---
id: vulnerability-memory-incorrect-pointer-arithmetic
title: Incorrect pointer arithmetic and scaled offset
kind: vulnerability
topics: [memory-safety, pointer-arithmetic, bounds, scaling, one-past]
platforms: [cross-platform]
architectures: [any]
---

# Incorrect pointer arithmetic and scaled offset

## Definition and violated invariant

An incorrect-pointer-arithmetic vulnerability computes or dereferences an address outside the intended array object because an offset is scaled in the wrong unit, applied to the wrong base, wrapped, or confused with a one-past endpoint. In C and C++, adding an integer to a typed pointer scales by the pointed-to type; a one-past pointer can participate in limited arithmetic and comparison but cannot be dereferenced.

At binary level the decisive condition is a reachable memory access whose full byte range exceeds the live intended object. Keep source-language undefined behavior distinct from the observed machine address and effect.

## Conditions that establish the issue

Recover the base object, its byte extent, offset origin and unit, implicit or explicit scale, arithmetic width, and access width. Prove a feasible path where the effective address range is outside that object. Check negative offsets, wrapped additions, and whether the base already points to a field or interior element.

For an endpoint, distinguish forming or comparing it from loading or storing through it. A computed address that is never consumed does not establish an out-of-bounds access.

## Evidence that is not sufficient

An `LEA` with a scale, pointer addition in a decompiler, or an address numerically beyond one inferred field is not sufficient. The scale may match an element type, the allocation may contain a larger intentional array, or the decompiler may have selected the wrong base type.

Readable adjacent memory and noncrashing execution do not extend the object. Conversely, prove that an apparent byte offset was not deliberately divided or cast to a byte pointer before use.

## Investigation sequence

Express every address as `base + index * scale + displacement` in bytes, then track the complete access interval. Relate the check to that same byte expression, including representability. Identify object and subobject boundaries from allocation, format, type metadata, and repeated access patterns.

At branches, recover signedness and whether comparison occurs before or after scaling. Check the empty range, last valid element, one-past value, and first invalid value only when the input representation can supply them.

## Constructed source example

This hypothetical function validates `byte_offset` as bytes but applies it as an index of 32-bit elements:

```c
int read_value(const uint32_t *base, size_t available_bytes,
               size_t byte_offset, uint32_t *result)
{
    if (available_bytes < sizeof(*result) ||
        byte_offset > available_bytes - sizeof(*result))
        return -1;
    *result = base[byte_offset];
    return 0;
}
```

With 16 available bytes and `byte_offset == 12`, the check accepts the last four-byte byte range, but the typed index loads at byte offset 48. Casting `base` to a byte pointer before adding the offset would change this conclusion.

## Constructed Windows x64 representation

Under Windows x64 the arguments arrive as base `RCX`, available bytes `RDX`, byte offset `R8`, and result pointer `R9`:

```asm
cmp  rdx, 4
jb   reject
lea  rax, [rdx-4]
cmp  r8, rax
ja   reject
mov  eax, dword ptr [rcx+r8*4] ; byte offset is scaled again
mov  dword ptr [r9], eax
```

The check is in bytes while the load uses a scale of four. Confirm that `RCX` is the same 16-byte object and that `R8` was not already an element index despite its recovered name.

## Primitive and impact limits

The direct primitive is an out-of-bounds read or write at the computed address. Record direction, width, controllability, repeatability, and adjacent state. An invalid computed pointer that faults before access supports denial of service rather than a stronger primitive.

Disclosure or code execution requires an observable read or security-relevant write plus the necessary layout and control. Source-language undefined behavior alone does not prove a particular compiled effect.

## Related knowledge and primary sources

`reference-native-bounds-objects-terminators` owns object ranges and one-past semantics, while `reference-native-integer-size-buffer-arithmetic` owns representable offsets. This profile repeats the byte-expression proof required in isolation.

Reviewed 2026-10-09 against C pointer arithmetic in [WG14 N1570 section 6.5.6](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [pointer arithmetic](https://eel.is/c++draft/expr.add), [MITRE CWE-469](https://cwe.mitre.org/data/definitions/469.html), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The source and assembly are constructed.
