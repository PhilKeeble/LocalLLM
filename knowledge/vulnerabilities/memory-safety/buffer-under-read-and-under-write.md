---
id: vulnerability-memory-buffer-under-read-under-write
title: Buffer under-read and under-write from negative or wrapped indexes
kind: vulnerability
topics: [memory-safety, buffer-under-read, buffer-under-write, negative-index, signedness]
platforms: [cross-platform]
architectures: [any]
---

# Buffer under-read and under-write from negative or wrapped indexes

## Definition and violated invariant

A buffer under-read or under-write accesses memory before an intended object's beginning. It commonly arises when a negative index passes a maximum-only check, a subtraction crosses zero, or unsigned wrap turns a backward calculation into an unexpected address. Valid access requires both a lower bound and an upper bound in a consistent numeric domain.

Under-read and under-write are different primitives. A read can fault or expose preceding data; a write can corrupt a preceding object or subobject. The address being mapped does not make either access valid.

## Conditions that establish the issue

Prove the object's base and extent, the signed or wrapped index reaching address calculation, the actual machine extension and scale, and a feasible read or write before the base. Track the input representation: a negative mathematical test value is relevant only if the field and conversions can deliver it to the consuming operation.

For subtraction-derived offsets, recover the order and width of subtraction and comparison. An unsigned underflow can produce a large positive value that accesses after the object rather than immediately before it; classify the realized address, not the source expression's appearance.

## Evidence that is not sufficient

A signed comparison, `movsxd`, decrement, reverse loop or pointer below a decompiler variable is not sufficient. The accepted domain may deliberately include negative sentinel values that never reach memory access, the base may point inside a larger valid object, or an earlier lower-bound check may dominate the path.

Decompiler array bases are hypotheses. Recover the allocated object or subobject and intended indexing contract before calling an access an underflow.

## Investigation sequence

Record index width and signedness at input, validation, conversion and address formation. Determine whether the branch is signed or unsigned and whether the index is sign-extended, zero-extended or truncated before scaling. Calculate the effective address and complete access width relative to the true object base.

Check values `-1`, `0`, the largest valid index and boundary-adjacent wrapped values only when they are representable through the actual input path. For writes, trace controlled bytes and preceding layout; for reads, trace the consumed value to an observable output or decision.

## Constructed source and Windows x64 evidence

This hypothetical function checks only the upper bound of a signed index:

```c
void set_byte(unsigned char *buffer, int32_t index, int32_t length,
              unsigned char value)
{
    if (index < length)
        buffer[index] = value;
}
```

Under Windows x64 the four arguments arrive in `RCX`, `EDX`, `R8D` and `R9B`. One possible lowering is:

```asm
cmp  edx, r8d
jge  reject               ; signed maximum check only
movsxd rax, edx            ; preserve negative index
mov  byte ptr [rcx+rax], r9b
```

If `index == -1` is feasible and `length` is positive, the signed comparison permits the path and the store targets one byte before `buffer`. A prior `index >= 0` proof, a different base object or an unsigned branch changes the conclusion.

## Primitive and impact limits

Record whether the primitive is read or write, the reachable negative distance, access width, byte control and actual preceding object. A one-byte under-write can be security-relevant if it reaches a length or flag, but adjacency and later use require evidence. A wide wrapped address may simply fault.

Disclosure requires an observable use of under-read bytes. Code execution requires corruption or disclosure to develop a control primitive under target layout and mitigations; it does not follow from a negative index alone.

## Related knowledge and primary sources

`reference-native-integer-size-buffer-arithmetic` owns signedness, conversion and subtraction rules; `reference-native-bounds-objects-terminators` owns object ranges. This profile repeats the lower-bound requirement and machine-extension evidence needed for isolated classification.

Reviewed 2026-10-09 against [MITRE CWE-124](https://cwe.mitre.org/data/definitions/124.html), [MITRE CWE-127](https://cwe.mitre.org/data/definitions/127.html), C integer and array rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The source and assembly are constructed.
